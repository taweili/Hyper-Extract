"""
法律领域模板，用于从法律文档中提取结构化知识。

包含法学专著、合同文书、法院判决书、合规申报文件等模板。
"""

# 法学专著与评注
from .legal_concept_ontology import LegalConceptOntology
from .case_law_citation_net import CaseLawCitationNet

# 主服务协议
from .contract_obligation_hypergraph import ContractObligationHypergraph
from .defined_term_registry import DefinedTermRegistry
from .liability_clause_list import LiabilityClauseList

# 法院判决书
from .case_fact_timeline import CaseFactTimeline
from .adjudication_logic import AdjudicationLogic
from .litigation_participant_map import LitigationParticipantMap

# 合规申报文件
from .compliance_requirement_list import ComplianceRequirementList
from .beneficial_ownership_graph import BeneficialOwnershipGraph

__all__ = [
    # 法学专著与评注
    "LegalConceptOntology",
    "CaseLawCitationNet",
    # 主服务协议
    "ContractObligationHypergraph",
    "DefinedTermRegistry",
    "LiabilityClauseList",
    # 法院判决书
    "CaseFactTimeline",
    "AdjudicationLogic",
    "LitigationParticipantMap",
    # 合规申报文件
    "ComplianceRequirementList",
    "BeneficialOwnershipGraph",
]
