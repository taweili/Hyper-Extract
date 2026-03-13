"""
工业领域模板，用于从工业设备文档中提取结构化知识。

包含管理规范、技术规格书、操作运维、设备维护、事故报告等模板。
"""

# 管理规范
from .safety_control_graph import SafetyControlGraph
from .emergency_response_graph import EmergencyResponseGraph
from .incident_causality_map import IncidentCausalityMap
from .safety_timeline import SafetyTimeline

# 技术规格书
from .system_topology_graph import SystemTopologyGraph
from .equipment_topology_graph import EquipmentTopologyGraph
from .spec_parameter_table import SpecParameterTable
from .system_compatibility_graph import SystemCompatibilityGraph

# 操作运维
from .operation_flow_graph import OperationFlowGraph
from .operating_mode_graph import OperatingModeGraph
from .maintenace_operation_map import MaintenaceOperationMap

# 设备维护
from .inspection_record_graph import InspectionRecordGraph
from .failure_case_graph import FailureCaseGraph
from .failure_knowledge_hypergraph import FailureKnowledgeHypergraph
from .part_replacement_list import PartReplacementList

__all__ = [
    # 管理规范
    "SafetyControlGraph",
    "EmergencyResponseGraph",
    "IncidentCausalityMap",
    "SafetyTimeline",
    # 技术规格书
    "SystemTopologyGraph",
    "EquipmentTopologyGraph",
    "SpecParameterTable",
    "SystemCompatibilityGraph",
    # 操作运维
    "OperationFlowGraph",
    "OperatingModeGraph",
    "MaintenaceOperationMap",
    # 设备维护
    "InspectionRecordGraph",
    "FailureCaseGraph",
    "FailureKnowledgeHypergraph",
    "PartReplacementList",
]
