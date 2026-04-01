# 法律模板

Hyper-Extract 提供专门的法律文档提取模板。

## 可用模板

### 案件事实

从判决书中提取事实：

```yaml
name: case_facts
type: TemporalGraph
schema:
  nodes:
    - type: Party
    - type: Event
    - type: LegalFact
  edges:
    - type: PARTICIPATED_IN
    - type: OCCURRED_ON
```

### 合同条款

提取合同义务：

```yaml
name: contract_terms
type: List
schema:
  item:
    - name: clause_type
      type: string
    - name: parties
      type: array
    - name: obligations
      type: string
```

### 合规要求

提取合规要求：

```yaml
name: compliance_requirements
type: List
schema:
  item:
    - name: regulation
      type: string
    - name: requirement
      type: string
    - name: deadline
      type: date
```

## 使用示例

### CLI

```bash
# 提取案件事实
he parse judgment.txt -t legal/case_facts -o output/

# 提取合同条款
he parse contract.pdf -t legal/contract_terms -o output/
```

### Python API

```python
from hyperextract import Template

# 加载法律模板
ka = Template.create("legal/case_facts")

# 从文档提取
result = ka.parse(judgment_text)

# 访问当事人
for party in result.get_nodes("Party"):
    print(f"Party: {party.name}")
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
- [模板库](../../reference/template-gallery.md)
