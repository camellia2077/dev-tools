# scanner.py
import os
from typing import Iterator, Tuple

class FileFinder:
    def __init__(self, extensions: Tuple[str, ...]):
        self.extensions = extensions

    def find_files(self, root_path: str) -> Iterator[str]:
        """使用生成器 (Iterator) 节省内存，流式返回文件路径"""
        if not os.path.isdir(root_path):
            return
            
        for root, _, files in os.walk(root_path):
            for file in files:
                if file.lower().endswith(self.extensions):
                    yield os.path.join(root, file)