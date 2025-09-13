import os
import re
from collections import Counter

# ==================== 全局配置区 ====================
# 1. 设置要扫描的文件夹路径
TARGET_PATH = r"C:\Computer\my_github\github_cpp\time_master\Time_Master_cpp\time_master\src"

# 2. 设置要分析的前 N 个结果
TOP_N = 50

# 3. 配置第三方库的识别特征（前缀或完整名称）
THIRD_PARTY_IDENTIFIERS = [
    "nlohmann/",
    "sqlite3.h",
    "windows.h",
]

# C++ 标准库头文件列表 (基于 C++17/23)
CPP_STANDARD_HEADERS = {
    'iostream', 'fstream', 'sstream', 'iomanip', 'cstdio', 'string',
    'string_view', 'cstring', 'vector', 'list', 'deque', 'map', 'set',
    'unordered_map', 'unordered_set', 'queue', 'stack', 'array', 'algorithm',
    'numeric', 'cmath', 'cstdlib', 'random', 'complex', 'memory', 'new',
    'utility', 'functional', 'chrono', 'tuple', 'optional', 'variant', 'any',
    'stdexcept', 'exception', 'cassert', 'type_traits', 'iterator', 'thread',
    'mutex', 'atomic', 'future', 'condition_variable', 'filesystem', 'regex',
    'cstdint', 'limits', 'cctype', 'locale', 'ctime', 'print', 'format'
}
# ==================== 配置结束 ====================

def find_files(path, extensions):
    """
    递归查找指定目录下特定扩展名的文件。
    """
    file_paths = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths

def count_includes(file_paths):
    """
    统计给定文件列表中所有 #include 的头文件。
    """
    include_counter = Counter()
    include_regex = re.compile(r'#\s*include\s*[<"](.+?)[>"]')

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = include_regex.findall(content)
                include_counter.update(matches)
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")

    return include_counter

def classify_includes(top_items, third_party_identifiers):
    """
    将统计后的头文件列表分类为标准库、第三方库和项目内头文件。
    """
    std_lib_list, third_party_list, project_list = [], [], []
    for header, count in top_items:
        base_header = os.path.basename(header).replace('.h', '')
        if base_header in CPP_STANDARD_HEADERS:
            std_lib_list.append((header, count))
        elif any(header.startswith(prefix) for prefix in third_party_identifiers):
            third_party_list.append((header, count))
        else:
            project_list.append((header, count))
    return std_lib_list, third_party_list, project_list

def print_pch_section(title, description, items, is_std_lib=False, is_third_party=False):
    """
    格式化并打印PCH文件的一个区域。
    """
    print(f"// ===================================================================")
    print(f"//  {title}")
    print(f"//  {description}")
    print(f"// ===================================================================")
    if not items:
        print("// (无)")
        print("")
        return

    for header, count in items:
        comment = f"// 使用次数: {count}"
        line = ""
        if is_std_lib:
            line = f"#include <{header}>"
            if header in ['print', 'format']:
                comment += " (C++23)"
        elif is_third_party:
            if header == "windows.h":
                print("#ifdef _WIN32")
                line = f"#include <{header}>"
                print(f"    {line.ljust(41)} {comment}")
                print("#endif")
                continue
            elif header.endswith(".h"):
                line = f"#include <{header}>"
            else:
                line = f"#include \"{header}\""
        else: # Project files
            line = f"#include \"{header}\""
        
        print(f"{line.ljust(45)} {comment}")
    print("")

def generate_pch_output(std_lib, third_party, project_lib):
    """
    根据分类好的列表，生成完整的PCH文件内容。
    """
    print("#pragma once")
    print("#ifndef PCH_H")
    print("#define PCH_H\n")

    print_pch_section(
        "1. C++ 标准库 (Standard Library)",
        "最稳定、最庞大、使用最频繁的部分，PCH的核心价值所在。",
        std_lib,
        is_std_lib=True
    )

    print_pch_section(
        "2. 平台与第三方库 (Platform & Third-Party)",
        "这些库的内容不会由您修改，是PCH的完美候选。",
        third_party,
        is_third_party=True
    )
    
    print_pch_section(
        "3. 项目内全局通用且稳定的头文件",
        "这些是项目的基础设施，一旦成型，很少改动。",
        project_lib
    )

    print("\n#endif //PCH_H")


def analyze_and_generate_pch(target_path, top_n, third_party_identifiers):
    """
    执行头文件依赖分析并生成PCH格式的输出。
    """
    if not os.path.isdir(target_path):
        print(f"错误: 目录 '{target_path}' 不存在。")
        return

    # 步骤 1: 查找并统计
    cpp_hpp_files = find_files(target_path, ('.cpp', '.hpp'))
    if not cpp_hpp_files:
        print("未找到 .cpp 或 .hpp 文件。")
        return

    include_counts = count_includes(cpp_hpp_files)
    if not include_counts:
        print("未找到 #include 指令。")
        return

    top_items = include_counts.most_common(top_n)

    # 步骤 2: 分类
    std_lib, third_party, project_lib = classify_includes(top_items, third_party_identifiers)

    # 步骤 3: 生成输出
    generate_pch_output(std_lib, third_party, project_lib)


if __name__ == '__main__':
    analyze_and_generate_pch(TARGET_PATH, TOP_N, THIRD_PARTY_IDENTIFIERS)