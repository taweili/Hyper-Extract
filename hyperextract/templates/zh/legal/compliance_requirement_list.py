"""合规要求清单 - 提取文件中承诺遵守的具体义务或整改措施。

适用于反洗钱申报文件、合规审计报告、监管申报材料等。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class ComplianceRequirement(BaseModel):
    """合规要求"""
    requirement_type: str = Field(
        description="要求类型：客户身份识别、受益所有权识别、可疑交易报告、大额交易报告、客户风险分类、反洗钱培训、整改措施、其他"
    )
    requirement_name: str = Field(description="要求名称或简要描述")
    content: str = Field(description="要求的详细内容")
    compliance_status: str = Field(
        description="合规状态：已合规、持续改进、待整改、已整改"
    )
    deadline: Optional[str] = Field(
        description="完成期限，如2025年6月30日",
        default=None
    )
    responsible_department: Optional[str] = Field(
        description="责任部门",
        default=None
    )


_PROMPT = """## 角色与任务
你是一位专业的合规专员，请从反洗钱合规申报文件中提取所有合规要求。

## 提取规则
1. 提取文件中承诺遵守的具体义务或整改措施
2. 为每项要求指定类型：客户身份识别、受益所有权识别、可疑交易报告、大额交易报告、客户风险分类、反洗钱培训、整改措施、其他
3. 记录合规状态：已合规、持续改进、待整改、已整改
4. 记录完成期限和责任部门（如果有）

### 要求类型说明
- **客户身份识别**：客户身份识别相关要求
- **受益所有权识别**：受益所有权识别相关要求
- **可疑交易报告**：可疑交易监测和报告要求
- **大额交易报告**：大额交易报告要求
- **客户风险分类**：客户风险等级分类要求
- **反洗钱培训**：反洗钱培训要求
- **整改措施**：针对监管检查问题的整改承诺

### 约束条件
- 每项合规要求作为独立条目提取
- 保持内容与原文一致

## 合规申报文件:
{source_text}
"""


class ComplianceRequirementList(AutoList[ComplianceRequirement]):
    """
    适用文档: 反洗钱申报文件、合规审计报告、监管申报材料

    功能介绍:
    提取文件中承诺遵守的具体义务或整改措施。
    适用于合规差距分析、监管应对等应用场景。

    设计说明:
    - 元素（ComplianceRequirement）：存储合规要求信息，包括类型、名称、内容、状态、期限、部门

    Example:
        >>> template = ComplianceRequirementList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("合规申报文件内容...")
        >>> template.show()
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
        初始化合规要求清单模板。

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
            item_schema=ComplianceRequirement,
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
        展示合规要求清单。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: ComplianceRequirement) -> str:
            return f"[{item.compliance_status}] {item.requirement_name}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
