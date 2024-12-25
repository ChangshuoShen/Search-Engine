import requests
from bs4 import BeautifulSoup
import os
import re

# 目标URL列表
urls = [
    'https://ese.ustc.edu.cn/wdxz_26766/list.htm',
    'https://ese.ustc.edu.cn/wdxz_26766/list2.htm',
]

# 基础URL，用于处理相对路径
base_url = 'https://ese.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/Shencs/ese'
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
    解析列表页，并提取文件下载链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    files = []
    # 查找 class 为 "item" 的 <div> 元素
    items = soup.select('div.item')
    print(f"Found {len(items)} items on page {url}")  # 调试输出找到的条目数

    for item in items:
        title_elem = item.select_one('p.dot')  # 查找文件标题
        link_elem = item.select_one('div.btn a')  # 查找下载链接

        if title_elem and link_elem:
            title = title_elem.text.strip()
            file_url = link_elem.get('href', '').strip()
            # 转换为完整的 URL
            full_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
            files.append((full_url, title))
    return files

def crawl_site(url):
    """
    爬取列表页并下载文件
    """
    print(f"Processing list page: {url}")
    files = parse_list_page(url)
    
    for file_url, file_title in files:
        save_file(file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)