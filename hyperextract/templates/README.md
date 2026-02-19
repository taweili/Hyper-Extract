# Hyper-Extract Domain Knowledge Templates

The **Hyper-Extract Domain Templates** library allows you to extract structured knowledge graphs (Temporal, Spatial, Hypergraph, etc.) directly from raw documents.

This library is organized by **Domain**, ensuring that the extraction logic matches the specific vocabulary, document structures, and extraction goals of different industries.

## Domain Index

| Domain | Description | Key Focus |
| :--- | :--- | :--- |
| **`general`** | General Purpose | Arbitrary Text, Encyclopedias, Biographies |
| **`finance`** | Finance & Investment | Reports, Filings, Transcripts |
| **`medicine`** | Medicine & Health | Clinical Records, Guidelines, Drug Info |
| **`tcm`** | Traditional Chinese Medicine | Case Records, Herbology, Acupuncture |
| **`industry`** | Industry | Maintenance, Safety, Operations |
| **`history`** | History & Culture | Chronicles, Timelines, Archives |
| **`biology`** | Biological Science | Genomics, Proteomics, Ecology |
| **`legal`** | Legal & Compliance | Contracts, Judgments, Regulations |
| **`literature`** | Literature & Fiction | Scripts, Novels, World Building |
| **`travel`** | Travel & Geography | Itineraries, Guides, Spatial Maps |
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
| **`KnowledgeGraph`** | `AutoGraph` | **General Knowledge Graph**. Extracts entities and SPO relations using a broad, universal schema. | Open-domain text, web pages |
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

*   **Non-fiction Books (Popular Science)**: Books covering broad topics with cross-domain concepts and arguments.
| Template Name | Primitive | Description | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`ArgumentMap`** | `AutoHypergraph` | **Logical Argument Map**. Models complex logic: multiple premises supporting a conclusion. | Philosophical/Scientific books |
| **`ConceptEvolution`** | `AutoTemporalGraph` | **Conceptual History**. Tracks how a specific idea or term evolves throughout a text. | History of ideas, evolving concepts |

### 2. `finance` (Finance)
Optimized for complex financial relationships, market sentiment, and temporal events.
*   **Equity Research Reports**: Detailed analysis by analysts containing ratings (Buy/Sell), target prices, valuation logic, and risk factors.
*   **Earnings Call Transcripts**: Dialogue between management and analysts, rich in non-structured performance attribution and strategic outlook.
*   **Prospectuses / IPO Filings (S-1)**: Comprehensive disclosures of company history, shareholder structure, and use of proceeds prior to listing.
*   **M&A Due Diligence Reports**: Documents detailing legal risks, business synergies, and financial health of target companies.

### 3. `medicine` (Medicine)
Focuses on causality, standardized terminology (UMLS mappings), and precise relationships.
*   **Medical Textbooks & Monographs**: Systematized knowledge of anatomy, pathology, and treatment protocols (e.g., "Principles of Neural Science").
*   **Clinical Practice Guidelines**: Standardized procedures for treating diseases, defining "Symptom -> Diagnosis -> Treatment" decision trees.
*   **Discharge Summaries**: Narrative records of a patient's hospital stay, including admission reason, hospital course, and discharge instructions.
*   **Pathology Reports**: Microscopic descriptions of tissue samples, detailing tumor grades, invasion depths, and histological features.
*   **Drug Package Inserts**: Legal documents listing indications, contraindications, dosage, and adverse reactions.

### 4. `tcm` (Traditional Chinese Medicine)
Specialized for the unique logic of syndrome differentiation (`Bian Zheng`) and herbal compatibility.
*   **Medical Case Records (Yi An)**: Clinical records from famous practitioners detailing symptoms, pattern differentiation logic, and the reasoning behind prescribed formulas.
*   **Herbal Compendiums (Ben Cao)**: Encyclopedic entries for single herbs describing their nature (Qi), flavor, meridian tropism, and functions.
*   **Prescription Formularies (Fang Zhu)**: Documents defining herbal formulas, including the role of each ingredient (Monarch, Minister, Assistant, Envoy).
*   **Meridian & Acupoint Treatises**: Texts defining the anatomical location of acupoints and their specific therapeutic effects.

### 5. `industry` (Industry)
Focuses on unstructured operational data in manufacturing, energy, and power sectors.
*   **Maintenance Logs & Work Orders**: Field records of equipment failures, repair actions taken, and parts replaced. often containing jargon and abbreviations.
*   **HSE Incident Reports**: Investigations into safety incidents, detailing the sequence of events, root causes, and corrective actions.
*   **Shift Handover Logs**: Summaries written by operators regarding equipment status changes, anomalies, and ongoing issues.
*   **Technical Specifications / Datasheets**: Semi-structured text describing equipment parameters, design standards, and performance curves.

### 6. `history` (History)
Heavily focused on long-span timelines and social networks.
*   **Historical Monographs**: Academic books analyzing specific eras, events, or figures with rich causal analysis and citations.
*   **Chronicles & Annals**: Year-by-year records of events, focusing on temporal sequencing and regime changes.
*   **Oral History Transcripts**: First-person narratives, often non-linear and focused on personal experiences within historical events.
*   **Archival Correspondence**: Personal exchanges revealing social networks, hidden intents, and dates of specific interactions.

### 7. `biology` (Biology)
Goes beyond genomics to include proteomics, metabolism, and ecology.
*   **Biological Monographs**: Specialized books detailing species taxonomy, evolutionary history, or complex biological systems.
*   **Protein Structure Summaries (PDB Headers)**: Descriptions of protein crystal structures, ligand binding sites, and post-translational modifications.
*   **Metabolic Pathway Descriptions**: Texts explaining biochemical cascades, detailing enzymes, substrates, products, and regulation mechanisms.
*   **Ecological Survey Reports**: Documents recording species distribution, abundance, and habitat characteristics in specific geographic areas.
*   **Taxonomic Descriptions**: Detailed physical characterizations of organisms used for classification and identification.

### 8. `legal` (Legal)
Handles precise logical conditions, obligations, and citations.
*   **Legal Treatises / Commentaries**: Scholarly books analyzing legal principles, statutes, and case law logic.
*   **Master Service Agreements (MSA)**: Contracts defining long-term business relationships, liability limits, and intellectual property rights.
*   **Court Judgments**: Final rulings by judges, containing fact-finding sections, legal reasoning, and citations of precedents.
*   **Regulatory Compliance Filings**: Detailed reports submitted to government bodies regarding data privacy, anti-money laundering, or environmental impact.

### 9. `literature` (Literature & Fiction)
Focuses on narrative structure, character interactions, and world-building.
*   **Screenplays / Scripts**: Highly structured texts (Scene Heading, Action, Dialogue) ideal for extracting character interaction graphs.
*   **Character Bibles**: Internal documents describing character backstories, personality traits, and relationships.
*   **Literary Criticism**: Analytical texts exploring themes, motifs, and intertextuality.

### 10. `travel` (Travel)
Focuses on spatial relationships and temporal sequences.
*   **Travel Itineraries**: Sequential plans including times, locations (POIs), transport modes, and accommodation.
*   **Destination Guides**: Comprehensive descriptions of places, including top logical relations (Next To, Inside) and cultural tips.

### 11. `news` (News)
Focuses on the "5Ws" (Who, What, Where, When, Why) and causality.
*   **Investigative Features**: Long-form reporting revealing complex causal chains and multi-party stakeholder relationships.
*   **Breaking News Wires**: Short, factual updates focusing on immediate events and entities.

### 12. `agriculture` (Agriculture)
*   **Agricultural Manuals**: Technical guides on crop management, planting standards, and pest control techniques.
*   **Crop Scouting Reports**: Observations of crop growth stages, pest identification, and disease severity.
*   **Soil Analysis Reports**: Textual descriptions of soil chemical properties and corresponding fertilizer recommendations.

### 13. `food` (Food)
*   **Standardized Recipes**: Step-by-step instructions including ingredients, preparation methods, and critical control points.
*   **Menu Engineering Reports**: Analysis of dishes involving flavor profiles, ingredients, and customer preferences.
