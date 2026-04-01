# 模板

模板使用声明式 YAML 定义要提取的内容。它们提供了一种强大的方式来指定提取模式，无需编写代码。

## 模板结构

模板由以下部分组成：

1. **元数据**: name、description、author
2. **类型**: 提取类型（Graph、List、Model 等）
3. **模式**: 节点、边和字段的定义

## 基本示例

```yaml
name: 事件时间线
description: 提取财务事件及其时间关系
type: TemporalGraph
schema:
  nodes:
    - type: Event
      properties:
        - name: description
          type: string
        - name: date
          type: string
  edges:
    - type: TIMELINE
      source: Event
      target: Event
      properties:
        - name: relation
          type: string
```

## 模板类型

### 图模板

```yaml
type: Graph
schema:
  nodes:
    - type: Person
    - type: Organization
  edges:
    - type: WORKS_AT
      source: Person
      target: Organization
```

### 列表模板

```yaml
type: List
schema:
  item:
    - name: ingredient
      type: string
    - name: quantity
      type: string
```

### 模型模板

```yaml
type: Model
schema:
  - name: product_name
    type: string
    required: true
  - name: price
    type: float
    required: true
```

## 属性类型

| 类型 | 描述 | 示例 |
|------|------|------|
| string | 文本值 | "你好世界" |
| integer | 整数 | 42 |
| float | 小数 | 3.14 |
| boolean | 布尔值 | true |
| date | 日期值 | 2024-01-15 |
| array | 值列表 | ["a", "b", "c"] |

## 高级功能

### 验证规则

```yaml
- name: email
  type: string
  pattern: "^[a-zA-Z0-9._%+-]+@[a-z]+.[a-z]{2,}$"
```

### 枚举

```yaml
- name: status
  type: string
  enum: [pending, active, completed]
```

### 条件字段

```yaml
- name: end_date
  type: date
  required_if: type == "event"
```

## 预设模板

Hyper-Extract 包含 6 个领域 80+ 预设模板：

### 金融
- `finance/earnings_summary`
- `finance/risk_factors`
- `finance/ownership_graph`

### 法律
- `legal/case_facts`
- `legal/contract_terms`
- `legal/compliance_requirements`

### 医学
- `medicine/drug_interactions`
- `medicine/treatment_plan`
- `medicine/patient_history`

### 中医
- `tcm/herb_properties`
- `tcm/formula_composition`
- `tcm/syndrome_reasoning`

### 工业
- `industry/safety_controls`
- `industry/equipment_topology`
- `industry/operation_flow`

### 通用
- `general/biography`
- `general/concepts`
- `general/workflow`

## 使用模板

### CLI

```bash
he parse document.txt -t finance/earnings_summary
```

### Python API

```python
from hyperextract import Template

# 加载预设
ka = Template.create("finance/earnings_summary")

# 加载自定义模板
ka = Template.from_yaml("my_template.yaml")
```

## 下一步

- 浏览[模板库](../reference/template-gallery.md)
- 了解[领域模板](../guides/domain-templates/index.md)
- 创建您自己的模板
