# 提取方法

Hyper-Extract 提供多种提取方法，每种都针对不同的用例进行了优化。

## 可用方法

### 基本方法

| 方法 | 描述 | 用例 |
|------|------|------|
| atom | 直接提取 | 简单、直接的提取 |
| kg_gen | 知识图谱生成 | 结构化知识提取 |

### 基于 RAG 的方法

| 方法 | 描述 | 用例 |
|------|------|------|
| graph_rag | 基于图的 RAG | 复杂关系提取 |
| light_rag | 轻量级 RAG | 快速、高效提取 |
| hyper_rag | 超图 RAG | 多实体关系 |
| hypergraph_rag | 高级超图 | 复杂网络分析 |
| cog_rag | 认知 RAG | 基于推理的提取 |

### 专业化方法

| 方法 | 描述 | 用例 |
|------|------|------|
| itext2kg | 文本转知识图谱 | 文档转换 |
| itext2kg_star | 增强文本转知识图谱 | 高级文档处理 |

## 方法比较

### 速度

```
快速: atom > light_rag > kg_gen > graph_rag
慢速: hyper_rag > cog_rag > hypergraph_rag
```

### 准确性

```
高: cog_rag > graph_rag > hypergraph_rag > hyper_rag
中等: kg_gen > itext2kg > light_rag > atom
```

### 用例矩阵

| 任务 | 推荐方法 |
|------|----------|
| 简单提取 | atom |
| 快速原型 | light_rag |
| 知识图谱 | graph_rag |
| 复杂关系 | hyper_rag |
| 推理任务 | cog_rag |
| 文档转换 | itext2kg |

## 使用示例

### 使用 atom 方法

```python
from hyperextract.methods import atom

result = atom.extract(text, schema=MySchema)
```

### 使用 graph_rag 方法

```python
from hyperextract.methods import graph_rag

result = graph_rag.extract(
    text,
    node_types=["Person", "Organization"],
    edge_types=["WORKS_AT", "KNOWS"]
)
```

### 使用 cog_rag 方法

```python
from hyperextract.methods import cog_rag

result = cog_rag.extract(
    text,
    task="提取因果关系"
)
```

## 方法选择指南

### 快速决策树

```
任务是否简单？
├── 是 → 使用 atom
└── 否 → 是否需要推理？
    ├── 是 → 使用 cog_rag
    └── 否 → 是否需要图？
        ├── 是 → graph_rag 或 hyper_rag
        └── 否 → 使用 light_rag
```

## 高级配置

每种方法都支持自定义配置：

```python
result = graph_rag.extract(
    text,
    max_nodes=100,
    max_edges=200,
    temperature=0.0,
    confidence_threshold=0.8
)
```

## 下一步

- 探索 [模板](templates.md)
- 查看 [CLI 参考](../reference/cli-reference.md)
- 浏览 [示例](../guides/index.md)
