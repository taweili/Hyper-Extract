# 自动类型 (AutoTypes)

Hyper-Extract 使用自动类型来确定提取模式，共支持 8 种类型。

## 类型概览

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| `model` | 单个结构化对象 | 提取单一记录 |
| `list` | 有序列表 | 提取排序项目 |
| `set` | 去重集合 | 提取唯一实体 |
| `graph` | 二元关系图 | 提取实体关系 |
| `hypergraph` | 多元关系图 | 提取多方关系 |
| `temporal_graph` | 时序图 | 添加时间维度 |
| `spatial_graph` | 空间图 | 添加空间维度 |
| `spatio_temporal_graph` | 时空图 | 添加时间和空间 |

## 选择决策树

```
需要关系？
├─ 否 → 记录类型
│   ├─ 单个对象 → model
│   ├─ 有序列表 → list
│   └─ 去重集合 → set
└─ 是 → 图类型
    ├─ 二元关系 (A→B) → graph
    └─ 多元关系 (A+B+C→D) → hypergraph

+ 时间维度 → temporal_graph
+ 空间维度 → spatial_graph
+ 两者都有 → spatio_temporal_graph
```

## 详细说明

### Model

用于提取单个结构化对象。

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "zh")
result = ka.parse(text)

print(result.fields["company_name"])
print(result.fields["revenue"])
```

### List

用于提取有序列表。

```python
from hyperextract import Template

ka = Template.create("finance/risk_factor_set", "zh")
result = ka.parse(text)

for item in result.fields:
    print(item)
```

### Set

用于提取去重集合。

```python
from hyperextract import Template

ka = Template.create("general/entity_registry", "zh")
result = ka.parse(text)

for entity in result.fields:
    print(entity)
```

### Graph

用于提取二元关系。

```python
from hyperextract import Template

ka = Template.create("finance/ownership_graph", "zh")
result = ka.parse(text)

for entity in result.entities:
    print(f"{entity['name']} ({entity['type']})")

for relation in result.relations:
    print(f"{relation['source']} --[{relation['type']}]--> {relation['target']}")
```

### Hypergraph

用于提取多元关系。

```python
from hyperextract import Template

ka = Template.create("tcm/formula_composition", "zh")
result = ka.parse(text)

for relation in result.relations:
    print(f"Formula: {relation['formula_name']}")
    print(f"Herbs: {relation['herbs']}")
```

### Temporal Graph

用于提取带时间的关系。

```python
from hyperextract import Template

ka = Template.create("finance/event_timeline", "zh")
result = ka.parse(text)

for relation in result.relations:
    print(f"{relation['source']} --[{relation['type']}]--> {relation['target']} @ {relation['time']}")
```

## 下一步

- 了解 [模板](./templates.md)
- 查看 [预设模板](./templates.md)
- 浏览 [领域模板](../guides/domain-templates/index.md)
