import os
import re
import sys
from pathlib import Path

def generate_expected_guard(file_path: Path) -> str:
    """
    根据文件名生成一个符合规范的头文件守卫名称。
    例如: 'MyClass.hpp' -> 'MY_CLASS_HPP'
          'detail/private_impl.hpp' -> 'DETAIL_PRIVATE_IMPL_HPP'
    """
    # 将路径的所有部分和文件名（不含扩展名）连接起来
    parts = list(file_path.parts)
    parts[-1] = file_path.stem
    
    # 将所有部分用下划线连接，并转换为大写
    guard = '_'.join(parts)
    
    # 清理不合法的字符（替换为下划线）并确保没有连续的下划线
    guard = re.sub(r'[^A-Z0-9_]', '_', guard.upper())
    guard = re.sub(r'__+', '_', guard)
    
    return f"{guard}_HPP"

def check_header_guards(directory: str):
    """
    遍历指定目录下的所有 .hpp 文件，并检查它们的头文件守卫。
    """
    print(f"--- 开始检查目录: {directory} ---\n")
    found_mismatch = False
    
    # 使用 pathlib 和 rglob 递归查找所有 .hpp 文件
    for hpp_file in Path(directory).rglob('*.hpp'):
        try:
            with open(hpp_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找 #ifndef 和 #define 语句
            ifndef_match = re.search(r'#ifndef\s+([A-Z0-9_]+)', content)
            define_match = re.search(r'#define\s+([A-Z0-9_]+)', content)

            if not ifndef_match or not define_match:
                print(f"❌ 文件 '{hpp_file}' 中未找到标准的头文件守卫。")
                found_mismatch = True
                continue

            # 提取找到的守卫名称
            ifndef_guard = ifndef_match.group(1)
            define_guard = define_match.group(1)

            if ifndef_guard != define_guard:
                print(f"❌ 文件 '{hpp_file}' 的 #ifndef 和 #define 守卫不匹配:")
                print(f"   - #ifndef: {ifndef_guard}")
                print(f"   - #define: {define_guard}\n")
                found_mismatch = True
                continue

            # 生成期望的守卫名称
            # 为了更准确，我们使用相对于输入目录的路径来生成守卫
            relative_path = hpp_file.relative_to(directory)
            expected_guard = generate_expected_guard(relative_path)
            
            # 检查是否匹配
            if ifndef_guard != expected_guard:
                print(f"❌ 文件 '{hpp_file}' 的头文件守卫不匹配:")
                print(f"   - 期望的守卫: {expected_guard}")
                print(f"   - 文件中的守卫: {ifndef_guard}\n")
                found_mismatch = True

        except Exception as e:
            print(f"❗️ 读取或处理文件 '{hpp_file}' 时发生错误: {e}")
            found_mismatch = True

    if not found_mismatch:
        print("✅ 所有 .hpp 文件的头文件守卫均符合规范。")
    
    print("\n--- 检查完成 ---")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python check_guards.py <your_directory_path>")
        sys.exit(1)
        
    target_directory = sys.argv[1]
    
    if not os.path.isdir(target_directory):
        print(f"错误: 提供的路径 '{target_directory}' 不是一个有效的目录。")
        sys.exit(1)
        
    check_header_guards(target_directory)