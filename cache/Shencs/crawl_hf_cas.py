import requests
from bs4 import BeautifulSoup
import os
import re

# 目标 URL 列表
urls = [
    'http://hf.cas.cn/sbpy/yjsc/xzzx/zs',
    'http://hf.cas.cn/sbpy/yjsc/xzzx/xw',
    'http://hf.cas.cn/sbpy/yjsc/xzzx/py',
    'http://hf.cas.cn/sbpy/yjsc/xzzx/yjsdj',
    'http://hf.cas.cn/sbpy/yjsc/xzzx/xsgl'
]

# 基础 URL，用于处理相对路径
base_url = 'http://hf.cas.cn'

# 目标保存路径
save_path = 'cache/Shencs/hfcas'
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
    解析文章详情页，提取文件下载链接和标题
    """
    print("article_url: ", article_url)
    soup = fetch_page(article_url)
    if soup is None:
        return []

    files = []
    
    # 获取当前文章 URL 的基础路径（去掉最后一个 '/' 后的部分）
    article_base_url = "/".join(article_url.split("/")[:-1])
    
    # 查找所有 <script> 标签
    script_tags = soup.find_all('script')
    
    # 用正则表达式提取 appLinkStr 和 appDescStr 内容
    app_link_str = None
    app_desc_str = None
    for script in script_tags:
        # 查找包含附件链接的字符串
        if 'var appLinkStr' in script.text:
            app_link_match = re.search(r'var appLinkStr\s*=\s*\'(.*?)\';', script.text)
            if app_link_match:
                app_link_str = app_link_match.group(1)
        
        # 查找包含附件描述的字符串
        if 'var appDescStr' in script.text:
            app_desc_match = re.search(r'var appDescStr\s*=\s*\'(.*?)\';', script.text)
            if app_desc_match:
                app_desc_str = app_desc_match.group(1)

    # 如果找到附件链接和描述
    if app_link_str and app_desc_str:
        app_links = app_link_str.split('|')
        app_descs = app_desc_str.split('|')
        
        # 创建文件链接和标题的配对
        for link, desc in zip(app_links, app_descs):
            # 生成完整 URL
            link = link.strip(".")
            full_url = link if link.startswith("http") else f"{article_base_url}{link}"
            files.append((full_url, desc))

    return files

def parse_list_page(url):
    """
    解析列表页，提取文章链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    articles = []
    # 查找 class 为 list-article-item 的 <li> 元素
    list_items = soup.select('li.list-article-item')
    print(f"Found {len(list_items)} articles on page {url}")  # 调试输出找到的条目数
    for item in list_items:
        link_elem = item.select_one("p.acticle-text a")  # 提取文章链接
        date_elem = item.select_one("span.time")  # 提取发布日期
        
        if link_elem:
            article_url = link_elem.get("href", "").strip()
            article_title = link_elem.get("title", "").strip() or link_elem.text.strip()
            article_date = date_elem.text.strip() if date_elem else "未知日期"
            
            # 转换为完整的 URL
            full_url = article_url if article_url.startswith("http") else f"{url}/{article_url.strip('./')}"
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
        
        if not files:
            print(f"  No downloadable files found directly on article page: {article_url}")
        for file_url, file_title in files:
            # 转换为完整的文件 URL
            full_file_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
            save_file(full_file_url, file_title, save_path)

# 主程序
if __name__ == "__main__":
    for url in urls:
        crawl_site(url)