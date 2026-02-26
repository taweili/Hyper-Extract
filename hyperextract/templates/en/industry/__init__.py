"""
Industry domain templates for extracting structured knowledge from industrial equipment documents.

Includes equipment topology, risk transmission, failure case, maintenance procedures and other graph templates.
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
