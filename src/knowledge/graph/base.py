from ..base import BaseKnowledge
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Represents a node in the knowledge graph."""

    id: str = Field(
        ...,
        description="The unique name or identifier of the entity (e.g., 'Elon Musk').",
    )
    type: str = Field(
        "Unknown",
        description="The category of the entity (e.g., 'Person', 'Organization', 'Concept').",
    )
    description: Optional[str] = Field(
        None, description="A brief summary of the entity found in the text."
    )
    # Using a dict allows storing extra attributes without changing the schema structure
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional attributes (e.g., {'age': 50, 'status': 'active'}).",
    )


class Relationship(BaseModel):
    """Represents an edge between two entities."""

    source: str = Field(..., description="The id of the source entity.")
    target: str = Field(..., description="The id of the target entity.")
    type: str = Field(
        ..., description="The type of the relationship (e.g., 'FOUNDED', 'LOCATED_IN')."
    )
    description: Optional[str] = Field(
        None, description="Contextual details about this relationship."
    )
    weight: float = Field(
        1.0,
        description="The confidence score or strength of the connection (0.0 to 1.0).",
    )


class GraphSchema(BaseModel):
    """The container for the entire graph structure."""

    nodes: List[Entity] = Field(default_factory=list)
    edges: List[Relationship] = Field(default_factory=list)

    def get_node_ids(self) -> set[str]:
        """Helper to get all current node IDs for quick lookup."""
        return {n.id for n in self.nodes}


class SimpleGraph(BaseKnowledge[GraphSchema]):
    def _get_schema_class(self):
        return GraphSchema

    async def extract(self, text: str, **kwargs):
        # 1. 构造 prompt
        prompt = f"Extract nodes and edges from: {text}"

        # 2. 调用自带的 LLM
        response = await self.llm.ainvoke(prompt)

        # 3. 解析结果 (假设 parsed_data 是解析后的 GraphSchema 对象)
        parsed_data = self._parse(response)

        # 4. 【直接在这里做合并逻辑】
        # 简单的去重合并
        existing_node_ids = {n.id for n in self.data.nodes}
        for node in parsed_data.nodes:
            if node.id not in existing_node_ids:
                self.data.nodes.append(node)
        self.data.edges.extend(parsed_data.edges)

    def dump(self, format="json"):
        if format == "json":
            return self.data.model_dump_json()
        return self.data.model_dump()
