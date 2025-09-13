import os
import re

class CommentUpdater:
    """
    一个用于管理源代码文件头部路径注释的类。

    它会遍历指定目录下的 .hpp 和 .cpp 文件，
    确保每个文件的第一行都有一个正确的、相对于根目录的路径注释。
    """

    def __init__(self, src_dir):
        """
        初始化 CommentUpdater。

        Args:
            src_dir (str): 要处理的源代码根目录的路径。
        
        Raises:
            FileNotFoundError: 如果提供的目录不存在。
        """
        if not os.path.isdir(src_dir):
            raise FileNotFoundError(f"错误: 目录 '{src_dir}' 不存在或不是一个有效的目录。")
        
        self.src_dir = os.path.abspath(src_dir)
        self.added_count = 0
        self.updated_count = 0

    def _find_source_files(self):
        """
        遍历目录，生成器函数，逐一产出所有 .hpp 和 .cpp 文件的绝对路径。
        这是一个内部方法。
        """
        for root, _, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith((".hpp", ".cpp")):
                    yield os.path.join(root, file)

    def _process_single_file(self, file_path):
        """
        处理单个文件：检查、新增或修改其路径注释。
        这是一个内部方法，并会更新实例的计数器。
        """
        try:
            relative_path = os.path.relpath(file_path, self.src_dir)
            normalized_path = relative_path.replace(os.sep, '/')
            correct_path_comment = f"// {normalized_path}\n"

            with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
                lines = f.readlines()
                status = 'skipped'

                if not lines:
                    print(f"--- {normalized_path}")
                    print(f"+ {correct_path_comment.strip()}\n")
                    f.write(correct_path_comment)
                    status = 'added'
                else:
                    first_line = lines[0]
                    is_comment = re.match(r"//.*", first_line)
                    is_correct = first_line.strip() == correct_path_comment.strip()

                    if is_comment and not is_correct:
                        print(f"--- {normalized_path}")
                        print(f"- {first_line.strip()}")
                        print(f"+ {correct_path_comment.strip()}\n")
                        lines[0] = correct_path_comment
                        status = 'updated'
                    elif not is_comment:
                        print(f"--- {normalized_path}")
                        print(f"+ {correct_path_comment.strip()}\n")
                        lines.insert(0, correct_path_comment)
                        status = 'added'
                
                # 如果文件被修改，则写回
                if status in ['added', 'updated']:
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()
                    if status == 'added':
                        self.added_count += 1
                    else:
                        self.updated_count += 1

        except Exception as e:
            print(f"处理文件时出错 {file_path}: {e}")

    def run(self):
        """
        执行注释更新的主流程。
        """
        print(f"🚀 开始处理目录: {self.src_dir}\n")
        for file_path in self._find_source_files():
            self._process_single_file(file_path)
        print(f"\n处理完成。")
        
    def print_summary(self):
        """
        打印新增、修改和总计的摘要信息。
        """
        total_changed = self.added_count + self.updated_count
        print("================== 总结 ==================")
        print(f"+ 新增注释的文件数量: {self.added_count}")
        print(f"- 修改注释的文件数量: {self.updated_count}")
        print(f"✅ 总共更改的文件数量: {total_changed}")
        print("========================================")


if __name__ == "__main__":
    # --- 配置区 ---
    # 只需在此处修改您的源代码根目录
    SRC_DIR = r"C:\Computer\my_github\github_cpp\time_master\Time_Master_cpp\apps\time_master\src"

    try:
        # 1. 创建实例
        updater = CommentUpdater(SRC_DIR)
        # 2. 运行处理
        updater.run()
        # 3. 打印总结
        updater.print_summary()
    except FileNotFoundError as e:
        print(e)