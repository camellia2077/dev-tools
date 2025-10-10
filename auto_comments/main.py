# main.py

import argparse
from comment_processor import CommentUpdater  # 从我们的核心逻辑模块导入类

def main():
    """
    主函数，用于解析命令行参数并启动注释更新流程。
    """
    parser = argparse.ArgumentParser(
        description="自动更新或添加 C/C++ 源代码文件的头部路径注释。",
        epilog="示例: python main.py \"C:\\path\\to\\your\\src\" --ext .h .c .hpp"
    )
    
    parser.add_argument(
        "src_dir",
        type=str,
        help="要处理的源代码根目录的路径。"
    )
    
    parser.add_argument(
        "--ext",
        nargs='+',  # 允许多个值，例如 --ext .h .c
        default=['.hpp', '.cpp', '.h', '.c'],
        help="要处理的文件扩展名列表。默认值: .hpp .cpp .h .c"
    )
    
    args = parser.parse_args()

    try:
        # 将解析出的扩展名列表转为元组，以供 endswith() 使用
        extensions_tuple = tuple(args.ext)
        
        # 使用从命令行获取的路径和扩展名创建实例
        updater = CommentUpdater(args.src_dir, extensions=extensions_tuple)
        updater.run()
        updater.print_summary()
        
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"发生了一个未知错误: {e}")


if __name__ == "__main__":
    main()