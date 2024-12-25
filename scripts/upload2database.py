from database.hdfs import HDFSClient
from database.hbase import store_meta_in_hbase


if __name__ == "__main__":
    # 上传文件到 HDFS
    hdfs_client = HDFSClient()
    hdfs_client.upload_files_to_hdfs()

    # 存储元数据到 HBase
    store_meta_in_hbase()