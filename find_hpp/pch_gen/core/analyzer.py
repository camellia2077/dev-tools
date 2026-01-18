# analyzer.py
from typing import List, Tuple, Dict, NamedTuple
from .classifier import HeaderClassifier, HeaderCategory

# === 数据结构定义 ===

class PchSection(NamedTuple):
    title: str
    description: str
    items: List[Tuple[str, int]]  # List[(header_name, count)]
    category_type: str            # 'std', '3rd', 'proj'

class PchReport:
    def __init__(self):
        self.sections: List[PchSection] = []

    def add_section(self, section: PchSection):
        self.sections.append(section)

# === 核心分析逻辑 ===

class ReportGenerator:
    def __init__(self, classifier: HeaderClassifier):
        """
        依赖注入：通过构造函数传入分类器。
        这样 analyzer 就不需要知道具体的标准库列表或配置。
        """
        self.classifier = classifier

    def _get_root_dir(self, path: str) -> str:
        """提取顶级目录，用于排序分组"""
        if '/' in path:
            return path.split('/')[0]
        return ""

    def _sort_headers(self, items: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """
        排序策略：
        1. 顶级目录 (字母序)：确保 writer 能在目录变化时插入空行。
        2. 使用次数 (降序)：同一目录下，高频文件排在前面。
        3. 文件名 (字母序)：作为 Tie-breaker，保证输出稳定。
        """
        return sorted(items, key=lambda x: (self._get_root_dir(x[0]), -x[1], x[0]))

    def generate_report(self, header_counts: List[Tuple[str, int]]) -> PchReport:
        """
        主流程：分类 -> 排序 -> 封装报告
        """
        # 1. 准备分类容器
        categorized: Dict[HeaderCategory, List[Tuple[str, int]]] = {
            HeaderCategory.STANDARD: [],
            HeaderCategory.THIRD_PARTY: [],
            HeaderCategory.PROJECT: []
        }

        # 2. 遍历并分类 (利用注入的 classifier)
        for header, count in header_counts:
            category = self.classifier.classify(header)
            categorized[category].append((header, count))

        # 3. 构建报告对象
        report = PchReport()
        
        # 添加标准库部分
        report.add_section(PchSection(
            title="1. C++ 标准库 (Standard Library)",
            description="最稳定、最庞大、使用最频繁的部分。",
            items=self._sort_headers(categorized[HeaderCategory.STANDARD]),
            category_type='std'
        ))

        # 添加第三方库部分
        report.add_section(PchSection(
            title="2. 平台与第三方库 (Platform & Third-Party)",
            description="改动频率低，是 PCH 的理想候选。",
            items=self._sort_headers(categorized[HeaderCategory.THIRD_PARTY]),
            category_type='3rd'
        ))

        # 添加项目代码部分
        report.add_section(PchSection(
            title="3. 项目内部稳定且常用的核心头文件",
            description="建议仅包含极少修改的核心接口。",
            items=self._sort_headers(categorized[HeaderCategory.PROJECT]),
            category_type='proj'
        ))

        return report