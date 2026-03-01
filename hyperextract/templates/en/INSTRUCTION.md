# Hyper-Extract Knowledge Template Definition Manual

This document defines the standard-specific knowledge extraction templates workflow for implementing domain in the `Hyper-Extract` framework.

---

## 0. Core Protocol: Read the Source

Before writing any code, you **MUST**:
1. **Identify the Base Class**: Choose the appropriate base class from the mapping table below.
2. **Read the Source**: Use tools to read the Python source code of the chosen base class in `hyperextract/types/` directory.

---

## 1. Design Phase

### 1.1 Document-First Protocol

Before designing any template, you **MUST** answer the following:
*   **What is the target document?**: Which core document type(s) in this domain is the template designed for? (e.g., Annual Reports, SOP Manuals, Court Rulings).
*   **Is the logic structure native to the text?**: Does this structure naturally exist in the original document, or is it artificially imposed?
*   **Is extraction evidence clear?**: Are there explicit linguistic cues in the text that allow the LLM to extract accurately?

Never design templates for abstract knowledge graphs disconnected from real documents. Templates must map the **inherent logical structures** of actual text.

### 1.2 AutoType Selection Mapping Table

| Data Nature | Recommended Base Class | Source Code Location | Key Constraints |
| :--- | :--- | :--- | :--- |
| **Single Object** (Summary/Meta) | `AutoModel` | `hyperextract/types/model.py` | One object per document |
| **Pattern Collection** (Repeating) | `AutoList` | `hyperextract/types/list.py` | No deduplication. Extracts all instances found. |
| **Key-Based Accumulator** (Glossary) | `AutoSet` | `hyperextract/types/set.py` | Information accumulation by exact key; requires `key_extractor` |
| **Standard Graph** (Entity-Relation) | `AutoGraph` | `hyperextract/types/graph.py` | Standard binary relationships |
| **Temporal Graph** (With Time) | `AutoTemporalGraph` | `hyperextract/types/temporal_graph.py` | Edges support flexible time formats |
| **Spatial Graph** (With Location) | `AutoSpatialGraph` | `hyperextract/types/spatial_graph.py` | Edges support flexible location formats |
| **Spatio-Temporal Graph** | `AutoSpatioTemporalGraph` | `hyperextract/types/spatio_temporal_graph.py` | Supports both flexible time and location |
| **N-ary/Complex Events** | `AutoHypergraph` | `hyperextract/types/hypergraph.py` | Models complex relationships among multiple entities |

### 1.3 AutoHypergraph Application Scenarios

#### Core Definition
Hyperedges are used to model complex relationships among multiple entities, breaking through the limitations of traditional binary relationships by connecting multiple related entities through a single hyperedge.

#### Core Value
- Describes events or stories involving multiple entities participating together
- Maintains event integrity, avoiding information loss from splitting into multiple binary relationships
- Better aligns with human cognition of "events" (multiple participants, multiple elements)

#### Typical Application Scenarios
- **Meeting Scenario**: Connect attendees, topics, location, time, decision outcomes
- **Transaction Scenario**: Connect buyer, seller, product, amount, time, location
- **Case Scenario**: Connect suspects, victims, witnesses, time, location, evidence
- **Competition Scenario**: Connect teams, players, event items, time, location, results

---

## 2. Schema Design Specifications

### 2.1 Core Principles
- **Field Count Control**: No more than 10 core fields
- **All Fields Must Have `description`**
- **Code Identifiers in English**: Class names, variable names, method names must be in English
- **All Descriptions in English**: For templates in the `en` directory, all field descriptions, comments, and Prompts MUST be in English

### 2.2 Naming Conventions
- Class names: `PascalCase` (e.g., `FinancialReportGraph`)
- Variable/Method names: `camelCase` (e.g., `node_label_extractor`)

### 2.3 Example
```python
class FinancialEntity(BaseModel):
    """Financial entity node"""
    name: str = Field(description="Entity name, such as company name, product name, department name")
    category: str = Field(description="Entity type: company, product, department")
    description: str = Field(description="Brief description", default="")

class FinancialRelation(BaseModel):
    """Financial relation edge"""
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    relationType: str = Field(description="Relation type: investment, acquisition, cooperation, competition")
    timeInfo: Optional[str] = Field(
        description="Time info, unified format is YYYY-MM-DD (e.g., 2023-06-15)",
        default=None
    )
```

### 2.4 Spatio-Temporal Format Consistency Principle

#### Within a Single Template: Strict Consistency
Within the same knowledge template, time formats and spatial formats must be strictly consistent. All extracted spatio-temporal information must be standardized and unified during the information extraction phase to ensure data standardization and consistency, avoiding confusion during LLM processing.

**Important Note**: The standard format used by the template MUST be explicitly specified in the Prompt. The LLM must be required to convert all time/spatial information to the specified standard format for output, rather than preserving the various expressions from the original text.

#### Across Different Templates: Flexible Adaptation
Time and spatial formats across different knowledge templates can be flexibly defined based on specific domain requirements, but each template must unify one standard format. Here are format suggestions for common domains (for reference only):
- **History Domain**: Suggested format is year (e.g., "2023") or dynasty (e.g., "Qing Dynasty")
- **Finance Domain**: Suggested format is YYYY-MM-DD (e.g., "2023-06-15")
- **Cooking Domain**: Suggested format is MM:SS (e.g., "30:00")
- **Geography Domain**: Suggested format is Province-City-District (e.g., "Beijing-Chaoyang")

**Note**: Format selection should be based on the actual information density and domain conventions of the target document, not over-design.

---

## 3. AutoType Specific Specifications

### 3.1 AutoTemporalGraph (Temporal Graph)

#### Required Extractors
- `node_key_extractor`: Unique entity identifier (e.g., `lambda x: x.name`)
- `edge_key_extractor`: Core relation identifier (excluding time)
- `time_in_edge_extractor`: Function to extract time from Edge
- `nodes_in_edge_extractor`: Function to extract source/target nodes from Edge

#### Observation Time Parameter
- User can specify, or defaults to current date
- Used for resolving relative time expressions

#### Prompt Must Include Time Resolution Rules
```
### Time Format Requirements
All time information must be unified to "YYYY-MM-DD" format (e.g., 2023-06-15).

### Time Resolution Rules
Current Observation Date: {observation_time}

1. Relative time resolution (based on observation date):
   - "last year" → year before {observation_time}, formatted as YYYY-01-01
   - "last month" → month before {observation_time}, formatted as YYYY-MM-01
   - "June 2023" → 2023-06-15

2. Exact time → convert to YYYY-MM-DD format
3. Missing time → leave empty
```

---

### 3.2 AutoSpatialGraph (Spatial Graph)

#### Required Extractors
- `node_key_extractor`, `edge_key_extractor`
- `location_in_edge_extractor`: Function to extract location from Edge
- `nodes_in_edge_extractor`

#### Prompt Must Include Location Resolution Rules
```
### Location Resolution Rules
Current Observation Location: {observation_location}

1. Relative location resolution (based on observation location):
   - "here", "local" → {observation_location}
   - "nearby", "adjacent" → vicinity of {observation_location}
   - "north of here" → north of {observation_location}

2. Exact location → keep as-is
3. Missing location → leave empty
```

---

### 3.3 AutoSet (Key-Based Accumulator)

- Must define `key_extractor` (exact key matching, not semantic similarity)
- Embedder is only used for semantic retrieval, not for merging logic

---

## 4. Prompt Construction Specifications

### 4.1 Fully Predefined
- Users do not need to write any Prompt
- All Prompts are predefined and encapsulated

### 4.2 Graph Types Require 3 Prompts
| Prompt | Usage |
|-------|------|
| `_PROMPT` | one_stage mode: extract nodes and edges simultaneously |
| `_NODE_PROMPT` | two_stage step 1: extract nodes only |
| `_EDGE_PROMPT` | two_stage step 2: extract edges based on known nodes |

### 4.3 Prompt Pre-Structure Specifications (Mandatory for Graph Types)

**Graph types (AutoGraph/AutoHypergraph etc.) must follow the following pre-structure**:

```
## Role and Task
You are a professional xxx expert, please extract xxx from the text...

## Core Concept Definitions (varies by AutoType)
- **Concept 1**: xxx
- **Concept 2**: xxx

## Extraction Rules
### Core Constraints
#### _NODE_PROMPT / _PROMPT (Node Extraction)
1. Each node must correspond to a single independent entity; do not merge multiple entities into one node
2. Entity names should remain consistent with the source text

#### _EDGE_PROMPT (Edge Extraction)
1. Only extract edges from the known entity list; do not create unlisted entities
2. Relationship descriptions should remain consistent with the source text

### Domain-Specific Rules (Optional)
Different domains have specialized terminology or specific expressions. You may add targeted rules as needed. For example:
- Traditional Chinese Medicine: Ancient dosage units (两, 钱, 分, 匕, 枚, etc.) can be kept in original form
- Finance: Professional terminology should remain in original form
- Medical: Professional abbreviations should remain in original form

### Special Placeholders (Required)
**Each Prompt must include special placeholders** to receive the text to be extracted:

- **_PROMPT / _NODE_PROMPT**: Must include `{source_text}` placeholder
  ```python
  ## Source Text:
  {source_text}
  ```

- **_EDGE_PROMPT**: Taking AutoGraph/AutoHypergraph as examples, must include `{known_nodes}` and `{source_text}` placeholders. For spatio-temporal graph types, additional `{observation_time}` or `{observation_location}` placeholders will be included (see table below for details).
  ```python
  ## Known Entities
  {known_nodes}

  ## Source Text:
  {source_text}
  ```

#### Placeholders by AutoType

| AutoType | Node Extraction | Edge Extraction |
|----------|-----------------|-----------------|
| `AutoModel` / `AutoList` / `AutoSet` | `{source_text}` | - |
| `AutoGraph` / `AutoHypergraph` | `{source_text}` | `{source_text}`, `{known_nodes}` |
| `AutoTemporalGraph` | `{source_text}` | `{source_text}`, `{known_nodes}`, `{observation_time}` |
| `AutoSpatialGraph` | `{source_text}` | `{source_text}`, `{known_nodes}`, `{observation_location}` |
| `AutoSpatioTemporalGraph` | `{source_text}` | `{source_text}`, `{known_nodes}`, `{observation_time}`, `{observation_location}` |

#### Placeholder Description

- **`{source_text}`**: The original text to be analyzed (required)
- **`{known_nodes}`**: Known nodes list in two-stage extraction mode (for edge extraction)
- **`{observation_time}`**: Observation time, used to resolve relative time expressions (e.g., "last year", "last month")
- **`{observation_location}`**: Observation location, used to resolve relative location expressions (e.g., "here", "nearby")

### Spatio-Temporal Resolution Rules (required for spatio-temporal graph types only)
- Time/location resolution rules...

**Why concept definitions are needed?**
- Let the LLM understand "what" to extract first, before telling it "how" to extract
- Different AutoTypes have different core concepts that must be clearly defined
- Concept definitions must be placed at the beginning of the Prompt

**Non-graph types do not require Core Concept Definitions**:
- **AutoModel**: Directly extract structured objects, object definitions are already clear in Pydantic Schema
- **AutoList**: Directly extract item lists, item definitions are already clear in Pydantic Schema
- **AutoSet**: Directly extract element collections, element definitions are already clear in Pydantic Schema

### 4.4 Core Concept Definition Templates for Each AutoType

#### AutoGraph
## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Relationships between nodes


#### AutoHypergraph

## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Connects multiple nodes, expressing complex relationships among multiple entities

#### AutoTemporalGraph / AutoSpatialGraph / AutoSpatioTemporalGraph
In addition to node and edge definitions, time/location definitions must also be added:

## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Relationships between nodes
- **Time**: xxx (define according to actual needs)
- **Location**: xxx (define according to actual needs)


---

## 5. Parameter Management Specifications

### 5.1 Standard Exposed Parameters
| Parameter | Type | Required | Description |
|-----|------|------|------|
| `llm_client` | `BaseChatModel` | ✓ | LLM client |
| `embedder` | `Embeddings` | ✓ | Embedding model |
| `extraction_mode` | `str` | ✗ | Extraction mode (graph types only), default `"two_stage"` |
| `verbose` | `bool` | ✗ | Verbose logging, default `False` |

### 5.2 Optional Class-Specific Parameters
| Parameter | Applicable Types | Description |
|-----|---------|------|
| `observation_time` | `AutoTemporalGraph`, `AutoSpatioTemporalGraph` | Observation time, defaults to current date if not specified |
| `observation_location` | `AutoSpatialGraph`, `AutoSpatioTemporalGraph` | Observation location |
| `max_workers` | All types | Maximum worker threads |

### 5.3 Hidden Parameters (Passed via **kwargs)
- `chunk_size`, `chunk_overlap`
- `node_strategy_or_merger`, `edge_strategy_or_merger`
- Other technical parameters

---

## 6. Show Function Design Specifications

### 7.1 Design Pattern

The `show()` method should follow the decorator pattern, wrapping the parent class implementation.

### 7.2 Implementation Example

```python
def show(
    self,
    *,
    top_k_nodes_for_search: int = 3,
    top_k_edges_for_search: int = 3,
    top_k_nodes_for_chat: int = 3,
    top_k_edges_for_chat: int = 3,
):
    """
    Display the knowledge graph.
    
    Args:
        top_k_nodes_for_search: Number of nodes returned for semantic search, default is 3
        top_k_edges_for_search: Number of edges returned for semantic search, default is 3
        top_k_nodes_for_chat: Number of nodes used for Q&A, default is 3
        top_k_edges_for_chat: Number of edges used for Q&A, default is 3
    """
    def node_label_extractor(node: MyNode) -> str:
        return node.name  # Simple label, not unique identifier, friendly for display
    
    def edge_label_extractor(edge: MyEdge) -> str:
        return edge.relationType
    
    super().show(
        node_label_extractor=node_label_extractor,
        edge_label_extractor=edge_label_extractor,
        top_k_nodes_for_search=top_k_nodes_for_search,
        top_k_edges_for_search=top_k_edges_for_search,
        top_k_nodes_for_chat=top_k_nodes_for_chat,
        top_k_edges_for_chat=top_k_edges_for_chat,
    )
```

---

## 7. Standard Example Skeleton

```python
from typing import Any, Callable, Optional
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema (English identifiers, ≤ 10 fields, English descriptions)
# ==============================================================================

class FinancialEntity(BaseModel):
    """Financial entity node"""
    name: str = Field(description="Entity name, such as company name, product name, department name")
    category: str = Field(description="Entity type: company, product, department")
    description: str = Field(description="Brief description", default="")

class FinancialRelation(BaseModel):
    """Financial relation edge"""
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    relationType: str = Field(description="Relation type: investment, acquisition, cooperation, competition")
    timeInfo: Optional[str] = Field(
        description="Time info, unified format is YYYY-MM-DD (e.g., 2023-06-15)",
        default=None
    )
    details: str = Field(description="Detailed description", default="")

# ==============================================================================
# 2. Predefined Prompts (Simplified Version)
# ==============================================================================

_NODE_PROMPT = """## Role and Task
You are a professional [domain] expert, extract all entities as nodes from the text.

## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Relationships between nodes

## Extraction Rules
### Core Constraints
1. Each node must correspond to a single independent entity; do not merge multiple entities into one node
2. Entity names should remain consistent with the source text

##  Pending Text to Analyze:
{source_text}
"""

_EDGE_PROMPT = """## Role and Task
You are a professional [domain] expert, extract relationships between given entities.

## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Relationships between nodes

## Extraction Rules
### Core Constraints
1. Only extract edges from the known entity list; do not create unlisted entities
2. Relationship descriptions should remain consistent with the source text

### Time Resolution Rules
Current Observation Date: {observation_time}

1. Relative time resolution (based on observation date):
   - "last year" → year before {observation_time}
   - "last month" → month before {observation_time}

2. Exact time → keep as-is
3. Missing time → leave empty

##  Known Entities
{known_nodes}

##  Pending Text to Analyze
{source_text}
"""

_PROMPT = """## Role and Task
You are a professional [domain] expert, extract entities and their relationships from text.

## Core Concept Definitions
- **Node**: Entities extracted from the document
- **Edge**: Relationships between nodes

## Extraction Rules
### Core Constraints
1. Each node must correspond to a single independent entity; do not merge multiple entities into one node
2. Entity names should remain consistent with the source text
3. Only extract edges from the known entity list; do not create unlisted entities
4. Relationship descriptions should remain consistent with the source text

### Time Resolution Rules
Current Observation Date: {observation_time}

1. Relative time resolution (based on observation date):
   - "last year" → year before {observation_time}
   - "last month" → month before {observation_time}

2. Exact time → keep as-is
3. Missing time → leave empty

##  Pending Text to Analyze:
{source_text}
"""

# ==============================================================================
# 3. Template Class
# ==============================================================================

class FinancialReportGraph(AutoTemporalGraph[FinancialEntity, FinancialRelation]):
    """
    Applicable Documents: SEC 10-K/10-Q annual reports, quarterly reports
    
    Functionality:
    Extracts companies, products, departments and their relationships (investment, acquisition, cooperation, etc.)
    from financial reports, supporting flexible time formats.
    
    Usage Example:
        >>> template = FinancialReportGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        observation_time: str | None = None,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize financial report graph template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            extraction_mode: Extraction mode, can be "one_stage" (extract nodes and edges simultaneously)
                or "two_stage" (extract nodes first, then edges), default is "two_stage"
            observation_time: Observation time for resolving relative time expressions,
                defaults to current date if not specified
            max_workers: Maximum worker threads, default is 10
            verbose: Enable verbose logging, default is False
            **kwargs: Other technical parameters passed to base class
        """
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")
        
        super().__init__(
            node_schema=FinancialEntity,
            edge_schema=FinancialRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
            time_in_edge_extractor=lambda x: x.timeInfo or "",
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
        Display the knowledge graph.
        
        Args:
            top_k_nodes_for_search: Number of nodes returned for semantic search, default is 3
            top_k_edges_for_search: Number of edges returned for semantic search, default is 3
            top_k_nodes_for_chat: Number of nodes used for Q&A, default is 3
            top_k_edges_for_chat: Number of edges used for Q&A, default is 3
        """
        def node_label_extractor(node: FinancialEntity) -> str:
            return node.name
        
        def edge_label_extractor(edge: FinancialRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
```

---

## 8. Runtime Behavior Description

After calling `feed_text()`, the framework automatically processes the text and executes knowledge extraction:
```python
template = MyTemplate(llm_client=..., embedder=...)
template.feed_text("...")  # Auto-trigger extraction
template.show()               # Visualization
```

Key Points:
- `feed_text()` automatically triggers the full pipeline, no need to call `extract()`
- Supports method chaining: `template.feed_text(...).show()`
- Supports accumulation: multiple calls to `feed_text()` accumulate knowledge
