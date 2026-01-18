"""
扫描模块：负责文件遍历和内容解析。
"""
import os
import re
import sys
from collections import Counter
from typing import List, Tuple

def scan_directory(path: str, extensions: Tuple[str, ...]) -> List[str]:
    """递归查找指定目录下特定扩展名的文件。"""
    file_paths = []
    if not os.path.isdir(path):
        raise FileNotFoundError(f"目录不存在: {path}")

    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith(extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths

def extract_includes_stats(file_paths: List[str]) -> Counter:
    """统计给定文件列表中所有 #include 的头文件频率。"""
    include_counter = Counter()
    # 编译正则：兼顾 <...> 和 "..."
    include_regex = re.compile(r'^\s*#\s*include\s*[<"](.+?)[>"]', re.MULTILINE)

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = include_regex.findall(content)
                include_counter.update(matches)
        except Exception as e:
            # 这里的 stderr 输出属于日志行为
            print(f"[Warning] 无法读取文件 {file_path}: {e}", file=sys.stderr)

    return include_counter