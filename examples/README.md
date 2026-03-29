# Hyper-Extract Examples

本目录包含 Hyper-Extract 的各种使用示例，按功能分为三个子目录。

## 目录结构

```
examples/
├── inputs/                    # 统一的输入数据目录
│   ├── sci_fi_story.md       # 科幻故事（用于 methods/ 系列演示）
│   └── mmorpg_guild_drama.md # 游戏公会剧情（用于 types/ 系列演示）
│
├── methods/                   # 方法演示（Method-based Extraction）
│   ├── light_rag_demo.py      # LightRAG 方法
│   ├── graph_rag_demo.py      # GraphRAG 方法
│   ├── hyper_rag_demo.py      # HyperRAG 方法
│   ├── hypergraph_rag_demo.py # HyperGraph-RAG 方法
│   ├── cog_rag_demo.py        # CogRAG 方法
│   ├── atom_demo.py           # Atom 时序知识图谱方法
│   ├── itext2kg_demo.py       # iText2KG 方法
│   ├── itext2kg_star_demo.py  # iText2KG-Star 方法
│   └── kg_gen_demo.py         # KG-Gen 方法
│
├── types/                    # 类型演示（AutoType Extraction）
│   ├── graph_demo.py          # AutoGraph 图谱提取
│   ├── hypergraph_demo.py     # AutoHypergraph 超图提取
│   ├── list_demo.py           # AutoList 列表提取
│   ├── model_demo.py          # AutoModel 模型提取
│   ├── set_demo.py            # AutoSet 集合提取
│   ├── temporal_graph_demo.py  # AutoTemporalGraph 时序图提取
│   ├── spatial_graph_demo.py   # AutoSpatialGraph 空间图提取
│   └── spatio_temporal_graph_demo.py  # AutoSpatioTemporalGraph 时空图提取
│
└── templates/                 # 模板演示（Preset Template Testing）
    ├── templates_mapping.yaml  # 模板与测试数据映射表
    ├── base_template.py        # 基础模板测试框架
    ├── finance_demo.py         # Finance 领域模板测试
    ├── general_demo.py         # General 领域模板测试
    ├── industry_demo.py        # Industry 领域模板测试
    ├── legal_demo.py          # Legal 领域模板测试
    ├── medicine_demo.py       # Medicine 领域模板测试
    └── tcm_demo.py            # TCM 领域模板测试
```

## 快速开始

### 方法演示（Methods）

方法演示展示了不同的知识提取策略：

```bash
# LightRAG 方法
python examples/methods/light_rag_demo.py

# GraphRAG 方法
python examples/methods/graph_rag_demo.py

# HyperRAG 方法（支持超边）
python examples/methods/hyper_rag_demo.py

# Atom 时序知识图谱
python examples/methods/atom_demo.py
```

### 类型演示（Types）

类型演示展示了不同的知识表示类型：

```bash
# 图谱提取
python examples/types/graph_demo.py

# 超图提取
python examples/types/hypergraph_demo.py

# 时序图谱
python examples/types/temporal_graph_demo.py

# 空间图谱
python examples/types/spatial_graph_demo.py
```

### 模板演示（Templates）

模板演示使用预设模板测试对应的测试数据：

```bash
# 查看 Finance 领域可用的模板
python examples/templates/finance_demo.py

# 测试特定模板
python examples/templates/finance_demo.py earnings_summary
python examples/templates/general_demo.py base_graph
```

## 输入数据

所有演示使用的输入数据统一存放在 `inputs/` 目录：

| 文件 | 用途 | 对应演示 |
|------|------|---------|
| `inputs/sci_fi_story.md` | 科幻故事 | methods/ 系列演示 |
| `inputs/mmorpg_guild_drama.md` | 游戏公会剧情 | types/graph_demo.py |

模板测试使用的详细测试数据位于 `tests/test_data/zh/` 目录，详见 `templates/templates_mapping.yaml`。

## 模板领域

Hyper-Extract 提供以下领域的预设模板：

| 领域 | 模板数量 | 测试数据目录 |
|------|---------|------------|
| Finance | 5 | `tests/test_data/zh/finance/` |
| General | 11 | `tests/test_data/zh/general/` |
| Industry | 5 | `tests/test_data/zh/industry/` |
| Legal | 5 | `tests/test_data/zh/legal/` |
| Medicine | 5 | `tests/test_data/zh/medicine/` |
| TCM | 5 | `tests/test_data/zh/tcm/` |

## 常见问题

### Q: 如何添加新的输入数据？

将数据文件放入 `examples/inputs/` 目录下的相应子目录，然后在示例文件中更新 `INPUT_FILE` 路径。

### Q: 如何测试新的模板？

1. 在 `templates/templates_mapping.yaml` 中添加模板与测试数据的映射
2. 运行对应的领域测试文件验证

### Q: 为什么某些模板测试文件没有运行实际提取？

模板测试框架目前提供模板和数据的加载与预览功能。完整的模板执行需要结合 `hyperextract` 的模板引擎。
