import os
import happybase
import json
from typing import List, Dict
from .utils import get_logger
from .const import HBASE_HOST, HBASE_TABLE_NAME, HBASE_COLUMN_FAMILY, HDFS_TARGET_DIR, LOCAL_CACHE_DIR
from .urlcontent import URLContent


class USTCHBase:
    """
    封装 HBase 操作类。
    """
    def __init__(self, host=HBASE_HOST, column_family=HBASE_COLUMN_FAMILY):
        self.logger = get_logger('ustc-hbase')
        self.logger.info("HBase Connecting...")
        self.connection = happybase.Connection(host)
        self.connection.open()
        self.name = HBASE_TABLE_NAME
        if self.name.encode() not in self.connection.tables():
            assert column_family is not None, "Need to indicate column families to create a table"
            self.create_table(self.name, column_family)
        self.logger.info("HBase Connected Successfully!")
        self.table = self.get_table(self.name)

    def __enter__(self):
        return self

    def __exit__(self, type, message, traceback):
        self.connection.close()
        if isinstance(type, Exception):
            traceback.print_exc()

    def create_table(self, table_name: str, column_families: List[str]):
        column_families = {family: dict() for family in column_families}
        self.connection.create_table(table_name, column_families)
        self.logger.info(f"Table {table_name} is created.")

    def get_table(self, table_name: str):
        try:
            return self.connection.table(table_name)
        except Exception as e:
            self.logger.warning(e, exc_info=True)
            return None

    def put(self, row: bytes, data: Dict[bytes, bytes]):
        for key in data.keys():
            data[key] = data[key].encode('utf-8') if isinstance(data[key], str) else data[key]
        self.table.put(row=row, data=data)

    def query_meta(self, file_name: str):
        """
        根据文件名查询文件的元数据。
        """
        row = self.table.row(file_name.encode("utf-8"))
        if not row:
            self.logger.warning(f"No data found for file: {file_name}")
            return None
        return {key.decode("utf-8"): value.decode("utf-8") for key, value in row.items()}

    def scan(self):
        """
        扫描表中的所有数据。
        """
        for key, data in self.table.scan():
            yield key.decode("utf-8"), {k.decode("utf-8"): v.decode("utf-8") for k, v in data.items()}

    def close_connection(self):
        self.connection.close()

def store_meta_in_hbase(json_file: str, hdfs_dir=HDFS_TARGET_DIR):
    """
    从 JSON 文件加载文件元数据，并存储到 HBase。
    """
    with USTCHBase() as hbase:
        # 加载 JSON 文件
        with open(json_file, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        for file_path, meta in file_data.items():
            # 构造 HDFS 路径
            hdfs_path = os.path.join(hdfs_dir, os.path.relpath(file_path, LOCAL_CACHE_DIR)).replace("\\", "/")

            # 构造 URLContent 对象
            url_content = URLContent(
                file_name=os.path.basename(file_path),
                hdfs_path=hdfs_path,
                keywords=meta.get("keywords", []),
                high_freq_words=meta.get("high_freq_words", [])
            )

            # 存储到 HBase
            hbase.put(
                row=file_path.encode("utf-8"),  # 使用文件路径作为 Row Key
                data=url_content.to_hbase_dict()
            )
            print(f"Stored metadata for file: {file_path}")
                    
                    
                    
                    
# 基本用法-备忘
        
# 存储数据：Hbase里 存储的数据都是原始的字节字符串    
# cloth_data = {'cf1:content': u'牛仔裤', 'cf1:price': '299', 'cf1:rating': '98%'}
# hat_data = {'cf1:content': u'鸭舌帽', 'cf1:price': '88', 'cf1:rating': '99%'}
# shoe_data = {'cf1:content': u'耐克', 'cf1:price': '988', 'cf1:rating': '100%'}
# author_data = {'cf2:name': u'LiuLin', 'cf2:date': '2017-03-09'}
 
# table.put(row='www.test1.com', data=cloth_data)
# table.put(row='www.test2.com', data=hat_data)
# table.put(row='www.test3.com', data=shoe_data)
# table.put(row='www.test4.com', data=author_data)

# 使用batch一次插入多行数据
# bat = table.batch()
# bat.put('www.test5.com', {'cf1:price': 999, 'cf2:title': 'Hello Python', 'cf2:length': 34, 'cf3:code': 'A43'})
# bat.put('www.test6.com', {'cf1:content': u'剃须刀', 'cf1:price': 168, 'cf1:rating': '97%'})
# bat.put('www.test7.com', {'cf3:function': 'print'})
# bat.send()


# 使用with来管理batch
# with table.batch() as bat:
#     bat.put('www.test5.com', {'cf1:price': '999', 'cf2:title': 'Hello Python', 'cf2:length': '34', 'cf3:code': 'A43'})
#     bat.put('www.test6.com', {'cf1:content': u'剃须刀', 'cf1:price': '168', 'cf1:rating': '97%'})
#     bat.put('www.test7.com', {'cf3:function': 'print'})


# 在batch中删除数据
# with table.batch() as bat:
#     bat.put('www.test5.com', {'cf1:price': '999', 'cf2:title': 'Hello Python', 'cf2:length': '34', 'cf3:code': 'A43'})
#     bat.put('www.test6.com', {'cf1:content': u'剃须刀', 'cf1:price': '168', 'cf1:rating': '97%'})
#     bat.put('www.test7.com', {'cf3:function': 'print'})
#     bat.delete('www.test1.com')

# 通过batch_size参数来设置batch的大小
# with table.batch(batch_size=10) as bat:
#     for i in range(16):
#         bat.put('www.test{}.com'.format(i), {'cf1:price': '{}'.format(i)})

# 获取一个table实例
# table = connection.table('my_table')

# 查看可以使用的table
# print connection.tables()
# 创建一个table   
# connection.create_table(
#     'my_table',
#     {
#         'cf1': dict(max_versions=10),
#         'cf2': dict(max_versions=1, block_cache_enabled=False),
#         'cf3': dict(),  # use defaults
#     }
# )
# 检索一行数据
# row = table.row('www.test4.com')
# return: {'cf2:name': 'LiuLin', 'cf2:date': '2017-03-09'}
# 通过row_start和row_stop参数来设置开始和结束扫描的row key
# for key, value in table.scan(row_start='www.test2.com', row_stop='www.test3.com'):
#     print key, value
# 通过row_prefix参数来设置需要扫描的row key
# for key, value in table.scan(row_prefix='www.test'):
#     print key, value
# 检索多行数据
# rows = table.rows(['www.test1.com', 'www.test4.com'])
# print rows
# 通过指定列族来检索数据
# row = table.row('www.test1.com', columns=['cf1'])
# print row
# 通过指定时间戳来检索数据，时间戳必须是整数
# row = table.row('www.test1.com', timestamp=1489070666)
# print row
# 在返回的数据里面包含时间戳
# row = table.row(row='www.test1.com', columns=['cf1:rating', 'cf1:price'], include_timestamp=True)
# print row
# 删除一整行数据
# table.delete('www.test4.com')
# 删除一个列族的数据
# table.delete('www.test2.com', columns=['cf1'])
# 删除一个列族中几个列的数据
# table.delete('www.test2.com', columns=['cf1：name', 'cf1:price'])
