# core/classifier.py
from enum import Enum
from typing import Set, List

class HeaderCategory(Enum):
    STANDARD = "std"
    THIRD_PARTY = "3rd"
    PROJECT = "proj"

class HeaderClassifier:
    def __init__(self, std_headers: Set[str], third_party_prefixes: List[str]):
        self.std_headers = std_headers
        self.third_party_prefixes = third_party_prefixes

    def classify(self, header: str) -> HeaderCategory:
        # 去掉路径和后缀检查标准库
        base_name = header.split('/')[-1].split('.')[0]
        
        if base_name in self.std_headers or header in self.std_headers:
            return HeaderCategory.STANDARD
        
        if any(header.startswith(pre) for pre in self.third_party_prefixes):
            return HeaderCategory.THIRD_PARTY
            
        return HeaderCategory.PROJECT