"""Hyperextract templates module.

此模块提供知识模板的配置文件和废弃的 Python 模板。

目录结构:
    templates/
    ├── presets/          # 预设模板（系统预置）
    ├── customs/         # 自定义模板（用户可自行创建）
    └── legacy/          # 废弃的 Python 模板

推荐使用方式:
    >>> from hyperextract.utils.template_engine import Gallery, TemplateFactory

    # 直接获取模板（自动加载 presets 和 customs）
    >>> config = Gallery.get("KnowledgeGraph")
    >>> template = TemplateFactory.create(config, llm_client, embedder)

    # 列出所有可用模板
    >>> print(Gallery.list_all())

    # 添加自定义模板目录
    >>> Gallery.add_path("/path/to/my/templates")

废弃的使用方式:
    >>> from hyperextract.templates.legacy.zh.general import KnowledgeGraph
    >>> template = KnowledgeGraph(llm_client=llm, embedder=embedder)
"""

from . import legacy

__all__ = [
    "legacy",
]
