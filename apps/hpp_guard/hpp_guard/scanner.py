from pathlib import Path
from . import worker

def scan_and_process_directory(directory: str, fix_mode: bool):
    """遍历目录并协调处理流程。"""
    project_root = Path(directory).resolve()
    
    print(f"--- 模式: {'修复 (Fix)' if fix_mode else '检查 (Check)'} ---")
    print(f"--- 根目录: {project_root} ---\n")

    stats = {
        'MATCH': 0, 'MISMATCH': 0, 'FIXED': 0, 'SKIP': 0, 'ERROR': 0
    }

    # 使用 rglob 获取所有 .hpp 文件
    files = list(project_root.rglob('*.hpp'))
    
    for file_path in files:
        status = worker.process_single_file(file_path, project_root, fix_mode)
        stats[status] += 1

    print("\n--- 检查总结 ---")
    print(f"扫描文件总数: {len(files)}")
    print(f"  ✅ 符合规范: {stats['MATCH']}")
    print(f"  🟡 跳过处理: {stats['SKIP']}")
    print(f"  ❗️ 读取错误: {stats['ERROR']}")

    if fix_mode:
        print(f"  🔧 成功修复: {stats['FIXED']}")
    else:
        print(f"  ❌ 发现不匹配: {stats['MISMATCH']}")
        if stats['MISMATCH'] > 0:
            print("\n提示: 添加 --fix 参数以自动修复这些问题。")
    
    print("--- 完成 ---")