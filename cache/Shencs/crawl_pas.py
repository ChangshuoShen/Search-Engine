import requests
from bs4 import BeautifulSoup
import os
import re

# 目标URL列表
urls = [
    'https://pas.ustc.edu.cn/wdxz/list.htm',
    'https://pas.ustc.edu.cn/wdxz/list2.htm',
    'https://pas.ustc.edu.cn/kxxw/list.htm',
]

mpa_url = 'https://ustc-mpa.ustc.edu.cn/wdxz/list.htm'

# 基础URL，用于处理相对路径
base_url = 'https://pas.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/Shencs/pas'
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
        response = requests.get(file_url)
        response.raise_for_status()
        
        file_extension = file_url.split('.')[-1].lower()
        # 添加文件扩展名（如果标题没有扩展名）
        if not title.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            title = f"{title}.{file_extension}"
        
        title = clean_filename(title)
        file_name = os.path.join(save_path, title)
        
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {file_name}")
    except Exception as e:
        print(f"Error saving file {title}: {str(e)}")

def parse_article_page(article_url):
    """
    解析文章详情页，提取下载文件链接和标题
    """
    soup = fetch_page(article_url)
    if soup is None:
        return []

    files = []
    # 找到具有 "sudyfile-attr" 属性的 <a> 标签
    file_links = soup.select('a[sudyfile-attr]')
    for file_link in file_links:
        file_url = file_link.get("href", "").strip()
        sudyfile_attr = file_link.get("sudyfile-attr", "")
        title_match = re.search(r"'title':'(.*?)'", sudyfile_attr)
        title = title_match.group(1) if title_match else "unknown"
        files.append((file_url, title))
    return files

def parse_list_page(url):
    """
    解析列表页，提取文章链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    articles = []
    # 查找 class 为 list_item 的 <li> 元素
    list_items = soup.select('li.list_item')
    print(f"Found {len(list_items)} articles on page {url}")  # 调试输出找到的条目数
    for item in list_items:
        link_elem = item.select_one("span.Article_Title a")  # 提取文章链接
        date_elem = item.select_one("span.Article_PublishDate")  # 提取发布日期
        
        if link_elem:
            article_url = link_elem.get("href", "").strip()
            article_title = link_elem.get("title", "").strip()
            article_date = date_elem.text.strip() if date_elem else "未知日期"
            
            # 转换为完整的 URL
            full_url = article_url if article_url.startswith("http") else f"{base_url}{article_url}"
            articles.append((full_url, article_title, article_date))
    return articles

def crawl_site(url):
    """
    爬取列表页并处理详情页中的文件下载
    """
    print(f"Processing list page: {url}")
    articles = parse_list_page(url)
    
    for article_url, article_title, article_date in articles:
        print(f"  Found article: {article_title} ({article_date})")
        files = parse_article_page(article_url)
        
        for file_url, file_title in files:
            # 转换为完整的文件 URL
            full_file_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
            save_file(full_file_url, file_title, save_path)

# 爬取所有目标URL
for url in urls:
    crawl_site(url)

# mpa的单独处理
files = parse_article_page(mpa_url)
for file_url, file_title in files:
    full_file_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
    save_file(full_file_url, file_title, save_path)