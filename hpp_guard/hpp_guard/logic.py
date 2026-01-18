import re
from pathlib import Path
from typing import Optional, Tuple

def calculate_expected_guard(file_path: Path, project_root: Path) -> str:
    """[逻辑] 根据文件路径生成 Google 风格的头文件守卫名称。"""
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        rel_path = Path(file_path.name)

    parts = list(rel_path.parts)
    processed_parts = []
    
    for part in parts:
        part = part.replace('.', '_')
        part = re.sub(r'(?<!^)(?=[A-Z])', '_', part) # CamelCase -> Snake_Case
        processed_parts.append(part.upper())

    return '_'.join(processed_parts) + '_'

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