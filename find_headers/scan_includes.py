import os
import re
from collections import Counter

# 用于查询头文件引用个数

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

if __name__ == '__main__':
    # ==================== 配置区域 ====================
    # 1. 设置要扫描的文件夹路径
    TARGET_PATH = r"C:\Computer\my_github\github_cpp\bills_master\Bills_Master_cpp\Bills_Master\src"

    # 2. 设置要分析的前 N 个结果 (建议值稍高，以便为PCH提供更多候选)
    TOP_N = 50

    # 3. 配置第三方库的识别特征（前缀或完整名称）
    THIRD_PARTY_IDENTIFIERS = [
        "nlohmann/",
        "sqlite3.h",
        "windows.h",
    ]
    # ==================== 配置结束 ====================

    if not os.path.isdir(TARGET_PATH):
        print(f"错误: 目录 '{TARGET_PATH}' 不存在。")
    else:
        # 不再打印扫描过程，直接输出最终结果
        # print(f"正在扫描 '{TARGET_PATH}' 目录下的 .cpp 和 .hpp 文件...")
        cpp_hpp_files = find_files(TARGET_PATH, ('.cpp', '.hpp'))

        if not cpp_hpp_files:
            print("未找到 .cpp 或 .hpp 文件。")
        else:
            include_counts = count_includes(cpp_hpp_files)

            if not include_counts:
                print("未找到 #include 指令。")
            else:
                top_items = include_counts.most_common(TOP_N)

                # 将它们分类
                std_lib_list = []
                third_party_list = []
                project_list = []

                for header, count in top_items:
                    base_header = os.path.basename(header).replace('.h', '')
                    if base_header in CPP_STANDARD_HEADERS:
                        std_lib_list.append((header, count))
                    elif any(header.startswith(prefix) for prefix in THIRD_PARTY_IDENTIFIERS):
                        third_party_list.append((header, count))
                    else:
                        project_list.append((header, count))
                
                # --- 开始生成 PCH 格式的输出 ---

                print("#pragma once")
                print("#ifndef PCH_H")
                print("#define PCH_H\n")

                # 1. 打印标准库头文件
                print("// ===================================================================")
                print("//  1. C++ 标准库 (Standard Library)")
                print("//  最稳定、最庞大、使用最频繁的部分，PCH的核心价值所在。")
                print("// ===================================================================")
                if std_lib_list:
                    for header, count in std_lib_list:
                        line = f"#include <{header}>"
                        comment = f"// 使用次数: {count}"
                        if header in ['print', 'format']:
                            comment += " (C++23)"
                        print(f"{line.ljust(45)} {comment}")
                else:
                    print("// (无)")
                print("")

                # 2. 打印第三方库头文件
                print("// ===================================================================")
                print("//  2. 平台与第三方库 (Platform & Third-Party)")
                print("//  这些库的内容不会由您修改，是PCH的完美候选。")
                print("// ===================================================================")
                if third_party_list:
                    for header, count in third_party_list:
                        line = ""
                        comment = f"// 使用次数: {count}"
                        # 特殊处理 windows.h
                        if header == "windows.h":
                            print("#ifdef _WIN32")
                            line = f"#include <{header}>"
                            print(f"    {line.ljust(41)} {comment}")
                            print("#endif")
                            continue
                        # C风格的库用 <>
                        elif header.endswith(".h"):
                            line = f"#include <{header}>"
                        # 其他用 ""
                        else:
                            line = f"#include \"{header}\""
                        print(f"{line.ljust(45)} {comment}")
                else:
                    print("// (无)")
                print("")

                # 3. 打印项目内头文件
                print("// ===================================================================")
                print("//  3. 项目内全局通用且稳定的头文件")
                print("//  这些是项目的基础设施，一旦成型，很少改动。")
                print("//  (建议根据项目结构手动调整此部分顺序和分组)")
                print("// ===================================================================")
                if project_list:
                    for header, count in project_list:
                        line = f"#include \"{header}\""
                        comment = f"// 使用次数: {count}"
                        print(f"{line.ljust(45)} {comment}")
                else:
                    print("// (无)")

                print("\n#endif //PCH_H")