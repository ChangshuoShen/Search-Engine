import os
import jieba
import fitz  # PyMuPDF，用于处理 PDF
from docx import Document  # 用于处理 DOCX
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import json

# 停用词表路径
STOPWORDS_PATH = "utils/stopwords.txt"


def load_stopwords(path):
    """
    加载停用词表
    """
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        stopwords = {line.strip() for line in f}
    return stopwords


def extract_text_from_pdf(file_path):
    """
    从 PDF 文件中提取文本
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()  # 提取每一页的文本
        doc.close()
        return text
    except Exception as e:
        print(f"无法读取 PDF 文件 {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path):
    """
    从 DOCX 文件中提取文本
    """
    try:
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])  # 提取所有段落的文本
        return text
    except Exception as e:
        print(f"无法读取 DOCX 文件 {file_path}: {e}")
        return ""


def extract_text_from_txt(file_path):
    """
    从 TXT 文件中提取文本
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"无法读取 TXT 文件 {file_path}: {e}")
        return ""


def extract_text_from_file(file_path):
    """
    根据文件类型提取文本
    """
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        print(f"不支持的文件格式: {file_path}")
        return ""


def extract_keywords_and_high_freq_words(file_contents, stopwords, top_k=10, high_freq_n=5):
    """
    使用 TF-IDF 提取关键词，并从单个文档中提取高频词
    :param file_contents: 文件内容列表
    :param stopwords: 停用词集合
    :param top_k: TF-IDF 提取的关键词数量
    :param high_freq_n: 高频词数量
    :return: 文件的关键词和高频词
    """
    # 分词器：使用 jieba 分词
    def jieba_tokenizer(text):
        words = jieba.lcut(text)
        return [word for word in words if word not in stopwords and len(word) > 1]

    # 初始化 TF-IDF 向量器
    vectorizer = TfidfVectorizer(
        tokenizer=jieba_tokenizer,
        max_df=0.85,  # 过滤高频词
        min_df=1,     # 过滤低频词
        use_idf=True,
        smooth_idf=True,
    )

    # 计算 TF-IDF
    tfidf_matrix = vectorizer.fit_transform(file_contents)
    feature_names = vectorizer.get_feature_names_out()

    # 提取每个文件的关键词和高频词
    results = {}
    for index, content in enumerate(file_contents):
        # 关键词提取
        tfidf_scores = tfidf_matrix[index].toarray()[0]
        top_indices = tfidf_scores.argsort()[::-1][:top_k]
        keywords = [feature_names[i] for i in top_indices]

        # 高频词提取
        words = jieba_tokenizer(content)
        word_counts = Counter(words)
        high_freq_words = [word for word, _ in word_counts.most_common(high_freq_n)]

        # 保存结果
        results[index] = {
            "keywords": keywords,
            "high_freq_words": high_freq_words
        }

    return results


def process_all_files(base_folder, output_file, top_k=10, high_freq_n=5):
    """
    扫描所有文件，提取每个文件的关键词和高频词
    :param base_folder: 主文件夹路径
    :param output_file: 结果保存路径（JSON 格式）
    :param top_k: TF-IDF 提取的关键词数量
    :param high_freq_n: 高频词数量
    """
    stopwords = load_stopwords(STOPWORDS_PATH)
    results = {}

    # 遍历所有文件
    file_contents = []
    file_names = []

    for root, _, files in os.walk(base_folder):
        for file_name in files:
            if file_name.endswith((".pdf", ".docx", ".txt")):
                file_path = os.path.join(root, file_name)
                print(f"正在处理文件: {file_path}")
                content = extract_text_from_file(file_path)
                if content.strip():  # 确保文件内容非空
                    file_contents.append(content)
                    file_names.append(file_path)

    # 提取关键词和高频词
    if file_contents:
        keywords_and_high_freq = extract_keywords_and_high_freq_words(file_contents, stopwords, top_k, high_freq_n)

        # 保存结果
        for i, file_path in enumerate(file_names):
            results[file_path] = keywords_and_high_freq[i]

    # 保存结果为 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"关键词提取完成，结果已保存至 {output_file}")


# 示例用法
if __name__ == "__main__":
    base_folder = "cache/"  # 主文件夹路径
    output_file = "keywords/file_keywords.json"  # 输出文件路径
    top_k = 10  # TF-IDF 提取的关键词数量
    high_freq_n = 5  # 高频词数量

    process_all_files(base_folder, output_file, top_k, high_freq_n)