import os
from . import core
from . import fs_utils

class BatchProcessor:
    def __init__(self, src_dir: str, extensions: tuple):
        self.src_dir = os.path.abspath(src_dir)
        self.extensions = extensions
        self.stats = {'added': 0, 'updated': 0, 'skipped': 0}

    def process(self):
        """执行批量处理流程。"""
        if not os.path.isdir(self.src_dir):
            raise FileNotFoundError(f"Directory not found: {self.src_dir}")

        print(f"🚀 开始扫描: {self.src_dir}")
        
        for file_path in fs_utils.walk_source_files(self.src_dir, self.extensions):
            self._handle_single_file(file_path)
            
        self._print_summary()

    def _handle_single_file(self, file_path: str):
        """处理单个文件的编排逻辑。"""
        # 1. 读取
        lines = fs_utils.read_file_lines(file_path)
        
        # 2. 逻辑计算
        expected_comment = core.calculate_header_comment(file_path, self.src_dir)
        status, new_lines, old_comment = core.analyze_and_update_content(lines, expected_comment)
        
        # 3. 根据结果执行 IO 和 UI 输出
        rel_path = os.path.relpath(file_path, self.src_dir)
        
        if status == 'added':
            print(f"[+] {rel_path}")
            fs_utils.write_file_lines(file_path, new_lines)
            self.stats['added'] += 1
            
        elif status == 'updated':
            print(f"[*] {rel_path}")
            print(f"    Old: {old_comment}")
            print(f"    New: {expected_comment.strip()}")
            fs_utils.write_file_lines(file_path, new_lines)
            self.stats['updated'] += 1
            
        else:
            # skipped
            self.stats['skipped'] += 1

    def _print_summary(self):
        print("\n================== 总结 ==================")
        print(f"+ 新增注释: {self.stats['added']}")
        print(f"* 更新注释: {self.stats['updated']}")
        print(f"- 跳过文件: {self.stats['skipped']}")
        print("========================================")