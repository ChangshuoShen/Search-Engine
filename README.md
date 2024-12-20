# Search-Engine
--USTC 大数据系统及综合实验大作业

by 申长硕 & 高茂航

## 实验内容

从科大的网站爬取`文件数据`，存储在分布式数据库（HBase）中，实现一个搜索引擎，实现校内文件搜索的目的。

### 要求

1. 各学院官网以及各管理部门官网
2. 至少包含“下载中心”中的文件
3. `搜索引擎`需实现的基本结果：根据搜索内容召回文档（独立的文件）或文本信息，召回结果按照`相关性`和`契合度`排序
    1. 相关性：表示`搜索结果`与`用户查询内容在`语义或关键词层面的匹配程度。“搜索结果是否与用户的查询有关”。
        1. **TF-IDF**
        2. **BM25**
        3. Enbedding之后的向量相似度（如余弦相似度）
    2. 契合度：表示`搜索结果`是否能够满足用户的`查询意图`。不仅关注内容的匹配，还关注结果是否对用户有用或符合上下文需求。
        1. 用户行为分析
        2. 意图识别：导航型查询、事务型查询、信息型查询
        3. 内容属性：文档类型的匹配、文档新鲜度、文档权威性



## 爬取的网站列表：

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





## 报告内容

1. ⼩组成员名单和具体分⼯
2.  技术路线（介绍⼀下该项⽬⽤到的主要技术并做简要介绍， 尤其是与本课程相关的技术）
3. 实现功能介绍和相应的效果展示
4. 核⼼代码块（可截图放上去）
5. 该组所有同学各⾃的总结与⼼得（如踩坑、 错误总结、实验收获等）

