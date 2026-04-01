# 医学模板

Hyper-Extract 提供专门的医疗文档提取模板。

## 可用模板

### 药物相互作用

提取药物相互作用信息：

```yaml
name: drug_interactions
type: Graph
schema:
  nodes:
    - type: Drug
    - type: Interaction
  edges:
    - type: INTERACTS_WITH
    - type: CAUSES
```

### 治疗计划

提取治疗计划详情：

```yaml
name: treatment_plan
type: TemporalGraph
schema:
  nodes:
    - type: Treatment
    - type: Medication
    - type: Procedure
  edges:
    - type: INCLUDES
    - type: SCHEDULED_FOR
```

### 患者病史

提取患者病史：

```yaml
name: patient_history
type: TemporalGraph
schema:
  nodes:
    - type: Condition
    - type: Treatment
    - type: Medication
  edges:
    - type: DIAGNOSED_ON
    - type: TREATED_WITH
```

## 使用示例

### CLI

```bash
# 提取药物相互作用
he parse clinical_note.txt -t medicine/drug_interactions -o output/

# 提取治疗计划
he parse discharge_summary.pdf -t medicine/treatment_plan -o output/
```

### Python API

```python
from hyperextract import Template

# 加载医学模板
ka = Template.create("medicine/drug_interactions")

# 从文档提取
result = ka.parse(clinical_text)

# 访问药物信息
for drug in result.get_nodes("Drug"):
    print(f"Drug: {drug.name}")
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
