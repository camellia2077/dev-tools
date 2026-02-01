import re
from pathlib import Path
from typing import Optional, Tuple

def calculate_expected_guard(file_path: Path, project_root: Path) -> str:
    """[逻辑] 根据文件路径生成符合 Google 风格且无双下划线的头文件守卫。"""
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        rel_path = Path(file_path.name)

    parts = list(rel_path.parts)
    processed_parts = []
    
    for i, part in enumerate(parts):
        is_file = (i == len(parts) - 1)
        
        if is_file:
            # 1. 先去掉扩展名，统一记下是否需要加 _H
            stem = Path(part).stem
            # 2. 处理驼峰命名或其它特殊符号
            # 在大写字母前加下划线（仅限原有的驼峰）
            stem = re.sub(r'(?<!^)(?=[A-Z])', '_', stem)
            # 3. 转换为大写并替换点
            part_str = stem.upper().replace('.', '_')
            # 4. 拼接 Google 要求的 _H
            part_str += "_H"
        else:
            # 处理目录名
            part_str = re.sub(r'(?<!^)(?=[A-Z])', '_', part)
            part_str = part_str.upper().replace('.', '_')
        
        processed_parts.append(part_str)

    # 5. 用单下划线连接，并在末尾加上 Google 规范的最后一个下划线
    # 最终形式: PROJECT_PATH_FILE_H_
    return '_'.join(processed_parts).replace('__', '_') + '_'

def extract_guard_info(content: str) -> Tuple[Optional[str], bool]:
    """
    [解析] 从文件内容中提取当前的 #ifndef 守卫名称。
    返回: (found_guard_name, has_valid_endif)
    """
    ifndef_match = re.search(r'#ifndef\s+([A-Z0-9_]+)', content)
    define_match = re.search(r'#define\s+([A-Z0-9_]+)', content)
    
    if not ifndef_match or not define_match:
        return None, False

    current_guard = ifndef_match.group(1)
    
    # 检查是否存在匹配的 endif 注释
    endif_pattern = r'#endif\s*//\s*' + re.escape(current_guard)
    endif_match = re.search(endif_pattern, content)
    
    return current_guard, (endif_match is not None)

def replace_guard_content(content: str, old_guard: str, new_guard: str, has_endif_comment: bool) -> str:
    """[转换] 将内容中的旧守卫替换为新守卫。"""
    # 1. 替换 #ifndef 和 #define
    new_content = content.replace(f"#ifndef {old_guard}", f"#ifndef {new_guard}", 1)
    new_content = new_content.replace(f"#define {old_guard}", f"#define {new_guard}", 1)
    
    # 2. 替换 #endif 注释 (如果旧代码中存在注释)
    if has_endif_comment:
        pattern = r'(#endif\s*//\s*)' + re.escape(old_guard)
        new_content = re.sub(pattern, f'\\1{new_guard}', new_content, count=1)
        
    return new_content