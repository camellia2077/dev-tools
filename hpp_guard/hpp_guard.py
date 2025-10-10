import os
import re
import sys
import argparse
from pathlib import Path
# 用于检查和修复 C++ 头文件 (.hpp) 中的头文件守卫 (Include Guards)

def generate_expected_guard(file_path: Path) -> str:
    """
    根据文件名生成一个符合规范的头文件守卫名称。
    这个版本会正确处理驼峰命名 (CamelCase)。
    例如: 'FileHandler.hpp' -> 'FILE_HANDLER_HPP'
          'AnsiColors.hpp' -> 'ANSI_COLORS_HPP'
    """
    stem = file_path.stem
    guard = re.sub(r'(?<!^)(?=[A-Z])', '_', stem)
    guard = guard.upper() + '_HPP'
    return guard

def update_header_guards(directory: str, fix_files: bool = False):
    """
    遍历指定目录下的所有 .hpp 文件，检查并根据参数选择是否修复头文件守卫。
    :param directory: 要检查的目录路径。
    :param fix_files: 如果为 True，则自动修复不匹配的守卫。
    """
    if fix_files:
        print(f"--- 模式: 查找并修复 ---")
    else:
        print(f"--- 模式: 只读查询 (dry run) ---")
    
    print(f"--- 开始检查目录: {directory} ---\n")
    
    mismatched_files = []
    
    for hpp_file in Path(directory).rglob('*.hpp'):
        try:
            with open(hpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 使用正则表达式查找 #ifndef, #define, 和 #endif 语句
            ifndef_match = re.search(r'#ifndef\s+([A-Z0-9_]+)', content)
            define_match = re.search(r'#define\s+([A-Z0-9_]+)', content)
            # 查找与ifndef匹配的endif语句
            endif_match = re.search(r'#endif\s*//\s*' + re.escape(ifndef_match.group(1)) if ifndef_match else r'$^', content)

            if not ifndef_match or not define_match:
                print(f"🟡 文件 '{hpp_file}' 中未找到标准的头文件守卫，已跳过。")
                continue

            current_guard = ifndef_match.group(1)
            expected_guard = generate_expected_guard(hpp_file)

            if current_guard != expected_guard:
                mismatched_files.append({
                    "path": hpp_file,
                    "current": current_guard,
                    "expected": expected_guard,
                    "endif_found": endif_match is not None
                })
                
                # 如果是修复模式，则直接修改文件
                if fix_files:
                    print(f"🔧 正在修复文件: {hpp_file}")
                    print(f"   - 从: {current_guard}")
                    print(f"   - 到: {expected_guard}")
                    
                    # 替换 #ifndef 和 #define
                    new_content = content.replace(f"#ifndef {current_guard}", f"#ifndef {expected_guard}", 1)
                    new_content = new_content.replace(f"#define {current_guard}", f"#define {expected_guard}", 1)
                    
                    # 替换 #endif 注释 (如果存在)
                    if endif_match:
                        new_content = new_content.replace(f"#endif // {current_guard}", f"#endif // {expected_guard}", 1)
                    
                    # 将修改后的内容写回文件
                    with open(hpp_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                else:
                    # 如果只是查询模式，则打印信息
                    print(f"❌ 文件 '{hpp_file}' 的头文件守卫不匹配:")
                    print(f"   - 期望的守卫: {expected_guard}")
                    print(f"   - 文件中的守卫: {current_guard}\n")

        except Exception as e:
            print(f"❗️ 读取或处理文件 '{hpp_file}' 时发生错误: {e}")

    print("\n--- 检查总结 ---")
    if not mismatched_files:
        print("✅ 所有 .hpp 文件的头文件守卫均符合规范。")
    else:
        count = len(mismatched_files)
        if fix_files:
            print(f"✅ 成功修复了 {count} 个文件的头文件守卫。")
        else:
            print(f"发现 {count} 个文件存在不匹配的头文件守卫。")
            print("要自动修复这些文件，请在命令后添加 --fix 标志。")

    print("--- 检查完成 ---")

if __name__ == "__main__":
    # 使用 argparse 来处理命令行参数
    parser = argparse.ArgumentParser(
        description="检查并修复 C++ 头文件 (.hpp) 中的头文件守卫 (Include Guards)。",
        epilog="示例: python update_guards.py ./my_project --fix"
    )
    parser.add_argument("directory", help="要递归检查的 C++ 项目根目录的路径。")
    parser.add_argument("--fix", action="store_true", help="自动修复找到的不匹配的头文件守卫。如果未提供此项，则只进行检查（dry run）。")
    
    args = parser.parse_args()
    
    target_directory = args.directory
    
    if not os.path.isdir(target_directory):
        print(f"错误: 提供的路径 '{target_directory}' 不是一个有效的目录。")
        sys.exit(1)
        
    update_header_guards(target_directory, args.fix)