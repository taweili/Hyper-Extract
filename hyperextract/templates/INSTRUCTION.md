# Hyper-Extract Template Development & Master Prompt Protocol

This document defines the standard workflow for implementing domain-specific knowledge extraction templates in the `Hyper-Extract` framework.

## 0. Core Protocol: Source-First

Before writing any code, you MUST:
1.  **Identify the Base Class**: Choose the appropriate base class from the mapping table below.
2.  **Read the Source**: Use tools to read the Python source code of the chosen base class (located in `hyperextract/types/`).
    *   *Reason*: Source code is the source of truth for `__init__` parameters, `show` method signatures, and generic constraints.

## 1. Design Phase: Feasibility & Selection

### Document-First Protocol
Before designing any template, you **MUST** answer the following:
*   **What is the target document?**: Which core document type(s) in this domain is the template designed for? (e.g., Annual Reports, SOP Manuals, Court Filings, HACCP Safety Plans).
*   **Is the logic structure native to the text?**: Does this structure naturally exist in the original document, or is it artificially imposed? (Reject designs for "imagined knowledge structures").
*   **Is extraction evidence clear?**: Are there explicit linguistic cues in the text that allow the LLM to extract accurately?

Never design templates for abstract knowledge graphs disconnected from real documents. Templates must map the **inherent logical structures** of actual text.

### The Extractability Rule
Before designing a Schema, ask yourself:
*   **Evidence Availability**: Does the input text explicitly contain evidence for this field? (Do not design fields for dynamic data typically found in external databases).
*   **Structural Fit**: What is the most natural form for this data? (e.g., Unordered repeating patterns, unique set, or complex N-ary relations?)

### Mapping Table for Base Class Selection

| Data Nature | Recommended Base Class | Source Code Location | Key Constraints |
| :--- | :--- | :--- | :--- |
| **Single Object** (Summary/Meta) | `AutoModel` | `hyperextract/types/model.py` | One object per document |
| **Pattern Collection** (Repeating) | `AutoList` | `hyperextract/types/list.py` | No deduplication. Extracts all instances found. |
| **Key-Based Accumulator** (Glossary) | `AutoSet` | `hyperextract/types/set.py` | Information Accumulation by Exact Key; requires `key_extractor` |
| **Binary Graph** (Entity-Relation) | `AutoGraph` | `hyperextract/types/graph.py` | Standard binary relationships |
| **Temporal Graph** (Timestamps) | `AutoTemporalGraph` | `hyperextract/types/temporal_graph.py` | Edges MUST have time fields |
| **Spatial Graph** (Locations) | `AutoSpatialGraph` | `hyperextract/types/spatial_graph.py` | Nodes/Edges MUST have location/coords |
| **Spatio-Temporal Graph** | `AutoSpatioTemporalGraph` | `hyperextract/types/spatio_temporal_graph.py` | Tracks movement and evolution in space/time |
| **N-ary/Complex Events** | `AutoHypergraph` | `hyperextract/types/hypergraph.py` | Hyperedge connects N nodes |

---

## 1.1 Special Guidance: AutoSet (Key-Based Accumulation)

The `AutoSet` base class is designed for building **deduplicated, enriched knowledge collections** through **exact key matching**. 
It is fundamentally different from `AutoList` (which has no deduplication) and from semantic clustering/embedding-based merging.

### How AutoSet Works

**Core Mechanism**: 
- Defines a `key_extractor` function that maps each item to a unique identifier (e.g., `key_extractor=lambda x: x.name.strip().lower()`).
- When `feed_text()` is called, the framework extracts items and groups them by their keys.
- **All items with the same key are automatically merged into one comprehensive entry**.
- The **`embedder` parameter is NOT used for merging logic**; it is only used for semantic search and knowledge graph visualization.

**Example Scenario**:
```python
from hyperextract.templates.food.culinary_dish import CulinaryDishSet

dishes = CulinaryDishSet(llm_client=..., embedder=...)

# Text 1: Extract basic dish info
dishes.feed_text("Kung Pao Chicken is a Sichuan dish with peanuts and chilies.")  
# Result: {name: "kung pao chicken", cuisine: "Sichuan", primary_ingredients: "peanuts, chilies"}

# Text 2: Add complementary details about the same dish
dishes.feed_text("Kung Pao Chicken is stir-fried rapidly, creating a sweet and spicy flavor.")  
# Auto-merged: {name: "kung pao chicken", cuisine: "Sichuan", primary_ingredients: "peanuts, chilies", flavor_profile: "sweet and spicy"}

dishes.show()  # Shows the merged, enriched entry
```

**Key Design Principles**:
1. **Exact Key Matching**: The `key_extractor` defines what makes items "the same". Only items with identical keys are merged.
2. **Information Accumulation**: Merging combines and enriches all attributes from multiple mentions of the same item.
3. **No Semantic Similarity**: Unlike clustering, AutoSet does NOT group similar-but-different items (e.g., "Kung Pao Chicken" and "Gong Bao Chicken" with different keys remain separate).
4. **LLM Responsibility**: The LLM's extraction prompt should normalize/standardize names to ensure correct grouping by key.

**Embedder Role**:
- **NOT used for deduplication**. The `embedder` is used for:
  - Semantic retrieval during chat/search queries
  - Visualizing relationships in the knowledge graph
  - Future question-answering capabilities

---

## 2. Implementation Rules

### A. Prompt Definition
*   **Mandatory Constant**: Define `_PROMPT` (a multi-line string) outside the class.
*   **Content**: Clearly define the expert persona and extraction logic. Mention specific formatting rules if necessary.
*   **Graph/Hypergraph Two-Stage Support**: If your template inherits from `AutoGraph`, `AutoHypergraph`, `AutoTemporalGraph`, `AutoSpatialGraph`, or `AutoSpatioTemporalGraph`, you **MUST define three separate prompts** to support both extraction modes:
    1.  `_PROMPT`: For "one_stage" (extract Nodes & Edges simultaneously, faster).
    2.  `_NODE_PROMPT`: For "two_stage" step 1 (extract Nodes only, foundations).
    3.  `_EDGE_PROMPT`: For "two_stage" step 2 (extract Edges/Hyperedges given existing Nodes, more precise).
    
    Pass these to `super().__init__` as:
    ```python
    super().__init__(
        ...,
        prompt=_PROMPT,
        prompt_for_node_extraction=_NODE_PROMPT,
        prompt_for_edge_extraction=_EDGE_PROMPT,
        ...
    )
    ```

### B. Class Structure
*   **Schemas**: All Pydantic fields MUST include a `description` attribute. This is vital for the LLM to understand the target.
*   **Documentation**:
    *   **Class Docstring**:
        *   **Mandatory Declaration (First Line)**: At the **very beginning** of the class docstring, you **MUST** declare the **applicable document types** using this format:
            ```
            Applicable to: [List specific document types, e.g., "SEC 10-K Item 1A, Prospectus Filings"]
            ```
        *   High-level functional description.
        *   A usage **Example** showing how to instantiate and use the template.
    *   **Method Docstrings**: The `__init__` and `show` methods MUST include standard Google-style docstrings with detailed `Args` descriptions for every parameter.
*   **Parameter Accuracy**: Verify that every argument in your `__init__` exists in the base class. Common mistake: `extraction_mode` exists in `AutoGraph` but NOT in `AutoSet`.
*   **Initialization**: Explicitly list parameters (`llm_client`, `embedder`, etc.) and pass the prompt to `super().__init__(..., prompt=_TEMPLATE_PROMPT, ...)`.
*   **Visualization (`show`)**: YOU MUST override the `show` method.
    *   **Parameter Constraint**: **DO NOT** include `label_extractor` parameters (e.g., `node_label_extractor`) in the template's `show` method signature.
    *   **Implementation**: You should define the best **frontend visualization labels** and their extraction logic for your specific Schema internally within `show` and pass them to `super().show(...)`. This ensures users get the best visualization out-of-the-box by simply calling `template.show()`.

---

## 3. Standard Skeleton

```python
from typing import Any, Callable
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import ... # Import relevant base class

# 1. Define Schemas
class ItemSchema(BaseModel):
    name: str = Field(..., description="Name of the entity")
    ...

# 2. Define Prompt
_PROMPT = """
You are an expert in [Domain]. Your task is to extract [Structure] from text...
"""

# 3. Define Class
class MyTemplate(AutoType[ItemSchema]): # Replace with actual base class (AutoList, AutoSet, etc.)
    """Google Style Docstring."""

    def __init__(
        self, 
        llm_client: BaseChatModel, 
        embedder: Embeddings, 
        chunk_size: int = 2048,
        **kwargs: Any
    ):
        super().__init__(
            item_schema=ItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ): 
        # Define frontend visualization labels internally
        def my_label_extractor(item: ItemSchema) -> str:
            return item.name

        super().show(
            item_label_extractor=my_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
```


---

## 4. Runtime Behavior & Usage Guide

### Automatic Extraction

After calling the `feed_text()` method, the Hyper-Extract framework will **automatically and immediately** process the text and execute knowledge extraction:

```python
template = MyTemplate(llm_client=..., embedder=...)

# 1. Input text
template.feed_text("Your input text here...")

# 2. Framework handles it automatically! No need to call extract()
# - Text automatically chunked
# - Schemas automatically extracted
# - Deduplication and relationships established automatically

# 3. Directly view results or visualize
print(template.items)  # View extracted items
template.show()         # Visualize knowledge graph
```

**Key Points**:
- `feed_text()` action automatically triggers the full extraction pipeline
- **No need to call `extract()` method** (this is an internal implementation detail)
- Supports method chaining: `template.feed_text(...).show()`
- Supports accumulation: multiple calls to `feed_text()` accumulate knowledge

### Custom Extraction Mode

For `AutoGraph` series templates, you can choose the extraction strategy during initialization:

```python
# One-stage: Extract nodes and edges simultaneously (faster)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="one_stage")

# Two-stage: Extract nodes first, then edges (more accurate)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="two_stage")
```


---

## 4. Runtime Behavior & Usage Guide

### Automatic Extraction

After calling the `feed_text()` method, the Hyper-Extract framework will **automatically and immediately** process the text and execute knowledge extraction:

```python
template = MyTemplate(llm_client=..., embedder=...)

# 1. Input text
template.feed_text("Your input text here...")

# 2. Framework handles it automatically! No need to call extract()
# - Text automatically chunked
# - Schemas automatically extracted
# - Deduplication and relationships established automatically

# 3. Directly view results or visualize
print(template.items)  # View extracted items
template.show()         # Visualize knowledge graph
```

**Key Points**:
- `feed_text()` action automatically triggers the full extraction pipeline
- **No need to call `extract()` method** (this is an internal implementation detail)
- Supports method chaining: `template.feed_text(...).show()`
- Supports accumulation: multiple calls to `feed_text()` accumulate knowledge

### Custom Extraction Mode

For `AutoGraph` series templates, you can choose the extraction strategy during initialization:

```python
# One-stage: Extract nodes and edges simultaneously (faster)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="one_stage")

# Two-stage: Extract nodes first, then edges (more accurate)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="two_stage")
```

## 4. Runtime Behavior & Usage

### Automatic Extraction

Once the `feed_text()` method is called, the Hyper-Extract framework **automatically and immediately** processes the text and executes the knowledge extraction pipeline:

```python
template = MyTemplate(llm_client=..., embedder=...)

# 1. Input Text
template.feed_text("Your input text here...")

# 2. Framework handles extraction automatically! No need to call extract()
# - Automatic Text Chunking
# - Automatic Schema Extraction
# - Automatic Deduplication / Relation Building

# 3. View Results or Visualize
print(template.items)  # Access extracted items
template.show()         # Visualize the graph
```

**Key Points**:
- The `feed_text()` action automatically triggers the complete extraction pipeline.
- **Do NOT call the `extract()` method manually** (this is an internal implementation detail).
- Supports chain calling: `template.feed_text(...).show()`
- Supports accumulation: Multiple calls to `feed_text()` will accumulate knowledge.

### Custom Extraction Mode

For `AutoGraph` family templates, you can choose the extraction strategy during initialization:

```python
# One Stage: Extract Nodes and Edges simultaneously (Faster)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="one_stage")

# Two Stage: Extract Nodes first, then Edges (Higher Precision)
template = MyGraph(llm_client=..., embedder=..., extraction_mode="two_stage")
```
