import os
from typing import Iterator, List

def walk_source_files(src_dir: str, extensions: tuple) -> Iterator[str]:
    """生成器：遍历获取符合条件的文件路径。"""
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(extensions):
                yield os.path.join(root, file)

def read_file_lines(file_path: str) -> List[str]:
    """安全读取文件内容。"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def write_file_lines(file_path: str, lines: List[str]):
    """写入文件内容。"""
    try:
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(lines)
    except Exception as e:
        print(f"Error writing {file_path}: {e}")