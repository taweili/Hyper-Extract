# Hyper-Extract 知识模板重新设计实施计划

## 📋 概述

本文档详细规划了 Hyper-Extract 知识模板库的重新设计方案。核心目标是通过精简过度设计的模板、增加顺应热点的新模板、提高每个模板的实际使用价值，打造一个更实用、更精简、更有吸引力的模板库。

---

## 🎯 设计原则

### 1. 真实性检验
- ✅ 有真实文档需求：能否举出3个以上具体文档类型？
- ✅ 有明确使用场景：谁来用？解决什么问题？
- ✅ 有可视化价值：提取结果能否直观展示？

### 2. 精简高效
- ✅ 删除自我创造需求的模板
- ✅ 合并功能重叠的模板
- ✅ 控制每个类别模板数量在 6-10 个

### 3. 跟进热点
- 重点关注：AI Agents、MCP、Skill RAG、知识图谱等热点领域

---

## 📊 模板数量规划

| 类别 | Legacy数量 | 建议数量 | 精简比例 | 优先级 |
|------|----------|---------|---------|--------|
| **General** | ~15 | 8 | 47% | 🔴 高 |
| **Finance** | ~20 | 9 | 55% | 🔴 高 |
| **Legal** | ~12 | 8 | 33% | 🟡 中 |
| **Industry** | ~14 | 8 | 43% | 🟡 中 |
| **Medicine** | ~16 | 9 | 44% | 🟡 中 |
| **TCM** | ~10 | 8 | 20% | 🟢 低 |
| **总计** | ~87 | ~50 | 43% | - |

---

## 🗂️ 各类别详细设计

---

### 1️⃣ General（通用领域）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| KnowledgeGraph | ✅ 保留 | 通用图谱提取，适用性最广 | 任何文本 |
| EntityRegistry | ✅ 保留 | 实体集合提取，NER任务 | 新闻、简历 |
| KeywordList | ✅ 保留 | 关键词提取，索引构建 | 内容打标 |
| EncyclopediaItem | ✅ 保留 | 百科词条，结构化信息 | 词典词条 |
| ConceptHierarchy | ✅ 保留 | 概念层级，教材知识 | 教材、论文 |
| LifeEventTimeline | ✅ 保留 | 生平时序，传记分析 | 传记、年表 |
| SocialNetwork | ✅ 保留 | 人物关系，社交分析 | 人物分析 |
| ComplianceLogic | ✅ 保留 | 合规超图，制度分析 | 公司制度 |

#### 🆕 新增模板

##### 1. SkillFlowGraph（AI Agent 技能流程图）

**类型**: `graph`

**需求验证**:
- ✅ 真实场景：分析 Cursor Rules、refly skills、MCP workflows
- ✅ 使用者：AI开发者、Agent设计者
- ✅ 痛点：Skill文档缺乏可视化工具

**设计思路**:
- 将 Skill 的触发条件、执行步骤、工具调用、条件分支等建模为图的节点和边
- 不同于超图，因为每个节点之间有明确的流向关系

**示例输入**:
```
## Skill: code_review
trigger: "/review"
steps:
  1. 分析代码变更
  2. 调用 linter 工具
  3. 生成审查意见
  4. 如果有严重问题，标记需要修复
tools: [git, linter, openai]
```

##### 2. TechStackGraph（技术栈依赖图）

**类型**: `graph`

**需求验证**:
- ✅ 真实场景：理解项目架构、依赖关系
- ✅ 使用者：开发者、技术管理者
- ✅ 痛点：README太长，难以快速理解技术栈

**设计思路**:
- 从 README、技术文档中提取技术之间的依赖关系
- 支持不同粒度：语言→框架→库→服务

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| CrossReferenceNet | 与 ConceptHierarchy 功能重叠 |
| RegulationProfile | 过于简单，可并入 ComplianceLogic |
| ClauseList | 与 ComplianceLogic 部分重叠 |
| PenaltyRegistry | 与 PenaltyMapping 功能重叠 |
| PenaltyMapping | 与 ComplianceLogic 功能重叠 |
| OperationalProcedure | 可并入现有模板 |

---

### 2️⃣ Finance（金融投资）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| FilingFinancialSnapshot | ✅ 保留 | 财报关键数据 | 投资分析 |
| MDANarrativeGraph | ✅ 保留 | 管理层讨论因果 | 趋势分析 |
| RiskFactorSet | ✅ 保留 | 风险因子清单 | 风险监控 |
| MaterialEventTimeline | ✅ 保留 | 重大事件时间轴 | 事件驱动 |
| SegmentPerformanceList | ✅ 保留 | 分部业绩 | 分部估值 |
| FinancialDataTemporalGraph | ✅ 保留 | 跨期财务指标 | 趋势分析 |

#### 🆕 新增模板

##### 1. EarningsCallQA（财报问答抽取）

**类型**: `hypergraph`

**需求验证**:
- ✅ 真实场景：分析财报电话会议QA环节
- ✅ 使用者：分析师、投资者
- ✅ 痛点：会议记录太长，难以快速定位关键Q&A

##### 2. ResearchKeyPoints（研报要点）

**类型**: `list`

**需求验证**:
- ✅ 真实场景：快速提炼研报核心观点
- ✅ 使用者：研究员、投资者
- ✅ 痛点：研报太长，需要快速提取结论

##### 3. GuidanceTracker（管理层指引跟踪）

**类型**: `temporal_graph`

**需求验证**:
- ✅ 真实场景：跟踪管理层指引兑现情况
- ✅ 使用者：分析师、投资者
- ✅ 痛点：需要跨期对比指引与实际

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| ManagementGuidanceList | 并入 GuidanceTracker |
| ValuationLogicMap | 过于抽象，实际使用率低 |
| FactorInfluenceHypergraph | 过度设计，用户难以使用 |
| MultiSourceSentimentHypergraph | 合并到 MarketSentimentModel |
| SupplyChain | 与核心金融场景关联弱 |
| DiscussionGraph | 与 EarningsCallQA 功能重叠 |
| CompanyHistoryTimeline | 与 MaterialEventTimeline 重叠 |
| ProceedsUsage | 使用场景有限 |
| ShareholderStructure | 已有类似模板，可简化 |
| CallSentimentHypergraph | 过度设计 |
| MarketSentimentModel | 可简化为 ResearchKeyPoints |

---

### 3️⃣ Legal（法律合规）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| ContractObligationHypergraph | ✅ 保留 | 合同权利义务 | 合同审查 |
| DefinedTermRegistry | ✅ 保留 | 术语定义 | 合同理解 |
| LiabilityClauseList | ✅ 保留 | 违约责任 | 风险评估 |
| AdjudicationLogic | ✅ 保留 | 判决推理 | 案件分析 |
| CaseFactTimeline | ✅ 保留 | 事实时间线 | 案情分析 |
| LitigationParticipantMap | ✅ 保留 | 当事人关系 | 利益分析 |
| ComplianceRequirementList | ✅ 保留 | 合规要求 | 合规审查 |
| BeneficialOwnershipGraph | ✅ 保留 | 股权穿透 | AML/KYC |

#### 🆕 新增模板

##### 1. ClauseRegistry（条款清单）

**类型**: `list`

**需求验证**:
- ✅ 真实场景：提取合同所有条款并分类
- ✅ 使用者：律师、法务
- ✅ 痛点：条款太多，难以快速定位

##### 2. CaseLawCitation（判例引用）

**类型**: `graph`

**需求验证**:
- ✅ 真实场景：研究判例之间的引用关系
- ✅ 使用者：律师、研究人员
- ✅ 痛点：判例引用关系复杂，难以追溯

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| CaseLawCitationNet | 简化为 CaseLawCitation |
| LegalConceptOntology | 与通用 ConceptHierarchy 重叠 |

---

### 4️⃣ Industry（工业制造）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| SystemTopologyGraph | ✅ 保留 | 系统拓扑 | 架构理解 |
| EquipmentTopologyGraph | ✅ 保留 | 设备拓扑 | 设备管理 |
| SpecParameterTable | ✅ 保留 | 技术参数 | 设备台账 |
| SafetyControlGraph | ✅ 保留 | 安全规程 | 安全管理 |
| EmergencyResponseGraph | ✅ 保留 | 应急预案 | 应急响应 |
| OperationFlowGraph | ✅ 保留 | 操作流程 | 运维规程 |
| OperatingModeGraph | ✅ 保留 | 工况切换 | 运行管理 |
| FailureCaseGraph | ✅ 保留 | 故障案例 | 故障分析 |

#### 🆕 新增模板

##### 1. MaintenanceLog（维保日志）

**类型**: `temporal_graph`

**需求验证**:
- ✅ 真实场景：提取维保记录的时间序列
- ✅ 使用者：运维工程师
- ✅ 痛点：日志难以结构化分析

##### 2. IncidentChain（事故因果链）

**类型**: `hypergraph`

**需求验证**:
- ✅ 真实场景：分析事故发生的因果关系
- ✅ 使用者：安全工程师
- ✅ 痛点：事故分析需要完整因果链

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| SystemCompatibilityGraph | 过度设计 |
| PartReplacementList | 可并入 MaintenanceLog |
| InspectionRecordGraph | 与 MaintenanceLog 功能重叠 |
| MaintenaceOperationMap | 与 OperationFlowGraph 重叠 |
| IncidentCausalityMap | 简化为 IncidentChain |
| SafetyTimeline | 与 MaintenanceLog 功能重叠 |
| FailureKnowledgeHypergraph | 简化为 FailureCaseGraph |

---

### 5️⃣ Medicine（医疗健康）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| PharmacologyGraph | ✅ 保留 | 药理关系 | 药理分析 |
| AnatomyHierarchy | ✅ 保留 | 解剖层级 | 手术导航 |
| TreatmentRegimenMap | ✅ 保留 | 治疗方案 | 临床决策 |
| ClinicalPathway | ✅ 保留 | 临床路径 | 诊疗规范 |
| HospitalCourseTimeline | ✅ 保留 | 病程时间线 | 病历分析 |
| DischargeInstruction | ✅ 保留 | 出院指导 | 患者教育 |
| ComplexInteractionNet | ✅ 保留 | 药物相互作用 | 用药安全 |
| ContraindicationList | ✅ 保留 | 禁忌症 | 处方审核 |

#### 🆕 新增模板

##### 1. DiagnosisChain（诊断推理链）

**类型**: `hypergraph`

**需求验证**:
- ✅ 真实场景：提取鉴别诊断的推理过程
- ✅ 使用者：医生、医学生
- ✅ 痛点：病历中的诊断推理难以结构化

##### 2. LabResult（检验报告）

**类型**: `model`

**需求验证**:
- ✅ 真实场景：结构化提取检验报告数据
- ✅ 使用者：医生、数据分析
- ✅ 痛点：检验报告难以自动提取

##### 3. AdverseEventReport（不良事件报告）

**类型**: `hypergraph`

**需求验证**:
- ✅ 真实场景：提取不良事件的详细信息
- ✅ 使用者：药物警戒
- ✅ 痛点：需要完整的因果关系

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| PathologyHypergraph | 与 DiagnosisChain 功能重叠 |
| MedicalConceptNet | 与通用模板重叠 |
| LevelOfEvidence | 使用场景有限 |
| SurgicalEventGraph | 可并入 HospitalCourseTimeline |
| TumorStagingItem | 可并入 DiagnosisChain |
| MicroscopicFeatureSet | 可并入 LabResult |
| AdverseReactionStats | 简化为 AdverseEventReport |

---

### 6️⃣ TCM（中医中药）

#### 🔍 需求分析

| 模板名称 | 保留/新增 | 理由 | 实际场景 |
|---------|----------|------|---------|
| HerbPropertyModel | ✅ 保留 | 中药属性 | 中药数据库 |
| FormulaComposition | ✅ 保留 | 君臣佐使 | 方剂分析 |
| SyndromeReasoningGraph | ✅ 保留 | 证候推理 | 临床推理 |
| CompatibilityNet | ✅ 保留 | 药对配伍 | 配伍禁忌 |
| MeridianFlowGraph | ✅ 保留 | 经络循行 | 经络理论 |
| AcupointLocationMap | ✅ 保留 | 穴位定位 | 针灸教学 |
| ProcessingMethod | ✅ 保留 | 炮制方法 | 炮制规范 |

#### 🆕 新增模板

##### 1. CaseRecord（医案记录）

**类型**: `hypergraph`

**需求验证**:
- ✅ 真实场景：提取名医医案的完整信息
- ✅ 使用者：中医师、研究人员
- ✅ 痛点：医案难以结构化分析

##### 2. PrescriptionModification（处方加减）

**类型**: `graph`

**需求验证**:
- ✅ 真实场景：分析处方加减规律
- ✅ 使用者：中医师、方剂研究
- ✅ 痛点：处方演变难以追溯

---

#### ❌ 删除/合并的模板

| 删除模板 | 原因 |
|---------|------|
| FunctionIndicationMap | 可并入 FormulaComposition |
| PrescriptionModification | 已有同名模板，保留 |

---

## 📝 实施流程

### 每个模板的实现流程

```
┌─────────────────────────────────────────┐
│  1️⃣ Brainstorm（头脑风暴）              │
│     - 讨论模板的实际需求场景             │
│     - 验证是否是真需求                   │
│     - 确定合适的原语类型                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  2️⃣ Designer（设计）                    │
│     - 根据 brainstorm 结果设计 YAML      │
│     - record-designer: model/list/set   │
│     - graph-designer: graph/hypergraph  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  3️⃣ Validator（验证）                  │
│     - 验证 YAML 语法正确性              │
│     - 检查字段定义是否合理               │
│     - 验证与原语类型的匹配度             │
└─────────────────────────────────────────┘
```

---

## 📅 实施时间表

### Phase 1: General + Finance（高优先级）

| 步骤 | 任务 | 状态 |
|------|------|------|
| 1.1 | Brainstorm: SkillFlowGraph | ⏳ 待开始 |
| 1.2 | Design: SkillFlowGraph | ⏳ 待开始 |
| 1.3 | Validate: SkillFlowGraph | ⏳ 待开始 |
| 1.4 | Brainstorm: TechStackGraph | ⏳ 待开始 |
| 1.5 | Design: TechStackGraph | ⏳ 待开始 |
| 1.6 | Validate: TechStackGraph | ⏳ 待开始 |
| 1.7 | Brainstorm: Finance 新模板 | ⏳ 待开始 |
| 1.8 | Design: Finance 新模板 | ⏳ 待开始 |
| 1.9 | Validate: Finance 新模板 | ⏳ 待开始 |

### Phase 2: Legal + Industry

| 步骤 | 任务 | 状态 |
|------|------|------|
| 2.1 | Brainstorm: Legal 新模板 | ⏳ 待开始 |
| 2.2 | Design: Legal 新模板 | ⏳ 待开始 |
| 2.3 | Validate: Legal 新模板 | ⏳ 待开始 |
| 2.4 | Brainstorm: Industry 新模板 | ⏳ 待开始 |
| 2.5 | Design: Industry 新模板 | ⏳ 待开始 |
| 2.6 | Validate: Industry 新模板 | ⏳ 待开始 |

### Phase 3: Medicine + TCM

| 步骤 | 任务 | 状态 |
|------|------|------|
| 3.1 | Brainstorm: Medicine 新模板 | ⏳ 待开始 |
| 3.2 | Design: Medicine 新模板 | ⏳ 待开始 |
| 3.3 | Validate: Medicine 新模板 | ⏳ 待开始 |
| 3.4 | Brainstorm: TCM 新模板 | ⏳ 待开始 |
| 3.5 | Design: TCM 新模板 | ⏳ 待开始 |
| 3.6 | Validate: TCM 新模板 | ⏳ 待开始 |

---

## 📂 输出文件结构

```
hyperextract/templates/
├── presets/
│   ├── general/
│   │   ├── base_graph.yaml           # 基础图（已存在）
│   │   ├── base_hypergraph.yaml      # 基础超图（已存在）
│   │   ├── knowledge_graph.yaml      # 知识图谱
│   │   ├── entity_registry.yaml      # 实体集合
│   │   ├── keyword_list.yaml         # 关键词列表
│   │   ├── encyclopedia_item.yaml     # 百科条目
│   │   ├── concept_hierarchy.yaml    # 概念层级
│   │   ├── life_event_timeline.yaml  # 生平时序
│   │   ├── social_network.yaml       # 社交网络
│   │   ├── compliance_logic.yaml     # 合规逻辑（已存在）
│   │   ├── skill_flow_graph.yaml     # 🆕 AI技能流程图
│   │   └── tech_stack_graph.yaml     # 🆕 技术栈依赖图
│   │
│   ├── finance/
│   │   ├── filing_snapshot.yaml      # 🆕 财报快照
│   │   ├── mda_graph.yaml            # 🆕 MD&A因果图
│   │   ├── risk_factor_set.yaml      # 🆕 风险因子集
│   │   ├── event_timeline.yaml       # 🆕 重大事件时序
│   │   ├── segment_performance.yaml   # 🆕 分部业绩
│   │   ├── earnings_call_qa.yaml      # 🆕 财报问答
│   │   ├── research_keypoints.yaml    # 🆕 研报要点
│   │   └── guidance_tracker.yaml      # 🆕 指引跟踪
│   │
│   ├── legal/
│   │   ├── contract_obligations.yaml  # 🆕 合同义务
│   │   ├── defined_terms.yaml        # 🆕 术语定义
│   │   ├── liability_clauses.yaml    # 🆕 责任条款
│   │   ├── clause_registry.yaml       # 🆕 条款清单
│   │   ├── case_fact_timeline.yaml   # 🆕 案件事实时序
│   │   ├── adjudication_logic.yaml   # 🆕 裁判逻辑（已存在）
│   │   ├── litigation_participants.yaml  # 🆕 诉讼参与人
│   │   └── case_citation.yaml         # 🆕 判例引用
│   │
│   ├── industry/
│   │   ├── system_topology.yaml      # 🆕 系统拓扑
│   │   ├── equipment_spec.yaml        # 🆕 设备规格
│   │   ├── safety_control.yaml       # 🆕 安全控制
│   │   ├── operation_procedure.yaml  # 🆕 操作规程
│   │   ├── failure_case.yaml          # 🆕 故障案例
│   │   ├── maintenance_log.yaml       # 🆕 维保日志
│   │   ├── incident_chain.yaml        # 🆕 事故因果链
│   │   └── emergency_response.yaml    # 🆕 应急响应
│   │
│   ├── medicine/
│   │   ├── drug_info.yaml            # 🆕 药品信息
│   │   ├── drug_interaction.yaml      # 🆕 药物相互作用
│   │   ├── treatment_plan.yaml        # 🆕 治疗方案
│   │   ├── clinical_pathway.yaml     # 🆕 临床路径
│   │   ├── hospital_course.yaml      # 🆕 住院病程
│   │   ├── lab_result.yaml            # 🆕 检验结果
│   │   ├── discharge_summary.yaml    # 🆕 出院小结
│   │   ├── diagnosis_chain.yaml       # 🆕 诊断推理链
│   │   └── adverse_event.yaml         # 🆕 不良事件
│   │
│   └── tcm/
│       ├── herb_property.yaml        # 🆕 中药属性
│       ├── formula_composition.yaml  # 🆕 方剂组成
│       ├── syndrome_reasoning.yaml   # 🆕 证候推理
│       ├── herb_compatibility.yaml   # 🆕 药对配伍
│       ├── meridian_flow.yaml        # 🆕 经络循行
│       ├── acupoint_info.yaml        # 🆕 穴位信息
│       ├── case_record.yaml          # 🆕 医案记录
│       └── processing_method.yaml    # 🆕 炮制方法
│
└── IMPLEMENTATION_PLAN.md             # 本文档
```

---

## ✅ 检查清单

### 设计检查
- [ ] 是否有真实文档场景？
- [ ] 是否有明确的使用者？
- [ ] 是否有可视化的价值？
- [ ] 是否与现有模板功能重叠？

### YAML 检查
- [ ] 字段定义完整
- [ ] 描述清晰准确
- [ ] 语言支持（中/英）
- [ ] 符合原语类型规范
- [ ] 示例具有代表性

### 文档检查
- [ ] README 已更新
- [ ] 示例代码可用
- [ ] 测试用例覆盖

---

## 📌 备注

本计划将根据实施过程中的反馈持续迭代优化。

**最后更新**: 2026-03-27
**版本**: v1.0
