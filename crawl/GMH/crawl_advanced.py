import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://iat.ustc.edu.cn/iat/wdxz/20220329/5626.html',
    'https://iat.ustc.edu.cn/iat/wdxz/20220329/5625.html',
    'https://iat.ustc.edu.cn/iat/wdxz/20220329/5624.html',
    'https://iat.ustc.edu.cn/iat/wdxz/20220329/5623.html'
]

# 基础URL，用于处理相对路径
base_url = 'https://iat.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/GMH/advanced'
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
        file_extension = file_url.split('.')[-1].lower()
        
        # 处理文件名
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_article_page(element):
    if element is None:
        return [], []

    # 处理<a>标签中的文件链接
    file_xpath = "//div[@class='news-detail-news-con']//a[@href]/@href"
    title_xpath = "//div[@class='news-detail-news-con']//a[@href]/@title"
    
    # 获取所有文件链接和标题
    files = element.xpath(file_xpath)
    titles = element.xpath(title_xpath)
    
    # 处理标题
    processed_titles = []
    for title in titles:
        processed_titles.append(clean_filename(title))

    return files, processed_titles

def crawl_site(url):
    element = fetch_page(url)
    files, titles = parse_article_page(element)
    for file, title in zip(files, titles):
        file_url = base_url + file if file.startswith('/') else file
        save_file(file_url, title, save_path)

# 爬取所有目标URL
for url in urls:
    crawl_site(url)