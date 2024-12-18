import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://sme.ustc.edu.cn/wdxz/list.htm',
    'https://sme.ustc.edu.cn/wdxz_30880/list.htm',
    'https://sme.ustc.edu.cn/wdxz_30885/list.htm'
]

# 基础URL，用于处理相对路径
base_url = 'https://sme.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/GMH/micro'
os.makedirs(save_path, exist_ok=True)

def fetch_page(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    return etree.HTML(html)

def clean_filename(filename):
    # 移除非法字符
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_file(file_url, title, save_path):
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        file_extension = file_url.split('.')[-1].lower()
        
        # 处理文件名
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.pptx')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_list_page(element):
    # 提取列表页中的文档链接和标题的XPath表达式
    file_xpath = "//div[@class='DownList']//a/@href"
    title_xpath = "//div[@class='DownList']//a//div[@class='cell info']/text()"

    # 提取文档链接和标题
    files = element.xpath(file_xpath)
    titles = element.xpath(title_xpath)

    return files, titles

def is_direct_file_url(url):
    return any(url.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.pptx'])

def crawl_site(url):
    page_number = 1
    while True:
        page_url = f"{url[:-4]}_{page_number}.htm" if page_number > 1 else url
        element = fetch_page(page_url)
        files, titles = parse_list_page(element)
        if not files:
            break
        for file, title in zip(files, titles):
            file_url = base_url + file if file.startswith('/') else file
            print(f"Downloading: {file_url}")  # 添加调试输出
            save_file(file_url, title, save_path)
        page_number += 1

# 爬取所有目标URL
for url in urls:
    crawl_site(url)