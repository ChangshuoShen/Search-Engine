import os
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 目标URL列表
urls = [
    'https://marx.ustc.edu.cn/jxky/list.htm',
    'https://marx.ustc.edu.cn/xsgz/list.htm',
    'https://marx.ustc.edu.cn/zsjy/list.htm',
    'https://marx.ustc.edu.cn/pyfa/list.htm',
]

# 基础URL，用于处理相对路径
base_url = 'https://marx.ustc.edu.cn'

# 目标保存路径
save_path = 'cache/Shencs/marx'
os.makedirs(save_path, exist_ok=True)

# Selenium 的浏览器设置
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")  # 禁用GPU
    options.add_argument("--no-sandbox")  # 禁用沙盒
    options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(save_path),  # 设置默认下载目录
        "download.prompt_for_download": False,  # 禁用下载提示
        "plugins.always_open_pdf_externally": True  # 禁用内置PDF查看器
    })
    service = Service("/usr/local/bin/chromedriver")  # 替换为 ChromeDriver 的路径
    driver = webdriver.Chrome(service=service, options=options)
    return driver

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

def save_file_with_selenium(driver, article_url, title):
    """
    使用 Selenium 模拟点击按钮触发下载文件
    """
    try:
        driver.get(article_url)  # 打开文章详情页
        time.sleep(2)  # 等待页面加载
        
        # 查找打印按钮
        print_button = driver.find_element(By.ID, "print")
        print_button.click()  # 点击按钮
        print(f"Triggered download for: {title}")
        
        # 等待文件下载完成
        time.sleep(5)  # 下载时间视文件大小而定
    except Exception as e:
        print(f"Error triggering download for {title}: {e}")

def parse_article_page(article_url, driver):
    """
    解析详情页，提取文件下载链接和标题
    """
    soup = fetch_page(article_url)
    if soup is None:
        return []

    files = []
    # 找到直接的下载链接（如 <a href="文件链接">）
    file_links = soup.select('a[href]')
    for file_link in file_links:
        href = file_link.get("href", "").strip()
        # 检查 href 是否为文件下载链接（通过扩展名判断）
        if href.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
            file_url = href if href.startswith("http") else f"{base_url}{href}"
            title = file_link.text.strip() or "unknown"
            files.append((file_url, title))
    
    # 检查是否存在通过按钮下载的文件
    print_button = soup.select_one('button#print')
    if print_button:
        # 如果存在按钮，使用 Selenium 模拟点击下载
        title = soup.title.string.strip() if soup.title else "unknown_file"
        save_file_with_selenium(driver, article_url, title)
    
    return files

def parse_list_page(url):
    """
    解析列表页，提取文章链接和标题
    """
    soup = fetch_page(url)
    if soup is None:
        return []

    articles = []
    # 查找 class 为 news 的 <li> 元素
    list_items = soup.select('li.news')
    print(f"Found {len(list_items)} articles on page {url}")  # 调试输出找到的条目数
    for item in list_items:
        link_elem = item.select_one("span.news_title a")  # 提取文章链接
        date_elem = item.select_one("span.news_meta")  # 提取发布日期
        
        if link_elem:
            article_url = link_elem.get("href", "").strip()
            article_title = link_elem.get("title", "").strip() or link_elem.text.strip()
            article_date = date_elem.text.strip() if date_elem else "未知日期"
            
            # 转换为完整的 URL
            full_url = article_url if article_url.startswith("http") else f"{base_url}{article_url}"
            articles.append((full_url, article_title, article_date))
    return articles

def crawl_site(url, driver):
    """
    爬取列表页并处理详情页中的文件下载
    """
    print(f"Processing list page: {url}")
    articles = parse_list_page(url)
    
    for article_url, article_title, article_date in articles:
        print(f"  Found article: {article_title} ({article_date})")
        files = parse_article_page(article_url, driver)
        
        for file_url, file_title in files:
            # 转换为完整的文件 URL
            full_file_url = file_url if file_url.startswith("http") else f"{base_url}{file_url}"
            save_file_with_selenium(driver, full_file_url, file_title)

# 主程序
if __name__ == "__main__":
    driver = get_driver()  # 初始化 Selenium WebDriver
    try:
        for url in urls:
            crawl_site(url, driver)
    finally:
        driver.quit()  # 关闭浏览器