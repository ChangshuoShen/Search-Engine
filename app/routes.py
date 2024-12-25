import os
from flask import Blueprint, render_template, request, send_file, current_app
from database.search import SearchEngine

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