# 中医模板

Hyper-Extract 提供专门的中医（Traditional Chinese Medicine）文档提取模板。

## 可用模板

### 中药属性

提取中药属性：

```yaml
name: herb_properties
type: Model
schema:
  - name: herb_name
    type: string
  - name: properties
    type: array
  - name: channels
    type: array
  - name: indications
    type: array
```

### 方剂组成

提取方剂组成：

```yaml
name: formula_composition
type: List
schema:
  item:
    - name: herb_name
      type: string
    - name: dosage
      type: string
    - name: role
      type: string
```

### 经络图

提取经络关系：

```yaml
name: meridian_graph
type: Graph
schema:
  nodes:
    - type: Herb
    - type: Meridian
  edges:
    - type: ENTERS
```

### 证候推理

提取证候诊断和推理：

```yaml
name: syndrome_reasoning
type: TemporalGraph
schema:
  nodes:
    - type: Syndrome
    - type: Pattern
    - type: Treatment
```

## 使用示例

### CLI

```bash
# 提取中药属性
he parse herbal_compendium.txt -t tcm/herb_properties -o output/

# 提取方剂组成
he parse prescription.txt -t tcm/formula_composition -o output/
```

### Python API

```python
from hyperextract import Template

# 加载中医模板
ka = Template.create("tcm/herb_properties")

# 从文档提取
result = ka.parse(herbal_text)

# 访问中药信息
for herb in result.get_nodes("Herb"):
    print(f"Herb: {herb.name}")
    print(f"Properties: {herb.properties}")
```

## 支持的文档类型

- 本草纲目
- 处方单
- 医案记录
- 经络论述
- 方剂药典

## 下一步

- [医学模板](medicine.md)
- [金融模板](finance.md)
- [模板库](../../reference/template-gallery.md)
