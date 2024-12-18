import requests
from lxml import etree
import os
import re

# 目标URL列表
urls = [
    'https://scms.ustc.edu.cn/2418/list.htm',
    'https://scms.ustc.edu.cn/2416/list.htm',
    'https://scms.ustc.edu.cn/llxxcl/list.htm'
]

# 基础URL，用于处理相对路径
base_url = 'https://scms.ustc.edu.cn'

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
    article_xpath = "//ul[@class='wp_article_list']/li//a/@href"
    title_xpath = "//ul[@class='wp_article_list']/li//a/@title"
    date_xpath = "//ul[@class='wp_article_list']/li//span[@class='Article_PublishDate']/text()"

    # 提取文章链接和标题
    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return [], [], ""

    # 处理<a>标签中的文件链接和标题
    file_xpath = "//div[@class='wp_articlecontent']//a/@href"
    file_title_xpath = "//div[@class='wp_articlecontent']//a/span/text()"
    pdf_xpath = "//div[@class='wp_articlecontent']//div[@pdfsrc]/@pdfsrc"
    pdf_title_xpath = "//div[@class='wp_articlecontent']//div[@sudyfile-attr]/@sudyfile-attr"
    article_content_xpath = "//div[@class='wp_articlecontent']//text()"
    
    # 获取所有文件链接和标题
    files = element.xpath(file_xpath)
    file_titles = element.xpath(file_title_xpath)
    pdfs = element.xpath(pdf_xpath)
    pdf_titles = element.xpath(pdf_title_xpath)
    article_content = element.xpath(article_content_xpath)
    
    # 处理标题
    processed_titles = []
    for title in file_titles:
        processed_titles.append(clean_filename(title))
    
    # 处理嵌入的PDF文件标题
    for title in pdf_titles:
        title_dict = eval(title)
        processed_titles.append(clean_filename(title_dict['title']))

    # 合并文章内容
    article_text = "\n".join(article_content).strip()

    return files + pdfs, processed_titles, article_text

def is_direct_file_url(url):
    return any(url.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.pptx'])

def crawl_site(url):
    page_number = 1
    while True:
        page_url = f"{url[:-4]}_{page_number}.htm" if page_number > 1 else url
        element = fetch_page(page_url)
        articles, titles, dates = parse_list_page(element)
        if not articles:
            break
        for article, title, date in zip(articles, titles, dates):
            article_url = base_url + article if article.startswith('/') else article
            print(f"Processing article: {article_url}")  # 添加调试输出
            if is_direct_file_url(article_url):
                save_file(article_url, title, save_path)
            else:
                article_element = fetch_page(article_url)
                files, file_titles, article_content = parse_article_page(article_element)
                if files:
                    print(f"Found files: {list(zip(files, file_titles))}")  # 添加调试输出
                else:
                    print(f"No files found in article: {article_url}")  # 添加调试输出
                for file, file_title in zip(files, file_titles):
                    file_url = base_url + file if file.startswith('/') else file
                    print(f"Downloading: {file_url}")  # 添加调试输出
                    save_file(file_url, file_title, save_path)
                if article_content:
                    save_article_content(article_content, title, save_path)
        page_number += 1

# 爬取所有目标URL
for url in urls:
    crawl_site(url)