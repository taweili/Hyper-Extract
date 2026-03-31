"""
时序图示例 - 苏轼传记

使用 AutoTemporalGraph 从文本中提取时序关系。

使用方法：
    python examples/zh/autotypes/temporal_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    type: str = Field(description="类型：人物/地名/作品", default="人物")


class TimelineEvent(BaseModel):
    """时间线事件"""
    time: str = Field(description="时间（年份）")
    event: str = Field(description="事件描述")
    entities: list[str] = Field(description="参与实体")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  时序图示例")
    print("=" * 60)
    print("提取时序关系...")

    graph = AutoTemporalGraph[Entity, TimelineEvent](
        node_schema=Entity,
        edge_schema=TimelineEvent,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.time}-{x.event}",
        nodes_in_edge_extractor=lambda x: tuple(x.entities) if x.entities else (),
        time_in_edge_extractor=lambda x: x.time,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个事件")

    sorted_events = sorted(graph.edges, key=lambda x: x.time)
    for event in sorted_events[:5]:
        print(f"  {event.time}：{event.event}")

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

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: f"{x.event}@{x.time}")
