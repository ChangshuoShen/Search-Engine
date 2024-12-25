from typing import List
from .hbase import USTCHBase
from .const import SEARCH_TOP_K


class SearchEngine:
    """
    实现基于 HBase 的简单搜索引擎。
    """
    def __init__(self):
        self.hbase = USTCHBase()

    def search(self, query: str) -> List[dict]:
        """
        根据 query 搜索文件标题和描述。

        Args:
            query (str): 用户的搜索关键词。

        Returns:
            List[dict]: 按相关性排序的搜索结果。
        """
        results = []
        for _, data in self.hbase.scan():
            title = data.get("cf0:title", "")
            description = data.get("cf0:description", "")
            if query.lower() in title.lower() or query.lower() in description.lower():
                results.append({
                    "title": title,
                    "description": description,
                    "hdfs_path": data.get("cf0:hdfs_path", "")
                })

        # 按相关性排序（简单实现：标题匹配权重大于描述匹配）
        results.sort(key=lambda x: (query.lower() in x["title"].lower(), query.lower() in x["description"].lower()), reverse=True)
        return results[:SEARCH_TOP_K]