# 模板

模板使用声明式 YAML 定义要提取的内容，提供了一种强大的方式来指定提取模式，无需编写代码。

## 类型选择

![Knowledge Structures Matrix](../assets/8-types-v2.png)

在设计模板之前，先确定哪种类型适合您的需求：

```
需要关系？
├─ 否 → 记录类型 (model, list, set)
└─ 是 → 图类型 (graph, hypergraph, temporal_graph, spatial_graph)

记录类型：直接字段提取，没有实体和关系的概念
图类型：提取实体及其关系
```

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| `model` | 单个结构化对象 | 提取一条记录 |
| `list` | 有序数组 | 提取排序项目 |
| `set` | 去重集合 | 提取唯一实体 |
| `graph` | 二元关系 (A→B) | 提取实体关系 |
| `hypergraph` | 多元关系 | 提取多方事件 |
| `temporal_graph` | + 时间维度 | 提取随时间变化的事件 |
| `spatial_graph` | + 空间维度 | 提取特定地点的事件 |
| `spatio_temporal_graph` | + 时间 + 空间 | 提取特定地点随时间变化的事件 |

---

## 记录类型

记录类型使用 `output.fields` 直接定义数据结构，没有实体和关系。

### 通用结构

```yaml
language: zh

name: 模板名称
type: [model/list/set]
tags: [领域]

description: '模板描述。'

output:
  fields:
    - name: 字段名
      type: str
      description: '字段描述。'
      required: false
      default: '默认值'

guideline:
  target: '提取目标描述。'
  rules:
    - '规则 1'
    - '规则 2'

display:
  label: '{字段名}'
```

### model - 单个对象

提取单个结构化记录。

```yaml
language: zh

name: 财报摘要
type: model
tags: [finance]

description: '从财报中提取关键财务指标。'

output:
  fields:
    - name: company_name
      type: str
      description: '公司名称。'
    - name: revenue
      type: str
      description: '收入金额。'
    - name: quarter
      type: str
      description: '季度。'

guideline:
  target: '提取关键财务信息。'
  rules:
    - '提取公司名称和财务数据'
    - '使用原文中的数字'

display:
  label: '{company_name}'
```

### list - 有序数组

提取有序项目（排名、序列、要点列表）。

```yaml
language: zh

name: 风险因素列表
type: list
tags: [finance]

description: '按顺序提取风险因素。'

output:
  fields:
    - name: category
      type: str
      description: '风险类别。'
    - name: description
      type: str
      description: '风险描述。'

guideline:
  target: '提取风险因素。'
  rules:
    - '提取所有风险因素'
    - '保持出现顺序'

display:
  label: '{category}'
```

### set - 去重集合

提取具有自动去重的唯一实体。

```yaml
language: zh

name: 人物集合
type: set
tags: [general]

description: '提取唯一的人物实体。'

output:
  fields:
    - name: name
      type: str
      description: '人物姓名。'
    - name: role
      type: str
      description: '角色或职位。'
      required: false

guideline:
  target: '提取人物实体。'
  rules:
    - '提取所有唯一的人物'
    - '按姓名去重'

identifiers:
  item_id: name

display:
  label: '{name}'
```

**注意**：Set 类型需要 `identifiers.item_id` 来定义去重键。

---

## 图类型

图类型提取实体及其关系。使用 `output.entities` 和 `output.relations`。

### 通用结构

```yaml
language: zh

name: 模板名称
type: [graph/hypergraph/temporal_graph/spatial_graph]
tags: [领域]

description: '模板描述。'

output:
  entities:
    description: '实体描述。'
    fields:
      - name: name
        type: str
        description: '实体名称。'
      - name: type
        type: str
        description: '实体类型。'
  relations:
    description: '关系描述。'
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str

guideline:
  target: '提取目标描述。'
  rules_for_entities:
    - '规则 1'
  rules_for_relations:
    - '规则 2'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

### graph - 二元关系

提取两个实体之间的关系 (A→B)。

```yaml
language: zh

name: 所有权图谱
type: graph
tags: [finance]

description: '提取所有权关系。'

output:
  entities:
    fields:
      - name: name
        type: str
        description: '实体名称。'
      - name: type
        type: str
        description: '实体类型（公司/个人）。'
  relations:
    fields:
      - name: source
        type: str
        description: '所有者。'
      - name: target
        type: str
        description: '被拥有的实体。'
      - name: type
        type: str
        description: '关系类型。'

guideline:
  target: '提取所有权关系。'
  rules_for_entities:
    - '提取公司和个人'
    - '保持命名一致'
  rules_for_relations:
    - '仅在文本明确表达时创建关系'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

### hypergraph - 多元关系

提取涉及多个参与者的关系。

#### 简单超图（扁平列表）

所有参与者角色相同。

```yaml
language: zh

name: 会议超图
type: hypergraph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
  relations:
    fields:
      - name: topic
        type: str
        description: '会议主题。'
      - name: participants
        type: list
        description: '参与者列表。'
      - name: outcome
        type: str
        description: '会议结论。'
        required: false

identifiers:
  entity_id: name
  relation_id: '{topic}'
  relation_members: participants  # 字符串

display:
  entity_label: '{name}'
  relation_label: '{topic}'
```

#### 嵌套超图（语义分组）

参与者具有不同的语义角色。

```yaml
language: zh

name: 战役分析
type: hypergraph
tags: [history]

output:
  entities:
    fields:
      - name: name
        type: str
  relations:
    fields:
      - name: battle_name
        type: str
      - name: attackers
        type: list
        description: '攻击方。'
      - name: defenders
        type: list
        description: '防守方。'
      - name: outcome
        type: str

identifiers:
  entity_id: name
  relation_id: '{battle_name}'
  relation_members: [attackers, defenders]  # 列表

display:
  entity_label: '{name}'
  relation_label: '{battle_name}'
```

### temporal_graph - 时间维度

为图关系添加时间维度。

```yaml
language: zh

name: 事件时序图
type: temporal_graph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
        description: '事件名称。'
      - name: type
        type: str
        description: '事件类型。'
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str
      - name: time
        type: str
        description: '关系发生的时间。'
        required: false

guideline:
  target: '提取事件和时间关系。'
  rules_for_entities:
    - '提取关键事件'
  rules_for_relations:
    - '提取时间关系'
  rules_for_time:
    - '记录事件发生的时间'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{time}'
```

### spatial_graph - 空间维度

为图关系添加位置维度。

```yaml
language: zh

name: 空间图谱
type: spatial_graph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
      - name: type
        type: str
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str
      - name: location
        type: str
        description: '关系发生的地点。'
        required: false

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{location}'
  relation_members:
    source: source
    target: target
  location_field: location

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{location}'
```

### spatio_temporal_graph - 时间和空间

结合时间和空间维度。

```yaml
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{location}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time
  location_field: location

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{location}({time})'
```

---

## 字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `str` | 字符串 | "你好世界" |
| `int` | 整数 | 42 |
| `float` | 浮点数 | 3.14 |
| `bool` | 布尔值 | true |
| `list` | 列表 | ["a", "b", "c"] |

---

## 显示配置

| 类型 | entity_label | relation_label |
|------|--------------|----------------|
| graph | `{name} ({type})` | `{type}` |
| hypergraph | `{name}` | `{event_name}` |
| temporal_graph | `{name} ({type})` | `{type}@{time}` |
| spatial_graph | `{name} ({type})` | `{type}@{location}` |
| spatio_temporal_graph | `{name} ({type})` | `{type}@{location}({time})` |

---

## Schema 与 Guideline 的区别

| Schema 定义（WHAT） | Guideline 定义（HOW TO DO WELL） |
|---------------------|--------------------------------|
| 字段名 | 提取策略 |
| 字段类型 | 质量要求 |
| 字段描述 | 创建条件 |
| 必需/可选 | 避免常见错误 |

**重要**：Guideline 不应重复 schema 定义。

---

## 预设模板

Hyper-Extract 包含 6 个领域 80+ 预设模板：

### 金融
- `finance/earnings_summary` (model)
- `finance/risk_factor_set` (set)
- `finance/ownership_graph` (graph)
- `finance/event_timeline` (temporal_graph)

### 法律
- `legal/case_fact_timeline` (temporal_graph)
- `legal/case_citation` (graph)
- `legal/contract_obligation` (list)

### 医学
- `medicine/drug_interaction` (graph)
- `medicine/treatment_map` (temporal_graph)
- `medicine/discharge_instruction` (list)

### 中医
- `tcm/herb_property` (model)
- `tcm/formula_composition` (list)
- `tcm/meridian_graph` (graph)

### 工业
- `industry/safety_control` (list)
- `industry/equipment_topology` (graph)
- `industry/failure_case` (temporal_graph)

### 通用
- `general/graph` (graph)
- `general/list` (list)
- `general/model` (model)
- `general/set` (set)
- `general/biography_graph` (spatio_temporal_graph)

---

## 使用模板

### CLI

```bash
# 使用预设模板
he parse document.txt -t finance/ownership_graph -o output/

# 使用自定义模板
he parse document.txt -t template.yaml -o output/
```

### Python API

```python
from hyperextract import Template

# 加载预设模板
ka = Template.create("finance/ownership_graph", "zh")

# 从 YAML 加载
ka = Template.create("template.yaml", "zh")

# 解析文档
result = ka.parse(document_text)
```

---

## 下一步

- 浏览[模板库](../../reference/template-gallery.md)
- 了解[领域模板](../guides/domain-templates/index.md)
- 创建您自己的模板
- 查看[设计指南](https://github.com/hyper-extract/hyper-extract/blob/main/hyperextract/templates/DESIGN_GUIDE_zh.md)
