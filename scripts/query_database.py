from database.hbase import USTCHBase
from database.hdfs import HDFSClient

if __name__ == "__main__":
    # 查询元数据
    hbase = USTCHBase()
    file_meta = hbase.query_meta("example.pdf")
    print(file_meta)

    # 下载文件
    if file_meta:
        hdfs_client = HDFSClient()
        hdfs_client.download_file_from_hdfs(file_meta["cf0:hdfs_path"])