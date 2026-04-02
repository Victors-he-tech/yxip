import requests
import os
import time

# 配置：输入和输出文件名
INPUT_FILE = 'myip.txt'
OUTPUT_FILE = 'myip-location.txt'

def get_location(ip):
    """从接口获取地理位置"""
    try:
        # 使用 ip-api 中文接口
        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('city') or data.get('country') or "未知地点"
            elif data.get('message') == 'reserved range':
                return "局域网/内网IP"
        return "查询失败"
    except Exception:
        return "查询出错"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误：找不到输入文件 {INPUT_FILE}，请确保仓库根目录有这个文件。")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    print(f"开始处理 {len(lines)} 行数据，结果将保存至 {OUTPUT_FILE}...")

    for index, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 提取 IP 部分（兼容已有 # 的情况，确保重新标注）
        raw_ip_part = line.split('#')[0]
        # 提取纯 IP 用于查询
        ip_only = raw_ip_part.split(':')[0]
        
        print(f"正在查询 [{index+1}/{len(lines)}]: {ip_only} ...")
        location = get_location(ip_only)
        
        # 拼接结果
        new_line = f"{raw_ip_part}#{location}"
        processed_lines.append(new_line)

        # 频率限制保护（每1.5秒一次）
        time.sleep(1.5)

    # 写入新文件，不覆盖旧文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_lines) + '\n')
    
    print(f"✅ 处理完成！结果已另存为: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
