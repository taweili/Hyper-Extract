# Python模板转YAML配置指南

本文档说明如何将现有的Python模板文件转换为YAML配置文件格式。

---

## 目录结构

```
hyperextract/templates/presets/
├── finance/           # 财经领域
├── medicine/          # 医疗领域
├── tcm/               # 中医领域
├── law/               # 法律领域
├── general/           # 通用领域
└── ...                # 其他领域
```

每个YAML文件代表一个模板。

---

## YAML配置结构

以下是完整的配置字段说明：

```yaml
# 必需字段
name: 模板名称                    # 模板类名，如 EarningsCallSummary
autotype: model                  # 类型：model | list | set | graph | hypergraph | temporal_graph | spatial_graph | spatio_temporal_graph
tag: [finance]                   # 标签数组，用于索引和检索，如 [finance], [medicine], [general] 等

# 语言配置（目前只用中文）
language: zh                     # 语言代码，目前统一使用 zh

# 描述（多语言格式）
description:
  zh: 中文描述文字              # 注意：要用 zh: 格式，即使只有一个语言

# Schema定义（根据autotype不同）
# autotype: model 时使用 schema
schema:
  fields:
    - name: 字段名
      type: string             # 类型：string | int | float | bool | array
      description:
        zh: 字段描述          # 注意：这里也要用 zh: 格式
      required: false          # 是否必填，默认 false
      default: ""              # 默认值

# autotype: list 或 set 时使用 item_schema
item_schema:
  fields:
    - name: 字段名
      type: string
      description:
        zh: 字段描述
      required: false
      default: ""

# autotype: graph 类时使用 node_schema 和 edge_schema
node_schema:
  fields:
    - name: 字段名
      type: string
      description:
        zh: 字段描述

edge_schema:
  fields:
    - name: 字段名
      type: string
      description:
        zh: 字段描述

# 提取指南（多语言格式）
extraction_guide:
  target:
    zh: |
      你是一位xxx专家...
      这里写角色定义和提取任务说明

  rules:
    zh: |
      1. 规则1
      2. 规则2

  rules_for_nodes:
    zh: |
      1. 节点规则1
      2. 节点规则2

  rules_for_edges:
    zh: |
      1. 边规则1
      2. 边规则2

  rules_for_time:               # temporal_graph / spatio_temporal_graph 使用
    zh: |
      1. 时间规则1

  rules_for_location:           # spatial_graph / spatio_temporal_graph 使用
    zh: |
      1. 位置规则1

# 标识配置
identifiers:
  item_id: 字段名              # set 类型使用
  node_id: 字段名              # graph 类型使用
  edge_id: "{source}|{relation}"  # graph 类型使用，支持模板格式
  edge_members:                # graph 类型使用
    source: source
    target: target
  time_field: 字段名           # temporal_graph / spatio_temporal_graph 使用
  location_field: 字段名       # spatial_graph / spatio_temporal_graph 使用

# 运行时参数（可选，不填则使用默认值）
parameters:
  extraction_mode: two_stage   # graph 类型使用：one_stage | two_stage
  node_merge_strategy: llm_balanced  # graph 类型使用，不填默认为 llm_balanced
  edge_merge_strategy: llm_balanced  # graph 类型使用，不填默认为 llm_balanced
  observation_time: "2024-01-01"     # temporal_graph / spatio_temporal_graph 使用
  observation_location: "北京"       # spatial_graph / spatio_temporal_graph 使用
  chunk_size: 2048
  chunk_overlap: 256
  max_workers: 10
  verbose: false

# 展示配置（必需）
# 注意：支持模板字符串格式，使用 {字段名} 占位，可组合多个字段
display:
  label: 字段名                 # model / list / set 使用
  node_label: "{字段1} ({字段2})"  # graph 类型使用，支持模板格式如 "{name} ({type})"
  edge_label: "{字段1}"            # graph 类型使用，可使用模板如 "{relation_type}"
```

---

## 多语言字段格式要求

**重要**：以下字段都需要使用 `zh:` 格式，即使只有一个语言：

### 1. 整体description

```yaml
# 正确格式
description:
  zh: 这是一个描述文字
```

### 2. Schema字段的description

```yaml
# 正确格式（每个字段的description都要用zh:格式）
schema:
  fields:
    - name: company_name
      type: string
      description:
        zh: 公司名称
      required: false
```

### 3. extraction_guide中的字段

```yaml
# 正确格式（每个子字段都要用zh:格式）
extraction_guide:
  target:
    zh: |
      你是一位专业的财务分析师，擅长从财报电话会议中提取关键信息。
      请从财报电话会议记录中提取关键财务指标、业绩指引和整体基调。
  
  rules:
    zh: |
      1. 每个字段对应一个独立的信息项，禁止合并
      2. 数据必须与原文保持一致，不得编造
      3. 如果信息缺失，该字段留空
```

---

## 各AutoType配置对照表

| AutoType | Schema字段 | identifiers必需字段 | 特有parameters |
|----------|-----------|-------------------|---------------|
| model | schema | - | - |
| list | item_schema | - | - |
| set | item_schema | item_id | - |
| graph | node_schema + edge_schema | node_id, edge_id, edge_members | extraction_mode |
| hypergraph | node_schema + edge_schema | node_id, edge_id, edge_members | extraction_mode |
| temporal_graph | node_schema + edge_schema | node_id, edge_id, edge_members, time_field | extraction_mode, observation_time |
| spatial_graph | node_schema + edge_schema | node_id, edge_id, edge_members, location_field | extraction_mode, observation_location |
| spatio_temporal_graph | node_schema + edge_schema | node_id, edge_id, edge_members, time_field, location_field | extraction_mode, observation_time, observation_location |

**注意**：parameters不填时使用默认值（merge_strategy默认为llm_balanced）

---

## 转换示例

### Python模板 (原格式)

```python
class EarningsCallSummary(AutoModel):
    schema = EarningsCallSummarySchema

    def __init__(self, llm_client, embedder):
        super().__init__(
            data_schema=EarningsCallSummarySchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt="""你是一位专业的财务分析师...""",
            strategy_or_merger=MergeStrategy.LLM.BALANCED,
        )
```

### YAML配置 (目标格式)

```yaml
name: EarningsCallSummary
autotype: model
tag: [finance]

language: zh

description:
  zh: 财报电话会议摘要

schema:
  fields:
    - name: company_name
      type: string
      description:
        zh: 公司名称
    - name: quarter
      type: string
      description:
        zh: 报告季度
    - name: revenue
      type: string
      description:
        zh: 营收数据
    - name: guidance
      type: string
      description:
        zh: 业绩指引

extraction_guide:
  target:
    zh: |
      你是一位专业的财务分析师，擅长从财报电话会议中提取关键信息。
      请从财报电话会议记录中提取关键财务指标、业绩指引和整体基调。
  rules:
    zh: |
      1. 每个字段对应一个独立的信息项，禁止合并
      2. 数据必须与原文保持一致，不得编造
      3. 如果信息缺失，该字段留空

identifiers: {}

parameters: {}

display:
  label: company_name
```

---

## 常用配置值

### merge_strategy（不填默认为 llm_balanced）
- `none`: 不合并
- `field`: 基于字段合并
- `llm_balanced`: LLM平衡合并（默认）
- `llm_conservative`: LLM保守合并

### extraction_mode (graph类型)
- `one_stage`: 单阶段提取（同时提取节点和边）
- `two_stage`: 双阶段提取（先提取节点，再提取边）

---

## 时空图参数的特殊处理

对于 `temporal_graph`、`spatial_graph`、`spatio_temporal_graph` 类型的模板，有两个特殊的参数：

### observation_time 和 observation_location

- **observation_time**: 观察日期，用于解析相对时间表达式（如"去年"、"昨天"）
- **observation_location**: 观察位置，用于解析相对位置表达式（如"这里"、"附近"）

### 在YAML配置中

这两个参数**不应该在YAML配置文件中硬编码**，应该由用户在运行时提供：

```yaml
parameters:
  extraction_mode: two_stage
  # observation_time 和 observation_location 由用户在运行时提供
```

### 在运行时传入

使用 `TemplateFactory.create` 时，可以通过 kwargs 传入这些参数：

```python
from hyperextract.templates.generator import TemplateRegistry, TemplateFactory

# 加载配置
registry = TemplateRegistry()
registry.load_from_directory("hyperextract/templates/presets")
config = registry.get("FinancialDataTemporalGraph")

# 创建模板时传入参数
template = TemplateFactory.create(
    config, 
    llm, 
    embedder,
    observation_time="2024-06-15",  # 覆盖默认值
    observation_location="北京",       # 覆盖默认值
    chunk_size=4096,                # 也可以覆盖其他参数
)
```

### 在提示词中引用

可以在 extraction_guide 中使用这些参数占位符：

```yaml
extraction_guide:
  rules_for_time:
    zh: |
      1. 相对时间解析（基于观察日期）
         - 当前观察日期为 {observation_time}
         - "去年" -> 计算 {observation_time} 前一年的年份
         - "昨天" -> 计算 {observation_time} 前一天的日期

  rules_for_location:
    zh: |
      1. 相对位置解析（基于观察位置）
         - 当前观察位置为 {observation_location}
         - "这里"、"本地" -> {observation_location}
         - "附近"、"周边" -> {observation_location} 附近区域
```

---

## 转换检查清单

转换时请确认：

- [ ] name 字段正确
- [ ] autotype 字段正确
- [ ] tag 数组包含正确的领域标签
- [ ] description 使用 `zh:` 格式
- [ ] schema/item_schema/node_schema/edge_schema 的每个字段的 description 都使用 `zh:` 格式
- [ ] extraction_guide 的每个子字段（target, rules, rules_for_nodes 等）都使用 `zh:` 格式
- [ ] identifiers 配置正确（graph类型需要完整配置）
- [ ] parameters 可选配置
- [ ] display 配置必须存在（label / node_label + edge_label）
