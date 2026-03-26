# Hyper-Extract 核心领域知识模板

**Hyper-Extract 领域模板库** 旨在为不同垂直行业提供专业的非结构化文本抽取能力。

> 切换至 [English Version](./README.md)

---

## 📁 目录结构

```
templates/
├── presets/              # 领域模板（6个核心领域）
│   ├── finance/         # 金融投资
│   ├── general/         # 通用领域
│   ├── industry/        # 工业制造
│   ├── legal/           # 法律合规
│   ├── medicine/        # 医疗健康
│   └── tcm/            # 中医中药
├── customs/              # 自定义模板（用户可自行创建）
└── README_ZH.md
```

---

## 🚀 快速开始

### 推荐方式：使用 YAML 配置

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

# 获取模板
config = Gallery.get("KnowledgeGraph")

# 创建模板
template = TemplateFactory.create(config, llm, embedder)
result = template.parse("您的文本内容...")

# 列出所有可用模板
print(Gallery.list_all())
```

---

## 📋 领域索引

| 领域 | 描述 | 核心关注点 |
| :--- | :--- | :--- |
| **`general`** | 通用领域 | 任意文本、百科全书、人物传记、规章制度 |
| **`finance`** | 金融投资 | 财报、研报、会议纪要、金融资讯 |
| **`medicine`** | 医疗健康 | 临床指南、病历、药品文档 |
| **`tcm`** | 中医中药 | 医案、本草、方剂、经络 |
| **`industry`** | 工业制造 | 运维日志、安全报告、技术规格 |
| **`legal`** | 法律合规 | 合同协议、判决书、监管文件 |

---

## 🔧 底层原语

| 原语 | 说明 |
| :--- | :--- |
| **`AutoGraph`** | 知识图谱 - 提取实体及成对关系 |
| **`AutoSet`** | 实体集合 - 去重并汇总唯一实体 |
| **`AutoList`** | 列表 - 提取数值数组（关键词、条目等）|
| **`AutoModel`** | 数据模型 - 提取结构化字段（如信息框）|
| **`AutoTemporalGraph`** | 时序图谱 - 构建时间有序的事件序列 |
| **`AutoHypergraph`** | 超图 - 建模复杂的多实体关系 |

---

## 📚 领域详情

### 1. 📚 `general` (通用领域)

适用于无法归类或多领域交叉的文本，通过提取基础实体和SPO关系构建通用图谱。

*   **通用结构知识模板**：覆盖所有 AutoType 原语的基础模板。可直接使用或作为领域模板的扩展基础。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`BaseModel`** | `AutoModel` | 通用结构模型提取 | 通用单一对象提取 |
| **`BaseList`** | `AutoList` | 通用列表提取 | 通用有序列表提取 |
| **`BaseSet`** | `AutoSet` | 通用实体集合去重 | 通用实体汇总 |
| **`BaseGraph`** | `AutoGraph` | 通用图谱提取 | 通用二元关系提取 |
| **`BaseHypergraph`** | `AutoHypergraph` | 通用超图提取 | 通用多元关系提取 |
| **`BaseTemporalGraph`** | `AutoTemporalGraph` | 通用时序图谱提取 | 通用时间有序关系提取 |
| **`BaseSpatialGraph`** | `AutoSpatialGraph` | 通用空间图谱提取 | 通用位置感知关系提取 |
| **`BaseSpatioTemporalGraph`** | `AutoSpatioTemporalGraph` | 通用时空图谱提取 | 通用时间与位置关系提取 |

*   **任意文本 (通用提取)**：适用于任何类型的文本，直接提取其中的实体及关系。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`KnowledgeGraph`** | `AutoGraph` | 通用知识图谱提取 | 任意文本、网页内容 |
| **`EntityRegistry`** | `AutoSet` | 去重唯一实体（人名、机构） | 实体发现、NER任务 |
| **`KeywordList`** | `AutoList` | 核心概念、主题或标签 | 内容打标、索引生成 |

*   **百科条目**：对实体的综合性描述，包含结构化属性信息。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`EncyclopediaItem`** | `AutoModel` | 结构化属性信息（信息框风格）| 百科词典词条 |
| **`ConceptHierarchy`** | `AutoGraph` | 上下位/组成关系 | 科学教材知识点 |
| **`CrossReferenceNet`** | `AutoGraph` | 超链接与相互引用 | 跨词条关联 |

*   **人物传记与回忆录**：记录个人生平事迹、主要成就及社会关系。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`LifeEventTimeline`** | `AutoTemporalGraph` | 带时间戳的生平事件 | 传记、年表 |
| **`SocialNetwork`** | `AutoGraph` | 人际关系与互动 | 人物分析 |
| **`PersonalProfile`** | `AutoModel` | 静态属性（生卒年、学历）| 简历、简介 |

*   **规章制度与合规文档**：公司制度、操作手册、合规指南。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`RegulationProfile`** | `AutoModel` | 制度名称、版本、生效日期 | 制度概览 |
| **`ComplianceLogic`** | `AutoHypergraph` | 条件性行为逻辑 | 合规审计 |
| **`PenaltyRegistry`** | `AutoSet` | 违规行为与后果 | 风险管控 |
| **`OperationalProcedure`** | `AutoGraph` | 申报审批具体步骤 | SOP流程 |
| **`PenaltyMapping`** | `AutoGraph` | 违规到结果的演变路径 | 风险溯源 |
| **`ClauseList`** | `AutoList` | 原子化条文 | 条文检索 |

---

### 2. 💰 `finance` (金融投资)

专注于提取复杂的交易关系、市场观点及时间敏感事件。

*   **SEC财报 (10-K / 10-Q / 8-K)**：标准化财务申报文件，涵盖财务报表、MD&A、风险因素。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`FilingFinancialSnapshot`** | `AutoModel` | 关键财务数据 | 基本面筛选 |
| **`MDANarrativeGraph`** | `AutoGraph` | MD&A因果关系 | 叙事分析 |
| **`FilingRiskFactorSet`** | `AutoSet` | 风险因素登记 | 风险监控 |
| **`MaterialEventTimeline`** | `AutoTemporalGraph` | 重大事件时间轴 | 事件驱动分析 |
| **`SegmentPerformanceList`** | `AutoList` | 分部/区域业绩 | 分部估值 |
| **`FinancialDataTemporalGraph`** | `AutoTemporalGraph` | 跨期财务指标 | 趋势分析 |
| **`RiskAssessmentGraph`** | `AutoGraph` | 风险传导路径 | 风险监控 |
| **`SupplyChainGraph`** | `AutoGraph` | 供应链主体与风险 | ESG分析 |

*   **股票研究报告**：分析师深度报告，包含评级、目标价及投资逻辑。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`ResearchNoteSummary`** | `AutoModel` | 评级、目标价、投资逻辑 | 研报数据库 |
| **`FinancialForecast`** | `AutoList` | 营收、EPS、PE预测 | 一致性预期 |
| **`ValuationLogicMap`** | `AutoGraph` | 股价驱动因果链 | 策略映射 |
| **`FactorInfluenceHypergraph`** | `AutoHypergraph` | 宏观→行业→公司关联 | 因子归因 |
| **`RiskFactorList`** | `AutoList` | 下行风险点 | 风险监控 |

*   **招股说明书 (IPO)**：企业上市前披露文件，详述股权结构、募集资金用途。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`ShareholderStructure`** | `AutoGraph` | 股东占比、层级关系 | 尽职调查 |
| **`ProceedsUsage`** | `AutoList` | 募投项目、金额、时间表 | 投后管理 |
| **`CompanyHistoryTimeline`** | `AutoTemporalGraph` | 成立、融资、并购大事 | 企业历史 |

*   **财报电话会议**：管理层业绩说明会实录，包含前瞻性指引。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`EarningsCallSummary`** | `AutoModel` | 核心指标、指引、会议基调 | 季度回顾 |
| **`ManagementGuidanceList`** | `AutoList` | 前瞻性声明 | 业绩指引跟踪 |
| **`DiscussionGraph`** | `AutoGraph` | 讨论实体及多元关系 | 分析师关注分析 |
| **`CallSentimentHypergraph`** | `AutoHypergraph` | 多维情感信号 | 交易信号 |

*   **金融新闻与市场评论**：传递市场情绪、事件影响的新闻报道。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`MarketSentimentModel`** | `AutoModel` | 情感极性、实体、价格影响 | 交易信号 |
| **`FinancialEventCausalGraph`** | `AutoGraph` | 事件→实体→市场反应 | 策略分析 |
| **`MultiSourceSentimentHypergraph`** | `AutoHypergraph` | 多源情绪融合 | 集成评分 |
| **`MarketNarrativeTimeline`** | `AutoTemporalGraph` | 市场叙事演变 | 主题投资 |

---

### 3. 🏥 `medicine` (医疗健康)

专注于疾病诊疗逻辑、标准化术语映射及因果关系提取。

*   **医学教科书与专著**：系统性阐述解剖、病理、治疗原则。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`PathologyHypergraph`** | `AutoHypergraph` | 基因+环境+诱因→疾病 | 研究知识库 |
| **`MedicalConceptNet`** | `AutoGraph` | 医学术语及语义关系 | 术语标准化 |
| **`PharmacologyGraph`** | `AutoGraph` | 药物-受体-生理反应 | 药理分析 |
| **`AnatomyHierarchy`** | `AutoGraph` | 解剖位置层级 | 手术导航 |
| **`SymptomDifferential`** | `AutoSet` | 症状→鉴别疾病 | 辅助诊断 |

*   **临床诊疗指南**：标准化治疗决策路径。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`TreatmentRegimenMap`** | `AutoHypergraph` | 多因素治疗方案 | 肿瘤化疗方案 |
| **`ClinicalPathway`** | `AutoGraph` | 临床决策树 | 诊疗规范化 |
| **`LevelOfEvidence`** | `AutoList` | 推荐意见及证据等级 | 临床质控 |

*   **出院小结**：患者住院全过程的叙述性记录。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`SurgicalEventGraph`** | `AutoHypergraph` | 手术复杂事件 | 手术质控 |
| **`HospitalCourseTimeline`** | `AutoTemporalGraph` | 入院→检查→治疗→转归 | 病历质控 |
| **`DischargeInstruction`** | `AutoModel` | 出院带药、复诊、康复 | 患者随访 |

*   **病理报告**：对组织样本的微观描述。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`TumorStagingItem`** | `AutoModel` | TNM分期 | 肿瘤登记 |
| **`MicroscopicFeatureSet`** | `AutoSet` | 免疫组化、基因突变 | 靶向药匹配 |

*   **药品说明书**：包含适应症、禁忌症等专业信息。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`ComplexInteractionNet`** | `AutoHypergraph` | 药物相互作用 | CDSS |
| **`ContraindicationList`** | `AutoList` | 绝对禁忌 | 处方拦截 |
| **`AdverseReactionStats`** | `AutoList` | 不良反应及发生率 | 药物警戒 |

---

### 4. 🌿 `tcm` (中医中药)

针对中医特有的辨证论治逻辑和药性理论进行优化。

*   **名医医案**：记录症状、辨证分析、治法及处方的临床实录。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`SyndromeReasoningGraph`** | `AutoHypergraph` | 症状→证型→治则→处方 | 医案挖掘 |
| **`PrescriptionModification`** | `AutoGraph` | 处方加减逻辑 | 用药规律分析 |
| **`PulseTongueRecord`** | `AutoList` | 舌象与脉象特征 | 诊断客观化 |

*   **本草典籍**：描述单味药的四气五味、归经、功效。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`HerbPropertyModel`** | `AutoModel` | 四气五味、归经、毒性 | 中药数据库 |
| **`CompatibilityNet`** | `AutoGraph` | 七情配伍关系 | 配伍禁忌 |
| **`ProcessingMethod`** | `AutoList` | 炮制方法及影响 | 炮制规范 |

*   **方剂规范**：记载方剂组成，包含君臣佐使配伍结构。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`FormulaComposition`** | `AutoHypergraph` | 君臣佐使层级结构 | 方剂解析 |
| **`FunctionIndicationMap`** | `AutoGraph` | 方剂→功能→主治 | 推荐系统 |

*   **经络腧穴专著**：描述穴位定位、归经及主治功能。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`AcupointLocationMap`** | `AutoGraph` | 腧穴空间定位 | 针灸教学 |
| **`MeridianFlowGraph`** | `AutoGraph` | 十二经脉循行 | 经络理论 |

---

### 5. ⚙️ `industry` (工业制造)

专注于电力、制造、能源等行业的运维数据与日志分析。

*   **管理规范**：安全规程、应急预案等。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`SafetyControlGraph`** | `AutoGraph` | 危险源、风险点、管控 | 安全规程 |
| **`EmergencyResponseGraph`** | `AutoGraph` | 事故场景、响应动作 | 应急预案 |
| **`IncidentCausalityMap`** | `AutoHypergraph` | 隐患→触发→违章→后果 | 风险预防 |
| **`SafetyTimeline`** | `AutoTemporalGraph` | 操作与响应序列 | 事故复盘 |

*   **技术规格书**：设备额定参数、设计标准。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`SystemTopologyGraph`** | `AutoGraph` | 厂区、系统、设备层级 | 系统说明书 |
| **`EquipmentTopologyGraph`** | `AutoGraph` | 设备实体及连接 | 设备图纸 |
| **`SpecParameterTable`** | `AutoModel` | 额定功率、材质、精度 | 设备台账 |
| **`SystemCompatibilityGraph`** | `AutoHypergraph` | 设备与环境关系 | 选型辅助 |

*   **操作运维**：设备运行规程、工况切换。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`OperationFlowGraph`** | `AutoGraph` | 操作步骤、状态、结果 | 运行规程 |
| **`OperatingModeGraph`** | `AutoGraph` | 工况类型和切换条件 | 工况切换 |
| **`MaintenaceOperationMap`** | `AutoHypergraph` | 操作人、工具、对象、耗时 | 维修标准化 |

*   **设备维护**：巡检记录、故障案例、备件更换。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`InspectionRecordGraph`** | `AutoGraph` | 设备和巡检项 | 巡检记录 |
| **`FailureCaseGraph`** | `AutoGraph` | 现象、原因、措施、教训 | 故障案例库 |
| **`FailureKnowledgeHypergraph`** | `AutoHypergraph` | 现象、根因、部件、方案 | 故障诊断 |
| **`PartReplacementList`** | `AutoList` | 零件型号、数量、原因 | 备件管理 |

*   **HSE事故报告**：生产事故调查报告。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`IncidentCausalityMap`** | `AutoHypergraph` | 隐患→触发→违章→后果 | 事故推演 |
| **`SafetyTimeline`** | `AutoTemporalGraph` | 操作与响应序列 | 事故复盘 |

---

### 6. ⚖️ `legal` (法律合规)

专注于权利义务逻辑、条件约束及法律事实。

*   **法学专著与评注**：法律原则、法条逻辑分析。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`LegalConceptOntology`** | `AutoGraph` | 术语定义、上下位关系 | 法律检索 |
| **`CaseLawCitationNet`** | `AutoGraph` | 案件引用关系 | 判例研究 |

*   **主服务协议 (MSA)**：长期商业合同。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`ContractObligationHypergraph`** | `AutoHypergraph` | 主体+义务+条件+例外+责任 | 合同审查 |
| **`DefinedTermRegistry`** | `AutoSet` | 定义的专有名词 | 一致性检查 |
| **`LiabilityClauseList`** | `AutoList` | 赔偿、责任限制条款 | 风险评估 |

*   **法院判决书**：法官最终裁定。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`CaseFactTimeline`** | `AutoTemporalGraph` | 时间顺序的事实链条 | 案情分析 |
| **`AdjudicationLogic`** | `AutoHypergraph` | 事实+法律→结论 | 判决预测 |
| **`LitigationParticipantMap`** | `AutoGraph` | 原告被告律师证人关系 | 利益冲突 |

*   **合规申报文件**：数据合规、反洗钱报告。

| 模板 | 原语 | 描述 | 应用场景 |
| :--- | :--- | :--- | :--- |
| **`ComplianceRequirementList`** | `AutoList` | 具体义务或整改措施 | 合规分析 |
| **`BeneficialOwnershipGraph`** | `AutoGraph` | 股权穿透至UBO | AML/KYC |

---

## 📝 创建自定义模板

用户可以在 `templates/customs/` 目录下创建自己的模板：

```python
# 添加自定义模板目录（自动加载）
Gallery.add_path("/path/to/my/templates")

# 获取自定义模板
config = Gallery.get("MyCustomTemplate")
```
