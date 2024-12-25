import os
import jieba
import fitz  # PyMuPDF，用于处理 PDF
from docx import Document  # 用于处理 DOCX
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict, Counter
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


def extract_keywords_from_folder(folder_path, top_k=10, high_freq_n=5):
    """
    从文件夹中的所有文本提取关键词
    :param folder_path: 单个子文件夹路径
    :param top_k: 使用 TF-IDF 提取的关键词数量
    :param high_freq_n: 添加的高频词数量
    :return: 文件夹的关键词列表
    """
    # 加载停用词
    stopwords = load_stopwords(STOPWORDS_PATH)

    # 存储所有文本内容
    file_contents = []

    # 遍历文件夹中的所有文件
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith((".pdf", ".docx", ".txt")):  # 支持的文件类型
                file_path = os.path.join(root, file_name)
                print(f"正在处理文件: {file_name}")
                content = extract_text_from_file(file_path)
                if content:  # 确保文件内容非空
                    file_contents.append(content)


    if len(file_contents) < 2:
        print(f"文件夹 {folder_path} 中有效文件数量少于2（或没有文件），跳过关键词提取。")
        return []

    # 分词器：使用 jieba 分词
    def jieba_tokenizer(text):
        words = jieba.lcut(text)
        # 去除停用词和长度小于 2 的词
        return [word for word in words if word not in stopwords and len(word) > 1]

    # 初始化 TF-IDF 向量器
    vectorizer = TfidfVectorizer(
        tokenizer=jieba_tokenizer,  # 自定义分词器
        max_df=0.85,  # 过滤出现在 85% 文档中的高频词
        min_df=2,     # 过滤出现在少于 2 个文档中的低频词
        use_idf=True, # 启用 IDF
        smooth_idf=True,
    )

    # 计算 TF-IDF 矩阵
    tfidf_matrix = vectorizer.fit_transform(file_contents)
    feature_names = vectorizer.get_feature_names_out()

    # 提取文件夹级别的关键词
    tfidf_scores = tfidf_matrix.sum(axis=0).A1  # 按列求和，得到每个词的总分
    top_indices = tfidf_scores.argsort()[::-1][:top_k]
    tfidf_keywords = [feature_names[index] for index in top_indices]

    # 统计高频词（排除停用词）
    all_words = []
    for content in file_contents:
        all_words.extend(jieba_tokenizer(content))
    word_counts = Counter(all_words)
    high_freq_keywords = [
        word for word, _ in word_counts.most_common(high_freq_n)
        if word not in tfidf_keywords  # 避免重复
    ]

    # 合并关键词
    final_keywords = tfidf_keywords + high_freq_keywords
    return final_keywords


def process_all_subfolders(base_folder, output_file, top_k=10, high_freq_n=5):
    """
    对主文件夹中的所有子文件夹进行处理，提取每个子文件夹的关键词
    :param base_folder: 主文件夹路径
    :param output_file: 结果保存路径（JSON 格式）
    :param top_k: 每个文件夹提取的关键词数量
    :param high_freq_n: 每个文件夹添加的高频词数量
    """
    results = {}

    # 遍历主文件夹中的每个子文件夹
    for subfolder in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subfolder)
        if os.path.isdir(subfolder_path):  # 只处理子文件夹
            print(f"正在处理文件夹: {subfolder}")
            keywords = extract_keywords_from_folder(subfolder_path, top_k, high_freq_n)
            results[subfolder] = keywords

    # 保存结果为 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"关键词提取完成，结果已保存至 {output_file}")


# 示例用法
if __name__ == "__main__":
    base_folder = "cache/"  # 主文件夹路径
    output_file = "keywords/folder_keywords.json"  # 输出文件路径
    top_k = 10  # TF-IDF 提取的关键词数量
    high_freq_n = 5  # 添加的高频词数量

    process_all_subfolders(base_folder, output_file, top_k, high_freq_n)