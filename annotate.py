#!/usr/bin/env python3
"""
批量标注 IP 文件的国家/地区
"""
import os
import sys
import glob
from ip2region import Ip2Region

# 下载 ip2region.xdb 数据库（若不存在）
DB_PATH = "ip2region.xdb"
DB_URL = "https://raw.githubusercontent.com/lionsoul2014/ip2region/master/data/ip2region.xdb"

def download_db():
    import urllib.request
    print(f"正在下载 IP 数据库...")
    urllib.request.urlretrieve(DB_URL, DB_PATH)
    print("下载完成。")

if not os.path.exists(DB_PATH):
    download_db()

searcher = Ip2Region(DB_PATH)

def annotate_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            ip = line.strip()
            if not ip or ip.startswith('#'):
                fout.write(line)
                continue
            try:
                region = searcher.search(ip)
                country = region.split('|')[0] if region else "未知"
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
        print(f"处理 {ip_file} -> {out_file}")
        annotate_file(ip_file, out_file)

    print("所有 IP 文件标注完成！")
  添加标注脚本
