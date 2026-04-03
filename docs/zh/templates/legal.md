# 法律模板

Hyper-Extract 提供专门的法律文档提取模板。

## 可用模板

### 案件事实

从判决书中提取事实：

```yaml
language: zh

name: 案件事实时序图
type: temporal_graph
tags: [legal]

description: '从判决书中提取案件事实。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称'
    - name: type
      type: str
      description: '实体类型（当事人/事件/事实）'
  relations:
    fields:
    - name: source
      type: str
      description: '源实体'
    - name: target
      type: str
      description: '目标实体'
    - name: type
      type: str
      description: '关系类型'
    - name: time
      type: str
      description: '时间'
      required: false

guideline:
  target: '提取案件事实。'
  rules_for_entities:
    - '提取当事人和事件'
  rules_for_relations:
    - '提取事实关系'

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

### 合同条款

提取合同义务：

```yaml
language: zh

name: 合同条款列表
type: list
tags: [legal]

description: '提取合同条款。'

output:
  fields:
  - name: clause_type
    type: str
    description: '条款类型'
  - name: parties
    type: str
    description: '涉及方'
  - name: obligations
    type: str
    description: '义务内容'

guideline:
  target: '提取合同条款。'
  rules:
    - '提取所有合同条款'
    - '每个条款包含类型、涉及方和义务'

display:
  label: '{clause_type}'
```

### 合规要求

提取合规要求：

```yaml
language: zh

name: 合规要求列表
type: list
tags: [legal]

description: '提取合规要求。'

output:
  fields:
  - name: regulation
    type: str
    description: '法规名称'
  - name: requirement
    type: str
    description: '合规要求'
  - name: deadline
    type: str
    description: '截止日期'
    required: false

guideline:
  target: '提取合规要求。'
  rules:
    - '提取所有合规要求'

display:
  label: '{regulation}'
```

### 案件引用

提取案件引用关系：

```yaml
language: zh

name: 案件引用图谱
type: graph
tags: [legal]

description: '提取案件引用关系。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '案件名称'
    - name: type
      type: str
      description: '案件类型'
  relations:
    fields:
    - name: source
      type: str
      description: '引用案件'
    - name: target
      type: str
      description: '被引用案件'
    - name: type
      type: str
      description: '引用类型'

guideline:
  target: '提取案件引用关系。'
  rules_for_entities:
    - '提取案件名称'
  rules_for_relations:
    - '提取案件之间的引用关系'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name}'
  relation_label: '{type}'
```

## 使用示例

### CLI

```bash
# 提取案件事实
he parse judgment.txt -t legal/case_fact_timeline -o output/

# 提取合同条款
he parse contract.pdf -t legal/contract_obligation -o output/

# 提取合规要求
he parse compliance.txt -t legal/compliance_list -o output/
```

### Python API

```python
from hyperextract import Template

# 加载法律模板
ka = Template.create("legal/case_fact_timeline", "zh")

# 从文档提取
result = ka.parse(judgment_text)

# 访问结果
print(result.entities)
```

## 支持的文档类型

- 法院判决
- 法律合同
- 合规文件
- 法律论文
- 监管文件

## 下一步

- [金融模板](finance.md)
- [医学模板](medicine.md)

