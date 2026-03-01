"""责任条款清单 - 提取关于赔偿、责任限制、保证及免责声明的具体条款。

适用于主服务协议、劳动合同、采购合同等商业合同文本。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class LiabilityClause(BaseModel):
    """责任条款"""
    clause_type: str = Field(
        description="条款类型：赔偿条款、责任限制、保证条款、免责声明、违约金、连带责任、其他"
    )
    clause_title: str = Field(description="条款标题或简要名称")
    content: str = Field(description="条款的具体内容")
    liability_amount: Optional[str] = Field(
        description="涉及的责任金额或计算方式，如合同总价的10%、人民币20万元等",
        default=None
    )
    source_clause: str = Field(description="条款来源的章节编号", default="")


_PROMPT = """## 角色与任务
你是一位专业的合同法律师，请从文本中提取所有关于责任、赔偿、保证的条款。

## 提取规则
1. 提取文本中所有关于责任分配的具体条款
2. 为每一条款指定类型：赔偿条款、责任限制、保证条款、免责声明、违约金、连带责任、其他
3. 记录条款的具体内容和涉及的责任金额
4. 记录条款来源的章节编号

### 条款类型说明
- **赔偿条款**：约定一方给另一方造成损失时的赔偿方式
- **责任限制**：限制某方承担责任的最高限额
- **保证条款**：一方对某事项的保证承诺
- **免责声明**：免除或限制某方责任的条款
- **违约金**：约定违约时支付的违约金
- **连带责任**：约定多方承担连带责任
- **其他**：不属于上述类别的责任条款

### 约束条件
- 每项责任条款作为独立条目提取
- 保持条款内容与原文一致
- 不要遗漏任何责任相关条款

## 合同条款:
{source_text}
"""


class LiabilityClauseList(AutoList[LiabilityClause]):
    """
    适用文档: 主服务协议（MSA）、劳动合同、采购合同、技术合同

    功能介绍:
    提取关于赔偿、责任限制、保证及免责声明的具体条款。
    适用于合同风险评估、法务审核等应用场景。

    设计说明:
    - 元素（LiabilityClause）：存储责任条款信息，包括类型、标题、内容、责任金额、来源

    Example:
        >>> template = LiabilityClauseList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("合同条款内容...")
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
        初始化责任条款清单模板。

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
            item_schema=LiabilityClause,
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
        展示责任条款清单。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: LiabilityClause) -> str:
            return f"[{item.clause_type}] {item.clause_title}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
