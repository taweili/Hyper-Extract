# Hyper-Extract Domain Knowledge Templates

The **Hyper-Extract Domain Templates** library allows you to extract structured knowledge graphs (Temporal, Spatial, Hypergraph, etc.) directly from raw documents.

This library is organized by **Domain**, ensuring that the extraction logic matches the specific vocabulary, document structures, and extraction goals of different industries.

> 切换至 [中文版](./README_ZH.md)

---

## 📋 Table of Contents

- [📚 General](#1-general-general-purpose)
- [💰 Finance](#2-finance-finance)
- [🏥 Medicine](#3-medicine-medicine)
- [🌿 TCM](#4-tcm-traditional-chinese-medicine)
- [⚙️ Industry](#5-industry-industry)
- [📜 History](#6-history-history)
- [🧬 Biology](#7-biology-biology)
- [⚖️ Legal](#8-legal-legal)
- [🎭 Literature](#9-literature-literature--fiction)
- [📰 News](#10-news-news--journalism)
- [🌾 Agriculture](#11-agriculture-agriculture)
- [🍜 Food](#12-food-food)

---

## Primitive Types Overview

| Primitive | Description |
| :--- | :--- |
| **`AutoGraph`** | Knowledge Graph - extracts entities and pairwise relationships |
| **`AutoSet`** | Entity Set - deduplicates and collects unique entities |
| **`AutoList`** | List - extracts arrays of values (keywords, items, etc.) |
| **`AutoModel`** | Data Model - extracts structured data fields (like an infobox) |
| **`AutoTemporalGraph`** | Temporal Graph - builds time-ordered event sequences |
| **`AutoHypergraph`** | Hypergraph - models complex multi-entity relationships |

---

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

## Domain Details

### 1. 📚 `general` (General Purpose)

The default choice for unstructured text that doesn't fit a specific industry.

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

[↑ Back to Top](#table-of-contents)

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

[↑ Back to Top](#table-of-contents)

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

[↑ Back to Top](#table-of-contents)

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

[↑ Back to Top](#table-of-contents)

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

[↑ Back to Top](#table-of-contents)

---

### 6. 📜 `history` (History)

Focuses on long-span timelines and social network reconstruction.

*   **Historical Monographs**: Academic analysis of periods, events, figures.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`HistoricalKnowledgeGraph`** | `AutoGraph` | Kinship, Minister-Ruler, causality | Social network analysis |
| **`MultiParticipantEventMap`** | `AutoHypergraph` | Events as hyperedges connecting participants | Event reconstruction |

*   **Chronicles**: Strictly chronological records.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ChronologicalEventChain`** | `AutoTemporalGraph` | Atomic events with timestamps | Timeline generation |
| **`HistoricalContextGraph`** | `AutoGraph` | Static relationships (kinship, alliances) | Background mining |
| **`PoliticalStruggleHypergraph`** | `AutoHypergraph` | {Attacker, Defender, Planner, Traitor} in battles | Faction analysis |

*   **Oral History**: First-person memoirs with non-linear narratives.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`PersonalTrajectoryHypergraph`** | `AutoHypergraph` | Life stages as {Period, Location, Peers, Experience} | Biography writing |
| **`NarrativeRelationGraph`** | `AutoGraph` | Interpersonal interactions from narrator's view | Social network analysis |
| **`MemoryFlashbackList`** | `AutoList` | Specific anecdotes, feelings, side descriptions | Historical detail |

*   **Archival Correspondence**: Letters revealing hidden social networks.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`EpistolaryKnowledgeGraph`** | `AutoGraph` | Entities and relations within letter content | Historical material mining |

[↑ Back to Top](#table-of-contents)

---

### 7. 🧬 `biology` (Biology)

Beyond genomics: proteomics, metabolism, and ecology.

*   **Biological Monographs**: Species taxonomy, evolutionary history.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SpeciesInteractionWeb`** | `AutoGraph` | Predation, parasitism, competition, symbiosis | Food web analysis |
| **`TaxonomicTree`** | `AutoGraph` | Kingdom → Phylum → ... → Species hierarchy | Taxonomy database |

*   **Protein Structure Summaries**: Crystal structures, binding sites.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ProteinComplexMap`** | `AutoHypergraph` | Multi-subunit assemblies | Complex databases |
| **`BindingSiteModel`** | `AutoModel` | Active site residues, binding pocket chemistry | Drug design |

*   **Metabolic Pathway Descriptions**: Biochemical cascades.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`BiochemicalReactionHypergraph`** | `AutoHypergraph` | Enzyme + Substrate → Product reactions | Pathway mapping |
| **`RegulatoryNetwork`** | `AutoGraph` | TF → Promoter → Gene expression | Gene regulation analysis |

*   **Ecological Surveys**: Species distribution, habitat characteristics.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`PhylogeneticRelationGraph`** | `AutoGraph` | Evolutionary relationships, branching patterns | Phylogenetic trees |
| **`BiodiversityRegistry`** | `AutoSet` | Observed species and populations | Biodiversity assessment |

[↑ Back to Top](#table-of-contents)

---

### 8. ⚖️ `legal` (Legal)

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

[↑ Back to Top](#table-of-contents)

---

### 9. 🎭 `literature` (Literature & Fiction)

Narrative structure, character interactions, world-building.

*   **Screenplays / Scripts**: Highly structured (Scene, Action, Dialogue).

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SceneEventHypergraph`** | `AutoHypergraph` | Scene as {Characters, Location, Props, Actions} | Scene analysis |
| **`CharacterArcTimeline`** | `AutoTemporalGraph` | Character location, emotion, actions over time | Development analysis |

*   **Novels**: Complex plots, numerous characters.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ComplexCharacterRelation`** | `AutoHypergraph` | Multi-party structures (triangles, alliances) | Ensemble analysis |
| **`StoryEntityGraph`** | `AutoGraph` | Items, locations, ownership | World-building DB |
| **`NarrativeEventChain`** | `AutoTemporalGraph` | Key plot points by internal timeline | Synopsis generation |

*   **Literary Criticism**: Themes, motifs, intertextuality.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`MotifAssociationNet`** | `AutoGraph` | Recurring symbols and motifs | Semiotics |
| **`CritiqueArgumentHypergraph`** | `AutoHypergraph` | {Evidence1, Evidence2, Quote} → Thesis | Paper analysis |
| **`NarrativeStructureTree`** | `AutoGraph` | Hierarchical narrative structure | Narratology |

[↑ Back to Top](#table-of-contents)

---

### 10. 📰 `news` (News & Journalism)

Focuses on 5Ws (Who, What, Where, When, Why), event causality, viewpoint analysis.

*   **Investigative Journalism**: Long-form reporting revealing complex truths.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`InvestigativeContextGraph`** | `AutoGraph` | Baseline relationships (employment, kinship) | Entity mapping |
| **`ComplexRelationNet`** | `AutoHypergraph` | Multi-party connections (family, political, business) | Political analysis |
| **`KeyEventSequence`** | `AutoGraph` | Chronological sequence of critical events | Backgrounders |

*   **Breaking News Wires**: Short, factual updates.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`NewsEntityGraph`** | `AutoGraph` | Key entities (people, orgs, locations, events) | News feeds |
| **`NewsSummaryModel`** | `AutoModel` | 5W1H extraction | News aggregation |
| **`LiveUpdateTimeline`** | `AutoGraph` | Minute-by-minute updates | Live blog summary |

*   **Policy Analysis & Editorials**: Opinions, arguments, future impacts.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`ViewpointStructure`** | `AutoHypergraph` | {Claim, Premises, Conclusion} | Opinion mining |
| **`ImpactChain`** | `AutoGraph` | Policy → Affected Groups → Consequences | Policy reviews |

[↑ Back to Top](#table-of-contents)

---

### 11. 🌾 `agriculture` (Agriculture)

Crop lifecycle, field monitoring, soil health.

*   **Agricultural Manuals**: Planting standards, pest control.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`CropGrowthCycle`** | `AutoTemporalGraph` | Farming operations per growth stage | Planting calendar |
| **`PestControlHypergraph`** | `AutoHypergraph` | {Crop, Stage, Factor} → {Target, Agent, Dosage} | Smart crop protection |

*   **Crop Scouting Reports**: Field observations.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`FieldObservationList`** | `AutoList` | {Field ID, Crop, Stage, Issue, Severity, Recommendation} | Pest early warning |

*   **Soil Analysis Reports**: Soil chemistry and fertilization recommendations.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`SoilNutrientModel`** | `AutoModel` | pH, Organic Matter, N-P-K, micronutrients | Fertilizer prescription |
| **`AmendmentPlan`** | `AutoGraph` | Test Result → Limiting Factor → Method → Outcome | Precision agriculture |

[↑ Back to Top](#table-of-contents)

---

### 12. 🍜 `food` (Food)

Recipe standardization, ingredient pairing, food reviews.

*   **Standardized Recipes**: Ingredient lists, cooking steps.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`RecipeCollection`** | `AutoSet` | Unique dish entities and classifications | Menu digitization |
| **`StandardRecipeCard`** | `AutoModel` | Complete ingredients, steps, tips | Kitchen SOP cards |
| **`IngredientCompositionHypergraph`** | `AutoHypergraph` | {Dish, Main, Accessory, Seasoning} relationships | Cost, allergen management |

*   **Food Reviews**: Professional evaluations.

| Template | Primitive | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **`DishReviewSummary`** | `AutoList` | Core points, recommendation level, price | Must-try lists |
| **`SensoryEvaluationGraph`** | `AutoGraph` | Dish → Taste/Texture → Ingredient/Technique | Flavor analysis |

[↑ Back to Top](#table-of-contents)

---
