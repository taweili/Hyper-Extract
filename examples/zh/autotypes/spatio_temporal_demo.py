"""
时空图示例 - 苏轼传记

使用 AutoSpatioTemporalGraph 从文本中提取时空关系。

使用方法：
    python examples/zh/autotypes/spatio_temporal_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from typing import Optional
from hyperextract.types import AutoSpatioTemporalGraph


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="类别", default="人物")


class SpatioTemporalEvent(BaseModel):
    """时空事件"""
    source: str = Field(description="起点实体")
    target: str = Field(description="终点实体")
    action: str = Field(description="动作或关系")
    time: Optional[str] = Field(description="何时", default=None)
    location: Optional[str] = Field(description="何地", default=None)


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  时空图示例")
    print("=" * 60)
    print("提取时空事件...")

    graph = AutoSpatioTemporalGraph[Entity, SpatioTemporalEvent](
        node_schema=Entity,
        edge_schema=SpatioTemporalEvent,
        llm_client=llm,
        embedder=embedder,
        observation_location="北宋",
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个事件")

    sorted_edges = sorted(graph.edges, key=lambda x: x.time or "")
    for edge in sorted_edges[:5]:
        time_info = f"（{edge.time}）" if edge.time else ""
        loc_info = f" 在 {edge.location}" if edge.location else ""
        print(f"  {edge.source} --[{edge.action}]--> {edge.target}{time_info}{loc_info}")

    graph.build_index()

    for q in ["黄州", "杭州", "贬谪"]:
        print(f"\n查询：{q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  找到 {len(nodes)} 个实体，{len(edges)} 个事件")


if __name__ == "__main__":
    main()
