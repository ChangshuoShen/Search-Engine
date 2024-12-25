from database.search import SearchEngine  # 导入搜索引擎类


def test_search(query):
    """
    测试搜索功能。
    :param query: 搜索关键词
    """
    engine = SearchEngine()
    results = engine.search(query)

    if not results:
        print(f"未找到与 '{query}' 相关的结果。")
    else:
        print(f"搜索结果（关键词: {query}）：")
        for i, result in enumerate(results, start=1):
            print(f"结果 {i}:")
            print(f"  文件名: {result['title']}")
            print(f"  关键词: {', '.join(result['keywords'])}")
            print(f"  高频词: {', '.join(result['high_freq_words'])}")
            print(f"  绝对路径: {result['hdfs_path']}")
            print()


if __name__ == "__main__":
    # 测试用例
    test_queries = [
        "数学",  # 测试关键词匹配
        "模板",  # 测试高频词匹配
        "不存在的关键词"  # 测试无结果情况
    ]

    for query in test_queries:
        test_search(query)