import requests
import os
from flask import Blueprint, render_template, request, send_file, current_app, jsonify
from database.search import SearchEngine
from transformers import AutoTokenizer

main = Blueprint('main', __name__)
search_engine = SearchEngine()


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query")
        results = search_engine.search(query)
        return render_template("results.html", query=query, results=results)
    return render_template("index.html")


@main.route("/download/<path:filepath>")
def download(filepath):
    """
    文件下载功能
    """
    try:
        # 将 HBase 中的绝对路径映射到 BASE_PATH
        base_path = current_app.config['BASE_PATH']
        filepath = '/'.join(
            filepath.split("/")[-2:]
        )
        if filepath.startswith(base_path):
            absolute_path = filepath
        else:
            absolute_path = os.path.join(base_path, filepath)

        # 检查文件是否存在
        if not os.path.exists(absolute_path):
            return f"文件未找到: {absolute_path}", 404
        
        return send_file(absolute_path, as_attachment=True)
    except Exception as e:
        return f"文件下载失败: {str(e)}", 404



@main.route("/preview/<path:filepath>")
def preview(filepath):
    """
    文件预览功能
    """
    file_extension = os.path.splitext(filepath)[1].lower()
    filepath = '/'.join(
        filepath.split("/")[-2:]
    )
    base_path = current_app.config['BASE_PATH']
    try:
        # 将 HBase 中的绝对路径映射到 BASE_PATH
        if filepath.startswith(base_path):
            absolute_path = filepath
        else:
            absolute_path = os.path.join(base_path, filepath)

        # 检查文件是否存在
        if not os.path.exists(absolute_path):
            return f"文件未找到: {absolute_path}", 404

        # 根据文件类型处理
        if file_extension in [".txt"]:
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read()
            return render_template("preview.html", content=content, title=os.path.basename(filepath))
        elif file_extension in [".pdf"]:
            # 返回 PDF 文件路径，用于前端 iframe 嵌入
            return render_template("preview.html", pdf_path=absolute_path, title=os.path.basename(filepath))
        elif file_extension in [".docx"]:
            from docx import Document
            doc = Document(absolute_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            return render_template("preview.html", content=content, title=os.path.basename(filepath))
        else:
            return "暂不支持预览该文件格式", 400
    except Exception as e:
        return f"文件预览失败: {str(e)}", 404
    
    
# 设置 tokenizer
# tokenizer = AutoTokenizer.from_pretrained("THUDM/glm-4-9b-chat", trust_remote_code=True)

# FastAPI 的地址
# FASTAPI_URL = "http://127.0.0.1:8000/generate"  # 假设 FastAPI 运行在本地

# @main.route("/rag", methods=["POST"])
# def rag():
#     """
#     通过接收用户的查询，并结合搜索结果构建新的 prompt，
#     然后调用 FastAPI 生成回答（RAG）。
#     """
#     if request.method == "POST":
#         # 获取用户查询的 prompt
#         query = request.form.get("query")
        
#         # 分词并生成检索词
#         tokenized_query = tokenizer.tokenize(query)
        
#         # 使用分词后的词语进行检索
#         search_results = search_engine.search(query)  # 假设返回的结果是文件列表或相关文本

#         # 将检索结果和原始查询组成新的 prompt
#         combined_prompt = f"用户查询：{query}\n相关文档：\n"
#         for result in search_results:
#             combined_prompt += f"- {result['content']}\n"  # 假设 result['content'] 是文档内容

#         # 发送请求到 FastAPI 服务，生成模型回答
#         try:
#             response = requests.post(
#                 FASTAPI_URL,
#                 json={"query": combined_prompt}  # 传递组合后的 prompt
#             )
#             response_data = response.json()
#             generated_text = response_data.get("response", "")
#         except requests.exceptions.RequestException as e:
#             return jsonify({"error": f"API 请求失败: {str(e)}"}), 500
        
#         # 返回生成的回答
#         return render_template(
#             "rag_result.html", query=query, 
#             generated_text=generated_text, search_results=search_results
#         )
    
#     return render_template("rag_form.html")  # 返回表单页面，用于输入查询
