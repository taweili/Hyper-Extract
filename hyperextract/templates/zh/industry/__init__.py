"""
工业领域模板，用于从工业设备文档中提取结构化知识。

包含设备拓扑、风险传导、故障案例、检修工序等图谱模板。
"""

from .equipment_topology_graph import EquipmentTopologyGraph
from .failure_case_graph import FailureCaseGraph
from .operation_flow_graph import OperationFlowGraph
from .inspection_record_graph import InspectionRecordGraph
from .emergency_response_graph import EmergencyResponseGraph
from .safety_control_graph import SafetyControlGraph
from .system_topology_graph import SystemTopologyGraph
from .operating_mode_graph import OperatingModeGraph

__all__ = [
    "EquipmentTopologyGraph",
    "FailureCaseGraph",
    "OperationFlowGraph",
    "InspectionRecordGraph",
    "EmergencyResponseGraph",
    "SafetyControlGraph",
    "SystemTopologyGraph",
    "OperatingModeGraph",
]
