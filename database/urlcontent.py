class URLContent:
    """
    封装文件的元数据（标题、HDFS 路径、关键词、高频词）。
    """
    def __init__(self, file_name: str, hdfs_path: str, keywords=None, high_freq_words=None):
        if keywords is None:
            keywords = []
        if high_freq_words is None:
            high_freq_words = []
        self.title = file_name
        self.hdfs_path = hdfs_path
        self.keywords = keywords
        self.high_freq_words = high_freq_words

    def to_hbase_dict(self):
        """
        转换为 HBase 存储所需的字典格式。
        """
        return {
            "cf0:title": self.title,
            "cf0:hdfs_path": self.hdfs_path,
            "cf0:keywords": ",".join(self.keywords),  # 存储为逗号分隔的字符串
            "cf0:high_freq_words": ",".join(self.high_freq_words)  # 存储为逗号分隔的字符串
        }