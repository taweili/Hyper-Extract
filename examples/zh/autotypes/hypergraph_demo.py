"""
超图示例 - 苏轼传记

使用 AutoHyperGraph 从文本中提取超关系。

使用方法：
    python examples/zh/autotypes/hypergraph_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoHyperGraph


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    type: str = Field(description="类型：人物/地名/作品", default="人物")


class HyperEdge(BaseModel):
    """超边（多实体关系）"""
    description: str = Field(description="关系描述")
    members: list[str] = Field(description="参与的实体")
    type: str = Field(description="关系类型")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  超图示例")
    print("=" * 60)
    print("提取多实体关系...")

    graph = AutoHyperGraph[Entity, HyperEdge](
        node_schema=Entity,
        edge_schema=HyperEdge,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个超边")

    for edge in graph.edges[:5]:
        print(f"\n{edge.type}：{edge.description}")
        print(f"  成员：{', '.join(edge.members)}")

    graph.build_index()

    for q in ["乌台诗案", "创作", "贬谪"]:
        print(f"\n查询：{q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  找到 {len(edges)} 个相关超边")


if __name__ == "__main__":
    main()
