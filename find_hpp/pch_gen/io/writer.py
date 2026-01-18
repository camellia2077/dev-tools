# io/writer.py
import sys
from typing import TextIO

# 修改点：从兄弟目录 core.analyzer 导入数据结构
# .. 表示上一级目录 (pch_gen)，然后进入 core
from ..core.analyzer import PchReport, PchSection

def _get_root_dir(path: str) -> str:
    if '/' in path:
        return path.split('/')[0]
    return ""

def _write_section(stream: TextIO, section: PchSection):
    # ... (内容保持不变) ...
    stream.write(f"// ===================================================================\n")
    stream.write(f"//  {section.title}\n")
    stream.write(f"//  {section.description}\n")
    stream.write(f"// ===================================================================\n")
    
    if not section.items:
        stream.write("// (无)\n\n")
        return

    last_root_dir = None

    for header, count in section.items:
        current_root_dir = _get_root_dir(header)
        if last_root_dir is not None and current_root_dir != last_root_dir:
            stream.write("\n")
        last_root_dir = current_root_dir

        comment = f"// 使用次数: {count}"
        line = ""

        if section.category_type == 'std':
            line = f"#include <{header}>"
            if header in ['print', 'format']:
                comment += " (C++23)"
        
        elif section.category_type == '3rd':
            if header == "windows.h":
                stream.write("#ifdef _WIN32\n")
                stream.write(f"    #include <windows.h>                      {comment}\n")
                stream.write("#endif\n")
                continue
            
            if header.endswith(".h") or "/" in header:
                line = f"#include <{header}>"
            else:
                line = f"#include \"{header}\""
        
        else: # Proj
            line = f"#include \"{header}\""
        
        stream.write(f"{line.ljust(45)} {comment}\n")
    
    stream.write("\n")

def write_pch_content(report: PchReport, stream: TextIO = sys.stdout):
    stream.write("#pragma once\n")
    stream.write("#ifndef PCH_H\n")
    stream.write("#define PCH_H\n\n")

    for section in report.sections:
        _write_section(stream, section)

    stream.write("#endif //PCH_H\n")