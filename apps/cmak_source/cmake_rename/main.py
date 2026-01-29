import re
import os
import argparse
import sys

# 匹配包含路径的 C++ 源文件名
# 解释：[\w/]+ 匹配路径，\.(...) 匹配后缀
FILE_REF_PATTERN = r'[\w/]+\.(cpp|hpp|c|h|cc|hh)'

def to_snake_case(name):
    """
    职责：【字符串转换】
    纯逻辑函数。将 PascalCase 转换为 snake_case。
    """
    # 处理连续大写，例如 XMLReader -> xml_reader
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 处理普通大写，例如 JsonReader -> json_reader
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def transform_path_string(full_path):
    """
    职责：【路径处理】
    接收一个文件路径字符串，仅修改文件名部分为 snake_case，并标准化分隔符。
    """
    # 分离路径和文件名 (src/common/, JsonReader.cpp)
    dir_name, base_name = os.path.split(full_path)
    
    # 分离文件名和后缀 (JsonReader, .cpp)
    file_root, file_ext = os.path.splitext(base_name)
    
    # 转换文件名
    new_file_root = to_snake_case(file_root)
    new_base_name = new_file_root + file_ext
    
    # 重新组合，强制使用正斜杠 / (CMake 标准)
    return os.path.join(dir_name, new_base_name).replace('\\', '/')

def regex_callback(match):
    """
    职责：【正则适配】
    连接正则匹配对象与路径处理逻辑。
    """
    return transform_path_string(match.group(0))

def process_content(content):
    """
    职责：【文本处理】
    接收原始文本，执行正则替换，返回新文本和修改次数。
    不涉及任何文件读写。
    """
    return re.subn(FILE_REF_PATTERN, regex_callback, content)

def read_cmake_file(file_path):
    """
    职责：【文件读取】
    处理文件存在性检查和读取异常。
    """
    if not os.path.exists(file_path):
        print(f"❌ 错误: 找不到文件 {file_path}")
        return None

    print(f"正在读取 {file_path} ...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取错误: {e}")
        return None

def write_cmake_file(file_path, content):
    """
    职责：【文件写入】
    将处理后的内容回写到磁盘。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ 写入错误: {e}")
        return False

def run():
    """
    职责：【程序入口与流程编排】
    解析参数 -> 读取 -> 处理 -> 写入 -> 汇报。
    """
    # 1. 参数解析
    parser = argparse.ArgumentParser(description="CMake 源码文件引用命名风格转换工具 (PascalCase -> snake_case)")
    parser.add_argument(
        "file_path", 
        type=str, 
        help="目标 CMake 文件的绝对或相对路径 (例如: SourceFileCollection.cmake)"
    )
    args = parser.parse_args()
    
    # 2. 读取文件
    content = read_cmake_file(args.file_path)
    if content is None:
        sys.exit(1)

    # 3. 核心逻辑处理
    new_content, count = process_content(content)

    # 4. 结果处理与写入
    if count > 0:
        if write_cmake_file(args.file_path, new_content):
            print(f"✅ 成功更新了 {count} 处引用！")
            print("建议使用 git diff 查看具体的修改内容。")
        else:
            sys.exit(1)
    else:
        print("⚠️ 未发现需要修改的文件引用。")