import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://sz.ustc.edu.cn/wdxz_list/98-1.html',
    'https://sz.ustc.edu.cn/wdxz_list/120-1.html'
]

# 基础URL，用于处理相对路径
base_url = 'https://sz.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/GMH/suzhou'
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

def parse_list_page(element):
    # 提取列表页中的文章链接、标题和日期的XPath表达式
    article_xpath = "//ul[@id='article_list_ul']/li/a/@href"
    title_xpath = "//ul[@id='article_list_ul']/li/a/@title"
    date_xpath = "//ul[@id='article_list_ul']/li/a//span[@class='n-f-2 n-c-2 n-block n-text-right']/text()"

    # 提取文章链接
    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return [], []

    # 处理<a>标签中的文件链接
    file_xpath = "//div[@id='divContent']//a[@href]/@href"
    title_xpath = "//div[@id='divContent']//a[@href]/@title"
    
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
    articles, titles, dates = parse_list_page(element)
    for article, title, date in zip(articles, titles, dates):
        article_url = base_url + article if article.startswith('/') else article
        print(f"Processing article: {article_url}")  # 添加调试输出
        article_element = fetch_page(article_url)
        files, file_titles = parse_article_page(article_element)
        if files:
            print(f"Found files: {list(zip(files, file_titles))}")  # 添加调试输出
        for file, file_title in zip(files, file_titles):
            file_url = base_url + file if file.startswith('/') else file
            print(f"Downloading: {file_url}")  # 添加调试输出
            save_file(file_url, file_title, save_path)

# 爬取所有目标URL
for url in urls:
    crawl_site(url)