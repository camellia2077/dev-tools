import os
import sys
import argparse
from . import scanner

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="检查并修复 C++ 头文件 (.hpp) 中的头文件守卫 (Google Style)。",
        epilog="示例: python run.py ./src --fix"
    )
    parser.add_argument("directory", help="C++ 项目的根目录。")
    parser.add_argument("--fix", action="store_true", help="自动修复不匹配的头文件守卫。")
    return parser.parse_args()

def run():
    args = parse_arguments()
    
    if not os.path.isdir(args.directory):
        print(f"错误: 目录不存在 '{args.directory}'")
        sys.exit(1)
        
    scanner.scan_and_process_directory(args.directory, args.fix)