"""
分析模块：负责对头文件数据进行清洗、分类和逻辑判断。
"""
import os
from typing import List, Tuple
from .config import CPP_STANDARD_HEADERS

def classify_headers(
    header_counts: List[Tuple[str, int]], 
    third_party_identifiers: List[str]
) -> Tuple[List, List, List]:
    """
    将统计后的头文件列表分类为：标准库、第三方库、项目内头文件。
    """
    std_lib_list = []
    third_party_list = []
    project_list = []

    for header, count in header_counts:
        # 移除 .h 后进行查找 (处理 C 兼容头文件)
        base_header_check = os.path.basename(header).replace('.h', '')
        
        # 判定逻辑
        if base_header_check in CPP_STANDARD_HEADERS or header in CPP_STANDARD_HEADERS:
            std_lib_list.append((header, count))
        elif any(header.startswith(prefix) for prefix in third_party_identifiers):
            third_party_list.append((header, count))
        else:
            project_list.append((header, count))
            
    return std_lib_list, third_party_list, project_list