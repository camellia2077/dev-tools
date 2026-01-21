# main.py
import sys
import argparse
from collections import Counter

# 注意：这里路径发生了变化
from . import config
from .io.scanner import FileFinder          
from .core.parser import HeaderParser       
from .core.classifier import HeaderClassifier
from .core.analyzer import ReportGenerator 
from .io.writer import write_pch_content

def parse_arguments():
    parser = argparse.ArgumentParser(description="PCH (预编译头文件) 生成工具")
    parser.add_argument("src_path", help="源代码根目录")
    parser.add_argument("-n", "--top", type=int, default=50, help="分析前 N 个高频头文件")
    parser.add_argument("--extra-libs", nargs="+", default=[], help="追加第三方库前缀 (例如: mylib/)")
    return parser.parse_args()

def run():
    args = parse_arguments()
    exclude_list = ["pch.hpp", "cmake_pch.hxx"]
    # 1. 组装组件
    finder = FileFinder(
        extensions=('.cpp', '.hpp', '.h', '.cc', '.cxx', '.c'),
        exclude_names=exclude_list
    )
    parser = HeaderParser()
    
    tp_prefixes = config.DEFAULT_THIRD_PARTY_IDENTIFIERS + args.extra_libs
    classifier = HeaderClassifier(config.CPP_STANDARD_HEADERS, tp_prefixes)
    
    analyzer = ReportGenerator(classifier)

    # 2. 执行扫描
    print(f"// 正在扫描目录: {args.src_path} ...", file=sys.stderr)
    
    stats = Counter()
    try:
        for file_path in finder.find_files(args.src_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    headers = parser.parse_content(f.read())
                    stats.update(headers)
            except Exception:
                continue
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not stats:
        print("// 未找到任何头文件引用，请检查路径。", file=sys.stderr)
        return

    # 3. 分析与输出
    top_items = stats.most_common(args.top)
    report = analyzer.generate_report(top_items)
    write_pch_content(report, stream=sys.stdout)

if __name__ == '__main__':
    run()