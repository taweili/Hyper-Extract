# Hyper-Extract Examples

Examples directory with bilingual demos (English & Chinese).

## Quick Start

### English Demos

```bash
cd examples
python en/autotypes/graph_demo.py
```

### 中文示例

```bash
cd examples
python zh/autotypes/graph_demo.py
```

## Directory Structure

```
examples/
├── README.md
├── en/                          # English demos
│   ├── tesla.md                # Tesla biography data
│   ├── tesla_question.md       # Query questions
│   ├── autotypes/             # AutoType demos
│   │   ├── graph_demo.py       # Knowledge graph
│   │   ├── list_demo.py        # List extraction
│   │   ├── set_demo.py         # Set extraction
│   │   ├── model_demo.py       # Model extraction
│   │   ├── temporal_demo.py     # Temporal graph
│   │   ├── spatial_demo.py      # Spatial graph
│   │   ├── spatio_temporal_demo.py  # Spatio-temporal
│   │   └── hypergraph_demo.py  # Hypergraph
│   ├── methods/               # RAG method demos
│   └── templates/             # Template demos
│
└── zh/                          # Chinese demos
    ├── sushi.md               # Su Shi biography data
    ├── sushi_question.md      # Query questions
    ├── autotypes/             # AutoType demos
    ├── methods/               # RAG method demos
    └── templates/             # Template demos
```

## AutoType Demos

Each demo showcases a specific extraction type:

| Demo | Description |
|------|-------------|
| `graph_demo.py` | Extract entities & relationships (knowledge graph) |
| `list_demo.py` | Extract list of items |
| `set_demo.py` | Extract deduplicated set |
| `model_demo.py` | Extract structured summary |
| `temporal_demo.py` | Extract temporal relationships |
| `spatial_demo.py` | Extract spatial relationships |
| `spatio_temporal_demo.py` | Extract both time & space |
| `hypergraph_demo.py` | Extract multi-entity relationships |

## Data Files

### Tesla (en/tesla.md)
Nikola Tesla biography (1856-1943):
- Early life & education
- Work with Edison
- War of Currents
- Colorado Springs experiments
- Wardenclyffe Tower

### Su Shi (zh/sushi.md)
苏轼传记 (1037-1101):
- 早年与家学
- 仕途与起伏
- 乌台诗案
- 与佛印的友谊
- 杭州岁月
- 晚年与贬谪

## Requirements

```bash
pip install hyperextract langchain-openai python-dotenv
export OPENAI_API_KEY=your-key
```
