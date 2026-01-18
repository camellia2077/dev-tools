import argparse
from .processor import BatchProcessor

def main():
    parser = argparse.ArgumentParser(
        description="C/C++ 源码头部路径注释自动维护工具。",
        epilog="示例: python run.py ./src --ext .h .c"
    )
    
    parser.add_argument("src_dir", help="源代码根目录路径")
    parser.add_argument(
        "--ext", 
        nargs='+', 
        default=['.hpp', '.cpp', '.h', '.c'],
        help="目标文件扩展名 (默认: .hpp .cpp .h .c)"
    )
    
    args = parser.parse_args()

    try:
        processor = BatchProcessor(args.src_dir, tuple(args.ext))
        processor.process()
    except Exception as e:
        print(f"程序执行出错: {e}")