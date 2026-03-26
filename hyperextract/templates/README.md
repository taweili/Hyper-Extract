# Hyper-Extract Core Domain Templates

The **Hyper-Extract Domain Templates** library provides structured knowledge graph extraction from raw documents.

> 切换至 [中文版](./README_ZH.md)

---

## 📁 Directory Structure

```
templates/
├── presets/              # Domain templates (6 core domains)
│   ├── finance/         # Finance & Investment
│   ├── general/         # General Purpose
│   ├── industry/        # Industry & Manufacturing
│   ├── legal/           # Legal & Compliance
│   ├── medicine/        # Medicine & Healthcare
│   └── tcm/            # Traditional Chinese Medicine
├── customs/              # Custom templates (user-created)
└── README.md
```

---

## 🚀 Quick Start

### Using YAML Config (Recommended)

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

# Get template
config = Gallery.get("KnowledgeGraph")

# Create template
template = TemplateFactory.create(config, llm, embedder)
result = template.parse("Your text here...")

# List all available templates
print(Gallery.list_all())
```

---

## 📋 Domain Index

| Domain | Description | Key Focus |
| :--- | :--- | :--- |
| **`general`** | General Purpose | Arbitrary text, encyclopedias, biographies, regulations |
| **`finance`** | Finance & Investment | Reports, filings, transcripts, earnings calls |
| **`medicine`** | Medicine & Healthcare | Clinical records, guidelines, drug information |
| **`tcm`** | Traditional Chinese Medicine | Case records, herbology, acupuncture |
| **`industry`** | Industry & Manufacturing | Maintenance, safety, operations |
| **`legal`** | Legal & Compliance | Contracts, judgments, regulations |

---

## 🔧 Primitive Types

| Primitive | Description |
| :--- | :--- |
| **`AutoGraph`** | Knowledge Graph - extracts entities and pairwise relationships |
| **`AutoSet`** | Entity Set - deduplicates and collects unique entities |
| **`AutoList`** | List - extracts arrays of values (keywords, items, etc.) |
| **`AutoModel`** | Data Model - extracts structured data fields (like an infobox) |
| **`AutoTemporalGraph`** | Temporal Graph - builds time-ordered event sequences |
| **`AutoHypergraph`** | Hypergraph - models complex multi-entity relationships |

---

## 📚 Domain Details

### 1. 📚 `general` (General Purpose)

The default choice for unstructured text that doesn't fit a specific industry.

*   **Base Templates**: General-purpose knowledge extraction templates covering all AutoType primitives. Use these as building blocks or extend them for domain-specific needs.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`BaseModel`** | `AutoModel` | General-purpose structured object extraction | Universal single-object extraction |
| **`BaseList`** | `AutoList` | General-purpose ordered list extraction | Universal list extraction |
| **`BaseSet`** | `AutoSet` | General-purpose entity deduplication | Universal entity collection |
| **`BaseGraph`** | `AutoGraph` | General-purpose knowledge graph extraction | Universal binary relation extraction |
| **`BaseHypergraph`** | `AutoHypergraph` | General-purpose hypergraph extraction | Universal multi-entity relation extraction |
| **`BaseTemporalGraph`** | `AutoTemporalGraph` | General-purpose temporal graph extraction | Universal time-ordered relation extraction |
| **`BaseSpatialGraph`** | `AutoSpatialGraph` | General-purpose spatial graph extraction | Universal location-aware relation extraction |
| **`BaseSpatioTemporalGraph`** | `AutoSpatioTemporalGraph` | General-purpose spatio-temporal graph extraction | Universal time & location relation extraction |

*   **Arbitrary Text (Universal Extraction)**: Any type of text for direct entity and relationship extraction.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`KnowledgeGraph`** | `AutoGraph` | General-purpose knowledge graph extraction | Open-domain text, web pages |
| **`EntityRegistry`** | `AutoSet` | Deduplicates unique entities (People, Orgs) | Entity collection, NER tasks |
| **`KeywordList`** | `AutoList` | Core concepts, topics, or tags | Content indexing, tagging |

*   **Wikipedia / Encyclopedias**: Comprehensive entity descriptions with structured attributes.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`EncyclopediaItem`** | `AutoModel` | Structured profile (infobox style) | Wiki pages, dictionaries |
| **`ConceptHierarchy`** | `AutoGraph` | Taxonomy: Subclass-Of, Part-Of relations | Scientific wikis, textbooks |
| **`CrossReferenceNet`** | `AutoGraph` | Hyperlinks and citations between concepts | Navigation maps |

*   **Biographies & Memoirs**: Life stories focusing on key events and relationships.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`LifeEventTimeline`** | `AutoTemporalGraph` | Chronological life events with timestamps | Biographies, diaries |
| **`SocialNetwork`** | `AutoGraph` | Interpersonal relationships and interactions | Character studies |
| **`PersonalProfile`** | `AutoModel` | Static attributes (birth, education, career) | Profiles, CVs |

*   **Regulations & Compliance**: Policies, SOPs, and compliance guidelines.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`RegulationProfile`** | `AutoModel` | Policy name, version, scope, effective date | Policy overview, version control |
| **`ComplianceLogic`** | `AutoHypergraph` | Complex "Who + Condition → Must/Must Not Do What" | Compliance auditing |
| **`PenaltyRegistry`** | `AutoSet` | Unique violations and consequences | Risk management |
| **`OperationalProcedure`** | `AutoGraph` | Sequential steps for applications/approvals | SOP visualization |
| **`PenaltyMapping`** | `AutoGraph` | Violation → Process → Consequence chain | Root cause analysis |
| **`ClauseList`** | `AutoList` | Atomic clauses for quick indexing | Clause retrieval |

---

### 2. 💰 `finance` (Finance)

Optimized for complex financial relationships, market sentiment, and temporal events.

*   **SEC Filings (10-K / 10-Q / 8-K)**: Standardized regulatory filings with financial statements, MD&A, risk factors.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`FilingFinancialSnapshot`** | `AutoModel` | Key figures from financial statements | Fundamental screening |
| **`MDANarrativeGraph`** | `AutoGraph` | Causal relationships from MD&A | Narrative analytics |
| **`FilingRiskFactorSet`** | `AutoSet` | Risk factors from Item 1A | Risk monitoring |
| **`MaterialEventTimeline`** | `AutoTemporalGraph` | Material events from 8-K reports | Event-driven analysis |
| **`SegmentPerformanceList`** | `AutoList` | Revenue, income by segment/region | Segment valuation |
| **`FinancialDataTemporalGraph`** | `AutoTemporalGraph` | Financial metrics across reporting periods | Trend analysis |
| **`RiskAssessmentGraph`** | `AutoGraph` | Risk factor → Financial impact paths | Risk monitoring |
| **`SupplyChainGraph`** | `AutoGraph` | Supply chain entities and risks | ESG analysis |

*   **Equity Research Reports**: Analyst reports with ratings, target prices, investment logic.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ResearchNoteSummary`** | `AutoModel` | Ratings, target price, investment logic | Report database |
| **`FinancialForecast`** | `AutoList` | Projected Revenue, EPS, PE | Consensus analysis |
| **`ValuationLogicMap`** | `AutoGraph` | Causal chains for stock performance | Strategy mapping |
| **`FactorInfluenceHypergraph`** | `AutoHypergraph` | Macro → Industry → Company relationships | Factor attribution |
| **`RiskFactorList`** | `AutoList` | Downside risks | Risk monitoring |

*   **Prospectuses / IPO (S-1)**: Company history, shareholder structure, use of proceeds.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ShareholderStructure`** | `AutoGraph` | Ownership percentages, controlling paths | Due diligence |
| **`ProceedsUsage`** | `AutoList` | Project names, amounts, timelines | Post-IPO monitoring |
| **`CompanyHistoryTimeline`** | `AutoTemporalGraph` | Founding, funding, pivots | History mapping |

*   **Earnings Call Transcripts**: Quarterly conference calls with financial results and guidance.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`EarningsCallSummary`** | `AutoModel` | Metrics, guidance, call tone | Quarterly review |
| **`ManagementGuidanceList`** | `AutoList` | Forward-looking statements | Guidance tracking |
| **`DiscussionGraph`** | `AutoGraph` | Entity relationships in Q&A | Analyst focus analysis |
| **`CallSentimentHypergraph`** | `AutoHypergraph` | Multi-dimensional sentiment analysis | Trading signals |

*   **Financial News & Market Commentary**: News articles and market commentary.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`MarketSentimentModel`** | `AutoModel` | Sentiment polarity, entities, price impact | Trading signals |
| **`FinancialEventCausalGraph`** | `AutoGraph` | Event → Entity → Market reaction | Strategy analysis |
| **`MultiSourceSentimentHypergraph`** | `AutoHypergraph` | Cross-source sentiment fusion | Ensemble scoring |
| **`MarketNarrativeTimeline`** | `AutoTemporalGraph` | Narrative evolution over time | Thematic investing |

---

### 3. 🏥 `medicine` (Medicine)

Focuses on causality, standardized terminology (UMLS), and precise relationships.

*   **Medical Textbooks**: Anatomy, pathology, treatment protocols.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`PathologyHypergraph`** | `AutoHypergraph` | Gene + Env + Trigger → Disease | Research KB |
| **`MedicalConceptNet`** | `AutoGraph` | Medical terms and semantic relations | Taxonomy building |
| **`PharmacologyGraph`** | `AutoGraph` | Drug-receptor-physiology interactions | Drug mechanism analysis |
| **`AnatomyHierarchy`** | `AutoGraph` | Hierarchical anatomy positions | Surgical planning |
| **`SymptomDifferential`** | `AutoSet` | Symptoms → Differential diseases | Diagnostic support |

*   **Clinical Practice Guidelines**: Standardized treatment decision trees.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`TreatmentRegimenMap`** | `AutoHypergraph` | Multi-modal treatments | Oncology protocols |
| **`ClinicalPathway`** | `AutoGraph` | If-Then-Else clinical decisions | Pathway management |
| **`LevelOfEvidence`** | `AutoList` | Recommendations with evidence grades | Clinical QA |

*   **Discharge Summaries**: Patient hospital stay narratives.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SurgicalEventGraph`** | `AutoHypergraph` | Surgery as {Surgeon, Site, Procedure, Tools} | Quality control |
| **`HospitalCourseTimeline`** | `AutoTemporalGraph` | Admission → Tests → Procedures → Outcomes | Case review |
| **`DischargeInstruction`** | `AutoModel` | Medications, follow-ups, rehabilitation | Patient management |

*   **Pathology Reports**: Microscopic tissue descriptions.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`TumorStagingItem`** | `AutoModel` | TNM staging (T, N, M, Stage) | Tumor registry |
| **`MicroscopicFeatureSet`** | `AutoSet` | IHC results and mutations | Targeted therapy |

*   **Drug Package Inserts**: Indications, contraindications, interactions.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplexInteractionNet`** | `AutoHypergraph` | Drug A + B + condition → Reaction | CDSS |
| **`ContraindicationList`** | `AutoList` | Absolute contraindications | Prescription blocking |
| **`AdverseReactionStats`** | `AutoList` | Reactions by system with frequency | Pharmacovigilance |

---

### 4. 🌿 `tcm` (Traditional Chinese Medicine)

Specialized for syndrome differentiation (`Bian Zheng`) and herbal compatibility.

*   **Medical Case Records (Yi An)**: Clinical records with symptoms, pattern differentiation, and formulas.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SyndromeReasoningGraph`** | `AutoHypergraph` | Symptoms → Syndrome → Principle → Formula | Experience mining |
| **`PrescriptionModification`** | `AutoGraph` | Base formula modifications by symptoms | Clinical rules analysis |
| **`PulseTongueRecord`** | `AutoList` | Tongue and pulse characteristics | Diagnosis objectification |

*   **Herbal Compendiums (Ben Cao)**: Herb properties, flavors, meridian tropism.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`HerbPropertyModel`** | `AutoModel` | Four Natures, Five Flavors, Toxicity | TCM database |
| **`CompatibilityNet`** | `AutoGraph` | Seven Emotions relationships | Contraindication warning |
| **`ProcessingMethod`** | `AutoList` | Processing methods and effects | Processing standards |

*   **Prescription Formularies (Fang Zhu)**: Formula composition with Monarch/Minister/Assistant/Envoy roles.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`FormulaComposition`** | `AutoHypergraph` | Formula hierarchy (Monarch, Minister, Assistant, Envoy) | Structure analysis |
| **`FunctionIndicationMap`** | `AutoGraph` | Formula → Functions → Indications | Recommendation systems |

*   **Meridian & Acupoint Treatises**: Acupoint locations and therapeutic effects.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`AcupointLocationMap`** | `AutoGraph` | Acupoint spatial relationships | Acupuncture teaching |
| **`MeridianFlowGraph`** | `AutoGraph` | Twelve meridian pathways | Meridian theory |

---

### 5. ⚙️ `industry` (Industry)

Focuses on operational data in manufacturing, energy, and power sectors.

*   **Management Specifications**: Safety procedures, emergency plans.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SafetyControlGraph`** | `AutoGraph` | Hazard sources, risk points, controls | Safety procedures |
| **`EmergencyResponseGraph`** | `AutoGraph` | Incident scenarios, response actions | Emergency plans |
| **`IncidentCausalityMap`** | `AutoHypergraph` | Hazard → Trigger → Violation → Consequence | Risk prevention |
| **`SafetyTimeline`** | `AutoTemporalGraph` | Operations and response sequences | Accident review |

*   **Technical Specifications / Datasheets**: Equipment parameters, design standards.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SystemTopologyGraph`** | `AutoGraph` | Factory areas, systems, equipment hierarchy | System manuals |
| **`EquipmentTopologyGraph`** | `AutoGraph` | Equipment entities and connections | Equipment diagrams |
| **`SpecParameterTable`** | `AutoModel` | Rated power, materials, tolerances | Equipment records |
| **`SystemCompatibilityGraph`** | `AutoHypergraph` | Device-environment relationships | Selection assistance |

*   **Operations**: Operating procedures, mode switching.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`OperationFlowGraph`** | `AutoGraph` | Operation steps, states, results | Operating procedures |
| **`OperatingModeGraph`** | `AutoGraph` | Operating modes and switching conditions | Mode switching |
| **`MaintenaceOperationMap`** | `AutoHypergraph` | Operator, tool, object, duration | SOP standardization |

*   **Maintenance**: Inspection records, failure cases, spare parts.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`InspectionRecordGraph`** | `AutoGraph` | Equipment and inspection items | Inspection logs |
| **`FailureCaseGraph`** | `AutoGraph` | Phenomena, causes, measures, lessons | Failure case libraries |
| **`FailureKnowledgeHypergraph`** | `AutoHypergraph` | Phenomena, causes, components, solutions | Fault diagnosis |
| **`PartReplacementList`** | `AutoList` | Part numbers, quantities, reasons | Spare parts management |

*   **HSE Incident Reports**: Safety incident investigations.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`IncidentCausalityMap`** | `AutoHypergraph` | Hazard, trigger, violation, consequence | Accident simulation |
| **`SafetyTimeline`** | `AutoTemporalGraph` | Operations and response sequences | Accident review |

---

### 6. ⚖️ `legal` (Legal)

Precise logical conditions, obligations, and citations.

*   **Legal Treatises**: Analysis of legal principles and case law.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`LegalConceptOntology`** | `AutoGraph` | Definitions, Is-A relations, interpretations | Legal research |
| **`CaseLawCitationNet`** | `AutoGraph` | Case citations, distinguish, overrule | Precedent analysis |

*   **Master Service Agreements (MSA)**: Long-term contracts, liability, IP rights.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ContractObligationHypergraph`** | `AutoHypergraph` | {Party, Duty, Trigger, Exception, Penalty} | Contract review |
| **`DefinedTermRegistry`** | `AutoSet` | Defined capitalized terms | Consistency check |
| **`LiabilityClauseList`** | `AutoList` | Indemnification, limitations, warranties | Risk assessment |

*   **Court Judgments**: Rulings with fact-finding and reasoning.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`CaseFactTimeline`** | `AutoTemporalGraph` | Chronological sequence of events | Case analysis |
| **`AdjudicationLogic`** | `AutoHypergraph` | {Proven Fact + Law → Conclusion} | Judgment prediction |
| **`LitigationParticipantMap`** | `AutoGraph` | Plaintiff, defendant, counsel, witness relations | Conflict check |

*   **Regulatory Compliance Filings**: Data privacy, AML, environmental reports.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplianceRequirementList`** | `AutoList` | Specific affirmative/negative duties | Gap analysis |
| **`BeneficialOwnershipGraph`** | `AutoGraph` | Corporate ownership layers to UBO | AML/KYC screening |

---

## 📝 Creating Custom Templates

Users can create their own templates in `templates/customs/`:

```python
# Add custom template directory (auto-loaded)
Gallery.add_path("/path/to/my/templates")

# Get custom template
config = Gallery.get("MyCustomTemplate")
```
