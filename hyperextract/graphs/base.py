from ..core.base import BaseAutoType
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


class GraphSchema(BaseModel):
    """The container for the entire graph structure."""

    nodes: List[Entity] = Field(default_factory=list)
    edges: List[Relationship] = Field(default_factory=list)

    def get_node_ids(self) -> set[str]:
        """Helper to get all current node IDs for quick lookup."""
        return {n.id for n in self.nodes}


class SimpleGraph(BaseAutoType[GraphSchema]):
    def _get_schema_class(self):
        return GraphSchema

    async def aextract(self, text: str, **kwargs):
        # 1. 构造 prompt
        prompt = f"Extract nodes and edges from: {text}"

        # 2. 调用自带的 LLM
        response = await self.llm_client.ainvoke(prompt)

        # 3. 解析结果 (假设 parsed_data 是解析后的 GraphSchema 对象)
        parsed_data = self._parse(response)

        # 4. 【直接在这里做合并逻辑】
        # 简单的去重合并
        existing_node_ids = {n.id for n in self._data.nodes}
        for node in parsed_data.nodes:
            if node.id not in existing_node_ids:
                self._data.nodes.append(node)
        self._data.edges.extend(parsed_data.edges)

    def dump(self, format="json"):
        if format == "json":
            return self._data.model_dump_json()
        return self._data.model_dump()
