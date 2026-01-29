import argparse
import sys
import re
import difflib
from pathlib import Path

# 配置常量
CPP_EXTENSIONS = {'.h', '.hpp', '.cpp', '.c', '.cc', '.hh'}
INCLUDE_PATTERN = re.compile(r'#include\s+"([^/\\\s]+\.(?:hpp|h|cpp|c|cc|hh))"')

def build_file_map(root_dir):
    """
    职责：【索引构建】
    遍历目录，建立 "文件名 -> 相对路径" 的映射字典。
    """
    file_map = {}
    for path in root_dir.rglob('*'):
        if path.is_file() and path.suffix in CPP_EXTENSIONS:
            try:
                # as_posix() 确保路径分隔符为正斜杠 /
                rel_path = path.relative_to(root_dir).as_posix()
                file_map[path.name] = rel_path
            except ValueError:
                continue
    return file_map

def read_source_file(file_path):
    """
    职责：【文件读取】
    处理编码兼容性 (UTF-8 / GBK)，返回文件内容字符串。
    如果读取失败，返回 None。
    """
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding='gbk')
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
            return None

def fix_include_lines(content, file_map):
    """
    职责：【核心转换逻辑】
    纯粹的字符串处理。输入原始内容，输出新旧行列表和修改标记。
    不涉及任何 IO 操作。
    """
    old_lines = content.splitlines(keepends=True)
    new_lines = []
    modified = False

    for line in old_lines:
        match = INCLUDE_PATTERN.search(line)
        if match:
            filename = match.group(1)
            # 检查引用的文件是否存在于我们的索引中
            if filename in file_map:
                new_path = file_map[filename]
                # 仅当新路径与原写法不同时才替换
                if new_path != filename:
                    new_line = line.replace(f'"{filename}"', f'"{new_path}"')
                    new_lines.append(new_line)
                    modified = True
                    continue
        # 保持原样
        new_lines.append(line)
    
    return old_lines, new_lines, modified

def save_and_report_diff(file_path, root_dir, old_lines, new_lines):
    """
    职责：【结果输出】
    打印 Diff 信息并将新内容写入文件。
    """
    # 生成 Diff
    diff = difflib.unified_diff(
        old_lines, 
        new_lines, 
        fromfile=f"a/{file_path.name}", 
        tofile=f"b/{file_path.name}"
    )
    
    print(f"\nRefactoring: {file_path.relative_to(root_dir)}")
    print("".join(diff))

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def process_single_file(file_path, root_dir, file_map):
    """
    职责：【单文件流程编排】
    串联读取、转换、写入三个步骤。
    """
    content = read_source_file(file_path)
    if content is None:
        return

    old_lines, new_lines, modified = fix_include_lines(content, file_map)

    if modified:
        save_and_report_diff(file_path, root_dir, old_lines, new_lines)

def scan_and_update(root_dir, file_map):
    """
    职责：【批量任务分发】
    遍历目标列表，对每个文件调用处理函数。
    """
    target_files = [
        p for p in root_dir.rglob('*') 
        if p.is_file() and p.suffix in CPP_EXTENSIONS
    ]

    for file_path in target_files:
        process_single_file(file_path, root_dir, file_map)

def run():
    """
    职责：【程序入口】
    处理命令行参数，初始化环境，启动主流程。
    """
    parser = argparse.ArgumentParser(description="Fix C++ include paths to be relative to source root.")
    
    parser.add_argument(
        "target_dir", 
        type=str, 
        help="Target source directory to scan and fix (e.g., src/)"
    )

    args = parser.parse_args()
    target_path = Path(args.target_dir).resolve()

    if target_path.exists() and target_path.is_dir():
        print(f"--- Refactoring Includes in {target_path} ---\n")
        
        # 1. 建立全局索引
        mapping = build_file_map(target_path)
        # 2. 执行更新
        scan_and_update(target_path, mapping)
        
        print("\n--- Process Finished ---")
    else:
        print(f"Error: Directory not found or is not a directory: {target_path}")
        sys.exit(1)