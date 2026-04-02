# 中医模板

Hyper-Extract 提供专门的中医（Traditional Chinese Medicine）文档提取模板。

## 可用模板

### 中药属性

提取中药属性：

```yaml
language: zh

name: 中药属性
type: model
tags: [tcm]

description: '提取中药属性信息。'

output:
  fields:
  - name: herb_name
    type: str
    description: '中药名称'
  - name: properties
    type: str
    description: '药性'
  - name: channels
    type: str
    description: '归经'
  - name: indications
    type: str
    description: '功效主治'

guideline:
  target: '提取中药属性。'
  rules:
    - '提取中药名称和属性'
    - '保持原文表述'

display:
  label: '{herb_name}'
```

### 方剂组成

提取方剂组成：

```yaml
language: zh

name: 方剂组成列表
type: list
tags: [tcm]

description: '提取方剂组成。'

output:
  fields:
  - name: herb_name
    type: str
    description: '药材名称'
  - name: dosage
    type: str
    description: '剂量'
  - name: role
    type: str
    description: '角色（君/臣/佐/使）'
    required: false

guideline:
  target: '提取方剂组成。'
  rules:
    - '提取方剂中的所有药材'
    - '记录剂量和角色'

display:
  label: '{herb_name}'
```

### 经络图

提取经络关系：

```yaml
language: zh

name: 经络关系图谱
type: graph
tags: [tcm]

description: '提取经络关系。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称（中药/经络）'
    - name: type
      type: str
      description: '类型'
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

guideline:
  target: '提取经络关系。'
  rules_for_entities:
    - '提取中药和经络'
  rules_for_relations:
    - '提取中药进入经络的关系'

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

### 证候推理

提取证候诊断和推理：

```yaml
language: zh

name: 证候推理超图
type: hypergraph
tags: [tcm]

description: '提取证候诊断和推理。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称'
    - name: type
      type: str
      description: '类型（证候/症状/治法）'
  relations:
    fields:
    - name: syndrome
      type: str
      description: '证候名称'
    - name: symptoms
      type: list
      description: '相关症状'
    - name: treatment
      type: str
      description: '治疗方法'
      required: false

guideline:
  target: '提取证候诊断和推理。'
  rules_for_entities:
    - '提取证候和症状'
  rules_for_relations:
    - '提取证候与症状、治法的关系'

identifiers:
  entity_id: name
  relation_id: '{syndrome}'
  relation_members: symptoms

display:
  entity_label: '{name}'
  relation_label: '{syndrome}'
```

## 使用示例

### CLI

```bash
# 提取中药属性
he parse herbal_compendium.txt -t tcm/herb_property -o output/

# 提取方剂组成
he parse prescription.txt -t tcm/formula_composition -o output/

# 提取经络关系
he parse meridian.txt -t tcm/meridian_graph -o output/
```

### Python API

```python
from hyperextract import Template

# 加载中医模板
ka = Template.create("tcm/herb_property", "zh")

# 从文档提取
result = ka.parse(herbal_text)

# 访问结果
print(result.fields)
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
