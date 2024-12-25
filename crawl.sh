#!/bin/bash

# 设置 Python 环境（如果需要的话）
# 激活你的 Python 虚拟环境，例如：
# source /path/to/your/venv/bin/activate
conda activate search_engine

# 定义 crawl 目录
CRAWL_DIR="./crawl"

# 执行 GMH 目录下的所有 Python 脚本
echo "开始执行 GMH 目录下的爬虫脚本..."
for script in "$CRAWL_DIR"/GMH/*.py; do
    echo "执行 $script"
    python "$script"
    if [ $? -ne 0 ]; then
        echo "脚本 $script 执行失败!"
        exit 1
    fi
done

# 执行 Shencs 目录下的所有 Python 脚本
echo "开始执行 Shencs 目录下的爬虫脚本..."
for script in "$CRAWL_DIR"/Shencs/*.py; do
    echo "执行 $script"
    python "$script"
    if [ $? -ne 0 ]; then
        echo "脚本 $script 执行失败!"
        exit 1
    fi
done


echo "所有爬虫脚本执行完成!"
