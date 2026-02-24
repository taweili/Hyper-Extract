"""Life Event Timeline - Extract timestamped events and arrange them chronologically.

Suitable for biographies, chronologies, memoirs, etc.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class LifeEntity(BaseModel):
    """Life entity node"""

    name: str = Field(description="Entity name")
    type: str = Field(
        description="Entity type: Person, Location, Organization, Item, Concept, Other"
    )
    description: str = Field(description="Brief description", default="")


class LifeEvent(BaseModel):
    """Life event edge (with optional timestamp)"""

    source: str = Field(description="Event subject/related entity")
    target: str = Field(description="Event object/related entity")
    eventType: str = Field(
        description="Event type: Birth, Death, Education, Work, Achievement, Interaction, Travel, Other"
    )
    eventDate: Optional[str] = Field(
        description="Event date, format: YYYY-MM-DD or YYYY, optional", default=None
    )
    details: str = Field(description="Detailed event description", default="")


_PROMPT = """## Role and Task
You are a professional biography chronology expert. Please extract entities such as people, locations, organizations, etc., and life events from the text to build a life event timeline.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a life entity, including types such as Person, Location, Organization, Item, and Concept, used to represent entities in a life timeline.
- **Edge**: In this template, "Edge" refers to a life event, connecting multiple entities to record binary relationships of life experiences such as birth, education, work, and achievements.
- **Time**: In this template, "Time" refers to the temporal information of when events occur, used to arrange life events in chronological order, supporting relative time parsing.

## Extraction Rules
### Node Extraction Rules
1. Extract all related entities: Person, Location, Organization, Item, Concept, etc.
2. Assign a type to each entity: Person, Location, Organization, Item, Concept, Other
3. Add a brief description for each entity

### Event Extraction Rules
1. Only create event edges from extracted entities
2. Event types include:
   - Birth: Birth events
   - Death: Death events
   - Education: Learning, education events
   - Work: Work, career events
   - Achievement: Achievement, honor events
   - Interaction: Interpersonal interaction, social activity events
   - Travel: Travel, relocation events
   - Other: Other events
3. Event date is optional, only extract when explicitly mentioned in the text
4. Date format: YYYY-MM-DD (e.g., 429-01-01) or year only (e.g., 429)
5. Each edge must connect extracted nodes

### Time Parsing Rules
Current observation date: {observation_time}

1. Relative time parsing (based on observation date):
   - "last year" → the year before {observation_time}
   - "last month" → the month before {observation_time}
   - "this quarter" → the quarter of {observation_time}
   - "recent" → the last 3 months from {observation_time}

2. Exact time → Keep as is
3. Missing time → Leave blank, do not guess

### Constraints
- Do not create entities or events not mentioned in the text
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional entity recognition expert. Please extract all related entities as nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a life entity, including types such as Person, Location, Organization, Item, and Concept, used to represent entities in a life timeline.

## Extraction Rules
1. Extract all related entities: Person, Location, Organization, Item, Concept, etc.
2. Assign a type to each entity: Person, Location, Organization, Item, Concept, Other
3. Add a brief description for each entity

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional life event extraction expert. Please extract life events from the given entity list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a life entity, as participants in life events.
- **Edge**: In this template, "Edge" refers to a life event, connecting multiple entities to record binary relationships of life experiences such as birth, education, work, and achievements.
- **Time**: In this template, "Time" refers to the temporal information of when events occur, used to arrange life events in chronological order, supporting relative time parsing.

## Extraction Rules
### Event Type Explanation
- Birth: Birth events
- Death: Death events
- Education: Learning, education events
- Work: Work, career events
- Achievement: Achievement, honor events
- Interaction: Interpersonal interaction, social activity events
- Travel: Travel, relocation events
- Other: Other events

### Time Parsing Rules
Current observation date: {observation_time}

1. Relative time parsing (based on observation date):
   - "last year" → the year before {observation_time}
   - "last month" → the month before {observation_time}
   - "this quarter" → the quarter of {observation_time}
   - "recent" → the last 3 months from {observation_time}

2. Exact time → Keep as is
3. Missing time → Leave blank, do not guess

### Date Format Requirements
- All date information should be converted to "YYYY-MM-DD" format (e.g., 429-01-01) or year only (e.g., 429)
- Time information is optional, only extract when explicitly mentioned in the text

### Constraints
1. Only extract events from the known entity list below
2. Do not create unlisted entities
3. Time information is optional, only extract when explicitly mentioned in the text

"""


class LifeEventTimeline(AutoTemporalGraph[LifeEntity, LifeEvent]):
    """
    Applicable documents: Biographies, chronologies, memoirs, autobiographies

    Function introduction:
    Extract timestamped events and arrange them chronologically. Suitable for biographies, chronologies, memoirs, etc.

    Example:
        >>> template = LifeEventTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Zu Chongzhi (429-500), courtesy name Wenyuan, was from Qiuxian, Fanyang...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str | None = None,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize life event timeline template.

        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            observation_time: Observation date, used for parsing relative time expressions, default: today
            extraction_mode: Extraction mode, either "one_stage" (extract nodes and edges simultaneously)
                or "two_stage" (extract nodes first, then edges), default: "two_stage"
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            node_schema=LifeEntity,
            edge_schema=LifeEvent,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.eventType}|{x.target}",
            time_in_edge_extractor=lambda x: x.eventDate,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        Display life event timeline.

        Args:
            top_k_nodes_for_search: Number of nodes to retrieve for search callback (default: 3)
            top_k_edges_for_search: Number of edges to retrieve for search callback (default: 3)
            top_k_nodes_for_chat: Number of nodes to retrieve for chat callback (default: 3)
            top_k_edges_for_chat: Number of edges to retrieve for chat callback (default: 3)
        """

        def node_label_extractor(node: LifeEntity) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: LifeEvent) -> str:
            if edge.eventDate:
                return f"{edge.eventType} ({edge.eventDate})"
            return edge.eventType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
