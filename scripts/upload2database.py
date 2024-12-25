import os
import json
from hdfs import InsecureClient  # HDFS 客户端
from database.hbase import USTCHBase  # HBase 操作类
from database.urlcontent import URLContent  # URLContent 数据封装类
from database.const import HDFS_TARGET_DIR, LOCAL_CACHE_DIR  # 常量配置


# HDFS 和 HBase 配置
HDFS_HOST = "http://localhost:50070"  # HDFS Web UI 地址
HDFS_USER = "root"  # HDFS 用户名
HDFS_TARGET_DIR = "/data/cache/"  # HDFS 目标目录
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


def upload_to_hdfs(local_path, hdfs_path, client):
    """
    将本地文件上传到 HDFS。
    :param local_path: 本地文件路径
    :param hdfs_path: HDFS 文件路径
    :param client: HDFS 客户端
    """
    try:
        # 如果文件已存在，则覆盖
        if client.status(hdfs_path, strict=False):
            print(f"HDFS 文件已存在，覆盖: {hdfs_path}")
            client.delete(hdfs_path)
        client.upload(hdfs_path, local_path)
        print(f"文件上传成功: {local_path} -> {hdfs_path}")
    except Exception as e:
        print(f"文件上传失败: {local_path} -> {hdfs_path}, 错误: {e}")


def process_files_and_store_in_hbase(cache_dir, hdfs_target_dir, keywords_dict):
    """
    扫描 cache 文件夹，将文件上传到 HDFS 并将元数据存储到 HBase。
    :param cache_dir: 本地 cache 根目录
    :param hdfs_target_dir: HDFS 目标根目录
    :param keywords_dict: 关键词字典
    """
    # 初始化 HDFS 客户端和 HBase 客户端
    hdfs_client = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=120)
    print(hdfs_client)
    
    with USTCHBase() as hbase:
        # 遍历 cache 文件夹中的所有文件
        for root, _, files in os.walk(cache_dir):
            
            for file_name in files:
                local_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(local_path, cache_dir)
                # print(relative_path)
                
                # 将文件路径中的 "/" 替换为 "_"
                hdfs_path = os.path.join(hdfs_target_dir, relative_path.replace("\\", "/").replace("/", "_"))
                # print(hdfs_path)
                # import pdb; pdb.set_trace()
                # 上传文件到 HDFS
                upload_to_hdfs(local_path, hdfs_path, hdfs_client)

                # 检查关键词字典中是否有该文件的信息
                file_metadata = keywords_dict.get(local_path, {})

                # 构造 URLContent 对象
                url_content = URLContent(
                    file_name=file_name,
                    hdfs_path=hdfs_path,
                    keywords=file_metadata.get("keywords", []),
                    high_freq_words=file_metadata.get("high_freq_words", [])
                )

                # 存储到 HBase
                hbase.put(
                    row=local_path.encode("utf-8"),  # 使用文件的本地路径作为 Row Key
                    data=url_content.to_hbase_dict()
                )
                print(f"存储到 HBase: {file_name}")


if __name__ == "__main__":
    # 加载关键词字典
    keywords_dict = load_keywords(KEYWORDS_FILE)

    # 扫描文件并存储到 HDFS 和 HBase
    process_files_and_store_in_hbase(
        cache_dir=LOCAL_CACHE_DIR,
        hdfs_target_dir=HDFS_TARGET_DIR,
        keywords_dict=keywords_dict
    )