import os

def rename_h_to_hpp_recursively(root_directory: str):
    """
    Recursively finds all files with the .h extension in a directory
    and its subdirectories, and renames them to .hpp.

    Args:
        root_directory (str): The root path of the folder to process.
    """
    if not os.path.isdir(root_directory):
        print(f"错误: 根目录 '{root_directory}' 不存在或不是一个有效的目录。")
        return

    print(f"开始递归扫描目录: '{root_directory}'...")
    renamed_count = 0
    
    # os.walk() 会遍历目录树，包括根目录和所有子目录
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # 检查文件后缀是否为 .h 
            if filename.endswith(".h"):
                # 构建原始文件的完整路径和新文件的完整路径 
                old_filepath = os.path.join(dirpath, filename)
                new_filename = filename[:-2] + ".hpp"
                new_filepath = os.path.join(dirpath, new_filename)

                # 执行重命名操作 
                try:
                    os.rename(old_filepath, new_filepath)
                    print(f"  已重命名: '{old_filepath}' -> '{new_filepath}'")
                    renamed_count += 1
                except OSError as e:
                    print(f"错误：重命名 '{old_filepath}' 时出错: {e}")

    if renamed_count == 0:
        print("在所有子目录中均未找到需要重命名的 .h 文件。")
    else:
        print(f"\n操作完成。总共重命名了 {renamed_count} 个文件。")

# --- 主要执行部分 ---
if __name__ == "__main__":
    # 指定要开始扫描的根目录 
    target_folder_path = r"C:\Computer\my_github\github_cpp\bill_master\Bills_Master_cpp\Bills_Master\src"

    # 调用函数，执行递归重命名操作
    rename_h_to_hpp_recursively(target_folder_path)