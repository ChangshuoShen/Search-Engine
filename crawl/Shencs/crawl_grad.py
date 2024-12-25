import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'http://gradschool.ustc.edu.cn/column/178',
    'http://gradschool.ustc.edu.cn/column/64',
    'http://gradschool.ustc.edu.cn/column/65',
    'http://gradschool.ustc.edu.cn/column/66',
    'http://gradschool.ustc.edu.cn/column/67',
    'http://gradschool.ustc.edu.cn/column/68',
    'http://gradschool.ustc.edu.cn/column/69',
    'http://gradschool.ustc.edu.cn/column/70',
]

# 基础 URL，用于处理相对路径
base_url = 'http://gradschool.ustc.edu.cn'

# 本地保存文件路径
save_path = 'cache/Shencs/grad'
os.makedirs(save_path, exist_ok=True)

def fetch_page(url):
    """
    获取网页内容并解析为 BeautifulSoup 对象
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Failed to fetch page {url}: {e}")
        return None

def clean_filename(filename):
    """
    移除非法字符
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_file(file_url, title, save_path):
    """
    下载并保存文件
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        
        file_extension = file_url.split('.')[-1].lower()
        # 添加文件扩展名（如果标题没有扩展名）
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_list_page(url):
    """
    解析列表页，提取文件下载链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    files = []
    # 查找 <ul> 下的 <li> 元素
    list_items = soup.select('div.r-box ul li a')
    print(f"Found {len(list_items)} files on page {url}")  # 调试输出找到的条目数

    for item in list_items:
        file_url = item.get("href", "").strip()
        title = item.text.strip()
        
        # 拼接完整 URL
        full_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
        files.append((full_url, title))
    return files

def crawl_site(url):
    """
    爬取列表页并下载文件
    """
    print(f"Processing page: {url}")
    files = parse_list_page(url)
    
    for file_url, file_title in files:
        print(f"  Found file: {file_title} -> {file_url}")
        save_file(file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)