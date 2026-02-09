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
| **`art`** | Fine arts, museum collections, and provenance. | Artwork catalogs, historical art movements. |
| **`automotive`** | Vehicles, manufacturing, and maintenance. | Car specs, maintenance logs. |
| **`biology`** | Life sciences, genetics, and taxonomy. | Protein interactions, species classification. |
| **`business`** | General corporate profiles and strategy. | Company bios, strategic goals. |
| **`chemistry`** | Molecular structures and reactions. | Chemical compounds, lab experiments. |
| **`construction`** | Building, BIM, and project planning. | Construction milestones, blueprint entities. |
| **`cybersecurity`** | Threat intelligence and network defense. | STIX models, attack vectors. |
| **`education`** | Knowledge points and curriculum. | Course prerequisites, learning paths. |
| **`environment`** | Climate, ecology, and sustainability. | Weather patterns, carbon footprint tracking. |
| **`fashion`** | Garments, trends, and collections. | Design lookbooks, seasonal trends. |
| **`finance`** | Banking, stocks, and investments. | Earnings reports, stock analysis. |
| **`food`** | Culinary, recipes, and nutrition. | Menu planning, recipe breakdown. |
| **`game`** | Game lore, mechanics, and quests. | NPC relations, quest trees, item crafting. |
| **`general`** | Basic encyclopedic knowledge. | General Person/Org/Event extraction. |
| **`history`** | Events, timelines, and figures. | War campaigns, historical biographies. |
| **`legal`** | Law, contracts, and compliance. | Contract obligations, court rulings. |
| **`literature`** | Fiction, poetry, and character arcs. | Character maps, literary themes. |
| **`marketing`** | Campaigns, SEO, and personas. | Customer journeys, brand archetypes. |
| **`medicine`** | Western and clinical medicine. | Diagnosis, symptom mapping, pharma. |
| **`movie`** | Film, TV, and scripts. | Screenplay beats, cast & crew networks. |
| **`music`** | Theory, albums, and discography. | Genre evolution, tracklists. |
| **`news`** | Media and trending topics. | Investigative boards, causality analysis. |
| **`physics`** | Particle physics, astronomy, and circuits. | Celestial systems, circuit paths. |
| **`politics`** | Governance, policy, and geopolitics. | Legislative tracking, election maps. |
| **`real_estate`** | Property, leasing, and zoning. | Property listings, floor plans. |
| **`recruitment`** | HR, resumes, and hiring. | Skill mapping, interview assessment. |
| **`software`** | Architecture, APIs, and DevOps. | Microservices, software dependencies. |
| **`sports`** | Tournaments, matches, and stats. | Match event logs, player profiles. |
| **`supply_chain`**| Logistics and inventory flow. | Supplier tiering, logistics routes. |
| **`travel`** | Tourism and itineraries. | Trip planning, attraction reviews. |

## Usage
Simply import the template you need:
```python
from hyperextract.templates.en.finance import StockGraph
```
