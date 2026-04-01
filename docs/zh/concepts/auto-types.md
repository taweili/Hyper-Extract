# 自动类型

Hyper-Extract 提供 8 种自动类型用于表示知识。每种类型都针对特定的提取场景进行了优化。

## 概览

| 类型 | 模块 | 描述 |
|------|------|------|
| AutoModel | `hyperextract.types.model` | Pydantic 模型提取 |
| AutoList | `hyperextract.types.list` | 列表/集合提取 |
| AutoSet | `hyperextract.types.set` | 唯一集合提取 |
| AutoGraph | `hyperextract.types.graph` | 知识图谱提取 |
| AutoHypergraph | `hyperextract.types.hypergraph` | 超图提取 |
| AutoTemporalGraph | `hyperextract.types.temporal_graph` | 时序知识图谱 |
| AutoSpatialGraph | `hyperextract.types.spatial_graph` | 空间知识图谱 |
| AutoSpatioTemporalGraph | `hyperextract.types.spatio_temporal_graph` | 时空图 |

## 使用示例

### AutoModel

提取到 Pydantic 模型的结构化数据：

```python
from hyperextract import AutoModel
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

extractor = AutoModel(schema=Person)
result = extractor.parse("John Smith 是一位 35 岁的软件工程师。")
```

### AutoList

提取项目列表：

```python
from hyperextract import AutoList

extractor = AutoList(item_type="string")
result = extractor.parse("配料包括面粉、糖、鸡蛋和牛奶。")
# result: ["面粉", "糖", "鸡蛋", "牛奶"]
```

### AutoGraph

提取知识图谱：

```python
from hyperextract import AutoGraph

extractor = AutoGraph(node_types=["Person", "Organization"], edge_types=["WORKS_AT"])
result = extractor.parse("Alice 在 Google 工作。")
# result: 包含节点和边的图
```

### AutoHypergraph

提取超图（连接多个节点的边）：

```python
from hyperextract import AutoHypergraph

extractor = AutoHypergraph()
result = extractor.parse("Alice、Bob 和 Carol 合作完成了 X 项目。")
```

### AutoTemporalGraph

提取带有时间信息的图谱：

```python
from hyperextract import AutoTemporalGraph

extractor = AutoTemporalGraph()
result = extractor.parse("周一，Alice 加入 Google。周二，她开始工作。")
```

## 选择正确的类型

### 何时使用 AutoModel
- 需要结构化、经验证的输出
- 使用定义良好的模式
- 想要 Pydantic 验证

### 何时使用 AutoList
- 提取项目集合
- 顺序重要
- 简单项目提取

### 何时使用 AutoSet
- 只需要唯一项
- 不关心顺序
- 需要去重

### 何时使用 AutoGraph
- 实体之间的复杂关系
- 知识图谱
- 网络分析

### 何时使用 Temporal/Spatial 变体
- 时间感知：使用 `AutoTemporalGraph`
- 位置感知：使用 `AutoSpatialGraph`
- 两者都需要：使用 `AutoSpatioTemporalGraph`

## 下一步

- 了解 [提取方法](methods.md)
- 探索 [模板](templates.md)
