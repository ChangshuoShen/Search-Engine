import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'https://young.ustc.edu.cn/15056/list.htm',
    'https://young.ustc.edu.cn/15056/list2.htm'
]

# 基础 URL，用于处理相对路径
base_url = 'https://young.ustc.edu.cn'

# 本地保存文件路径
save_path = 'cache/Shencs/young'
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

    # 查找 iframe 中的 PDF 文件链接
    iframe = soup.select_one('iframe.wp_pdf_player')  # 更精确的选择器
    if iframe:
        pdf_url = iframe.get("src", "").strip()
        if pdf_url:
            full_pdf_url = pdf_url if pdf_url.startswith("http") else f"{base_url}{pdf_url}"
            title = full_pdf_url.split('/')[-1]  # 使用文件名作为标题
            files.append((full_pdf_url, title))

    # 查找 <a> 标签中直接包含的文件链接
    links = soup.select('a[sudyfile-attr]')
    for link in links:
        file_url = link.get("href", "").strip()
        sudyfile_attr = link.get("sudyfile-attr", "")
        title_match = re.search(r"'title':'(.*?)'", sudyfile_attr)
        title = title_match.group(1) if title_match else link.text.strip()
        title = title.replace('&nbsp;', ' ')  # 替换 HTML 中的空格实体

        # 转换为完整 URL
        full_file_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
        files.append((full_file_url, title))

    return files

def parse_list_page(url):
    """
    解析列表页，提取详情页链接和直接下载文件链接
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    details = []
    # 查找 <ul class="text-ul"> 下的 <li> 元素
    list_items = soup.select('ul.text-ul li a')
    print(f"Found {len(list_items)} items on page {url}")

    for item in list_items:
        link_url = item.get("href", "").strip()
        title = item.get("title", "").strip()

        # 判断链接是否为直接文件下载
        if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip)$', link_url, re.IGNORECASE):
            full_url = link_url if link_url.startswith("http") else f"{base_url}{link_url}"
            details.append((full_url, title, True))  # True 表示直接下载链接
        else:
            full_url = link_url if link_url.startswith("http") else f"{base_url}{link_url}"
            details.append((full_url, title, False))  # False 表示详情页链接
    return details

def crawl_site(url):
    """
    爬取列表页并处理文件下载
    """
    print(f"Processing list page: {url}")
    details = parse_list_page(url)

    for detail_url, detail_title, is_direct_download in details:
        if is_direct_download:  # 直接下载文件
            print(f"  Found direct download: {detail_title} -> {detail_url}")
            save_file(detail_url, detail_title, save_path)
        else:  # 跳转到详情页处理
            print(f"  Found detail page: {detail_title} -> {detail_url}")
            files = parse_detail_page(detail_url)
            for file_url, file_title in files:
                print(f"    Found file in detail page: {file_title} -> {file_url}")
                save_file(file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)