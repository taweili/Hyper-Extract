"""医学领域知识模板"""

from hyperextract.templates.legacy.zh.medicine.pathology_hypergraph import PathologyHypergraph
from hyperextract.templates.legacy.zh.medicine.medical_concept_net import MedicalConceptNet
from hyperextract.templates.legacy.zh.medicine.pharmacology_graph import PharmacologyGraph
from hyperextract.templates.legacy.zh.medicine.anatomy_hierarchy import AnatomyHierarchy
from hyperextract.templates.legacy.zh.medicine.symptom_differential import SymptomDifferential
from hyperextract.templates.legacy.zh.medicine.treatment_regimen_map import TreatmentRegimenMap
from hyperextract.templates.legacy.zh.medicine.clinical_pathway import ClinicalPathway
from hyperextract.templates.legacy.zh.medicine.level_of_evidence import LevelOfEvidence
from hyperextract.templates.legacy.zh.medicine.surgical_event_graph import SurgicalEventGraph
from hyperextract.templates.legacy.zh.medicine.hospital_course_timeline import HospitalCourseTimeline
from hyperextract.templates.legacy.zh.medicine.discharge_instruction import DischargeInstruction
from hyperextract.templates.legacy.zh.medicine.tumor_staging_item import TumorStagingItem
from hyperextract.templates.legacy.zh.medicine.microscopic_feature_set import MicroscopicFeatureSet
from hyperextract.templates.legacy.zh.medicine.complex_interaction_net import ComplexInteractionNet
from hyperextract.templates.legacy.zh.medicine.contraindication_list import ContraindicationList
from hyperextract.templates.legacy.zh.medicine.adverse_reaction_stats import AdverseReactionStats

__all__ = [
    # 医学教科书与专著
    "PathologyHypergraph",
    "MedicalConceptNet",
    "PharmacologyGraph",
    "AnatomyHierarchy",
    "SymptomDifferential",
    # 临床诊疗指南
    "TreatmentRegimenMap",
    "ClinicalPathway",
    "LevelOfEvidence",
    # 出院小结
    "SurgicalEventGraph",
    "HospitalCourseTimeline",
    "DischargeInstruction",
    # 病理报告
    "TumorStagingItem",
    "MicroscopicFeatureSet",
    # 药品说明书
    "ComplexInteractionNet",
    "ContraindicationList",
    "AdverseReactionStats",
]