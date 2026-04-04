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

# 访问节点
for node in result.nodes:
    print(f"{node.name} ({node.type})")
    print(f"  描述: {node.description}")

# 访问边
for edge in result.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
```

#### AutoHypergraph

多实体关系提取。

```python
from hyperextract import Template

ka = Template.create("general/base_hypergraph", "en")
result = ka.parse(text)

# 超边连接多个实体
for edge in result.edges:
    print(f"类型: {edge.type}")
    print(f"实体: {edge.entities}")
```

#### AutoTemporalGraph

基于时间的图谱提取。

```python
from hyperextract import Template

ka = Template.create("general/base_temporal_graph", "en")
result = ka.parse(text)

# 边包含时间信息
for edge in result.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
    if hasattr(edge, 'time'):
        print(f"  时间: {edge.time}")
```

#### AutoSpatialGraph

基于位置的图谱提取。

```python
from hyperextract import Template

ka = Template.create("general/base_spatial_graph", "en")
result = ka.parse(text)

# 节点/边包含位置
for node in result.nodes:
    if hasattr(node, 'location'):
        print(f"{node.name} at {node.location}")
```

#### AutoSpatioTemporalGraph

时间和空间组合提取。

```python
from hyperextract import Template

ka = Template.create("general/base_spatio_temporal_graph", "en")
result = ka.parse(text)

# 完整上下文：谁、什么、何时、何地
for edge in result.edges:
    print(f"事件: {edge.type}")
    if hasattr(edge, 'time'):
        print(f"  何时: {edge.time}")
    if hasattr(edge, 'location'):
        print(f"  何地: {edge.location}")
```

---

## 常见操作

### 检查是否为空

```python
if result.empty():
    print("未提取到数据")
else:
    print(f"提取了 {len(result.nodes)} 个节点")
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
nodes = result.nodes
edges = result.edges

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
# 遍历节点
for node in result.nodes:
    print(f"名称: {node.name}")
    print(f"类型: {node.type}")
    if hasattr(node, 'description'):
        print(f"描述: {node.description}")

# 带筛选的边迭代
for edge in result.edges:
    if edge.type == "worked_with":
        print(f"{edge.source} 与 {edge.target} 合作")
```

### 筛选

```python
# 按类型筛选节点
people = [n for n in result.nodes if n.type == "person"]
organizations = [n for n in result.nodes if n.type == "organization"]

# 筛选边
inventions = [e for e in result.edges if "invent" in e.type.lower()]
```

### 统计

```python
# 基本计数
node_count = len(result.nodes)
edge_count = len(result.edges)

# 类型分布
from collections import Counter
node_types = Counter(n.type for n in result.nodes)
edge_types = Counter(e.type for e in result.edges)

print(f"节点: {node_types}")
print(f"边: {edge_types}")
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
