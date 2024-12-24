import requests
from bs4 import BeautifulSoup

def scrape_a_tags(url):
    # 请求目标网址
    response = requests.get(url)
    
    # 检查请求是否成功
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return None
    # 手动设置编码为 'utf-8' 或 'gb2312'
    # 1. 如果网页声明了编码，使用 response.apparent_encoding 自动检测
    response.encoding = response.apparent_encoding
    
    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到所有的 <a> 标签
    a_tags = soup.find_all('a')
    
    # 存储结果的字典
    result = {}
    
    # 遍历所有 <a> 标签
    for a_tag in a_tags:
        # 获取 href 属性
        href = a_tag.get('href')
        # 获取标签内容
        content = a_tag.get_text(strip=True)
        
        # 将 href 和内容存入字典（避免空值）
        if href:
            result[content] = href
            
    return result

# 调用函数并打印结果
url = "https://www.ustc.edu.cn/yxjs.htm"
a_tags_dict = scrape_a_tags(url)
import json
with open('tag_a.json', 'w', encoding='utf-8') as f:
    json.dump(a_tags_dict, f, ensure_ascii=False, indent=4)
# print(a_tags_dict)
# if a_tags_dict:
#     for href, content in a_tags_dict.items():
#         print(f"链接: {href}, 内容: {content}")