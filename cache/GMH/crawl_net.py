import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://ustcnet.ustc.edu.cn/33490/list.htm',
    'https://ustcnet.ustc.edu.cn/33491/list.htm',
    'https://ustcnet.ustc.edu.cn/33492/list.htm'
]

# 基础URL，用于处理相对路径
base_url = 'https://ustcnet.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/GMH/net'
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
    article_xpath = "//ul[@class='news_list list2']//li//a/@href"
    title_xpath = "//ul[@class='news_list list2']//li//a/@title"
    date_xpath = "//ul[@class='news_list list2']//li//span[@class='news_meta']/text()"

    # 提取文章链接和标题
    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return [], [], ""

    # 更新的XPath：正确提取pdfsrc属性
    pdf_xpath = "//div[@class='wp_pdf_player']/@pdfsrc"
    
    # 提取文章内容的XPath表达式
    article_content_xpath = "//div[@class='wp_articlecontent']//text()"
    
    # 获取PDF文件链接
    pdfs = element.xpath(pdf_xpath)
    
    # 获取文章内容
    article_content = element.xpath(article_content_xpath)
    
    # 合并文章内容
    article_text = "\n".join(article_content).strip()

    return pdfs, article_text

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
            pdfs, article_content = parse_article_page(article_element)
            
            # 下载PDF文件
            if pdfs:
                for pdf in pdfs:
                    pdf_url = base_url + pdf if pdf.startswith('/') else pdf
                    save_file(pdf_url, title, save_path)
            
            # 保存文章内容
            if article_content:
                save_article_content(article_content, title, save_path)
        
        # 获取下一页URL
        url = get_next_page_url(element)

# 爬取所有目标URL
for url in urls:
    crawl_site(url)
