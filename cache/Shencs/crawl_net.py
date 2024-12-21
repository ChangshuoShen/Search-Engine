import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'http://ustcnet.ustc.edu.cn/33489/list.psp',
    'http://ustcnet.ustc.edu.cn/33489/list2.psp',
    'http://ustcnet.ustc.edu.cn/33490/list.htm',
    'http://ustcnet.ustc.edu.cn/33490/list2.htm',
    'http://ustcnet.ustc.edu.cn/33490/list3.htm',
    'http://ustcnet.ustc.edu.cn/33490/list4.htm',
    'http://ustcnet.ustc.edu.cn/33491/list.htm',
    'http://ustcnet.ustc.edu.cn/33491/list2.htm',
    'http://ustcnet.ustc.edu.cn/33492/list.htm'
]

# 基础 URL，用于处理相对路径
base_url = 'http://ustcnet.ustc.edu.cn'

# 本地保存文件路径
save_path = 'cache/Shencs/ustcnet'
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
    # print(soup)
    # import pdb; pdb.set_trace()
    if soup is None:
        return []

    files = []
    # 查找 iframe 中的 PDF 文件链接
    iframe = soup.select_one('div.wp_pdf_player')
    if iframe:
        pdf_url = iframe.get("src", "").strip()
        if pdf_url:
            # 提取文件名作为标题
            title = pdf_url.split('/')[-1].split('?')[0]
            # 转换为完整文件 URL
            full_pdf_url = pdf_url if pdf_url.startswith("http") else f"{base_url}{pdf_url}"
            files.append((full_pdf_url, title))
    else:
        print(f"No iframe found in {detail_url}")
    return files

def parse_list_page(url):
    """
    解析列表页，提取详情页链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    details = []
    # 查找列表中的 <a> 标签
    list_items = soup.select('ul.news_list li a')
    print(f"Found {len(list_items)} items on page {url}")

    for item in list_items:
        link_url = item.get("href", "").strip()
        title = item.get("title", "").strip()

        # 转换为完整 URL
        full_url = link_url if link_url.startswith("http") else f"{base_url}{link_url}"
        details.append((full_url, title))
    return details

def crawl_site(url):
    """
    爬取列表页并处理文件下载
    """
    print(f"Processing list page: {url}")
    details = parse_list_page(url)

    for detail_url, detail_title in details:
        print(f"  Found detail page: {detail_title} -> {detail_url}")
        files = parse_detail_page(detail_url)
        for file_url, file_title in files:
            print(f"    Found file in detail page: {file_title} -> {file_url}")
            save_file(file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)