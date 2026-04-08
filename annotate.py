#!/usr/bin/env python3
"""
批量标注 IP 文件的国家/地区
依赖：pip install py-ip2region
"""
import os
import sys
import glob
import urllib.request
import ssl

# 解决某些环境下 SSL 证书问题
ssl._create_default_https_context = ssl._create_unverified_context

# 数据库文件路径
DB_PATH = "ip2region_v4.xdb"

# 多个备用下载地址（按优先级排序）
DB_URLS = [
    # 官方 GitHub raw 链接
    "https://raw.githubusercontent.com/lionsoul2014/ip2region/master/data/ip2region_v4.xdb",
    # 官方 GitHub 直接链接
    "https://github.com/lionsoul2014/ip2region/raw/master/data/ip2region_v4.xdb",
    # 备用：jsDelivr CDN 加速
    "https://cdn.jsdelivr.net/gh/lionsoul2014/ip2region@master/data/ip2region_v4.xdb",
]

def download_db():
    """下载数据库文件，尝试多个源"""
    for url in DB_URLS:
        try:
            print(f"尝试下载: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(DB_PATH, 'wb') as f:
                    f.write(response.read())
            file_size = os.path.getsize(DB_PATH)
            print(f"数据库下载成功，大小: {file_size} 字节")
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            continue
    
    print("所有下载源均失败，请检查网络连接。")
    return False

# 检查并下载数据库
if not os.path.exists(DB_PATH):
    print("未找到数据库文件，开始下载...")
    if not download_db():
        sys.exit(1)

# 导入 ip2region
from ip2region import Ip2Region

try:
    searcher = Ip2Region(DB_PATH)
except Exception as e:
    print(f"加载数据库失败: {e}")
    sys.exit(1)

def annotate_file(input_path, output_path):
    """处理单个文件，给每行 IP 添加国家标注"""
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            ip = line.strip()
            if not ip or ip.startswith('#'):
                fout.write(line)
                continue
            try:
                result = searcher.search(ip)
                country = result.split('|')[0] if result else "未知"
            except:
                country = "查询失败"
            fout.write(f"{ip} -> {country}\n")

if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "ips"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results"

    os.makedirs(output_dir, exist_ok=True)

    txt_files = glob.glob(f"{input_dir}/*.txt")
    if not txt_files:
        print(f"警告: 在 {input_dir} 目录下没有找到 .txt 文件")
        sys.exit(0)

    for ip_file in txt_files:
        base = os.path.basename(ip_file)
        out_file = os.path.join(output_dir, base.replace('.txt', '_annotated.txt'))
        print(f"处理: {ip_file} -> {out_file}")
        annotate_file(ip_file, out_file)

    print("所有 IP 文件标注完成！")
