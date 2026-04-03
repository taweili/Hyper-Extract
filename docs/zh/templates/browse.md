# 浏览所有模板

可用模板的完整列表。

---

## 统计信息

- **总模板数**：80+
- **类别**：6 个领域
- **自动类型**：8 种类型
- **语言**：中文、英文

---

## 按领域

### 通用模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `general/base_model` | model | 基础结构化模型 |
| `general/base_list` | list | 基础有序列表 |
| `general/base_set` | set | 基础唯一集合 |
| `general/base_graph` | graph | 基础知识图谱 |
| `general/base_hypergraph` | hypergraph | 基础超图 |
| `general/base_temporal_graph` | temporal_graph | 基础时序图 |
| `general/base_spatial_graph` | spatial_graph | 基础空间图 |
| `general/base_spatio_temporal_graph` | spatio_temporal_graph | 基础时空图 |
| `general/biography_graph` | temporal_graph | 人物生平时间线 |
| `general/concept_graph` | graph | 研究概念提取 |
| `general/doc_structure` | model | 文档大纲结构 |
| `general/workflow_graph` | graph | 流程工作流 |

### 金融模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `finance/earnings_summary` | model | 季度/年度财报 |
| `finance/event_timeline` | temporal_graph | 金融事件 |
| `finance/ownership_graph` | graph | 公司股权结构 |
| `finance/risk_factor_set` | set | 风险因素 |
| `finance/sentiment_model` | model | 情感分析 |

### 法律模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `legal/case_citation` | graph | 法律案例先例 |
| `legal/case_fact_timeline` | temporal_graph | 案件时间线 |
| `legal/compliance_list` | list | 合规要求 |
| `legal/contract_obligation` | list | 合同义务 |
| `legal/defined_term_set` | set | 定义术语 |

### 医疗模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `medicine/anatomy_graph` | graph | 解剖结构 |
| `medicine/discharge_instruction` | model | 患者出院摘要 |
| `medicine/drug_interaction` | graph | 药物相互作用 |
| `medicine/hospital_timeline` | temporal_graph | 住院时间线 |
| `medicine/treatment_map` | graph | 治疗方案 |

### 中医模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `tcm/formula_composition` | graph | 草药方剂组成 |
| `tcm/herb_property` | model | 草药属性 |
| `tcm/herb_relation` | graph | 草药关系 |
| `tcm/meridian_graph` | graph | 经络路径 |
| `tcm/syndrome_reasoning` | graph | 辨证推理 |

### 工业模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `industry/emergency_response` | graph | 应急程序 |
| `industry/equipment_topology` | graph | 设备连接 |
| `industry/failure_case` | temporal_graph | 故障分析 |
| `industry/operation_flow` | graph | 操作流程 |
| `industry/safety_control` | graph | 安全控制系统 |

---

## 按自动类型

### Model 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_model` | general | 基础结构化模型 |
| `finance/earnings_summary` | finance | 财务摘要 |
| `finance/sentiment_model` | finance | 情感分析 |
| `medicine/discharge_instruction` | medical | 出院摘要 |
| `tcm/herb_property` | tcm | 草药属性 |

### List 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_list` | general | 基础列表 |
| `legal/compliance_list` | legal | 合规要求 |
| `legal/contract_obligation` | legal | 合同义务 |

### Set 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_set` | general | 基础集合 |
| `finance/risk_factor_set` | finance | 风险因素 |
| `legal/defined_term_set` | legal | 定义术语 |

### Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_graph` | general | 基础图谱 |
| `general/knowledge_graph` | general | 知识图谱 |
| `general/concept_graph` | general | 概念图谱 |
| `finance/ownership_graph` | finance | 股权结构 |
| `legal/case_citation` | legal | 案例先例 |
| `medicine/anatomy_graph` | medical | 解剖结构 |
| `tcm/herb_relation` | tcm | 草药关系 |

### Temporal Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/biography_graph` | general | 传记时间线 |
| `finance/event_timeline` | finance | 金融事件 |
| `legal/case_fact_timeline` | legal | 案例时间线 |
| `medicine/hospital_timeline` | medical | 住院时间线 |

---

## 按语言

### 仅英文

方法（不是模板）：
- `method/light_rag`
- `method/graph_rag`
- `method/hyper_rag`
- `method/itext2kg`
- 等等

### 双语（zh、en）

所有模板都支持两种语言：
- `general/biography_graph`
- `finance/earnings_summary`
- `legal/contract_obligation`
- 等等

---

## 使用此列表

### CLI

```bash
# 列出所有
he list template

# 按领域筛选
he list template | grep finance
```

### Python

```python
from hyperextract import Template

# 获取所有
templates = Template.list()

# 按类型筛选
graphs = Template.list(filter_by_type="graph")

# 按标签筛选
finance = Template.list(filter_by_tag="finance")
```

---

## 参见

- [如何选择](how-to-choose.md)
- [模板库](index.md)
- [领域特定指南](general/index.md)
