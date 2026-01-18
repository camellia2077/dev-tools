import os
import re
from typing import List, Tuple, Optional

def calculate_header_comment(file_path: str, root_dir: str) -> str:
    """计算文件应有的头部路径注释。"""
    try:
        relative_path = os.path.relpath(file_path, root_dir)
        # 统一使用正斜杠
        normalized_path = relative_path.replace(os.sep, '/')
        return f"// {normalized_path}\n"
    except ValueError:
        # 处理路径不在 root_dir 下的情况
        return f"// {os.path.basename(file_path)}\n"

def analyze_and_update_content(lines: List[str], expected_comment: str) -> Tuple[str, List[str], Optional[str]]:
    """
    分析文件内容列表，决定是否需要更新。
    
    Returns:
        status (str): 'added', 'updated', 'skipped'
        new_lines (List[str]): 更新后的内容列表
        old_comment (str):如果被替换，返回旧注释，否则为 None
    """
    if not lines:
        # 空文件
        return 'added', [expected_comment], None

    first_line = lines[0]
    is_comment = re.match(r"^\s*//", first_line) is not None
    # 比较时忽略首尾空白，但写入时保留换行
    is_correct = first_line.strip() == expected_comment.strip()

    if is_comment:
        if not is_correct:
            # 存在注释但不对 -> 更新
            new_lines = lines[:]
            new_lines[0] = expected_comment
            return 'updated', new_lines, first_line.strip()
        else:
            # 存在且正确 -> 跳过
            return 'skipped', lines, None
    else:
        # 第一行不是注释 -> 新增
        new_lines = [expected_comment] + lines
        return 'added', new_lines, None