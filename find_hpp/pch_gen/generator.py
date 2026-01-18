"""
生成模块：负责将分类后的数据格式化为 PCH 源码。
"""
from typing import List, Tuple

def _print_section(title: str, description: str, items: List[Tuple[str, int]], category_type: str):
    """(内部函数) 打印 PCH 的单个区块。"""
    print(f"// ===================================================================")
    print(f"//  {title}")
    print(f"//  {description}")
    print(f"// ===================================================================")
    
    if not items:
        print("// (无)\n")
        return

    for header, count in items:
        comment = f"// 使用次数: {count}"
        line = ""

        if category_type == 'std':
            line = f"#include <{header}>"
            if header in ['print', 'format']:
                comment += " (C++23)"
        
        elif category_type == '3rd':
            if header == "windows.h":
                print("#ifdef _WIN32")
                print(f"    #include <windows.h>                      {comment}")
                print("#endif")
                continue
            
            # 简单启发式策略
            if header.endswith(".h") or "/" in header:
                line = f"#include <{header}>"
            else:
                line = f"#include \"{header}\""
        
        else: # Project
            line = f"#include \"{header}\""
        
        print(f"{line.ljust(45)} {comment}")
    print("")

def generate_pch_content(std_lib, third_party, project_lib):
    """输出完整的 PCH 内容到标准输出。"""
    print("#pragma once")
    print("#ifndef PCH_H")
    print("#define PCH_H\n")

    _print_section(
        "1. C++ 标准库 (Standard Library)",
        "最稳定、最庞大、使用最频繁的部分。",
        std_lib, 'std'
    )

    _print_section(
        "2. 平台与第三方库 (Platform & Third-Party)",
        "改动频率低，是 PCH 的理想候选。",
        third_party, '3rd'
    )
    
    _print_section(
        "3. 项目内部稳定且常用的核心头文件 (Stable & Common Project Headers)",
        "建议仅包含极少修改的核心接口，频繁变动的头文件不应放入 PCH。",
        project_lib, 'proj'
    )

    print("#endif //PCH_H")