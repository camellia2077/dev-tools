import os
import re
import sys

# --- 全局变量 ---
# 请将这里设置为您的项目源代码根目录
SRC_DIR = r"C:\Computer\my_github\github_cpp\time_master\Time_Master_cpp\apps\time_master\src"

# ANSI 颜色代码
# 检查是否在 Windows 的 cmd.exe 中，它可能不支持 ANSI
if sys.platform == "win32" and os.getenv("TERM") is None:
    COLOR_RED = ""
    COLOR_GREEN = ""
    COLOR_YELLOW = ""
    COLOR_RESET = ""
else:
    COLOR_RED = "\033[91m"      # 亮红色
    COLOR_GREEN = "\033[92m"    # 亮绿色
    COLOR_YELLOW = "\033[93m"   # 亮黄色
    COLOR_RESET = "\033[0m"     # 重置颜色

def process_source_files():
    """
    遍历并更新源文件注释，使用 diff 风格的彩色输出。
    """
    added_count = 0
    updated_count = 0
    
    src_dir_abs = os.path.abspath(SRC_DIR)

    for root, _, files in os.walk(src_dir_abs):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                file_path = os.path.join(root, file)
                try:
                    relative_path = os.path.relpath(file_path, src_dir_abs)
                    normalized_path = relative_path.replace(os.sep, '/')
                    correct_path_comment = f"// {normalized_path}\n"

                    # 使用 'r+' 模式打开文件进行读写
                    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
                        lines = f.readlines()

                        if not lines:
                            # --- 新增逻辑 (空文件) ---
                            print(f"{COLOR_YELLOW}--- {normalized_path}{COLOR_RESET}")
                            print(f"{COLOR_GREEN}+ {correct_path_comment.strip()}{COLOR_RESET}\n")
                            f.write(correct_path_comment)
                            added_count += 1
                            continue

                        first_line = lines[0]
                        match = re.match(r"//.*", first_line)

                        if match:
                            # 第一行是注释，检查是否需要修改
                            if first_line.strip() != correct_path_comment.strip():
                                # --- 修改逻辑 ---
                                print(f"{COLOR_YELLOW}--- {normalized_path}{COLOR_RESET}")
                                print(f"{COLOR_RED}- {first_line.strip()}{COLOR_RESET}")
                                print(f"{COLOR_GREEN}+ {correct_path_comment.strip()}{COLOR_RESET}\n")
                                
                                lines[0] = correct_path_comment
                                f.seek(0)
                                f.writelines(lines)
                                f.truncate()
                                updated_count += 1
                        else:
                            # --- 新增逻辑 (第一行非注释) ---
                            print(f"{COLOR_YELLOW}--- {normalized_path}{COLOR_RESET}")
                            print(f"{COLOR_GREEN}+ {correct_path_comment.strip()}{COLOR_RESET}\n")

                            lines.insert(0, correct_path_comment)
                            f.seek(0)
                            f.writelines(lines)
                            f.truncate()
                            added_count += 1

                except Exception as e:
                    print(f"处理文件时出错 {file_path}: {e}")

    return added_count, updated_count

if __name__ == "__main__":
    if not os.path.isdir(SRC_DIR):
        print(f"{COLOR_RED}❌ 错误: 目录 '{SRC_DIR}' 不存在或不是一个有效的目录。{COLOR_RESET}")
    else:
        print(f"🚀 开始处理目录: {SRC_DIR}\n")
        added, updated = process_source_files()
        total_changed = added + updated
        
        print(f"\n处理完成。")
        print("================== 总结 ==================")
        print(f"{COLOR_GREEN}+ 新增注释的文件数量: {added}{COLOR_RESET}")
        print(f"{COLOR_YELLOW}- 修改注释的文件数量: {updated}{COLOR_RESET}")
        print(f"✅ 总共更改的文件数量: {total_changed}")
        print("========================================")