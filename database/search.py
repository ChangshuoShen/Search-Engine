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
        根据 query 搜索文件标题、关键词和高频词。

        Args:
            query (str): 用户的搜索关键词。

        Returns:
            List[dict]: 按相关性排序的搜索结果。
        """
        results = []
        for _, data in self.hbase.scan():
            title = data.get("cf0:title", "")
            keywords = data.get("cf0:keywords", "").split(",")
            high_freq_words = data.get("cf0:high_freq_words", "").split(",")

            # 检查查询词是否匹配
            if query.lower() in title.lower() or \
               query.lower() in [k.lower() for k in keywords] or \
               query.lower() in [h.lower() for h in high_freq_words]:
                results.append({
                    "title": title,
                    "keywords": keywords,
                    "high_freq_words": high_freq_words,
                    "hdfs_path": data.get("cf0:hdfs_path", "")
                })

        # 按相关性排序（简单实现：标题 > 关键词 > 高频词）
        results.sort(
            key=lambda x: (
                query.lower() in x["title"].lower(),
                query.lower() in [k.lower() for k in x["keywords"]],
                query.lower() in [h.lower() for h in x["high_freq_words"]]
            ),
            reverse=True
        )
        return results[:SEARCH_TOP_K]