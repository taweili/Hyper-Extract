"""术语定义表 - 去重并汇总合同中定义的所有专有名词。

适用于主服务协议、合同条款、法律文书等文本。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class DefinedTerm(BaseModel):
    """合同术语定义"""
    term: str = Field(description="术语名称，如机密信息、不可抗力、项目")
    definition: str = Field(description="术语的定义说明")
    source_clause: str = Field(description="定义来源的条款编号", default="")


_PROMPT = """## 角色与任务
你是一位专业的合同法律师，请从文本中提取所有定义的术语，形成术语定义表。

## 提取规则
1. 识别合同中用引号或黑体定义的专有名词（如"机密信息"、"不可抗力"）
2. 提取术语的定义说明
3. 记录定义出现的条款位置
4. 去重：同一术语只保留一条记录

### 约束条件
- 术语名称必须与原文保持一致（包括引号）
- 仅提取真正被定义的术语，不要提取普通业务词汇
- 保持客观准确，不添加文本中没有的信息

### 术语类型（供参考）
- 合同标的相关的术语（项目、软件产品、技术文档）
- 权利义务相关的术语（投资款、服务费、违约金）
- 风险相关的术语（不可抗力、机密信息）
- 程序相关的术语（验收标准、付款条件）

### 源文本:
"""


class DefinedTermRegistry(AutoSet[DefinedTerm]):
    """
    适用文档: 主服务协议（MSA）、劳动合同、采购合同、技术合同

    功能介绍:
    去重并汇总合同中定义的所有专有名词（如"机密信息"、"不可抗力"）。
    适用于术语一致性检查、合同摘要等应用场景。

    设计说明:
    - 元素（DefinedTerm）：存储术语定义信息，包括术语名称、定义、来源条款
    - 使用术语名称作为唯一键进行累加

    Example:
        >>> template = DefinedTermRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("合同条款内容...")
        >>> print(list(template))
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化术语定义表模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=DefinedTerm,
            key_extractor=lambda x: x.term.strip(),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示术语定义表。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: DefinedTerm) -> str:
            return f"{item.term}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
