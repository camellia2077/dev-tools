# file_handler.py

import os

def find_source_files(src_dir, extensions=(".hpp", ".cpp", ".h", ".c")):
    """
    遍历目录，生成器函数，逐一产出所有指定后缀文件的绝对路径。

    Args:
        src_dir (str): 要搜索的根目录。
        extensions (tuple): 包含文件扩展名的元组。

    Yields:
        str: 匹配文件的绝对路径。
    """
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(extensions):
                yield os.path.join(root, file)