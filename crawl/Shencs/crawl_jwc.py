import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'https://www.teach.ustc.edu.cn/download/all',
] + [f'https://www.teach.ustc.edu.cn/download/all/page/{i}' for i in range(2, 16)]

# 目标保存路径
save_path = 'cache/Shencs/teach'
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

def parse_detail_page(detail_url):
    """
    解析详情页，提取文件下载链接和标题
    """
    soup = fetch_page(detail_url)
    if soup is None:
        return None, None

    # 查找手动下载的链接
    download_link = soup.select_one('a.download-link')
    if download_link:
        file_url = download_link.get("href", "").strip()
        title = download_link.get("download", "").strip() or download_link.text.strip()
        full_url = file_url if file_url.startswith("http") else f"https://www.teach.ustc.edu.cn{file_url}"
        return full_url, title
    return None, None

def parse_list_page(url):
    """
    解析列表页，提取详情页链接和相关信息
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    details = []
    # 查找 <ul class="article-list with-tag download-list"> 中的 <li>
    list_items = soup.select('ul.article-list.with-tag.download-list li a')
    print(f"Found {len(list_items)} articles on page {url}")  # 调试输出找到的条目数

    for item in list_items:
        detail_url = item.get("href", "").strip()
        detail_title = item.text.strip()
        
        # 转换为完整 URL（如果是相对路径）
        full_detail_url = detail_url if detail_url.startswith("http") else f"https://www.teach.ustc.edu.cn{detail_url}"
        details.append((full_detail_url, detail_title))
    return details

def crawl_site(url):
    """
    爬取列表页并处理详情页中的文件下载
    """
    print(f"Processing list page: {url}")
    details = parse_list_page(url)
    
    for detail_url, detail_title in details:
        print(f"  Found detail page: {detail_title} -> {detail_url}")
        file_url, file_title = parse_detail_page(detail_url)
        if file_url and file_title:
            save_file(file_url, file_title, save_path)
        else:
            print(f"  No downloadable file found on detail page: {detail_url}")

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)