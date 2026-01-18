"""
主程序入口：整合 CLI、Scanner、Analyzer 和 Generator。
"""
import sys
import argparse

# 使用相对导入 (需要作为模块运行) 或者将包路径加入 sys.path
from . import config
from . import scanner
from . import analyzer
from . import generator

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="扫描 C++ 项目并生成预编译头文件 (PCH) 建议。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("src_path", help="要扫描的源代码根目录路径")
    
    parser.add_argument(
        "-n", "--top", 
        type=int, 
        default=50, 
        help="只分析出现频率最高的前 N 个头文件 (默认: 50)"
    )
    
    parser.add_argument(
        "--extra-libs", 
        nargs="+", 
        default=[], 
        help="追加第三方库的识别特征（前缀），例如: --extra-libs mylib/ boost/"
    )

    return parser.parse_args()

def run():
    args = parse_arguments()
    
    target_path = args.src_path
    top_n = args.top
    # 组合配置
    current_third_party_identifiers = config.DEFAULT_THIRD_PARTY_IDENTIFIERS + args.extra_libs

    # 1. 扫描阶段
    print(f"// 正在扫描目录: {target_path} ...", file=sys.stderr)
    try:
        files = scanner.scan_directory(target_path, ('.cpp', '.hpp', '.c', '.h', '.cc', '.cxx'))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("Error: 未找到 C++ 源代码文件。", file=sys.stderr)
        sys.exit(1)

    # 2. 统计阶段
    counts = scanner.extract_includes_stats(files)
    if not counts:
        print("Warning: 未扫描到任何 #include 指令。", file=sys.stderr)
        sys.exit(0)
    
    top_items = counts.most_common(top_n)

    # 3. 分析阶段
    std_lib, third_party, project_lib = analyzer.classify_headers(
        top_items, 
        current_third_party_identifiers
    )

    # 4. 生成阶段
    generator.generate_pch_content(std_lib, third_party, project_lib)

if __name__ == '__main__':
    run()