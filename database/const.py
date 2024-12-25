# HBase 配置
HBASE_HOST = "localhost"
HBASE_TABLE_NAME = "ustc"
HBASE_COLUMN_FAMILY = ["cf0"]

# HDFS 配置
HDFS_HOST = "http://localhost:50070"  # HDFS Web UI 地址
HDFS_USER = "hdfs"                    # HDFS 用户
HDFS_TARGET_DIR = "/files"            # HDFS 存储目录
LOCAL_CACHE_DIR = "./cache"           # 本地爬取文件目录

# 有意义的文件类型
VALID_EXTENSIONS = {
    "doc", "docx", "pdf", "txt",      # 文档类
    "xls", "xlsx",                    # 表格类
    "rar", "zip",                     # 压缩类
    "ppt", "pptx"                     # 演示类
}

# 搜索相关配置
SEARCH_TOP_K = 10  # 返回结果的最大数量