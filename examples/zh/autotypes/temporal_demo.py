"""
时序图示例 - 苏轼传记

使用 AutoTemporalGraph 从文本中提取时序关系。

使用方法：
    python examples/zh/autotypes/temporal_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    type: str = Field(description="类型：人物/地名/作品", default="人物")


class TimelineEvent(BaseModel):
    """时间线事件"""
    time: str = Field(description="时间（年份）")
    event: str = Field(description="事件描述")
    entities: list[str] = Field(description="参与实体")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  时序图示例")
    print("=" * 60)
    print("提取时序关系...")

    graph = AutoTemporalGraph[Entity, TimelineEvent](
        node_schema=Entity,
        edge_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个事件")

    sorted_events = sorted(graph.edges, key=lambda x: x.time)
    for event in sorted_events[:5]:
        print(f"  {event.time}：{event.event}")

    graph.build_index()

    for q in ["黄州", "贬谪", "乌台诗案"]:
        print(f"\n查询：{q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  事件：{[e.time for e in edges]}")


if __name__ == "__main__":
    main()
