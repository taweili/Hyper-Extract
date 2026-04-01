# 模板库

Hyper-Extract 中所有可用预设模板的完整列表。

## 金融模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `finance/earnings_summary` | 提取财报亮点 |
| `finance/risk_factor_set` | 提取风险因素 |
| `finance/ownership_graph` | 提取所有权关系 |
| `finance/event_timeline` | 提取财务事件时间线 |
| `finance/sentiment_model` | 提取情感分析 |

## 法律模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `legal/case_facts` | 从判决书中提取案件事实 |
| `legal/case_citation` | 提取法律引用 |
| `legal/contract_obligation` | 提取合同义务 |
| `legal/compliance_list` | 提取合规要求 |
| `legal/defined_term_set` | 提取定义术语 |
| `legal/case_fact_timeline` | 提取案件事实时间线 |

## 医学模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `medicine/drug_interaction` | 提取药物相互作用 |
| `medicine/treatment_map` | 提取治疗计划 |
| `medicine/anatomy_graph` | 提取解剖学关系 |
| `medicine/hospital_timeline` | 提取患者住院时间线 |
| `medicine/discharge_instruction` | 提取出院指导 |

## 中医模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `tcm/herb_property` | 提取中药属性 |
| `tcm/formula_composition` | 提取方剂组成 |
| `tcm/herb_relation` | 提取中药关系 |
| `tcm/meridian_graph` | 提取经络关系 |
| `tcm/syndrome_reasoning` | 提取证候推理 |

## 工业模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `industry/safety_control` | 提取安全控制 |
| `industry/equipment_topology` | 提取设备关系 |
| `industry/operation_flow` | 提取操作流程 |
| `industry/failure_case` | 提取故障案例分析 |
| `industry/emergency_response` | 提取应急程序 |

## 通用模板

### 核心模板

| 模板 | 描述 |
|------|------|
| `general/biography` | 提取传记信息 |
| `general/concepts` | 提取概念关系 |
| `general/workflow` | 提取工作流程步骤 |
| `general/doc_structure` | 提取文档结构 |
| `general/base_model` | 基本模型提取 |
| `general/base_list` | 基本列表提取 |
| `general/base_set` | 基本集合提取 |
| `general/base_graph` | 基本图提取 |
| `general/base_hypergraph` | 基本超图提取 |

## 使用模板

### CLI

```bash
he parse document.txt -t <template_name>
```

### Python API

```python
ka = Template.create("<template_name>")
result = ka.parse(document_text)
```

## 创建自定义模板

请参阅[模板设计指南](../concepts/templates.md)了解如何创建您自己的模板。
