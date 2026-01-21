"""
配置模块：包含标准库列表和默认的第三方库特征。
"""

# 默认的第三方库特征
DEFAULT_THIRD_PARTY_IDENTIFIERS = [
    "nlohmann/",
    "sqlite3.h",
    "toml++/toml.h",
    "windows.h",
]

# C++ 标准库头文件列表 (C++17/23)
CPP_STANDARD_HEADERS = {
    'iostream', 'fstream', 'sstream', 'iomanip', 'cstdio', 'string',
    'string_view', 'cstring', 'vector', 'list', 'deque', 'map', 'set',
    'unordered_map', 'unordered_set', 'queue', 'stack', 'array', 'algorithm',
    'numeric', 'cmath', 'cstdlib', 'random', 'complex', 'memory', 'new',
    'utility', 'functional', 'chrono', 'tuple', 'optional', 'variant', 'any',
    'stdexcept', 'exception', 'cassert', 'type_traits', 'iterator', 'thread',
    'mutex', 'atomic', 'future', 'condition_variable', 'filesystem', 'regex',
    'cstdint', 'limits', 'cctype', 'locale', 'ctime', 'print', 'format'
}