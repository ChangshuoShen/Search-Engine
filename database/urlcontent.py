class URLContent:
    """
    封装文件的元数据（标题、描述、HDFS 路径）。
    """
    def __init__(self, file_name: str, description: str = '', hdfs_path: str = ''):
        self.title = file_name
        self.description = description
        self.hdfs_path = hdfs_path

    def to_hbase_dict(self):
        """
        转换为 HBase 存储所需的字典格式。
        """
        return {
            "cf0:title": self.title,
            "cf0:description": self.description,
            "cf0:hdfs_path": self.hdfs_path
        }