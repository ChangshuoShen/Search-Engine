from lxml import etree
import os
import requests

# 目标URL列表和分页URL模板
base_urls = [
    'https://saids.ustc.edu.cn/15443/list.htm',
    'https://saids.ustc.edu.cn/15410/list.htm'
]
page_url_templates = [
    'https://saids.ustc.edu.cn/15443/list{page}.htm',
    'https://saids.ustc.edu.cn/15410/list{page}.htm'
]

# 目标保存路径
save_path = 'cache/GMH/saids'

# 确保保存路径存在
os.makedirs(save_path, exist_ok=True)

def fetch_page(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    return etree.HTML(html)

def save_file(file_url, title, save_path):
    response = requests.get(file_url)
    file_extension = file_url.split('.')[-1]
    # 检查文件名是否已经包含扩展名
    if not title.endswith(f".{file_extension}"):
        title = f"{title}.{file_extension}"
    file_name = os.path.join(save_path, title)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print(f"File saved to {file_name}")

def parse_list_page(element):
    # 提取列表页中的文章链接、标题和日期的XPath表达式
    article_xpath = "//ul[@class='wp_article_list']/li//a/@href"
    title_xpath = "//ul[@class='wp_article_list']/li//a/@title"
    date_xpath = "//ul[@class='wp_article_list']/li//span[@class='Article_PublishDate']/text()"

    # 提取文章链接
    articles = element.xpath(article_xpath)
    titles = element.xpath(title_xpath)
    dates = element.xpath(date_xpath)

    return articles, titles, dates

def parse_article_page(element):
    if element is None:
        return [], [], []

    # 提取文章页中的文件链接和标题的XPath表达式
    file_xpath = "//a[@sudyfile-attr]/@href | //div[@class='wp_pdf_player']/@pdfsrc"
    title_xpath = "//a[@sudyfile-attr]/@sudyfile-attr | //div[@class='wp_pdf_player']/@sudyfile-attr"
    content_xpath = "//div[@class='wp_articlecontent']//text()"

    # 提取文件链接
    files = element.xpath(file_xpath)
    titles = element.xpath(title_xpath)
    content = element.xpath(content_xpath)

    # 提取标题
    titles = [eval(title)['title'] for title in titles]

    return files, titles, content

def get_max_page(element):
    # 获取最大页码
    max_page_xpath = "//em[@class='all_pages']/text()"
    max_page = element.xpath(max_page_xpath)
    return int(max_page[0]) if max_page else 1

def crawl_site(base_url, page_url_template):
    # 获取第一页内容并解析最大页码
    first_page_element = fetch_page(base_url)
    max_page = get_max_page(first_page_element)

    # 爬取所有页面
    for page in range(1, max_page + 1):
        if page == 1:
            element = first_page_element
        else:
            page_url = page_url_template.format(page=page)
            element = fetch_page(page_url)
        
        articles, titles, dates = parse_list_page(element)
        for article, title, date in zip(articles, titles, dates):
            article_url = 'https://saids.ustc.edu.cn' + article if article.startswith('/') else article
            article_element = fetch_page(article_url)
            files, file_titles, content = parse_article_page(article_element)
            if not files and not file_titles and not content:
                print(f"Skipping article: {article_url}")
                continue
            article_content = '\n'.join(content)
            save_article(title, date, article_content, save_path)
            for file, file_title in zip(files, file_titles):
                file_url = 'https://saids.ustc.edu.cn' + file if file.startswith('/') else file
                save_file(file_url, file_title, save_path)

def save_article(title, date, content, save_path):
    file_name = os.path.join(save_path, f"{title}.txt")
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Date: {date}\n\n")
        f.write(content)
    print(f"Article saved to {file_name}")

# 爬取所有目标URL
for base_url, page_url_template in zip(base_urls, page_url_templates):
    crawl_site(base_url, page_url_template)