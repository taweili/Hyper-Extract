# AutoTypes

AutoTypes 定义了知识提取的**输出数据结构**。共有 8 种类型：

## 记录型

### AutoModel

使用 Pydantic 模型提取结构化数据。

```python
from pydantic import BaseModel, Field
from hyperextract import AutoModel

class Summary(BaseModel):
    title: str = Field(description="标题")
    summary: str = Field(description="摘要")

model = AutoModel(data_schema=Summary, llm_client=llm)
```

### AutoList

提取列表项。

```python
from hyperextract.types import AutoList

lst = AutoList[str](item_schema=str, llm_client=llm)
lst.feed_text(text)
```

### AutoSet

提取唯一项（去重）。

```python
from hyperextract.types import AutoSet

s = AutoSet[str](item_schema=str, llm_client=llm)
s.feed_text(text)
```

## 图谱型

### AutoGraph

实体-关系提取。

```python
from hyperextract.types import AutoGraph

graph = AutoGraph(node_schema=Entity, edge_schema=Relation, llm_client=llm)
graph.feed_text(text)
```

### AutoHypergraph

多元关系（n 元关系）。

```python
from hyperextract.types import AutoHypergraph
```

### AutoTemporalGraph

时间相关的关嗧。

```python
from hyperextract.types import AutoTemporalGraph
```

### AutoSpatialGraph

位置相关的关嗧。

```python
from hyperextract.types import AutoSpatialGraph
```

### AutoSpatioTemporalGraph

时间和位置同时相关的关嗧。

```python
from hyperextract.types import AutoSpatioTemporalGraph
```

## 快速链接

- [领域模板](../templates/index.md) - 开箱即用的模板
