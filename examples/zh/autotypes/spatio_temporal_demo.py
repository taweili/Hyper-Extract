"""
时空图示例 - 苏轼传记

使用 AutoSpatioTemporalGraph 从文本中提取时空关系。

使用方法：
    python examples/zh/autotypes/spatio_temporal_demo.py
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoSpatioTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


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


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  时空图示例")
    print("=" * 60)
    print("提取时空事件...")

    graph = AutoSpatioTemporalGraph[Entity, SpatioTemporalEvent](
        node_schema=Entity,
        edge_schema=SpatioTemporalEvent,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.action}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        time_in_edge_extractor=lambda x: x.time or "",
        location_in_edge_extractor=lambda x: x.location or "",
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

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: f"{x.action}@{x.time}")
