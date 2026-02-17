# Hyper-Extract Domain Templates (English)

Welcome to the **Hyper-Extract Domain Templates** library. This directory contains a robust, flat collection of pre-defined schemas, prompts, and extraction models tailored for specific industries and expertise areas.

## Design Philosophy
- **Flat Discovery**: No deep nesting. Find your domain directly in the top-level folders.
- **Intuitive Naming**: Folders are named after common industry terminology (e.g., `finance`, `medicine`, `game`).
- **Schema-Driven**: Each template provides a professional Pydantic schema to ensure high-quality extraction.

## Domain Index

| Folder | Description | Potential Use Cases |
| :--- | :--- | :--- |
| **`agriculture`** | Farming, livestock, and crop management. | Crop rotation, irrigation systems. |
| **`biology`** | Life sciences, genetics, and taxonomy. | Protein interactions, species classification. |
| **`finance`** | Banking, stocks, and investments. | Earnings reports, stock analysis. |
| **`food`** | Culinary, recipes, and nutrition. | Menu planning, recipe breakdown. |
| **`general`** | Basic encyclopedic knowledge. | General Person/Org/Event extraction. |
| **`history`** | Events, timelines, and figures. | War campaigns, historical biographies. |
| **`legal`** | Law, contracts, and compliance. | Contract obligations, court rulings. |
| **`literature`** | Fiction, poetry, and character arcs. | Character maps, literary themes. |
| **`medicine`** | Western and clinical medicine. | Diagnosis, symptom mapping, pharma. |
| **`news`** | Media and trending topics. | Investigative boards, causality analysis. |
| **`travel`** | Geography, tourism, and locations. | Travel guides, spatial relationships, tourism routes. |


## Usage
Simply import the template you need:
```python
from hyperextract.templates.en.finance import StockGraph
```
