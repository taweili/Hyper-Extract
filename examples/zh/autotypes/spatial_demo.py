"""
空间图示例 - 苏轼传记

使用 AutoSpatialGraph 从文本中提取空间关系。

使用方法：
    python examples/zh/autotypes/spatial_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoSpatialGraph


class Location(BaseModel):
    """地点实体"""
    name: str = Field(description="地点名称")
    category: str = Field(description="类别：城市/建筑/地区", default="地区")
    description: str = Field(description="简要描述", default="")


class SpatialRelation(BaseModel):
    """空间关系"""
    source: str = Field(description="起点地点")
    target: str = Field(description="终点地点")
    relation: str = Field(description="空间关系类型")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  空间图示例")
    print("=" * 60)
    print("提取空间关系...")

    graph = AutoSpatialGraph[Location, SpatialRelation](
        node_schema=Location,
        edge_schema=SpatialRelation,
        llm_client=llm,
        embedder=embedder,
        observation_location="北宋疆域",
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个地点和 {len(graph.edges)} 个关系")

    for node in graph.nodes[:5]:
        print(f"  {node.name}")

    graph.build_index()

    for q in ["眉山", "黄州", "杭州"]:
        print(f"\n查询：{q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  地点：{[n.name for n in nodes]}")


if __name__ == "__main__":
    main()
