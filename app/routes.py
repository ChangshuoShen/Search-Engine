from flask import Blueprint, request, jsonify
from .database.hbase import USTCHBase

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "Welcome to the HBase Search Engine!"

@main.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    # 示例：从 HBase 获取数据
    with USTCHBase(host="localhost") as hbase:
        table = hbase.get_table("ustc")
        rows = table.scan(row_prefix=query.encode("utf-8"))

    # 将结果返回为 JSON
    results = [{"key": k.decode("utf-8"), "data": {kk.decode("utf-8"): vv.decode("utf-8") for kk, vv in v.items()}} for k, v in rows]
    return jsonify(results)