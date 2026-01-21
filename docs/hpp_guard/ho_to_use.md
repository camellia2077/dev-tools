## 模式一：查询 (Dry Run)
此模式仅查找问题而不做任何修改。这是最安全的第一步，用于评估需要修改的文件范围。

```bash
python update_guards.py <your_project_directory>
```

## 模式二：自动修复 (Fix)
重要: 在运行此命令之前，强烈建议您使用 Git 等版本控制工具提交当前所有更改，或对项目进行备份。此操作将直接修改您的源代码文件。

```bash
python update_guards.py <your_project_directory> --fix
```