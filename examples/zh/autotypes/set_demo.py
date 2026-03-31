"""
AutoSet 示例 - 苏轼相关人物

使用 AutoSet 从文本中提取去重的人物集合。

使用方法：
    python examples/zh/autotypes/set_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract import AutoSet


class Person(BaseModel):
    """人物实体"""
    name: str = Field(description="人物姓名")
    category: str = Field(description="类别：家人/师友/政敌", default="人物")
    description: str = Field(description="简要描述", default="")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoSet 示例 - 苏轼相关人物")
    print("=" * 60)
    print("提取并去重人物...")

    entities = AutoSet[Person](
        item_schema=Person,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )

    entities.feed_text(text)

    print(f"\n提取了 {len(entities.items)} 个不同人物")

    categories = {}
    for p in entities.items:
        categories.setdefault(p.category, []).append(p)

    for cat, persons in sorted(categories.items()):
        print(f"\n{cat}：")
        for p in persons[:5]:
            print(f"  - {p.name}")

    entities.build_index()

    for q in ["苏洵", "王安石", "欧阳修"]:
        print(f"\n查询：{q}")
        results = entities.search(q, top_k=3)
        for r in results:
            print(f"  {r.name}（{r.category}）")


if __name__ == "__main__":
    main()
