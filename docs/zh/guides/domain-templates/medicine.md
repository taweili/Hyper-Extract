# 医学模板

Hyper-Extract 提供专门的医疗文档提取模板。

## 可用模板

### 药物相互作用

提取药物相互作用信息：

```yaml
language: zh

name: 药物相互作用图谱
type: graph
tags: [medicine]

description: '提取药物相互作用信息。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '药物名称'
    - name: type
      type: str
      description: '药物类型'
  relations:
    fields:
    - name: source
      type: str
      description: '源药物'
    - name: target
      type: str
      description: '目标药物'
    - name: type
      type: str
      description: '相互作用类型'

guideline:
  target: '提取药物相互作用。'
  rules_for_entities:
    - '提取药物名称'
  rules_for_relations:
    - '提取药物之间的相互作用'

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

### 治疗计划

提取治疗计划详情：

```yaml
language: zh

name: 治疗计划时序图
type: temporal_graph
tags: [medicine]

description: '提取治疗计划详情。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称'
    - name: type
      type: str
      description: '类型（治疗/药物/手术）'
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
  target: '提取治疗计划。'
  rules_for_entities:
    - '提取治疗方案和药物'
  rules_for_relations:
    - '提取治疗步骤'

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

### 解剖图

提取解剖结构关系：

```yaml
language: zh

name: 解剖结构图谱
type: graph
tags: [medicine]

description: '提取解剖结构关系。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '解剖结构名称'
    - name: type
      type: str
      description: '结构类型'
  relations:
    fields:
    - name: source
      type: str
      description: '源结构'
    - name: target
      type: str
      description: '目标结构'
    - name: type
      type: str
      description: '关系类型'

guideline:
  target: '提取解剖结构关系。'
  rules_for_entities:
    - '提取解剖结构'
  rules_for_relations:
    - '提取结构之间的关系'

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
# 提取药物相互作用
he parse clinical_note.txt -t medicine/drug_interaction -o output/

# 提取治疗计划
he parse discharge_summary.pdf -t medicine/treatment_map -o output/
```

### Python API

```python
from hyperextract import Template

# 加载医学模板
ka = Template.create("medicine/drug_interaction", "zh")

# 从文档提取
result = ka.parse(clinical_text)

# 访问结果
print(result.entities)
```

## 支持的文档类型

- 临床指南
- 出院小结
- 药品说明书
- 病理报告
- 医学教科书
- 临床笔记

## 下一步

- [中医模板](tcm.md)
- [金融模板](finance.md)
- [模板库](../../reference/template-gallery.md)
