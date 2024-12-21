import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'https://vista.ustc.edu.cn/download'
]

# 本地保存文件路径
save_path = 'cache/Shencs/vista'
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
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        
        # 获取文件扩展名
        file_extension = file_url.split('.')[-1].lower()
        # 如果标题没有扩展名，添加扩展名
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        
        # 保存文件到本地
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_list_page(url):
    """
    解析列表页，提取资料名称和跳转链接
    """
    soup = fetch_page(url)
    print(soup)
    import pdb; pdb.set_trace()
    if soup is None:
        return []

    files = []
    # 查找列表中的资料项
    list_items = soup.select('ul.ant-list-items li.ant-list-item')
    print(f"Found {len(list_items)} items on page {url}")

    for item in list_items:
        # 获取资料名称
        title_tag = item.select_one('h4.ant-list-item-meta-title')
        if not title_tag:
            continue
        title = title_tag.text.replace('资料名称: ', '').strip()

        # 获取下载按钮所属的链接
        button = item.select_one('button.ant-btn-primary')
        if not button:
            continue

        # 从按钮中提取跳转链接（可能需要进一步获取文件的实际下载地址）
        file_url = button.get('onclick')
        if file_url:
            # 如果文件链接是 JavaScript 形式的，需要从中提取 URL
            match = re.search(r'window\.open\(["\'](.+?)["\']', file_url)
            if match:
                file_url = match.group(1)
        files.append((file_url, title))
    return files

def crawl_site(url):
    """
    爬取列表页并处理文件下载
    """
    print(f"Processing list page: {url}")
    files = parse_list_page(url)

    for file_url, title in files:
        if file_url:
            print(f"  Found file: {title} -> {file_url}")
            save_file(file_url, title, save_path)
        else:
            print(f"  No file URL found for {title}")

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)