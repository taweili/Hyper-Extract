"""
空间图示例 - 苏轼传记

使用 AutoSpatialGraph 从文本中提取空间关系。

使用方法：
    python examples/zh/autotypes/spatial_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoSpatialGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


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


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  空间图示例")
    print("=" * 60)
    print("提取空间关系...")

    graph = AutoSpatialGraph[Location, SpatialRelation](
        node_schema=Location,
        edge_schema=SpatialRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        location_in_edge_extractor=lambda x: x.target,
        llm_client=llm,
        embedder=embedder,
        observation_location="北宋疆域",
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个地点和 {len(graph.edges)} 个关系")

    for node in graph.nodes[:5]:
        print(f"  {node.name}")

    graph.build_index()

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = graph.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: x.relation)
