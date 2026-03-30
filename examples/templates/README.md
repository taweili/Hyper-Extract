# Templates 目录

本目录包含 Hyper-Extract 各领域预设模板的测试工具。

## 文件说明

| 文件 | 说明 |
|------|------|
| `list_templates.py` | 列出所有可用的预设模板 |
| `finance_template.py` | 金融领域模板测试 |
| `general_template.py` | 通用领域模板测试 |
| `industry_template.py` | 工业领域模板测试 |
| `legal_template.py` | 法律领域模板测试 |
| `medicine_template.py` | 医学领域模板测试 |
| `tcm_template.py` | 中医领域模板测试 |

## 使用方法

### 列出所有模板

```bash
python examples/templates/list_templates.py
```

### 运行领域模板测试

每个领域对应一个独立的测试文件，直接运行即可：

```bash
# 金融领域
python examples/templates/finance_template.py

# 通用领域
python examples/templates/general_template.py

# 工业领域
python examples/templates/industry_template.py

# 法律领域
python examples/templates/legal_template.py

# 医学领域
python examples/templates/medicine_template.py

# 中医领域
python examples/templates/tcm_template.py
```

### 切换测试用例

每个模板文件包含多个测试用例，通过注释的方式切换：

1. 打开对应的模板文件
2. 找到"测试用例"部分
3. 取消注释要测试的用例，注释其他用例
4. 修改 `main()` 函数中的 `text` 和 `template_name`

```python
# // test for 财报电话会议摘要
# text = """星河智能科技股份有限公司..."""
# template_name = "finance/earnings_summary"

# // test for 股权结构图（取消注释此行）
text = """IPO招股说明书"""
template_name = "finance/ownership_graph"
```

## 支持的领域

| 领域 | 文件 | 模板数量 | 描述 |
|------|------|---------|------|
| finance | finance_template.py | 5 | 金融领域：财报摘要、股权结构、风险因子等 |
| general | general_template.py | 11 | 通用领域：基础图谱、传记、概念图等 |
| industry | industry_template.py | 5 | 工业领域：设备拓扑、应急响应、故障分析等 |
| legal | legal_template.py | 5 | 法律领域：案例引用、合规清单、合同义务等 |
| medicine | medicine_template.py | 5 | 医学领域：解剖图谱、药物相互作用、治疗方案等 |
| tcm | tcm_template.py | 5 | 中医领域：方剂组成、经络图、证候推理等 |

## 各领域模板列表

### Finance (金融)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| earnings_summary | model | 财报电话会议摘要 |
| event_timeline | temporal_graph | 重大事件时间线 |
| ownership_graph | graph | 股权结构图 |
| risk_factor_set | set | 风险因子集合 |
| sentiment_model | model | 市场情绪模型 |

### General (通用)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| base_graph | graph | 基础知识图谱 |
| base_hypergraph | hypergraph | 基础超图 |
| base_list | list | 基础列表 |
| biography_graph | graph | 传记图谱 |
| concept_graph | graph | 概念图谱 |
| doc_structure | list | 文档结构 |
| workflow_graph | graph | 工作流程图 |
| base_model | model | 基础模型 |
| base_set | set | 基础集合 |
| base_temporal_graph | temporal_graph | 基础时序图 |
| base_spatial_graph | spatial_graph | 基础空间图 |

### Industry (工业)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| equipment_topology | graph | 设备拓扑图 |
| operation_flow | list | 操作流程 |
| safety_control | set | 安全控制 |
| emergency_response | temporal_graph | 应急响应时间线 |
| failure_case | hypergraph | 故障案例 |

### Legal (法律)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| case_citation | graph | 案例引用图 |
| case_fact_timeline | temporal_graph | 案件事实时间线 |
| compliance_list | list | 合规清单 |
| contract_obligation | set | 合同义务 |
| defined_term_set | set | 术语定义 |

### Medicine (医学)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| anatomy_graph | graph | 解剖结构图 |
| discharge_instruction | list | 出院指导 |
| drug_interaction | graph | 药物相互作用图 |
| hospital_timeline | temporal_graph | 医院事件时间线 |
| treatment_map | hypergraph | 治疗方案图 |

### TCM (中医)

| 模板名称 | 类型 | 说明 |
|---------|------|------|
| formula_composition | graph | 方剂组成图 |
| herb_property | model | 药材属性 |
| herb_relation | graph | 药材关系图 |
| meridian_graph | graph | 经络图 |
| syndrome_reasoning | hypergraph | 证候推理 |

## 模板类型

| 类型 | 对应 AutoType |
|------|--------------|
| graph | AutoGraph |
| hypergraph | AutoHypergraph |
| list | AutoList |
| model | AutoModel |
| set | AutoSet |
| temporal_graph | AutoTemporalGraph |
| spatial_graph | AutoSpatialGraph |
| spatio_temporal_graph | AutoSpatioTemporalGraph |
