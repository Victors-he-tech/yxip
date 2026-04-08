#!/usr/bin/env python3
"""
批量标注 IP 文件的国家/地区
依赖：pip install py-ip2region
"""
import os
import sys
import glob
import urllib.request

# 下载 ip2region.xdb 数据库文件
DB_PATH = "ip2region.xdb"
DB_URL = "https://raw.githubusercontent.com/lionsoul2014/ip2region/master/data/ip2region.xdb"

def download_db():
    print("正在下载 IP 数据库...")
    urllib.request.urlretrieve(DB_URL, DB_PATH)
    print("数据库下载完成。")

if not os.path.exists(DB_PATH):
    download_db()

# 导入 ip2region
from ip2region import Ip2Region

searcher = Ip2Region(DB_PATH)

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
                # result 格式: "国家|区域|省份|城市|ISP"
                country = result.split('|')[0] if result else "未知"
            except:
                country = "查询失败"
            fout.write(f"{ip} -> {country}\n")

if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "ips"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results"

    os.makedirs(output_dir, exist_ok=True)

    for ip_file in glob.glob(f"{input_dir}/*.txt"):
        base = os.path.basename(ip_file)
        out_file = os.path.join(output_dir, base.replace('.txt', '_annotated.txt'))
        print(f"处理: {ip_file} -> {out_file}")
        annotate_file(ip_file, out_file)

    print("所有 IP 文件标注完成！")
