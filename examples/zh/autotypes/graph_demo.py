"""
图谱提取示例 - 苏轼传记

使用 AutoGraph 从文本中提取实体和关系，构建知识图谱。

使用方法：
    python examples/zh/autotypes/graph_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph


class Entity(BaseModel):
    """知识图谱中的实体"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型：人物/地名/作品", default="人物")


class Relation(BaseModel):
    """实体之间的关系"""
    source: str = Field(description="关系起点实体")
    target: str = Field(description="关系终点实体")
    type: str = Field(description="关系类型：父亲/兄弟/师徒/朋友/政敌")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "zh" / "sushi.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  图谱提取示例")
    print("=" * 60)
    print("从苏轼传记中提取实体和关系...")

    graph = AutoGraph[Entity, Relation](
        node_schema=Entity,
        edge_schema=Relation,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个关系")

    graph.build_index()

    for q in [
        "苏轼的家庭关系有哪些？",
        "苏轼与哪些人有过师徒关系？",
        "苏轼创作了哪些著名作品？",
    ]:
        print(f"\n问题：{q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  实体：{[n.name for n in nodes]}")
        print(f"  关系：{[e.type for e in edges]}")


if __name__ == "__main__":
    main()
