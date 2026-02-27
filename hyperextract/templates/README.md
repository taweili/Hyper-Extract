# Hyper-Extract Domain Knowledge Templates

The **Hyper-Extract Domain Templates** library allows you to extract structured knowledge graphs (Temporal, Spatial, Hypergraph, etc.) directly from raw documents.

This library is organized by **Domain**, ensuring that the extraction logic matches the specific vocabulary, document structures, and extraction goals of different industries.

## Domain Index

| Domain | Description | Key Focus |
| :--- | :--- | :--- |
| **`general`** | General Purpose | Arbitrary Text, Encyclopedias, Biographies, Regulations |
| **`finance`** | Finance & Investment | Reports, Filings, Transcripts, Earnings Calls, Market News |
| **`medicine`** | Medicine & Health | Clinical Records, Guidelines, Drug Info |
| **`tcm`** | Traditional Chinese Medicine | Case Records, Herbology, Acupuncture |
| **`industry`** | Industry | Maintenance, Safety, Operations |
| **`history`** | History & Culture | Chronicles, Timelines, Archives |
| **`biology`** | Biological Science | Genomics, Proteomics, Ecology |
| **`legal`** | Legal & Compliance | Contracts, Judgments, Regulations |
| **`literature`** | Literature & Fiction | Scripts, Novels, World Building |
| **`news`** | News & Media | Investigative Reports, Breaking News |
| **`agriculture`** | Agriculture | Crop Management, Soil Analysis |
| **`food`** | Food & Culinary | Recipes, Menu Engineering |

---

## Domain Details and Typical Documents

### 1. `general` (General Purpose)
The default choice for unstructured text that doesn't fit a specific industry.

*   **Arbitrary Text (Universal Extraction)**: Any type of text (e.g., web content, notes, blogs) for direct entity and relationship extraction.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`KnowledgeGraph`** | `AutoGraph` | **General Knowledge Graph**. Extracts entities and relations using a broad, universal schema. | Open-domain text, web pages |
| **`EntityRegistry`** | `AutoSet` | **Entity Registry**. Deduplicates and compiles a list of unique entities (People, Organizations). | Entity collection, NER tasks |
| **`KeywordList`** | `AutoList` | **Keyword List**. Extracts core concepts, main topics, or tags from the text. | Content indexing, tagging |

*   **Wikipedia Articles / Encyclopedias**: Comprehensive descriptions of entities with structured infobox-like attributes.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`EncyclopediaItem`** | `AutoModel` | **Encyclopedia Profile**. Extracts a structured profile for a single main entity (infobox style). | Wiki pages, dictionary entries |
| **`ConceptHierarchy`** | `AutoGraph` | **Concept Hierarchy**. Builds a taxonomy graph (Subclass-Of, Part-Of relations). | Scientific wikis, textbook units |
| **`CrossReferenceNet`** | `AutoGraph` | **Cross-Reference Net**. Maps hyperlinks and citations between different concepts. | Inter-article navigation maps |

*   **Biographies & Memoirs**: Life stories of individuals, focusing on key life events and relationships.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`LifeEventTimeline`** | `AutoTemporalGraph` | **Life Timeline**. Extracts life events with timestamps, sorted chronologically. | Biographies, annals, diaries |
| **`SocialNetwork`** | `AutoGraph` | **Social Network**. Specifically captures interpersonal relationships and interactions. | Character studies, memoirs |
| **`PersonalProfile`** | `AutoModel` | **Personal Bio**. Aggregates static personal attributes (birth, education, career tags). | Profiles, CVs, obituary summaries |

*   **Regulations & Compliance**: Internal policies, administrative regulations, SOPs, and compliance guidelines.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`RegulationProfile`** | `AutoModel` | **Policy Snapshot**. Extracts policy name, version, scope, effective date, and core purpose. | Policy overview, version control |
| **`ComplianceLogic`** | `AutoHypergraph` | **Compliance Logic Map**. Models complex "Who, Under what conditions, Must/Must not do What" logic. | Compliance auditing, risk identification |
| **`PenaltyRegistry`** | `AutoSet` | **Violation-Penalty Registry**. Aggregates unique violations and their specific consequences into a ledger. | Risk management, compliance check |
| **`OperationalProcedure`** | `AutoGraph` | **Operational Workflow**. Extracts sequential steps for applications, approvals, or operational procedures. | SOP visualization, process guides |
| **`PenaltyMapping`** | `AutoGraph` | **Enforcement Chain**. Describes the path from violation trigger to handling process and final consequences. | Root cause analysis, penalty logic |
| **`ClauseList`** | `AutoList` | **Atomic Clause List**. Dissects the regulation into individual atomic clauses for quick indexing. | Clause retrieval, document comparison |

### 2. `finance` (Finance)
Optimized for complex financial relationships, market sentiment, and temporal events.

*   **SEC Filings (10-K / 10-Q / 8-K)**: Standardized regulatory filings containing financial statements, management discussion, risk factors, and material event disclosures with complex document structures (tables, narratives, exhibits).

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`FilingFinancialSnapshot`** | `AutoModel` | **Financial Data Extraction**. Extracts key figures from income statements, balance sheets, and cash flow statements embedded in filings. | Fundamental screening, financial database population |
| **`MDANarrativeGraph`** | `AutoGraph` | **MD&A Causal Map**. Extracts causal relationships from Management Discussion & Analysis (e.g., "Supply chain disruption -> Revenue decline -> Margin compression"). | Narrative analytics, driver attribution |
| **`FilingRiskFactorSet`** | `AutoSet` | **Risk Factor Registry**. Deduplicates and catalogs all risk factors disclosed across Item 1A, tracking additions and removals between filing periods. | Risk evolution monitoring, cross-company risk comparison |
| **`MaterialEventTimeline`** | `AutoTemporalGraph` | **8-K Event Timeline**. Chronologically extracts material events (executive changes, M&A announcements, restatements) from current reports. | Event-driven analysis, regulatory monitoring |
| **`SegmentPerformanceList`** | `AutoList` | **Segment Breakdown**. Extracts revenue, operating income, and key metrics by business segment or geographic region. | Segment-level valuation, geographic exposure analysis |
| **`FinancialDataTemporalGraph`** | `AutoTemporalGraph` | **Financial Data Timeline**. Builds a temporal graph of financial metrics across reporting periods, tracking how revenue, margins, segment contributions, and key ratios evolve over time. | Multi-period trend analysis, cross-period comparison, financial data lineage |
| **`RiskAssessmentGraph`** | `AutoGraph` | **Risk Assessment Graph**. Systematically extracts transmission paths from risk factors to financial impacts, including likelihood, severity, and mitigation strategies. | Risk monitoring, cross-filing comparative analysis |
| **`SupplyChainGraph`** | `AutoGraph` | **Supply Chain Graph**. Extracts supply chain entities, transaction relationships, and risk assessments to identify critical suppliers and geopolitical risks. | Supply chain resilience analysis, ESG report analysis |

*   **Equity Research Reports**: Detailed analysis by analysts containing ratings, target prices, and investment logic.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ResearchNoteSummary`** | `AutoModel` | **Research Core**. Extracts ratings (Buy/Sell), target price, and top-level investment logic. | Report database, screening |
| **`FinancialForecast`** | `AutoList` | **Financial Estimates**. Extracts projected data (Revenue, EPS, PE) for future years. | Consensus analysis, modeling |
| **`ValuationLogicMap`** | `AutoGraph` | **Valuation Logic**. Maps causal chains driving stock performance (e.g., New Market -> Growth). | Investment strategy mapping |
| **`FactorInfluenceHypergraph`** | `AutoHypergraph` | **Multi-factor Analysis**. Models complex relationships between macro factors, industry trends, and company metrics. | Quantamental strategy, factor attribution |
| **`RiskFactorList`** | `AutoList` | **Risk Registry**. Lists specific downside risks (Regulatory, FX, Supply Chain). | Risk monitoring, negatives scan |

*   **Prospectuses / IPO Filings (S-1)**: Comprehensive disclosures of company history, shareholder structure, and use of proceeds.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ShareholderStructure`** | `AutoGraph` | **Ownership Graph**. Extracts percentages, controlling paths, and parent-subsidiary relations. | Ultimate controller analysis |
| **`ProceedsUsage`** | `AutoList` | **Fund Usage**. Details project names, allocated amounts, and estimated timelines for proceeds. | Post-IPO monitoring |
| **`CompanyHistoryTimeline`** | `AutoTemporalGraph` | **Corporate Milestones**. Chronological extraction of founding, funding rounds, and major pivots. | Due diligence, history mapping |

*   **Earnings Call Transcripts**: Quarterly conference calls where management presents financial results and answers analyst questions, containing forward-looking guidance and sentiment signals. 

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`EarningsCallSummary`** | `AutoModel` | **Call Overview**. Extracts reported metrics (Revenue, EPS), management guidance, and overall call tone (positive/cautious/negative). | Quarterly review dashboards, consensus tracking |
| **`ManagementGuidanceList`** | `AutoList` | **Forward Guidance**. Extracts forward-looking statements: projected figures, strategic priorities, and qualitative outlook. | Guidance tracking, expectation management |
| **`DiscussionGraph`** | `AutoGraph` | **Earnings Call Discussion Graph**. Extracts entities and their多元 relationships (Q&A, attention, business, financial) from earnings call transcripts. | Analyst focus analysis, Q&A tracking |
| **`CallSentimentHypergraph`** | `AutoHypergraph` | **Topic-Sentiment Analysis**. Models multi-dimensional sentiment: `{Topic (Revenue/Margin/Guidance), Speaker, Sentiment, Driving Factor}` across the call. | Sentiment-driven trading signals, tone shift detection |

*   **Financial News & Market Commentary**: News articles, analyst commentaries, and social media posts conveying market sentiment, event impact, and forward-looking opinions about financial instruments or markets. 

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`MarketSentimentModel`** | `AutoModel` | **Sentiment Snapshot**. Extracts sentiment polarity (Bullish/Bearish/Neutral), mentioned entities (tickers, sectors), and expected price impact. | Real-time sentiment feeds, trading signal generation |
| **`FinancialEventCausalGraph`** | `AutoGraph` | **Event Impact Graph**. Maps financial events to affected entities and downstream market reactions (e.g., "Fed rate hike -> Bank sector rally -> Bond yield rise"). | Event-driven strategy, macro impact analysis |
| **`MultiSourceSentimentHypergraph`** | `AutoHypergraph` | **Cross-Source Sentiment Fusion**. Integrates sentiment signals from multiple sources: `{News Article, Social Media Post, Analyst Note} -> Aggregated Sentiment -> Affected Entity`. | Ensemble sentiment scoring, fake signal filtering |
| **`MarketNarrativeTimeline`** | `AutoTemporalGraph` | **Narrative Evolution Timeline**. Tracks how market narratives and dominant themes evolve over time (e.g., shift from "inflation fear" to "soft landing hope"). | Thematic investing, regime detection |

### 3. `medicine` (Medicine)
Focuses on causality, standardized terminology (UMLS mappings), and precise relationships.

*   **Medical Textbooks & Monographs**: Systematized knowledge of anatomy, pathology, and treatment protocols.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`PathologyHypergraph`** | `AutoHypergraph` | **Pathology Mechanism**. Models complex "Gene + Env + Trigger -> Disease" logic. | Research, clinical knowledge base |
| **`MedicalConceptNet`** | `AutoGraph` | **Medical Concept Net**. Extracts terminology and semantic relations (Is-A, Defined-As). | Taxonomy building, semantic search |
| **`PharmacologyGraph`** | `AutoGraph` | **Pharmacology Action**. Maps interactions between drugs, receptors, and physiological responses. | Drug mechanism analysis |
| **`AnatomyHierarchy`** | `AutoGraph` | **Anatomy Tree**. Builds hierarchical positions (Part-Of) and connectivity. | Anatomy atlases, surgical planning |
| **`SymptomDifferential`** | `AutoSet` | **Differential Table**. Summarizes symptoms and their corresponding differentiator diseases. | Diagnostic support, education |

*   **Clinical Practice Guidelines**: Standardized procedures for treating diseases, defining decision trees.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`TreatmentRegimenMap`** | `AutoHypergraph` | **Therapy Regimen**. Extracts multi-modal treatments comprising Drugs, Therapy, and Lifestyle. | Oncology protocols, chronic care |
| **`ClinicalPathway`** | `AutoGraph` | **Decision Pathway**. Extracts "If-Then-Else" structures for clinical decision trees. | Pathway management, standardization |
| **`LevelOfEvidence`** | `AutoList` | **Evidence Grading**. Extracts recommendations with associated Grade/Level of Evidence. | Clinical QA, research citations |

*   **Discharge Summaries**: Narrative records of a patient's hospital stay.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SurgicalEventGraph`** | `AutoHypergraph` | **Surgical Event**. Models surgery as a complex event involving {Surgeon, Site, Procedure, Tools}. | Quality control, performance audit |
| **`HospitalCourseTimeline`** | `AutoTemporalGraph` | **Hospital Timeline**. Chronologically extracts admission, tests, procedures, and outcomes. | Case review, dispute tracing |
| **`DischargeInstruction`** | `AutoModel` | **Discharge Summary**. Extracts medications, follow-ups, and rehabilitation guidance. | Patient follow-up, management |

*   **Pathology Reports**: Microscopic descriptions of tissue samples.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`TumorStagingItem`** | `AutoModel` | **TNM Staging**. Extracts Tumor size (T), Node (N), Metastasis (M), and Stage. | Tumor registry, prognosis |
| **`MicroscopicFeatureSet`** | `AutoSet` | **Biomarker Registry**. Extracts immunohistochemistry (IHC) results and mutations. | Targeted therapy, research screening |

*   **Drug Package Inserts**: Legal documents listing indications, contraindications, and interactions.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplexInteractionNet`** | `AutoHypergraph` | **Conditional Interaction**. Models high-order "Drug A + B + condition -> Reaction" logic. | CDSS, clinical safety |
| **`ContraindicationList`** | `AutoList` | **Contraindications**. Explicitly lists absolute contraindications (Pregnancy, etc.). | Prescription blocking |
| **`AdverseReactionStats`** | `AutoList` | **Adverse Reaction Stats**. Extracts reactions by system with frequency descriptions. | Pharmacovigilance |

### 4. `tcm` (Traditional Chinese Medicine)
Specialized for the unique logic of syndrome differentiation (`Bian Zheng`) and herbal compatibility.

*   **Medical Case Records (Yi An)**: Clinical records from famous practitioners detailing symptoms, pattern differentiation logic, and the reasoning behind prescribed formulas.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SyndromeReasoningGraph`** | `AutoHypergraph` | **Reasoning Logic Graph**. Models the chain of `{Symptoms} -> Syndrome -> Principle -> {Formula}`. | Mining clinical experience, inheritance of TCM experts |
| **`PrescriptionModification`** | `AutoGraph` | **Formula Modification Logic**. Extracts additions/subtractions to a base formula based on specific symptoms. | Analysis of clinical medication rules |
| **`PulseTongueRecord`** | `AutoList` | **Pulse & Tongue Features**. Structured extraction of tongue body/coating and pulse characteristics. | Objectification of TCM diagnosis |

*   **Herbal Compendiums (Ben Cao)**: Encyclopedic entries for single herbs describing their nature (Qi), flavor, meridian tropism, and functions.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`HerbPropertyModel`** | `AutoModel` | **Herb Properties**. Extracts the Four Natures, Five Flavors, Meridian Tropism, and Toxicity. | TCM Basic Database Construction |
| **`CompatibilityNet`** | `AutoGraph` | **Compatibility Network**. Extracts "Seven Emotions" (Reinforcement, Counteraction, Incompatibility, etc.). | Contraindication warning, formula network analysis |
| **`ProcessingMethod`** | `AutoList` | **Processing Methods (Pao Zhi)**. Lists different processing methods (e.g., Honey-fried) and their effects. | TCM processing standards |

*   **Prescription Formularies (Fang Zhu)**: Documents defining herbal formulas, including the role of each ingredient (Monarch, Minister, Assistant, Envoy).

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`FormulaComposition`** | `AutoHypergraph` | **Structural Composition**. Models the formula as a hierarchy of roles: `{Monarch, Minister, Assistant, Envoy}`. | Formula structure analysis |
| **`FunctionIndicationMap`** | `AutoGraph` | **Function-Indication Map**. Links Formula -> Functions -> Indicated Syndromes/Symptoms. | Formula recommendation systems |

*   **Meridian & Acupoint Treatises**: Texts defining the anatomical location of acupoints and their specific therapeutic effects.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`AcupointLocationMap`** | `AutoGraph` | **Acupoint Spatial Map**. Extracts relative locations based on anatomical landmarks (e.g., "2 cun lateral to navel"). | Acupuncture teaching, Acupoint Atlases |
| **`MeridianFlowGraph`** | `AutoGraph` | **Meridian Flow Graph**. Extracts the pathway and flow sequence of the twelve meridians. | Meridian theory education |

### 5. `industry` (Industry)
Focuses on unstructured operational data in manufacturing, energy, and power sectors.

*   **Management Specifications**: Safety procedures, emergency plans and other management documents.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SafetyControlGraph`** | `AutoGraph` | **Safety Control Graph**. Extracts hazard sources, risk points, and control measures. | Safety procedures |
| **`EmergencyResponseGraph`** | `AutoGraph` | **Emergency Response Graph**. Extracts incident scenarios, response actions, and departments. | Emergency plans |
| **`IncidentCausalityMap`** | `AutoHypergraph` | **Incident Causality**. Models hazard, trigger, violation, consequence. | Risk prevention |
| **`SafetyTimeline`** | `AutoTemporalGraph` | **Incident Timeline**. Reconstructs operations and response sequences. | Accident review |

*   **Technical Specifications / Datasheets**: Semi-structured text describing equipment parameters, design standards, and performance curves.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SystemTopologyGraph`** | `AutoGraph` | **System Topology Graph**. Extracts factory areas, systems, subsystems, equipment hierarchy. | System manuals |
| **`EquipmentTopologyGraph`** | `AutoGraph` | **Equipment Topology Graph**. Extracts equipment entities and connections. | Equipment diagrams |
| **`SpecParameterTable`** | `AutoModel` | **Key Specs Table**. Extracts rated power, materials, tolerances. | Equipment records |
| **`SystemCompatibilityGraph`** | `AutoHypergraph` | **Compatibility Hypergraph**. Extracts device-environment relationships. | Selection assistance |

*   **Operations**: Equipment operating procedures, mode switching, etc.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`OperationFlowGraph`** | `AutoGraph` | **Operation Flow Graph**. Extracts operation steps, states, and expected results. | Operating procedures |
| **`OperatingModeGraph`** | `AutoGraph` | **Operating Mode Graph**. Extracts operating modes and switching conditions. | Mode switching docs |
| **`MaintenaceOperationMap`** | `AutoHypergraph` | **Maintenance Operation Map**. Links operator, tool, object, duration. | SOP standardization |

*   **Maintenance**: Inspection records, failure cases, spare parts replacement.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`InspectionRecordGraph`** | `AutoGraph` | **Inspection Record Graph**. Extracts equipment and inspection items. | Inspection logs |
| **`FailureCaseGraph`** | `AutoGraph` | **Failure Case Graph**. Extracts phenomena, causes, measures, lessons. | Failure case libraries |
| **`FailureKnowledgeHypergraph`** | `AutoHypergraph` | **Failure Hypergraph**. Models phenomena, causes, components, solutions. | Fault diagnosis |
| **`PartReplacementList`** | `AutoList` | **Spare Parts List**. Extracts part numbers, quantities, reasons. | Spare parts management |

*   **HSE Incident Reports**: Investigations into safety incidents, detailing the sequence of events, root causes, and corrective actions.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`IncidentCausalityMap`** | `AutoHypergraph` | **Incident Causality**. Models hazard, trigger, violation, consequence. | Accident simulation |
| **`SafetyTimeline`** | `AutoTemporalGraph` | **Incident Timeline**. Reconstructs operations and response sequences. | Accident review |

### 6. `history` (History)
Focuses on long-span timelines and social network reconstruction.

*   **Historical Monographs**: Academic books analyzing specific periods, events, or figures with causal depth.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`HistoricalKnowledgeGraph`** | `AutoGraph` | **General History Graph**. Extracts basic relationships (Kinship, Minister-Ruler) and causality. | Historical Social Network Analysis |
| **`MultiParticipantEventMap`** | `AutoHypergraph` | **Multi-Participant Event Map**. Models events as hyperedges connecting all participants (e.g., "Feast at Hong Gate"). | Complex event reconstruction |

*   **Chronicles**: Strictly chronological records focusing on temporal evolution.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ChronologicalEventChain`** | `AutoTemporalGraph` | **Event Chain**. Extracts atomic events with precise timestamps. | Timeline generation |
| **`HistoricalContextGraph`** | `AutoGraph` | **Historical Context Graph**. Extracts static relationships (kinship, alliances) underlying the events. | Background mining |
| **`PoliticalStruggleHypergraph`** | `AutoHypergraph` | **Political Struggle Hypergraph**. Models `{Attacker, Defender, Planner, Traitor}` in battles or coups. | Faction analysis, Battle review |

*   **Oral History**: First-person memoirs containing non-linear narratives and personal details.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`PersonalTrajectoryHypergraph`** | `AutoHypergraph` | **Personal Trajectory Hypergraph**. Models life stages as hyperedges: `{Period, Location, Peers, Experience}`. | Biography writing, Life course research |
| **`NarrativeRelationGraph`** | `AutoGraph` | **Narrative Relation Graph**. Extracts interpersonal interactions and evaluations from the narrator's perspective. | Oral history social network analysis |
| **`MemoryFlashbackList`** | `AutoList` | **Memory Flashbacks**. Extracts specific anecdotes, feelings, or side descriptions of historical moments. | Historical detail supplementation |

*   **Archival Correspondence**: Letters between historical figures revealing hidden social networks.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`EpistolaryKnowledgeGraph`** | `AutoGraph` | **Epistolary Content Graph**. Extracts entities and relations mentioned *within* the letter text, rather than just sender/receiver metadata. | Historical material mining |

### 7. `biology` (Biology)
Goes beyond genomics to include proteomics, metabolism, and ecology.

*   **Biological Monographs**: Specialized books detailing species taxonomy, evolutionary history, or complex biological systems.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SpeciesInteractionWeb`** | `AutoGraph` | **Species Interaction Network**. Extracts predation, parasitism, competition, and symbiosis relations. | Food web analysis, Ecosystem modeling |
| **`TaxonomicTree`** | `AutoGraph` | **Taxonomic Tree**. Builds hierarchical relationships (Kingdom -> Phylum -> ... -> Species). | Biological taxonomy database |

*   **Protein Structure Summaries**: Descriptions of protein crystal structures, ligand binding sites, and post-translational modifications.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ProteinComplexMap`** | `AutoHypergraph` | **Protein Complex Hypergraph**. Models multi-subunit assemblies: `{SubunitA, SubunitB, Cofactor}` forming one functional complex. | Complex databases, Structural research |
| **`BindingSiteModel`** | `AutoModel` | **Binding Site Profile**. Extracts active site residues, binding pocket chemistry, and functional annotations. | Drug design, Mutation analysis |

*   **Metabolic Pathway Descriptions**: Texts explaining biochemical cascades, detailing enzymes, substrates, products, and regulation mechanisms.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`BiochemicalReactionHypergraph`** | `AutoHypergraph` | **Reaction Hypergraph**. Precisely models multi-input/output reactions: `{Enzyme + SubstrateA + SubstrateB -> ProductC + ProductD}`. | Pathway mapping, Metabolic engineering |
| **`RegulatoryNetwork`** | `AutoGraph` | **Gene Regulatory Network**. Extracts transcription factor -> promoter -> gene expression relationships (activation, inhibition, cooperation). | Gene regulation analysis, Systems biology |

*   **Ecological Surveys**: Detailed physical characterizations and systematic relationships of organisms, as well as species distribution and habitat characteristics from field surveys.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`PhylogeneticRelationGraph`** | `AutoGraph` | **Phylogenetic Relations**. Extracts evolutionary relationships, divergence distances, and branching patterns. | Molecular systematics, Evolutionary tree building |
| **`BiodiversityRegistry`** | `AutoSet` | **Species Registry**. Deduplicates and consolidates observed species and population information from survey reports. | Biodiversity assessment, Conservation prioritization |

### 8. `legal` (Legal)
Handles precise logical conditions, obligations, and citations.

*   **Legal Treatises / Commentaries**: Scholarly books analyzing legal principles, statutes, and case law logic.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`LegalConceptOntology`** | `AutoGraph` | **Legal Concept Ontology**. Extracts definitions, hierarchical relationships (Is-A), and statutory interpretations from academic texts. | Legal research, Educational systems |
| **`CaseLawCitationNet`** | `AutoGraph` | **Citation Network**. Maps how cases cite, distinguish, or overrule previous precedents. | Precedent analysis, Legal history map |

*   **Master Service Agreements (MSA)**: Contracts defining long-term business relationships, liability limits, and intellectual property rights.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ContractObligationHypergraph`** | `AutoHypergraph` | **Obligation Hypergraph**. Models complex conditional obligations: `{Party, Duty, Trigger Condition, Exception, Penalty}`. | Contract review, Compliance automation |
| **`DefinedTermRegistry`** | `AutoSet` | **Defined Terms Registry**. Deduplicates definitions of capitalized terms (e.g., "Confidential Information") across the document. | Contract consistency check |
| **`LiabilityClauseList`** | `AutoList` | **Liability Clauses**. Extracts specific clauses regarding indemnification, limitations of liability, and warranties. | Risk assessment, Deal comparison |

*   **Court Judgments**: Final rulings by judges, containing fact-finding sections, legal reasoning, and citations of precedents.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`CaseFactTimeline`** | `AutoTemporalGraph` | **Fact Timeline**. Reconstructs the chronological sequence of events leading to the dispute from the "Findings of Fact" section. | Case analysis, Evidence marshalling |
| **`AdjudicationLogic`** | `AutoHypergraph` | **Reasoning Hypergraph**. Models the judicial logic: `{Proven Fact + Applicable Law -> Legal Conclusion}`. | Judgment prediction, Legal reasoning Support |
| **`LitigationParticipantMap`** | `AutoGraph` | **Participant Map**. Maps relationships between plaintiffs, defendants, counsel, and witnesses. | Conflict of interest check |

*   **Regulatory Compliance Filings**: Detailed reports submitted to government bodies regarding data privacy, anti-money laundering, or environmental impact.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplianceRequirementList`** | `AutoList` | **Requirement Checklist**. Extracts specific affirmative duties or negative covenants mandated by the filing. | Regulatory gap analysis |
| **`BeneficialOwnershipGraph`** | `AutoGraph` | **Ownership Structure**. Traces complex corporate ownership layers to identify Ultimate Beneficial Owners (UBO). | AML/KYC screening, Sanctions check |

### 9. `literature` (Literature & Fiction)
Focuses on narrative structure, character interactions, and world-building.

*   **Screenplays / Scripts**: Highly structured texts (Scene Heading, Action, Dialogue) ideal for extracting character interaction graphs.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SceneEventHypergraph`** | `AutoHypergraph` | **Scene Event Hypergraph**. Models a scene as a hyperedge connecting `{Characters, Location, Props, Key Actions}`. | Scene complexity analysis, Shooting schedule planning |
| **`CharacterArcTimeline`** | `AutoTemporalGraph` | **Character Arc Timeline**. Tracks a character's location, emotional state, or key actions chronologically through the script. | Character development analysis, Continuity check |

*   **Novels**: Texts with complex plots, numerous characters, and interwoven relationships.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplexCharacterRelation`** | `AutoHypergraph` | **Complex Character Relation**. Models multi-party social structures (e.g., Love Triangles, Alliances, Factions) beyond simple pairwise links. | Ensemble analysis, Fan wiki consistency |
| **`StoryEntityGraph`** | `AutoGraph` | **Story Entity Graph**. Focuses on key items, locations, and their ownership/location, distinct from character relations. | World-building database, Licensed game adaptation |
| **`NarrativeEventChain`** | `AutoTemporalGraph` | **Narrative Event Chain**. Extracts key plot points strictly following the story's internal timeline. | Synopsis generation, Timeline reconstruction |

*   **Literary Criticism**: Analytical texts exploring themes, motifs, and intertextuality.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`MotifAssociationNet`** | `AutoGraph` | **Motif Association Net**. Links recurring symbols and motifs (nodes are all "Motifs") based on co-occurrence. | Systematic text analysis, Semiotics |
| **`CritiqueArgumentHypergraph`** | `AutoHypergraph` | **Argument Hypergraph**. Models complex argumentation: `{Evidence1, Evidence2, Quoted Text} -> Core Thesis`. | Academic paper analysis, Thesis extraction |
| **`NarrativeStructureTree`** | `AutoGraph` | **Narrative Structure Tree**. Maps the hierarchical structure of the narrative (e.g., Frame Story -> Main Plot -> Subplot). | Narratology, Structure analysis |

### 10. `news` (News & Journalism)
Focuses on the "5Ws" (Who, What, Where, When, Why), event causality, and viewpoint analysis.

*   **Investigative Journalism**: Long-form reporting revealing complex societal relationships or hidden truths.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`InvestigativeContextGraph`** | `AutoGraph` | **Investigation Context Graph**. Extracts baseline static relationships (employment, kinship, location) between all entities mentioned in the report. | Entity mapping, Stakeholder identification |
| **`ComplexRelationNet`** | `AutoHypergraph` | **Complex Relationship Network**. Models multi-party social connections (e.g., family ties, political alliances, business partnerships) involving three or more entities. | Political analysis, feature stories |
| **`KeyEventSequence`** | `AutoGraph` | **Investigative Timeline**. Traces the chronological sequence of critical events discovered during an investigation. | Retrospective reports, backgrounders |

*   **Breaking News Wires**: Short, factual updates focusing on immediate events and entities.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`NewsEntityGraph`** | `AutoGraph` | **Core Entity Graph**. Extracts key entities (people, organizations, locations, products, events, states, etc.) and their actions or relations from news text. | News feeds, entity linking |
| **`NewsSummaryModel`** | `AutoModel` | **Structured Summary**. Standardized extraction of 5W1H elements (Who, What, When, Where, Why, How). | News aggregation, Ticker generation |
| **`LiveUpdateTimeline`** | `AutoGraph` | **Live Event Timeline**. Extracts minute-by-minute updates of an unfolding situation (e.g., press conferences, emergencies). | Live blog summary, Crisis monitoring |

*   **Policy Analysis & Editorials**: Analytical pieces focusing on opinions, arguments, and future impacts.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ViewpointStructure`** | `AutoHypergraph` | **Argument Structure**. Models the logical structure of an editorial: `{Claim, Premises/Evidence, Conclusion}`. | Opinion mining, editorial analysis |
| **`ImpactChain`** | `AutoGraph` | **Policy Impact Chain**. Extracts causal chains predicting how a policy or event affects specific groups or sectors. | Policy reviews, trend analysis |

### 11. `agriculture` (Agriculture)
Focuses on crop lifecycle management, field monitoring, and soil health data.

*   **Agricultural Manuals**: Technical guides on crop planting standards, field management practices, and pest/disease control techniques.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`CropGrowthCycle`** | `AutoTemporalGraph` | **Crop Growth Cycle Timeline**. Extracts key farming operations and environmental conditions required at each growth stage (seeding, tillering, maturation, etc.). | Planting calendar generation, Task scheduling |
| **`PestControlHypergraph`** | `AutoHypergraph` | **Pest Control Logic**. Models complex intervention rules: `{Crop, Growth Stage, Adverse Factor} -> {Target Disease/Pest, Recommended Agent, Dosage, Safe Interval}`. | Smart crop protection systems, Pesticide recommendation |

*   **Crop Scouting Reports**: Field observation records of crop growth stages and pest/disease conditions.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`FieldObservationList`** | `AutoList` | **Field Observation Log**. Structured extraction of scouting records: `{Field ID, Crop, Growth Stage, Observed Issue (Weed/Pest), Severity, Recommendation}`. | Scouting digitization, Pest/disease early warning |

*   **Soil Analysis Reports**: Reports describing soil chemical composition and corresponding fertilization recommendations.

| Template | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`SoilNutrientModel`** | `AutoModel` | **Soil Nutrient Profile**. Extracts core physicochemical indicators (pH, Organic Matter, N-P-K, micronutrients). | Soil-testing-based fertilizer prescription, Soil fertility grading |
| **`AmendmentPlan`** | `AutoGraph` | **Soil Amendment Plan**. Maps the logic: `{Test Result -> Limiting Factor -> Amendment Method -> Target Outcome}`. | Precision agriculture prescription generation |

### 12. `food` (Food)
Focuses on recipe standardization, ingredient pairing logic, and food review data.

*   **Standardized Recipes**: Structured texts containing ingredient lists, cooking steps, and critical control points.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`RecipeCollection`** | `AutoSet` | **Recipe Catalog**. Deduplicates and extracts all unique dish entities and basic classifications from text. | Menu digitization, dish index construction |
| **`StandardRecipeCard`** | `AutoModel` | **Standard Recipe Card**. Extracts complete ingredient list, step-by-step instructions, and key TIPS for a single dish. | Kitchen SOP cards, cooking instruction |
| **`IngredientCompositionHypergraph`** | `AutoHypergraph` | **Ingredient Pairing Hypergraph**. Models the complex combination of `{Dish, Main Ingredient, Accessory, Seasoning}`. | Cost calculation, allergen management, R&D |

*   **Food Reviews**: Detailed evaluation records by professional food critics or R&D teams.

| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`DishReviewSummary`** | `AutoList` | **Dish Review Summary**. Extracts core review points, recommendation level, and price perception by dish. | Structured exploration notes, must-try lists |
| **`SensoryEvaluationGraph`** | `AutoGraph` | **Sensory Evaluation Graph**. Extracts `{Dish} -[has feature]-> {Taste/Texture} -[attributed to]-> {Ingredient/Technique}` evaluation logic. | Flavor attribution analysis, R&D feedback |
