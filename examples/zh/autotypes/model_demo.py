"""
AutoModel 示例 - 苏轼传记摘要

使用 AutoModel 从文本中提取结构化摘要。

使用方法：
    python examples/zh/autotypes/model_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from typing import List, Optional
from hyperextract import AutoModel


class BiographySummary(BaseModel):
    """传记摘要结构"""
    title: str = Field(description="作品标题")
    subject: str = Field(description="主人公姓名")
    birth_year: Optional[str] = Field(default="", description="出生年份")
    death_year: Optional[str] = Field(default="", description="逝世年份")
    style_name: str = Field(description="字/号", default="")
    era: str = Field(description="所属朝代", default="")
    identity: List[str] = Field(default_factory=list, description="主要身份")
    summary: str = Field(description="人物生平概述")
    major_works: List[str] = Field(default_factory=list, description="代表作品")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoModel 示例 - 苏轼传记摘要")
    print("=" * 60)
    print("提取传记摘要...")

    model = AutoModel(
        data_schema=BiographySummary,
        llm_client=llm,
        embedder=embedder,
    )

    model.feed_text(text)

    data = model.data
    print(f"\n主人公：{data.subject}")
    print(f"生卒年份：{data.birth_year} - {data.death_year}")
    print(f"字号：{data.style_name}")
    print(f"\n摘要：{data.summary}")

    if data.major_works:
        print(f"\n代表作品：")
        for work in data.major_works[:3]:
            print(f"  - {work}")

    model.build_index()

    for q in ["作品", "黄州", "影响"]:
        print(f"\n查询：{q}")
        results = model.search(q, top_k=2)
        for r in results:
            print(f"  {r}")


if __name__ == "__main__":
    main()
