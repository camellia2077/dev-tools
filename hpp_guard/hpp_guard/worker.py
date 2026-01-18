from pathlib import Path
from . import logic  # 相对导入

def process_single_file(file_path: Path, project_root: Path, fix_mode: bool) -> str:
    """
    处理单个文件：读取 -> 检查 -> (可选修复) -> 报告状态。
    返回状态码: 'MATCH', 'MISMATCH', 'FIXED', 'SKIP', 'ERROR'
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        current_guard, has_endif_comment = logic.extract_guard_info(content)
        
        if not current_guard:
            print(f"🟡 [SKIP] 无标准守卫: {file_path.relative_to(project_root)}")
            return 'SKIP'

        expected_guard = logic.calculate_expected_guard(file_path, project_root)

        if current_guard == expected_guard:
            return 'MATCH'

        # 发现不匹配
        rel_path = file_path.relative_to(project_root)
        
        if fix_mode:
            print(f"🔧 [FIXING] {rel_path}")
            print(f"   Old: {current_guard} -> New: {expected_guard}")
            
            new_content = logic.replace_guard_content(
                content, current_guard, expected_guard, has_endif_comment
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return 'FIXED'
        else:
            print(f"❌ [MISMATCH] {rel_path}")
            print(f"   Expected: {expected_guard}")
            print(f"   Found:    {current_guard}")
            return 'MISMATCH'

    except Exception as e:
        print(f"❗️ [ERROR] 处理文件 {file_path} 时出错: {e}")
        return 'ERROR'