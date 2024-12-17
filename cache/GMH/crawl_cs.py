import requests
from lxml import etree
import os
import re

# 目标URL列表和分页URL模板
base_urls = [
    'https://cs.ustc.edu.cn/20158/list.htm',
    'https://cs.ustc.edu.cn/20165/list.htm',
    'https://cs.ustc.edu.cn/20181/list.htm'
]
page_url_templates = [
    'https://cs.ustc.edu.cn/20158/list{page}.htm',
    'https://cs.ustc.edu.cn/20165/list{page}.htm',
    'https://cs.ustc.edu.cn/20181/list{page}.htm'
]

# 目标保存路径
save_path = 'cache/GMH/cs'
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
    # 更新 xpath 以匹配新的 HTML 结构
    article_xpath = "//ul[@class='news_list list2']//span[@class='news_title']/a/@href"
    title_xpath = "//ul[@class='news_list list2']//span[@class='news_title']/a/@title"
    date_xpath = "//ul[@class='news_list list2']//span[@class='news_meta']/text()"

    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    # 清理数据
    dates = [date.strip() for date in dates]
    titles = [title.strip() for title in titles]

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return [], [], []

    # 处理<a>标签中的文件链接
    a_file_xpath = "//div[@class='wp_articlecontent']//a[@href and not(contains(@href, '.jpg') or contains(@href, '.png'))]/@href"
    a_title_xpath = "//div[@class='wp_articlecontent']//a[@sudyfile-attr and not(contains(@href, '.jpg') or contains(@href, '.png'))]/@sudyfile-attr"
    
    # 处理<div>标签中的文件链接
    div_file_xpath = "//div[@class='wp_articlecontent']//div[@pdfsrc]/@pdfsrc"
    div_title_xpath = "//div[@class='wp_articlecontent']//div[@pdfsrc]/@id"
    
    # 处理新的文档链接
    new_file_xpath = "//div[@class='wp_articlecontent']//a[@sudyfile-attr and not(contains(@href, '.jpg') or contains(@href, '.png'))]/@href"
    new_title_xpath = "//div[@class='wp_articlecontent']//a[@sudyfile-attr and not(contains(@href, '.jpg') or contains(@href, '.png'))]/@sudyfile-attr"
    
    content_xpath = "//div[@class='wp_articlecontent']//text()"

    # 获取所有文件链接和标题
    a_files = element.xpath(a_file_xpath)
    a_titles = element.xpath(a_title_xpath)
    div_files = element.xpath(div_file_xpath)
    div_titles = element.xpath(div_title_xpath)
    new_files = element.xpath(new_file_xpath)
    new_titles = element.xpath(new_title_xpath)
    
    # 合并文件链接和标题
    files = a_files + div_files + new_files
    
    # 处理标题
    titles = []
    for title_attr in a_titles + new_titles:
        try:
            title_dict = eval(title_attr)
            titles.append(title_dict['title'])
        except:
            titles.append("untitled")
            
    # 为div类型的文件添加标题
    titles.extend([f"document_{id}.pdf" for id in div_titles])

    # 提取和清理文本内容
    content = element.xpath(content_xpath)
    content = [text.strip() for text in content if text.strip()]

    return files, titles, content

def get_max_page(element):
    # 调整为计算机学院网站的xpath
    max_page_xpath = "//span[@class='p_no']/text()"
    pages = element.xpath(max_page_xpath)
    if not pages:
        return 1
    return max(map(int, [p for p in pages if p.isdigit()]))

def crawl_site(base_url, page_url_template):
    first_page_element = fetch_page(base_url)
    max_page = get_max_page(first_page_element)

    for page in range(1, max_page + 1):
        if page == 1:
            element = first_page_element
        else:
            page_url = page_url_template.format(page=page)
            element = fetch_page(page_url)
        
        articles, titles, dates = parse_list_page(element)
        for article, title, date in zip(articles, titles, dates):
            article_url = 'https://cs.ustc.edu.cn' + article if article.startswith('/') else article
            article_element = fetch_page(article_url)
            files, file_titles, content = parse_article_page(article_element)
            if not files and not file_titles and not content:
                print(f"Skipping article: {article_url}")
                continue
            article_content = '\n'.join(content)
            save_article(title, date, article_content, save_path)
            for file, file_title in zip(files, file_titles):
                file_url = 'https://cs.ustc.edu.cn' + file if file.startswith('/') else file
                save_file(file_url, file_title, save_path)

def save_article(title, date, content, save_path):
    title = clean_filename(title)
    file_name = os.path.join(save_path, f"{title}.txt")
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Date: {date}\n\n")
        f.write(content)
    print(f"Article saved to {file_name}")

# 爬取所有目标URL
for base_url, page_url_template in zip(base_urls, page_url_templates):
    crawl_site(base_url, page_url_template)