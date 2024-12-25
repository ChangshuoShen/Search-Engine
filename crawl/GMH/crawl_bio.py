import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://biox.ustc.edu.cn/jdxw/list.htm',
    'https://biox.ustc.edu.cn/xsbg/list.htm'
]

# 基础URL，用于处理相对路径
base_url = 'https://biox.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/GMH/bio'
os.makedirs(save_path, exist_ok=True)

def fetch_page(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    return etree.HTML(html)

def clean_filename(filename):
    # 移除非法字符
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_article_content(content, title, save_path):
    try:
        title = clean_filename(title)
        file_name = os.path.join(save_path, f"{title}.txt")
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Article saved to {file_name}")
    except Exception as e:
        print(f"Error saving article {title}: {str(e)}")

def parse_list_page(element):
    # 提取列表页中的文章链接、标题和日期的XPath表达式
    article_xpath = "//div[@class='NewsList']//li/a/@href"
    title_xpath = "//div[@class='NewsList']//li/a/p[@class='tit']/a/text()"
    date_xpath = "//div[@class='NewsList']//li/a/span[@class='date']/text()"

    # 提取文章链接和标题
    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return ""

    # 提取文章内容的XPath表达式
    article_content_xpath = "//article[@class='SinglePage']//text()"
    
    # 获取文章内容
    article_content = element.xpath(article_content_xpath)
    
    # 合并文章内容
    article_text = "\n".join(article_content).strip()

    return article_text

def get_next_page_url(element):
    next_page_xpath = "//ul[@class='wp_paging clearfix']//a[@class='next']/@href"
    next_page = element.xpath(next_page_xpath)
    if next_page and next_page[0] != 'javascript:void(0);':
        return base_url + next_page[0] if next_page[0].startswith('/') else next_page[0]
    return None

def crawl_site(url):
    while url:
        element = fetch_page(url)
        articles, titles, dates = parse_list_page(element)
        for article, title, date in zip(articles, titles, dates):
            article_url = base_url + article if article.startswith('/') else article
            print(f"Processing article: {article_url}")  # 添加调试输出
            article_element = fetch_page(article_url)
            article_content = parse_article_page(article_element)
            if article_content:
                save_article_content(article_content, title, save_path)
        url = get_next_page_url(element)

# 爬取所有目标URL
for url in urls:
    crawl_site(url)