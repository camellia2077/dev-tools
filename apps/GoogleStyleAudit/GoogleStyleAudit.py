import re
from pathlib import Path

def generate_suggested_name(stem):
    """
    逻辑：将任何非 Google 风格的名称转换为 snake_case
    1. 处理连续大写 (JSONValidator -> json_validator)
    2. 处理大小写切换 (TextParser -> text_parser)
    3. 将连字符或空格替换为下划线
    """
    # 处理缩写与单词边界
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', stem)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    # 将非法字符（空格、连字符）替换为下划线
    s3 = re.sub(r'[^a-z0-9_]', '_', s2)
    # 处理连续下划线
    return re.sub(r'_+', '_', s3).strip('_')

def audit_google_style(directory):
    # 严格匹配 Google 风格：全小写、数字、下划线，字母开头
    google_regex = re.compile(r'^[a-z][a-z0-9_]*$')
    
    # 常见的 C++ 源文件和头文件后缀
    extensions = {'.cpp', '.h', '.hpp', '.cc', '.cxx', '.c', '.hh'}
    
    root_path = Path(directory)
    if not root_path.exists():
        print(f"错误: 路径不存在 -> {directory}")
        return

    print(f"\n[Google Style 审计模式] - 仅读取")
    print(f"检查路径: {root_path}")
    print(f"{'当前不规范路径':<60} | {'建议文件名'}")
    print("-" * 100)

    total_files = 0
    issue_files = 0

    # 递归扫描
    for path in root_path.rglob('*'):
        if path.is_file() and path.suffix.lower() in extensions:
            total_files += 1
            original_stem = path.stem
            
            # 校验是否不符合 Google 规范
            if not google_regex.match(original_stem):
                issue_files += 1
                suggested_stem = generate_suggested_name(original_stem)
                suggested_full_name = f"{suggested_stem}{path.suffix}"
                
                # 获取相对路径以便阅读
                rel_path = path.relative_to(root_path)
                print(f"{str(rel_path):<60} | {suggested_full_name}")

    print("-" * 100)
    print(f"审计汇总: 扫描 {total_files} 个文件，发现 {issue_files} 个不合规项。")
    if issue_files == 0:
        print("结果: 该目录完全符合 Google C++ 文件命名规范。")

if __name__ == "__main__":
    src_dir = r"C:\Computer\my_github\github_cpp\time_tracer\time_tracer_cpp\apps\time_tracer\src"
    audit_google_style(src_dir)