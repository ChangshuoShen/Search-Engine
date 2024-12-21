import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'https://finance.ustc.edu.cn/xzzx/list.psp',
    'https://finance.ustc.edu.cn/xzzx/list2.psp',
    'https://finance.ustc.edu.cn/xzzx/list3.psp',
    'https://finance.ustc.edu.cn/xzzx/list4.psp',
    'https://finance.ustc.edu.cn/xzzx/list5.psp'
]

# 基础 URL，用于处理相对路径
base_url = 'https://finance.ustc.edu.cn'

# 本地保存文件路径
save_path = 'cache/Shencs/finance'
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
        
        file_extension = file_url.split('.')[-1].lower()
        # 添加文件扩展名（如果标题没有扩展名）
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_detail_page(detail_url):
    """
    解析详情页，提取文件下载链接和标题
    """
    soup = fetch_page(detail_url)
    if soup is None:
        return []

    files = []
    # 查找包含文件下载链接的 <a> 标签
    file_links = soup.select('div.wp_articlecontent a[sudyfile-attr]')
    for file_link in file_links:
        file_url = file_link.get("href", "").strip()
        title_match = re.search(r"'title':'(.*?)'", file_link.get("sudyfile-attr", ""))
        title = title_match.group(1) if title_match else file_link.text.strip()

        # 转换为完整 URL
        full_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
        files.append((full_url, title))
    return files

def parse_list_page(url):
    """
    解析列表页，提取文件下载链接或详情页链接
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    files = []
    # 查找 <ul class="news_list list2"> 下的 <li> 元素
    list_items = soup.select('ul.news_list.list2 li a')
    print(f"Found {len(list_items)} items on page {url}")

    for item in list_items:
        link_url = item.get("href", "").strip()
        title = item.get("title", "").strip()

        # 如果链接是直接文件下载链接
        if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip)$', link_url, re.IGNORECASE):
            full_url = link_url if link_url.startswith("http") else f"{base_url}{link_url}"
            files.append((full_url, title))
        else:  # 如果链接是详情页
            detail_url = link_url if link_url.startswith("http") else f"{base_url}{link_url}"
            files.append((detail_url, None))  # 标记为详情页链接
    return files

def crawl_site(url):
    """
    爬取列表页并处理文件下载
    """
    print(f"Processing list page: {url}")
    items = parse_list_page(url)
    # print(items)

    for item_url, item_title in items:
        if item_title:  # 如果是直接文件下载链接
            print(f"  Found file: {item_title} -> {item_url}")
            save_file(item_url, item_title, save_path)
        else:  # 如果是详情页链接
            print(f"  Found detail page: {item_url}")
            files = parse_detail_page(item_url)
            for file_url, file_title in files:
                print(f"    Found file in detail page: {file_title} -> {file_url}")
                save_file(file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)