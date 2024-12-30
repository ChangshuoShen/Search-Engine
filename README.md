# Search-Engine
**-- USTC 大数据系统及综合实验大作业**

> **by 申长硕 & 高茂航**

---

## 项目介绍

本项目开发了一个面向中国科学技术大学（USTC）各网站的文档检索系统，旨在解决校内文档检索难、效率低的问题。通过自动化爬取 USTC 官方网站的文档数据，结合 TF-IDF 算法进行关键词提取与相关性排序，最终实现快速、准确的文档搜索。同时，项目整合了本地部署的大语言模型 ChatGLM，采用 RAG（Retrieval Augmented Generation）技术，提供智能问答功能，提升用户体验。


---

## 实验内容与目标

### 实验内容

1. **网站爬取与数据收集：**  
   自动爬取 USTC 各学院、管理部门官网的文档数据（如 PDF、DOC 等）。
2. **关键词提取与分析：**  
   通过 TF-IDF 算法提取文档关键词，并记录高频词。
3. **HBase 数据存储：**  
   将爬取数据的元信息（如关键词、高频词、文档路径）存储在分布式数据库 HBase 中。
4. **文档检索引擎：**  
   根据用户输入的查询，计算文档与查询的相关性和契合度，并按分值排序返回文档列表。
5. **智能问答：**  
   利用 RAG 技术和 ChatGLM 模型，基于检索结果生成上下文相关的回答。
6. **前端可视化：**  
   使用 Flask 构建用户友好的前端界面，支持文档搜索、下载与预览。

---

### 实验目标

1. **构建校内文档库：**  
   自动化爬取 USTC 官网的文档数据，建立大规模校内文档库。
2. **实现高效文档检索：**  
   基于 TF-IDF 算法和高频词分析，快速检索文档并按相关性排序。
3. **增强搜索体验：**  
   提供智能问答功能，结合文档检索结果生成更准确的回答。
4. **技术综合应用：**  
   运用爬虫技术、分布式数据库（HBase）、文本分析与前端开发等技术，完成实验目标。

---

## 项目功能

1. **网站爬取与数据收集：**  
   爬取附录中列出的网站，下载文件（PDF、DOC、TXT 等），并分类存储。
2. **文本分析与关键词提取：**  
   使用 `jieba` 分词与 TF-IDF 算法提取文档关键词，同时记录高频词。
3. **元数据存储与优化：**  
   将文档的关键词、高频词等元数据信息存储在 HBase 中，加速检索过程。
4. **检索引擎实现：**  
   按相关性与契合度计算文档分值，并返回最优结果。
5. **智能问答（RAG + ChatGLM）：**  
   将检索结果作为上下文传递给 ChatGLM 模型，生成上下文相关的回答。
6. **前端界面展示：**  
   用户通过 Flask 构建的界面输入查询，查看检索结果，并支持在线文档预览与下载。

---

## 技术路线

### 使用的主要技术

1. **爬虫技术：**
   - 使用 `requests` + `BeautifulSoup` 实现递归爬取，获取目标文件。
   - 对“下载中心”或其他文件板块进行重点爬取。
2. **分词与关键词提取：**
   - 基于 `jieba` 分词，结合 `TF-IDF` 提取关键词。
   - 记录高频词以辅助检索排序。
3. **HBase 数据存储：**
   - 使用 `happybase` 操作 HBase，将文档元数据写入数据库。
   - 按 `row_key` 存储文件路径及其关键词、标题等信息。
4. **检索算法：**
   - 使用关键词交集和加权评分计算文档与查询的相关性。
   - 支持 TF-IDF 和 IoU（交并比）结合的检索排序。
5. **RAG + ChatGLM：**
   - 检索相关文档，将其作为上下文输入 ChatGLM 模型。
   - 生成基于校内文档回答的智能问答功能。
6. **前端开发：**
   - 使用 Flask 构建查询与结果展示界面。
   - 支持文档预览、下载及与 ChatGLM 模型的交互。

---

## 项目结构

```plaintext
.
├── app/                         # Flask 前端及路由逻辑
│   ├── __init__.py
│   ├── routes.py
│   ├── static/                  # 静态文件（CSS, JS, 视频等）
│   ├── templates/               # HTML 模板文件
├── cache/                       # 爬虫缓存数据
├── chat/                        # ChatGLM 集成
│   ├── chatglm_api.py           # ChatGLM API 接口
├── crawl/                       # 爬虫脚本及配置文件
│   ├── url_gmh.yml              # GMH 网站配置
│   ├── crawl.sh                 # 爬虫批量执行脚本
├── database/                    # HBase 和检索逻辑
│   ├── hbase.py                 # HBase 数据存储操作
│   ├── search.py                # 检索引擎实现
├── keywords/                    # 关键词提取相关代码
│   ├── keywords_each_file.py    # TF-IDF 关键词提取
│   ├── stopwords.txt            # 停用词表
├── scripts/                     # 数据库上传与测试脚本
│   ├── upload2hbase.py          # 数据上传至 HBase
├── run.py                       # Flask App 启动入口
├── requirements.txt             # Python 依赖库
└── README.md                    # 项目文档
```

---

## 运行指南

### 环境配置

1. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置 HBase：
   - 确保 HBase 已安装并运行。
   - 启动 Thrift 服务：
     ```bash
     hbase thrift start
     ```

### 项目运行

1. 执行爬虫，收集数据：
   ```bash
   bash crawl/crawl.sh
   ```

2. 提取关键词并上传到 HBase：
   ```bash
   python keywords/keywords_each_file.py
   python scripts/upload2hbase.py
   ```

3. 启动 Flask 前端：
   ```bash
   python run.py
   ```
   访问 `http://127.0.0.1:5000` 查看搜索引擎。

---

## 实验结果

1. **爬取数据：** 成功爬取 USTC 各官网文件约 3000 条。
2. **检索效果：** 测试关键词（如“数学”、“财务报销”）能快速返回高相关性文档。
3. **智能问答：** ChatGLM 基于检索结果生成上下文相关的回答。
4. **性能分析：** 检索耗时 <2 秒；ChatGLM 响应较慢，但实现了基本功能。

---

## 踩坑总结

1. **HBase 配置问题：** 权限设置和 Thrift 服务启动需特别注意。
2. **编码问题：** 爬虫与文本解析阶段容易出现中文编码错误，需统一 UTF-8 格式。
3. **文件解析失败：** 部分 PDF 文件因加密或格式异常无法解析，需添加异常处理。

---


## 附录
### 爬取的网站列表：

| 类别               | 网站名称                     | 网址                                         |
| ------------------ | ---------------------------- | -------------------------------------------- |
| **学院与研究院**   | 人工智能与数据科学学院       | http://saids.ustc.edu.cn/main.htm            |
|                    | 中科大计算机科学与技术学院   | http://cs.ustc.edu.cn/main.htm               |
|                    | 中科大网络空间安全学院       | http://cybersec.ustc.edu.cn/main.htm         |
|                    | 中科大数学科学学院           | https://math.ustc.edu.cn/main.htm            |
|                    | 中科大信息科学技术学院       | https://sist.ustc.edu.cn/main.htm            |
|                    | 中科大软件学院               | https://sse.ustc.edu.cn/main.htm             |
|                    | 中科大先进技术研究院         | https://iat.ustc.edu.cn/iat/index.html       |
|                    | 中科大苏州高等研究院         | https://sz.ustc.edu.cn/index.html            |
|                  | 少年班学院                 | https://sgy.ustc.edu.cn                |
|                  | 物理学院                   | https://physics.ustc.edu.cn            |
|                  | 化学与材料科学学院         | https://scms.ustc.edu.cn               |
|                  | 工程科学学院               | https://ses.ustc.edu.cn                |
|                  | 微电子学院                 | https://sme.ustc.edu.cn                |
|                  | 生命科学学院               | https://biox.ustc.edu.cn               |
|                  | 管理学院                   | https://som.ustc.edu.cn                |
|                  | 公共事务学院               | https://pas.ustc.edu.cn                |
|                  | 人文与社会科学学院         | https://hsss.ustc.edu.cn               |
|                  | 马克思主义学院             | https://marx.ustc.edu.cn               |
|                  | 环境科学与工程系（直属）   | https://ese.ustc.edu.cn                |
|                  | 核科学技术学院             | https://www.snst.ustc.edu.cn           |
|                  | 科技商学院                 | https://fbs.ustc.edu.cn                |
|                  | 科学岛分院                 | https://www.hf.cas.cn/sbpy/yjsc/       |
|                  | 材料科学与工程学院（科教融合学院） | https://gs.imr.ac.cn           |
|                  | 天文与空间科学学院（科教融合学院） | https://pmo.cas.cn/gs           |
|                  | 纳米技术与纳米仿生学院（科教融合学院） | http://nsti.ustc.edu.cn/main.htm        |
|                  | 应用化学与工程学院（科教融合学院） | https://www.ciac.cas.cn            |
|                  | 生物医学工程学院（苏州）（科教融合学院） | http://bme.ustc.edu.cn    |
|                  | 能源科学与技术学院（科教融合学院） | https://www.giec.ac.cn             |
|                  | 稀土学院（科教融合学院）   | https://www.gia.cas.cn                |
| **招生与培养**     | 中科大本科生招生网           | https://zsb.ustc.edu.cn/main.htm             |
|                    | 中科大教务处                 | https://www.teach.ustc.edu.cn/               |
|                    | 中科大研究生院               | http://gradschool.ustc.edu.cn/               |
|                    | 中科⼤就业信息⽹             | http://www.job.ustc.edu.cn/index.htm         |
| **行政与管理**     | 中科大财务处                 | https://finance.ustc.edu.cn/main.htm         |
|                    | 中科大资产与后勤保障处       | https://zhc.ustc.edu.cn/main.htm             |
|                    | 中科大保卫与校园管理处       | https://bwc.ustc.edu.cn/5655/list.htm        |
|                    | 学⼯⼀体化（需登陆）         | https://xgyth.ustc.edu.cn/usp/home/main.aspx |
| **学生服务与活动** | 青春科大                     | http://young.ustc.edu.cn/15056/list.htm      |
| **科研与创新**     | 中科大信息科学实验中心       | http://ispc.ustc.edu.cn/6299/list.htm        |
|                    | 中科大科技成果转移转化办公室 | http://zhb.ustc.edu.cn/18534/list1.htm       |
| **学术资源与出版** | 中科大出版社                 | http://press.ustc.edu.cn/xzzq/main.htm       |
| **网络与信息技术** | 中科大网络信息中心           | http://ustcnet.ustc.edu.cn/main.htm          |
| **国际合作与交流** | 国合部平台                   | https://vista.ustc.edu.cn/                   |

---

## 贡献者

- **申长硕**: 部分网站爬虫、前端开发、HBase 配置、ChatGLM 集成、实验报告撰写
- **高茂航**: 部分网站爬虫、数据清洗、课堂展示

如有问题，请联系：
- stephen_shen@mail.ustc.edu.cn
- gmh1627@mail.ustc.edu.cn
