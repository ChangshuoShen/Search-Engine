from hdfs import InsecureClient
import os
from .const import HDFS_HOST, HDFS_USER, HDFS_TARGET_DIR, LOCAL_CACHE_DIR, VALID_EXTENSIONS


class HDFSClient:
    """
    封装 HDFS 的操作。
    """
    def __init__(self, hdfs_host=HDFS_HOST, hdfs_user=HDFS_USER):
        self.client = InsecureClient(hdfs_host, user=hdfs_user)

    def upload_files_to_hdfs(self, local_dir=LOCAL_CACHE_DIR, hdfs_dir=HDFS_TARGET_DIR):
        """
        遍历本地目录，筛选有意义的文件并上传到 HDFS。
        """
        for root, _, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = file.split('.')[-1].lower()

                # 筛选有意义的文件类型
                if file_extension in VALID_EXTENSIONS:
                    # 生成 HDFS 路径
                    hdfs_path = os.path.join(hdfs_dir, os.path.relpath(file_path, local_dir)).replace("\\", "/")

                    try:
                        # 上传到 HDFS
                        self.client.upload(hdfs_path, file_path, overwrite=True)
                        print(f"Uploaded: {file_path} -> {hdfs_path}")
                    except Exception as e:
                        print(f"Failed to upload {file_path}: {e}")

    def download_file_from_hdfs(self, hdfs_path, local_dir=LOCAL_CACHE_DIR):
        """
        从 HDFS 下载文件到本地目录。
        """
        local_path = os.path.join(local_dir, os.path.basename(hdfs_path))
        self.client.download(hdfs_path, local_path)
        print(f"Downloaded: {hdfs_path} -> {local_path}")