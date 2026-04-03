# 使用自动类型

提取、操作和利用结构化知识数据。

---

## 什么是自动类型？

自动类型是智能数据结构，自动从文本中提取和组织知识。它们提供：

- **类型安全的 schema** — 基于 Pydantic 的验证
- **LLM 驱动的提取** — 自动内容处理
- **内置操作** — 搜索、合并、可视化
- **序列化** — 保存/加载到磁盘

---

## 8 种自动类型

### 标量类型

#### AutoModel

单个结构化对象提取。

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "en")
result = ka.parse(report_text)

# 直接访问字段
print(result.data.company_name)
print(result.data.revenue)
print(result.data.eps)
```

#### AutoList

有序集合提取。

```python
from hyperextract import Template

ka = Template.create("general/base_list", "en")
result = ka.parse(text)

# 遍历项目
for item in result.data.items:
    print(item)

# 按索引访问
first = result.data.items[0]
```

#### AutoSet

去重集合提取。

```python
from hyperextract import Template

ka = Template.create("general/base_set", "en")
result = ka.parse(text)

# 项目是唯一的
for item in result.data.items:
    print(item)
```

### 图谱类型

#### AutoGraph

实体关系图谱提取。

```python
from hyperextract import Template

ka = Template.create("general/knowledge_graph", "en")
result = ka.parse(text)

# 访问实体
for entity in result.data.entities:
    print(f"{entity.name} ({entity.type})")
    print(f"  描述: {entity.description}")

# 访问关系
for relation in result.data.relations:
    print(f"{relation.source} --{relation.type}--> {relation.target}")
```

#### AutoHypergraph

多实体关系提取。

```python
from hyperextract import Template

ka = Template.create("general/base_hypergraph", "en")
result = ka.parse(text)

# 超边连接多个实体
for hyperedge in result.data.hyperedges:
    print(f"类型: {hyperedge.type}")
    print(f"实体: {hyperedge.entities}")
```

#### AutoTemporalGraph

基于时间的图谱提取。

```python
from hyperextract import Template

ka = Template.create("general/base_temporal_graph", "en")
result = ka.parse(text)

# 关系包含时间信息
for relation in result.data.relations:
    print(f"{relation.source} --{relation.type}--> {relation.target}")
    if hasattr(relation, 'time'):
        print(f"  时间: {relation.time}")
```

#### AutoSpatialGraph

基于位置的图谱提取。

```python
from hyperextract import Template

ka = Template.create("general/base_spatial_graph", "en")
result = ka.parse(text)

# 实体/关系包含位置
for entity in result.data.entities:
    if hasattr(entity, 'location'):
        print(f"{entity.name} at {entity.location}")
```

#### AutoSpatioTemporalGraph

时间和空间组合提取。

```python
from hyperextract import Template

ka = Template.create("general/base_spatio_temporal_graph", "en")
result = ka.parse(text)

# 完整上下文：谁、什么、何时、何地
for relation in result.data.relations:
    print(f"事件: {relation.type}")
    if hasattr(relation, 'time'):
        print(f"  何时: {relation.time}")
    if hasattr(relation, 'location'):
        print(f"  何地: {relation.location}")
```

---

## 常见操作

### 检查是否为空

```python
if result.empty():
    print("未提取到数据")
else:
    print(f"提取了 {len(result.data.entities)} 个实体")
```

### 清除数据

```python
# 清除所有数据
result.clear()

# 仅清除索引
result.clear_index()
```

### 合并实例

```python
# 两次独立提取
result1 = ka.parse(text1)
result2 = ka.parse(text2)

# 合并到新实例
combined = result1 + result2
```

---

## 访问数据

### 属性访问

```python
result = ka.parse(text)

# 直接属性访问（Pydantic 模型）
entities = result.data.entities
relations = result.data.relations

# 字典转换
data_dict = result.data.model_dump()
```

### JSON 导出

```python
import json

# 导出为 JSON
json_data = result.data.model_dump_json(indent=2)

# 保存到文件
with open("output.json", "w") as f:
    f.write(json_data)
```

---

## 处理结果

### 迭代模式

```python
# 遍历实体
for entity in result.data.entities:
    print(f"名称: {entity.name}")
    print(f"类型: {entity.type}")
    if hasattr(entity, 'description'):
        print(f"描述: {entity.description}")

# 带筛选的关系迭代
for relation in result.data.relations:
    if relation.type == "worked_with":
        print(f"{relation.source} 与 {relation.target} 合作")
```

### 筛选

```python
# 按类型筛选实体
people = [e for e in result.data.entities if e.type == "person"]
organizations = [e for e in result.data.entities if e.type == "organization"]

# 筛选关系
inventions = [r for r in result.data.relations if "invent" in r.type.lower()]
```

### 统计

```python
# 基本计数
entity_count = len(result.data.entities)
relation_count = len(result.data.relations)

# 类型分布
from collections import Counter
entity_types = Counter(e.type for e in result.data.entities)
relation_types = Counter(r.type for r in result.data.relations)

print(f"实体: {entity_types}")
print(f"关系: {relation_types}")
```

---

## 高级用法

### 自定义 Schema 访问

```python
# 访问 schema
schema = result.data_schema

print(schema.model_fields)  # 可用字段
```

### 原始数据访问

```python
# 如需要访问内部数据
internal_data = result._data
```

### 类型检查

```python
from hyperextract import AutoGraph, AutoList

# 检查实例类型
if isinstance(result, AutoGraph):
    print("图谱提取")
elif isinstance(result, AutoList):
    print("列表提取")
```

---

## 最佳实践

1. **访问可选字段前检查 hasattr** — Schema 字段可能不同
2. **处理空结果** — 始终检查 `empty()`
3. **使用 model_dump 进行序列化** — 正确的 JSON 转换
4. **利用类型提示** — IDE 自动完成支持

---

## 另请参见

- [搜索和聊天](search-and-chat.md)
- [保存和加载](saving-loading.md)
- [自动类型参考](../../concepts/autotypes.md)
