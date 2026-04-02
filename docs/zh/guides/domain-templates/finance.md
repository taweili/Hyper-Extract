# 金融模板

Hyper-Extract 提供专门的金融文档提取模板。

## 可用模板

### 财报摘要

从财报中提取关键财务指标：

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
    description: '公司名称'
  - name: revenue
    type: str
    description: '收入金额'
  - name: quarter
    type: str
    description: '季度'

guideline:
  target: '提取财报关键信息。'
  rules:
    - '提取公司名称和财务数据'
    - '使用原文中的数字'

display:
  label: '{company_name}'
```

### 风险因素

从金融文档中提取风险因素：

```yaml
language: zh

name: 风险因素列表
type: list
tags: [finance]

description: '提取风险因素列表。'

output:
  fields:
  - name: category
    type: str
    description: '风险类别'
  - name: description
    type: str
    description: '风险描述'

guideline:
  target: '提取风险因素。'
  rules:
    - '提取所有风险因素'
    - '每个风险因素包含类别和描述'

display:
  label: '{category}'
```

### 所有权图

提取所有权关系：

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
      description: '实体名称'
    - name: type
      type: str
      description: '实体类型（公司/个人/机构）'
  relations:
    fields:
    - name: source
      type: str
      description: '所有者'
    - name: target
      type: str
      description: '被拥有的实体'
    - name: type
      type: str
      description: '关系类型'

guideline:
  target: '提取所有权关系。'
  rules_for_entities:
    - '提取公司和个人实体'
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

### 事件时序图

提取财务事件及其时间关系：

```yaml
language: zh

name: 事件时序图
type: temporal_graph
tags: [finance]

description: '提取财务事件及其时间关系。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '事件名称'
    - name: type
      type: str
      description: '事件类型'
  relations:
    fields:
    - name: source
      type: str
      description: '源事件'
    - name: target
      type: str
      description: '目标事件'
    - name: type
      type: str
      description: '关系类型'
    - name: time
      type: str
      description: '时间'
      required: false

guideline:
  target: '提取财务事件和时间关系。'
  rules_for_entities:
    - '提取关键财务事件'
  rules_for_relations:
    - '提取事件之间的时间关系'

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

## 使用示例

### CLI

```bash
# 提取财报摘要
he parse earnings_report.pdf -t finance/earnings_summary -o output/

# 提取风险因素
he parse 10k_filing.txt -t finance/risk_factor_set -o output/

# 提取所有权关系
he parse ownership.txt -t finance/ownership_graph -o output/
```

### Python API

```python
from hyperextract import Template

# 加载金融模板
ka = Template.create("finance/earnings_summary", "zh")

# 从文档提取
result = ka.parse(earnings_text)

# 访问结果
print(result.fields)
```

## 支持的文档类型

- 年度报告
- 季度财报
- 10-K/10-Q 文件
- 股权研究报告
- 财经新闻
- IPO 招股说明书
- 供应链分析

## 下一步

- [法律模板](legal.md)
- [医学模板](medicine.md)
- [模板库](../../reference/template-gallery.md)
