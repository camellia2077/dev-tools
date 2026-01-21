# io/scanner.py
import os
from typing import Iterator, Tuple, List

class FileFinder:
    def __init__(self, extensions: Tuple[str, ...], exclude_names: List[str] = None):
        self.extensions = extensions
        # 将排除名单存入 set 以实现 O(1) 查找
        self.exclude_names = set(exclude_names) if exclude_names else set()

    def find_files(self, root_path: str) -> Iterator[str]:
        if not os.path.isdir(root_path):
            return
            
        for root, _, files in os.walk(root_path):
            for file in files:
                # 逻辑推导：
                # 1. 检查后缀是否匹配
                # 2. 检查文件名是否在黑名单中
                if file.lower().endswith(self.extensions):
                    if file.lower() in self.exclude_names:
                        continue
                    yield os.path.join(root, file)