# parser.py
import re
from typing import List

class HeaderParser:
    def __init__(self):
        # 预编译正则，提高性能
        self._pattern = re.compile(r'^\s*#\s*include\s*[<"](.+?)[>"]', re.MULTILINE)

    def parse_content(self, content: str) -> List[str]:
        """输入文件内容字符串，返回头文件列表"""
        return self._pattern.findall(content)