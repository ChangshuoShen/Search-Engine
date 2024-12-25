import requests
from lxml import etree
import os
import re
import time

# 目标URL列表和分页URL模板
base_urls = [
    'https://sgy.ustc.edu.cn/notices',
    'https://sgy.ustc.edu.cn/admissions'
]
page_url_templates = [
    'https://sgy.ustc.edu.cn/notices?page={page}',
    'https://sgy.ustc.edu.cn/admissions?page={page}'
]

# 目标保存路径
save_path = 'cache/GMH/young'
print(f"Saving articles to: {save_path}")
os.makedirs(save_path, exist_ok=True)

def fetch_page(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    response.encoding = 'utf-8'
    return etree.HTML(response.text)

def clean_filename(filename):
    # 移除非法字符
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    print(f"Cleaned filename: {cleaned_filename}")  # Debugging line
    return cleaned_filename

def save_article(title, publisher, publish_date, content, save_path):
    title = clean_filename(title)
    file_name = os.path.join(save_path, f"{title}.txt")
    
    print(f"Attempting to save article: {file_name}")  # Debugging line
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Publisher: {publisher}\n")
        f.write(f"Publish Date: {publish_date}\n\n")
        f.write(content)
    print(f"Article saved to {file_name}")

def parse_list_page(element):
    # 更新 xpath 以匹配新的 HTML 结构
    article_xpath = "//ul[@class='notice_list clearfix']//a/@href"
    title_xpath = "//ul[@class='notice_list clearfix']//a//h2/text()"
    date_xpath = "//ul[@class='notice_list clearfix']//div[@class='notice_list_date']/p[2]/text()"

    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    # 清理数据
    dates = [date.strip() for date in dates]
    titles = [title.strip() for title in titles]

    # 输出找到的文章链接
    for article, title in zip(articles, titles):
        print(f"Found article: {title} at {article}")

    return articles, titles

def extract_article_content(element):
    # Extract title
    title = element.xpath("//h2[@class='detail_title']/text()")[0].strip()

    # Extract publisher and date
    tags = element.xpath("//div[@class='detail_tags']//span/text()")
    publisher = tags[1].strip() if len(tags) > 1 else ''
    publish_date = tags[3].strip() if len(tags) > 3 else ''

    # Extract content
    content = element.xpath("//div[@class='detail_content fr-view']//text()")
    content = [text.strip() for text in content if text.strip()]

    print(f"Extracted content length: {len(content)}")  # Debugging line

    return title, publisher, publish_date, '\n'.join(content)

def get_max_page(element):
    # 调整为目标网站的xpath
    max_page_xpath = "//ul[@class='pagination']//a[last()]/@href"
    pages = element.xpath(max_page_xpath)
    if not pages:
        return 1
    max_page = re.search(r'page=(\d+)', pages[0])
    return int(max_page.group(1)) if max_page else 1

def crawl_site(base_url, page_url_template):
    first_page_element = fetch_page(base_url)
    max_page = get_max_page(first_page_element)

    for page in range(1, max_page + 1):
        print(f"\nProcessing page {page}")
        if page == 1:
            element = first_page_element
        else:
            page_url = page_url_template.format(page=page)
            element = fetch_page(page_url)
        
        articles, titles = parse_list_page(element)

        for article, title in zip(articles, titles):
            article_url = 'https://sgy.ustc.edu.cn' + article if article.startswith('/') else article
                        
            # Fetch and process article
            article_element = fetch_page(article_url)
            article_title, publisher, publish_date, content = extract_article_content(article_element)
            
            # Save article
            save_article(article_title, publisher, publish_date, content, save_path)
            
# Scrape all target URLs
for base_url, page_url_template in zip(base_urls, page_url_templates):
    crawl_site(base_url, page_url_template)