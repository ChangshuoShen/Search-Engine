import jieba
from typing import List, Set
from .hbase import USTCHBase
from .const import SEARCH_TOP_K


class SearchEngine:
    """
    基于词集合匹配的简单搜索引擎，支持分词、关键词匹配和加权排序。
    """
    def __init__(self):
        self.hbase = USTCHBase()
        self.stopwords = self.load_stopwords("keywords/stopwords.txt")

    def load_stopwords(self, filepath: str) -> Set[str]:
        """
        加载停用词表。
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)

    def tokenize(self, text: str) -> List[str]:
        """
        对文本进行分词，并移除停用词。
        """
        words = jieba.lcut(text)
        return [word for word in words if word not in self.stopwords and word.strip()]

    def calculate_iou(self, query_set: Set[str], doc_set: Set[str]) -> float:
        """
        计算查询词集合与文档集合的 IoU（交并比）。
        """
        intersection = query_set & doc_set
        union = query_set | doc_set
        return len(intersection) / len(union) if union else 0.0

    def calculate_match_score(self, query_set: Set[str], doc_set: Set[str]) -> int:
        """
        计算查询词集合与文档集合的交集大小。
        """
        return len(query_set & doc_set)

    def search(self, query: str) -> List[dict]:
        """
        根据查询词搜索文档标题、关键词和高频词，并加权排序。

        Args:
            query (str): 用户的搜索关键词。

        Returns:
            List[dict]: 按相关性排序的搜索结果。
        """
        results = []
        query_tokens = set(self.tokenize(query))  # 查询词集合
        
        for _, data in self.hbase.scan():
            title = data.get("cf0:title", "")
            keywords = set(data.get("cf0:keywords", "").split(","))
            high_freq_words = set(data.get("cf0:high_freq_words", "").split(","))

            # 计算 IoU （可选，用于权重调整或额外排序依据）
            keywords_iou = self.calculate_iou(query_tokens, keywords)
            high_freq_iou = self.calculate_iou(query_tokens, high_freq_words)
            
            # 计算匹配得分
            title_score = self.calculate_match_score(query_tokens, set(self.tokenize(title)))
            keywords_score = self.calculate_match_score(
                query_tokens, keywords) + 0.1 * keywords_iou
            high_freq_score = self.calculate_match_score(
                query_tokens, high_freq_words) + 0.15 * high_freq_iou

            # 加权得分
            total_score = (
                title_score * 5 +  # 文档名权重较高
                keywords_score * 2 +  # 关键词权重
                high_freq_score * 1  # 高频词权重
            )
            if total_score > 0:
                results.append({
                    "title": title,
                    "keywords": list(keywords),
                    "high_freq_words": list(high_freq_words),
                    "hdfs_path": data.get("cf0:hdfs_path", ""),
                    "total_score": total_score,
                    "keywords_iou": keywords_iou,
                    "high_freq_iou": high_freq_iou
                })

        # 按总分排序，必要时可以结合 IoU 排序
        results.sort(key=lambda x: x["total_score"], reverse=True)

        return results[:SEARCH_TOP_K]