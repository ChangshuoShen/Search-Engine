import os
import json
from database.hbase import USTCHBase  # HBase 操作类
from database.urlcontent import URLContent  # URLContent 数据封装类
from database.const import LOCAL_CACHE_DIR  # 常量配置

# 配置
KEYWORDS_FILE = "keywords/file_keywords.json"  # 关键词文件路径


def load_keywords(file_path):
    """
    加载 file_keywords.json 文件到内存。
    :param file_path: file_keywords.json 文件路径
    :return: 关键词字典
    """
    if not os.path.exists(file_path):
        print(f"关键词文件 {file_path} 不存在！")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_files_and_store_in_hbase(cache_dir, keywords_dict):
    """
    扫描 cache 文件夹，将文件绝对路径和元数据存储到 HBase。
    :param cache_dir: 本地 cache 根目录
    :param keywords_dict: 关键词字典
    """
    with USTCHBase() as hbase:
        # 遍历 cache 文件夹中的所有文件
        for root, _, files in os.walk(cache_dir):
            for file_name in files:
                # 获取文件的绝对路径
                absolute_path = os.path.abspath(os.path.join(root, file_name))
                cache_path = '/'.join(
                    absolute_path.split('/')[-3:]
                )
                # 检查关键词字典中是否有该文件的信息
                file_metadata = keywords_dict.get(cache_path, {})

                # 构造 URLContent 对象
                url_content = URLContent(
                    file_name=file_name,
                    hdfs_path=absolute_path,  # 存储文件的绝对路径
                    keywords=file_metadata.get("keywords", []),
                    high_freq_words=file_metadata.get("high_freq_words", [])
                )

                # 存储到 HBase
                hbase.put(
                    row=absolute_path.encode("utf-8"),  # 使用文件的绝对路径作为 Row Key
                    data=url_content.to_hbase_dict()
                )
                print(f"存储到 HBase: {file_name} -> {absolute_path}")


if __name__ == "__main__":
    # 加载关键词字典
    keywords_dict = load_keywords(KEYWORDS_FILE)

    
    # 扫描文件并存储到 HBase
    process_files_and_store_in_hbase(
        cache_dir=LOCAL_CACHE_DIR,
        keywords_dict=keywords_dict
    )