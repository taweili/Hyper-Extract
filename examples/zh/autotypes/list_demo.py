"""
AutoList 示例 - 苏轼人生事件

使用 AutoList 从文本中提取列表项，合并多个文本块。

使用方法：
    python examples/zh/autotypes/list_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract import AutoList


class TimelineEvent(BaseModel):
    """人生事件"""
    year: str = Field(description="事件发生年份")
    title: str = Field(description="事件标题")
    description: str = Field(description="事件描述")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoList 示例 - 苏轼人生事件")
    print("=" * 60)
    print("提取人生事件时间线...")

    timeline = AutoList[TimelineEvent](
        item_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    timeline.feed_text(text)

    sorted_events = sorted(timeline.items, key=lambda x: x.year)
    print(f"\n提取了 {len(sorted_events)} 个事件")

    for event in sorted_events[:5]:
        print(f"  {event.year}：{event.title}")

    timeline.build_index()

    for q in ["贬谪", "创作", "黄州"]:
        print(f"\n查询：{q}")
        results = timeline.search(q, top_k=3)
        for r in results:
            print(f"  {r.year}：{r.title}")


if __name__ == "__main__":
    main()
