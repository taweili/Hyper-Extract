# Hyper-Extract 知识模板重构计划

## 📋 项目现状分析

### 当前结构
```
templates/
├── presets/              # 6个核心领域
│   ├── finance/          # 金融
│   ├── general/          # 通用（需保留base_*）
│   ├── industry/         # 工业
│   ├── legal/            # 法律
│   ├── medicine/         # 医学
│   └── tcm/              # 中医
└── legacy/               # 旧模板（归档，待清理）
    ├── presets/          # 6个归档领域
    └── zh/               # Python模板
```

### 现有问题
1. **过度设计**：创建了自我想象的需求
2. **模板膨胀**：许多模板功能重叠，用户难以选择
3. **脱离实际需求**：缺乏对技术趋势的响应

---

## 🔥 GitHub热点调研结论（2026年3月）

### 关键技术趋势
- **Agentic AI**：Sub-agents、Memory、Skills组合成为主流
- **MCP (Model Context Protocol)**：正在成为Agent间通信标准
- **Skills Marketplace**：3.7万+个可安装skill
- **Workflow as Code**：YAML配置文件定义AI工作流

---

## 🎯 重新设计原则

1. **用户真实需求驱动**：不是"可能有用"，而是"真正需要"
2. **控制模板数量**：每个领域5-8个精选模板
3. **言简意赅命名**：模板名称简洁明了
4. **每个图需描述**：明确用于什么文档、建模什么、可视化什么
5. **保持base_*不变**：通用基础模板已完善

---

## 📚 1. **general** - 通用领域 ⭐

### 设计原则
通用领域服务于所有文档类型，重点关注AI时代新需求和通用文档分析。

### 模板清单

#### 保留项（9个）

| 模板 | 类型 | 描述 |
|------|------|------|
| `base_graph` | graph | 通用图基础 |
| `base_hypergraph` | hypergraph | 通用超图基础 |
| `base_list` | list | 通用列表基础 |
| `base_model` | model | 通用模型基础 |
| `base_set` | set | 通用集合基础 |
| `base_temporal_graph` | temporal_graph | 时序图基础 |
| `base_spatial_graph` | spatial_graph | 空间图基础 |
| `base_spatio_temporal_graph` | spatio_temporal_graph | 时空图基础 |

#### 新增项（3个）

##### 1.1 `workflow_graph` - 流程图

**用于文档**：Skill定义文件（SKILL.md）、Agent工作流文档、SOP操作手册、业务流程说明

**建模内容**：步骤名称、步骤类型（skill/step/condition/branch）、输入要求、输出结果、条件分支

**可视化什么**：展示步骤之间的执行顺序、依赖关系、分支汇聚，形成流程可视化图

```yaml
type: temporal_graph
核心要素:
  - step_name: 步骤名称
  - step_type: 类型（skill/step/condition/branch）
  - description: 步骤描述
  - input: 输入要求
  - output: 输出结果
关系:
  - next: 顺序执行
  - triggers: 触发条件
  - branches_to: 条件分支
  - converges: 汇聚点
```

---

##### 1.2 `doc_structure` - 文档结构图

**用于文档**：技术文档（README、API docs）、论文、报告、规范文档

**建模内容**：章节标题、节点类型（chapter/section/paragraph/code/table）、层级深度、内容摘要、交叉引用

**可视化什么**：展示文档的层级结构、章节关系、引用关系，便于理解长文档脉络

```yaml
type: graph
核心要素:
  - node_type: 节点类型（chapter/section/paragraph/code/table）
  - title: 标题/名称
  - level: 层级深度
  - summary: 内容摘要
关系:
  - contains: 包含关系（父→子）
  - references: 引用关系（交叉引用）
```

---

##### 1.3 `biography_graph` - 传记图

**用于文档**：人物传记、回忆录、年谱、人物介绍文章

**建模内容**：事件名称、发生日期、发生地点、重要性、涉及人物、人物关系

**可视化什么**：展示人物的关键事件人生轨迹、事件因果关系、人物互动网络

```yaml
type: temporal_graph
核心要素:
  - event: 事件名称
  - event_date: 发生日期
  - location: 发生地点
  - significance: 重要性（高/中/低）
  - participants[]: 涉及人物
关系:
  - precedes: 时间先后
  - causes: 因果关系
  - involves: 参与关系
```

---

##### 1.4 `concept_graph` - 概念关系图

**用于文档**：教科书、百科全书、学术论文、概念解释文档

**建模内容**：概念名称、概念类型（实体/抽象/过程）、定义、层级关系

**可视化什么**：展示概念之间的层级关系（is-a/part-of）、语义关联，形成知识地图

```yaml
type: graph
核心要素:
  - concept: 概念名称
  - category: 概念类型（实体/抽象/过程/关系）
  - definition: 简要定义
关系:
  - subclass_of: 层级关系（子类）
  - part_of: 组成关系（部分）
  - related_to: 相关关系
```

---

### 删除项
- ❌ `clause_list` → 合并到legal
- ❌ `compliance_logic` → 合并到legal
- ❌ `knowledge_graph` → 用base_graph替代
- ❌ `social_network` → 过于泛化
- ❌ `cross_reference_net` → 用doc_structure替代
- ❌ `life_event_timeline` → 重命名为biography_graph

**general预期数量：13个（原14个）**

---

## 💰 2. **finance** - 金融

### 设计原则
金融领域用户需求明确，保留高频使用模板。

### 模板清单（5个）

##### 2.1 `earnings_summary` - 财报会议摘要

**用于文档**：财报电话会议记录（Earnings Call Transcript）

**建模内容**：公司名、季度、收入/EPS实际值、与预期对比、前瞻指引、整体基调、亮点/关切

**可视化什么**：快速理解会议核心内容，把握管理层信心和关键议题

```yaml
type: model
核心字段:
  - company_name, quarter
  - reported_revenue, reported_eps
  - revenue_vs_consensus, eps_vs_consensus
  - guidance_revenue, guidance_eps
  - overall_tone
  - key_highlights[], key_concerns[]
```

---

##### 2.2 `sentiment_model` - 市场情绪模型

**用于文档**：财经新闻、市场评论、研究报告、社交媒体帖子

**建模内容**：情绪分数（-1到1）、主导主题、关键实体、价格影响

**可视化什么**：量化市场情绪变化，识别舆情与股价的关联

```yaml
type: model
核心字段:
  - sentiment_score: -1到1
  - dominant_theme: 主导主题
  - key_entities[]: 关键实体
  - price_impact: 价格影响
```

---

##### 2.3 `event_timeline` - 重大事件时间线

**用于文档**：8-K报告、新闻稿、公司公告、投资评级调整

**建模内容**：事件名称、事件日期、重大性（是否重大）、影响程度

**可视化什么**：展示公司重要事件的时间顺序和因果关系，支持事件驱动分析

```yaml
type: temporal_graph
核心要素:
  - event: 事件名称
  - event_date: 事件日期
  - materiality: 重大性
关系:
  - causes: 因果关系
  - precedes: 时间先后
```

---

##### 2.4 `ownership_graph` - 股权结构图

**用于文档**：招股说明书（IPO S-1）、年度报告（10-K）、股东名册

**建模内容**：股东名称、持股比例、股东类型（机构/个人/关联方）、控制权关系

**可视化什么**：展示股权层级结构、控制关系路径，辅助尽职调查和UBO识别

```yaml
type: graph
核心要素:
  - shareholder: 股东名称
  - shareholder_type: 股东类型
  - ownership_percentage: 持股比例
关系:
  - controls: 控制关系
  - belongs_to: 归属集团
```

---

##### 2.5 `risk_factor_set` - 风险因子集合

**用于文档**：年报风险章节（10-K Item 1A）、季报风险披露、招股说明书风险章节

**建模内容**：风险因子、风险类别（经营/财务/市场/法规）、严重程度

**可视化什么**：提取和归类风险因子，便于风险监控和比较分析

```yaml
type: set
核心要素:
  - risk_factor: 风险因子
  - severity: 严重程度
  - category: 风险类别
```

---

### 删除项
- ❌ `SupplyChainGraph` → 合并到其他或删除
- ❌ `MDANarrativeGraph` → 合并到event_timeline
- ❌ `DiscussionGraph` → 使用率低
- ❌ `FactorInfluenceHypergraph` → 过于复杂
- ❌ `ValuationLogicMap` → 过于主观
- ❌ 其他20+个模板 → 删除

**finance预期数量：5个（原20+个）**

---

## 🏥 3. **medicine** - 医学

### 设计原则
医学文档标准化程度高，选择最通用的模板。

### 模板清单（5个）

##### 3.1 `treatment_map` - 治疗方案图

**用于文档**：临床实践指南、治疗方案文档、临床路径文件

**建模内容**：患者特征、诊断、治疗方案、适应症、禁忌组合、治疗结果

**可视化什么**：展示诊断→治疗→结果的决策路径，辅助临床决策支持系统（CDSS）

```yaml
type: hypergraph
核心要素:
  - patient: 患者特征
  - diagnosis: 诊断
  - treatment: 治疗方案
  - outcome: 治疗结果
关系:
  - indicates: 适应症
  - contraindicated_with: 禁忌组合
```

---

##### 3.2 `drug_interaction` - 药物相互作用图

**用于文档**：药品说明书、药物相互作用手册、临床药学文档

**建模内容**：药物A、药物B、相互作用类型（协同/拮抗）、作用机制、严重程度

**可视化什么**：展示多种药物之间的相互作用网络，辅助用药安全和药物重整

```yaml
type: graph
核心要素:
  - drug: 药物名称
  - drug_class: 药物类别
关系:
  - interacts_with: 相互作用（标注类型和严重程度）
  - contraindicated: 禁忌组合
```

---

##### 3.3 `anatomy_graph` - 解剖结构图

**用于文档**：解剖学教科书、解剖图谱、外科手术记录

**建模内容**：解剖结构名称、结构层级（系统→器官→组织→细胞）、位置

**可视化什么**：展示人体结构的层级包含关系和空间位置，辅助外科计划和医学教育

```yaml
type: graph
核心要素:
  - structure: 解剖结构
  - level: 层级（系统→器官→组织→细胞）
  - location: 空间位置
关系:
  - contains: 包含关系
  - located_in: 位于关系
```

---

##### 3.4 `hospital_timeline` - 住院病程时间线

**用于文档**：出院小结、病程记录、手术记录、会诊记录

**建模内容**：事件类型（入院/检查/手术/用药/出院）、事件日期、执行人、结果

**可视化什么**：展示患者住院期间的事件顺序，便于病历分析和质量控制

```yaml
type: temporal_graph
核心要素:
  - event: 事件（入院/检查/手术/用药/出院）
  - event_date: 发生日期
  - performer: 执行人
关系:
  - follows: 顺序关系
  - results_in: 结果关系
```

---

##### 3.5 `discharge_instruction` - 出院指导

**用于文档**：出院小结、患者教育材料、用药指导单

**建模内容**：用药列表及用法、随访安排、注意事项、警告信号

**可视化什么**：结构化呈现出院后患者需知内容，便于医患沟通和患者管理

```yaml
type: model
核心字段:
  - medications[]: 用药列表及用法
  - follow_up: 随访安排
  - restrictions: 注意事项
  - warning_signs[]: 警告信号
```

---

### 删除项
- ❌ `ComplexInteractionNet` → 合并到drug_interaction
- ❌ `PathologyHypergraph` → 合并到treatment_map
- ❌ `LevelOfEvidence` → 过于学术
- ❌ `MicroscopicFeatureSet` → 过于专业
- ❌ `TumorStagingItem` → 可作为treatment_map子集
- ❌ 其他10+个模板 → 删除

**medicine预期数量：5个（原15+个）**

---

## ⚖️ 4. **legal** - 法律

### 设计原则
法律文档逻辑严密，保留核心模板并简化。

### 模板清单（5个）

##### 4.1 `contract_obligation` - 合同义务图

**用于文档**：服务合同（MSA/SLA）、采购合同、租赁合同、劳动合同

**建模内容**：合同主体、义务内容、触发条件、例外情形、违约责任

**可视化什么**：展示合同中各方的权利义务关系、条件触发链，便于合同审查和履约监控

```yaml
type: hypergraph
核心要素:
  - party: 主体
  - obligation: 义务
  - trigger: 触发条件
  - exception: 例外情形
关系:
  - must_perform: 主体需履行
  - triggered_by: 条件触发
  - exempt_by: 例外免责
```

---

##### 4.2 `case_fact_timeline` - 案件事实时间线

**用于文档**：判决书、起诉状、答辩状、证据材料

**建模内容**：事实描述、发生日期、相关证据、是否争议、认定结果

**可视化什么**：展示案件事实的时间顺序和证据链，辅助诉讼分析

```yaml
type: temporal_graph
核心要素:
  - fact: 事实描述
  - date: 发生日期
  - evidence: 相关证据
  - disputed: 是否争议
关系:
  - preceded_by: 时间先后
  - proves: 证据支持
```

---

##### 4.3 `case_citation` - 判例引用图

**用于文档**：判决书、法律意见书、学术论文、判例汇编

**建模内容**：案件名称、引用条款、审理法院、判决结果

**可视化什么**：展示判例之间的引用关系和效力层级，辅助法律研究和先例分析

```yaml
type: graph
核心要素:
  - case: 案件名称
  - citation: 引用条款
  - court: 审理法院
关系:
  - cites: 引用关系
  - distinguished_from: 区分解释
  - overruled_by: 推翻
```

---

##### 4.4 `compliance_list` - 合规要求清单

**用于文档**：合规手册、法规汇编、审计报告、内控文档

**建模内容**：合规要求、依据法规、完成期限、责任人

**可视化什么**：结构化列出合规要求，便于合规审计和GAP分析

```yaml
type: list
核心字段:
  - requirement: 合规要求
  - regulation: 依据法规
  - deadline: 完成期限
  - responsible_party: 责任人
```

---

##### 4.5 `defined_term_set` - 定义术语集合

**用于文档**：合同（特别是英文合同）、法律意见书、法规定义章节

**建模内容**：定义术语、定义位置、含义摘要

**可视化什么**：提取合同中所有定义条款，便于术语一致性检查和快速理解

```yaml
type: set
核心要素:
  - term: 定义术语
  - defined_in: 定义位置
  - meaning: 含义摘要
```

---

### 删除项
- ❌ `AdjudicationLogic` → 过于复杂
- ❌ `BeneficialOwnershipGraph` → 合并到finance的ownership_graph
- ❌ `LiabilityClauseList` → 合并到contract_obligation
- ❌ 其他5+个模板 → 删除

**legal预期数量：5个（原10+个）**

---

## 🌿 5. **tcm** - 中医

### 设计原则
中医领域小众但专业，选择核心模板并增加关联图。

### 模板清单（5个）

##### 5.1 `formula_composition` - 方剂组成图

**用于文档**：经典方剂著作（《伤寒论》《金匮要略》）、现代方剂学教材、临床验方

**建模内容**：方剂名称、药材名称、角色（君/臣/佐/使）、剂量、配伍关系

**可视化什么**：展示方剂中各药材的角色分配和配伍关系，辅助方剂分析和药理研究

```yaml
type: hypergraph
核心要素:
  - formula: 方剂名称
  - herb: 药材名称
  - role: 角色（君/臣/佐/使）
  - dosage: 剂量
关系:
  - combines_with: 配伍关系
  - antagonizes: 相恶相反
```

---

##### 5.2 `syndrome_reasoning` - 证候推理图

**用于文档**：医案（医话/医论）、临床经验集、中医诊疗指南

**建模内容**：症状表现、证候类型、治法原则、推荐方剂

**可视化什么**：展示症状→证候→治法→方剂的推理链条，辅助辨证论治和经验挖掘

```yaml
type: hypergraph
核心要素:
  - symptom: 症状表现
  - syndrome: 证候类型
  - principle: 治法原则
  - formula: 推荐方剂
关系:
  - leads_to: 导致
  - treated_by: 治疗
```

---

##### 5.3 `meridian_graph` - 经络流注图

**用于文档**：针灸学教材、经络腧穴学、针灸临床指南

**建模内容**：穴位名称、所属经脉、位置描述、流注顺序

**可视化什么**：展示穴位在经脉上的分布和流注顺序，辅助针灸教学和临床取穴

```yaml
type: graph
核心要素:
  - acupoint: 穴位名称
  - meridian: 所属经脉
  - location: 位置描述
关系:
  - located_on: 位于经脉
  - flows_to: 流注顺序
```

---

##### 5.4 `herb_property` - 药材属性模型

**用于文档**：中药学教材（《神农本草经》《本草纲目》）、中药数据库、药品标准

**建模内容**：药材名称、四气、五味、归经、功效、毒性

**可视化什么**：结构化呈现药材的基本属性，便于中药数据库建设和临床查询

```yaml
type: model
核心字段:
  - name: 药材名称
  - nature: 四气（寒/热/温/凉）
  - flavor: 五味（酸/苦/甘/辛/咸）
  - meridian_entry: 归经
  - efficacy: 功效
  - toxicity: 毒性
```

---

##### 5.5 `herb_relation` - 药材关联图

**用于文档**：中药学教材、方剂学文献、临床用药指南、药对研究

**建模内容**：药材名称、关联类型（相须/相使/相畏/相杀/相恶/相反）、关联描述

**可视化什么**：展示药材之间的协同或对抗关系，辅助临床配伍和用药安全

```yaml
type: graph
核心要素:
  - herb: 药材名称
  - herb_property: 药材属性（可选）
关系:
  - synergizes: 相须/相使（协同）
  - reduces_toxicity: 相畏/相杀（减毒）
  - antagonizes: 相恶/相反（对抗）
```

---

### 删除项
- ❌ `AcupointLocationMap` → 合并到meridian_graph
- ❌ `PulseTongueRecord` → 过于细节
- ❌ `ProcessingMethod` → 可作为herb_property扩展
- ❌ 其他5+个模板 → 删除

**tcm预期数量：5个（原10+个）**

---

## ⚙️ 6. **industry** - 工业

### 设计原则
工业领域文档实用性强，保留操作相关模板。

### 模板清单（5个）

##### 6.1 `operation_flow` - 操作流程图

**用于文档**：SOP操作手册、设备操作规程、维修作业指导书

**建模内容**：操作步骤名称、步骤类型（动作/检查/切换）、设备状态、预期结果

**可视化什么**：展示操作的步骤顺序、状态变化和预期结果，辅助SOP可视化和操作培训

```yaml
type: graph
核心要素:
  - step: 操作步骤名称
  - step_type: 类型（动作/检查/切换）
  - equipment_state: 设备状态
  - expected_result: 预期结果
关系:
  - next: 顺序执行
  - triggers: 触发条件
  - results_in: 导致状态变化
```

---

##### 6.2 `safety_control` - 安全控制图

**用于文档**：安全管理手册、安全操作规程、风险评估报告、应急预案

**建模内容**：危险源、风险点、控制措施、责任角色

**可视化什么**：展示危险源→风险→控制措施的链条，辅助安全管理和审核

```yaml
type: graph
核心要素:
  - hazard: 危险源
  - risk_point: 风险点
  - control_measure: 控制措施
  - responsible_role: 责任角色
关系:
  - causes: 导致风险
  - mitigates: 减轻风险
  - assigned_to: 分配责任
```

---

##### 6.3 `failure_case` - 故障案例图

**用于文档**：故障分析报告、维修记录、设备履历、故障案例库

**建模内容**：故障现象、根本原因、纠正措施、预防措施、经验教训

**可视化什么**：展示故障现象→原因→措施的因果链，辅助故障诊断和经验积累

```yaml
type: graph
核心要素:
  - phenomenon: 故障现象
  - root_cause: 根本原因
  - corrective_action: 纠正措施
  - lesson: 经验教训
关系:
  - caused_by: 由...引起
  - resolved_by: 通过...解决
  - prevented_by: 预防措施
```

---

##### 6.4 `equipment_topology` - 设备拓扑图

**用于文档**：设备手册、系统设计文档、工厂布局图、备件清单

**建模内容**：设备名称、设备类型、安装位置、规格参数、连接关系

**可视化什么**：展示设备之间的物理连接和层级关系，辅助设备管理和系统理解

```yaml
type: graph
核心要素:
  - equipment: 设备名称
  - equipment_type: 设备类型
  - location: 安装位置
  - specifications: 规格参数
关系:
  - connected_to: 物理连接
  - located_in: 安装位置
  - contains: 包含关系
```

---

##### 6.5 `emergency_response` - 应急响应图

**用于文档**：应急预案、应急演练方案、事故处置规程

**建模内容**：事故场景、响应动作、责任人、响应顺序、资源需求

**可视化什么**：展示事故→响应动作→责任人的触发链，辅助应急演练和事故处置

```yaml
type: graph
核心要素:
  - scenario: 事故场景
  - action: 响应动作
  - responsible_role: 责任人
  - resource: 所需资源
关系:
  - triggers: 触发响应
  - executed_by: 执行责任人
  - requires: 所需资源
```

---

### 删除项
- ❌ `IncidentCausalityMap` → 合并到failure_case
- ❌ `SystemCompatibilityGraph` → 使用率低
- ❌ `PartReplacementList` → 过于细节
- ❌ `SystemTopologyGraph` → 与equipment_topology重复
- ❌ 其他10+个模板 → 删除

**industry预期数量：5个（原15+个）**

---

## 📊 重构预期效果

### 模板数量变化

| 领域 | 重构前 | 重构后 | 变化 |
|------|--------|--------|------|
| general | 14 | 13 | +4新增，-5删除 |
| finance | 20+ | 5 | -75% |
| medicine | 15+ | 5 | -67% |
| legal | 10+ | 5 | -50% |
| tcm | 10+ | 5 | -50% |
| industry | 15+ | 5 | -67% |
| **总计** | **80+** | **38** | **-53%** |

### 新增/重命名模板汇总

| 新模板 | 用途 | 来源 |
|--------|------|------|
| `workflow_graph` | 流程图（Skill/Workflow/SOP） | 新增 |
| `doc_structure` | 文档结构图 | 新增 |
| `biography_graph` | 传记图 | 重命名（life_event_timeline） |
| `concept_graph` | 概念关系图 | 重命名（concept_hierarchy） |
| `herb_relation` | 药材关联图 | 新增 |

---

## 🗓️ 实施计划

### Phase 1: 准备阶段
- [ ] 确认保留的base_*模板清单
- [ ] 制定各模板YAML格式规范
- [ ] 建立模板测试用例

### Phase 2: general领域（优先）
- [ ] workflow_graph
- [ ] doc_structure
- [ ] biography_graph
- [ ] concept_graph

### Phase 3: 其他领域精简
- [ ] finance：保留5个，删除15+
- [ ] medicine：保留5个，删除10+
- [ ] legal：保留5个，删除5+
- [ ] tcm：保留5个，新增herb_relation，删除5+
- [ ] industry：保留5个，删除10+

### Phase 4: legacy清理
- [ ] 将归档领域移至legacy/presets
- [ ] 清理Python模板（zh目录）
- [ ] 更新文档引用

### Phase 5: 验证与发布
- [ ] 运行模板测试
- [ ] 更新README
- [ ] 发布新版本

---

## 🤔 待确认事项

1. **workflow_graph的粒度**：
   - 是否需要支持嵌套的subskill/step？
   - 条件分支的表示方式？（if/else/loop）
   - 是否需要支持并行执行节点？

2. **biography_graph**：
   - 是否需要支持"人物关系"作为单独的关系类型？
   - 地点信息用spatial_graph还是作为event的属性？

3. **herb_relation关联类型**：
   - 是否需要区分"相须/相使/相畏/相杀/相恶/相反"？

4. **模板优先级**：哪些模板应该优先实现？

5. **legacy清理时机**：是现在清理还是分阶段？

---

## 📝 附录：GitHub热点参考

### 2026年3月Trending项目
| 项目 | Stars | 领域 |
|------|-------|------|
| DeerFlow | 47K | AI Agent |
| OpenClaw | 270K | AI Assistant |
| ruflo | 26K | Agent Orchestration |
| obra/superpowers | 15K | AI Coding OS |
