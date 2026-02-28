"""
Industry 知识模板测试演示

这个文件用于测试 hyperextract 中工业领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_industry_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有工业知识模板
from hyperextract.templates.zh.industry import (
    # 1. 管理规范 (Management Specifications)
    SafetyControlGraph,
    EmergencyResponseGraph,
    # 2. 技术规格书 (Technical Specifications)
    SystemTopologyGraph,
    EquipmentTopologyGraph,
    SpecParameterTable,
    SystemCompatibilityGraph,
    # 3. 操作运维 (Operations)
    OperationFlowGraph,
    OperatingModeGraph,
    MaintenaceOperationMap,
    # 4. 设备维护 (Maintenance)
    InspectionRecordGraph,
    FailureCaseGraph,
    FailureKnowledgeHypergraph,
    PartReplacementList,
    # 5. HSE事故报告 (Incident Reports)
    IncidentCausalityMap,
    SafetyTimeline,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = (
    Path(__file__).parent.parent
    / "tests"
    / "fixtures"
    / "test_samples"
    / "zh"
    / "industry"
)

# 模板到输入文件的映射关系（根据 README 分类顺序）
TEMPLATE_TO_INPUT = {
    # ==========================================
    # 1. 管理规范 (Management Specifications)
    # 安全规程、应急预案等管理性文档
    # ==========================================
    SafetyControlGraph: TEST_SAMPLES_ROOT / "safety_management_handbook.md",
    EmergencyResponseGraph: TEST_SAMPLES_ROOT / "safety_management_handbook.md",
    # ==========================================
    # 2. 技术规格书 (Technical Specifications)
    # 描述设备额定参数、材质标准及性能曲线的半结构化文本
    # ==========================================
    SystemTopologyGraph: TEST_SAMPLES_ROOT / "equipment_technical_manual.md",
    EquipmentTopologyGraph: TEST_SAMPLES_ROOT / "equipment_technical_manual.md",
    SpecParameterTable: TEST_SAMPLES_ROOT / "equipment_technical_manual.md",
    SystemCompatibilityGraph: TEST_SAMPLES_ROOT / "equipment_technical_manual.md",
    # ==========================================
    # 3. 操作运维 (Operations)
    # 设备运行规程、工况切换等操作相关知识
    # ==========================================
    OperationFlowGraph: TEST_SAMPLES_ROOT / "operation_maintenance_manual.md",
    OperatingModeGraph: TEST_SAMPLES_ROOT / "operation_maintenance_manual.md",
    MaintenaceOperationMap: TEST_SAMPLES_ROOT / "operation_maintenance_manual.md",
    # ==========================================
    # 4. 设备维护 (Maintenance)
    # 巡检记录、故障案例、备件更换等维护知识
    # ==========================================
    InspectionRecordGraph: TEST_SAMPLES_ROOT / "equipment_technical_manual.md",
    FailureCaseGraph: TEST_SAMPLES_ROOT / "operation_maintenance_manual.md",
    FailureKnowledgeHypergraph: TEST_SAMPLES_ROOT / "failure_analysis_report.md",
    PartReplacementList: TEST_SAMPLES_ROOT / "failure_analysis_report.md",
    # ==========================================
    # 5. HSE事故报告 (Incident Reports)
    # 对生产事故的调查报告，包含事件时间线、根本原因分析及整改措施
    # ==========================================
    IncidentCausalityMap: TEST_SAMPLES_ROOT / "safety_management_handbook.md",
    SafetyTimeline: TEST_SAMPLES_ROOT / "safety_management_handbook.md",
}


# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# 1. 管理规范 (Management Specifications) - 安全规程、应急预案
# TEMPLATE = SafetyControlGraph      # 安全管控图：提取危险源、风险点和管控措施
# TEMPLATE = EmergencyResponseGraph  # 应急预案图：提取事故场景、响应动作和部门

# 2. 技术规格书 (Technical Specifications) - 设备额定参数、材质标准
# TEMPLATE = SystemTopologyGraph       # 系统拓扑图：提取工厂的厂区、系统、子系统、设备等层级结构
TEMPLATE = EquipmentTopologyGraph   # 设备拓扑图：提取工业设备的实体及其相互连接关系
# TEMPLATE = SpecParameterTable       # 核心规格表：提取额定功率、材质、尺寸精度等关键技术指标
# TEMPLATE = SystemCompatibilityGraph # 系统兼容性超图：提取设备与环境、介质的对应关系

# 3. 操作运维 (Operations) - 设备运行规程、工况切换
# TEMPLATE = OperationFlowGraph      # 操作流程图：提取操作步骤、设备状态和预期结果
# TEMPLATE = OperatingModeGraph      # 工况切换图：提取工况类型和切换条件
# TEMPLATE = MaintenaceOperationMap  # 维修作业图：关联操作人、工具、对象、耗时

# 4. 设备维护 (Maintenance) - 巡检记录、故障案例、备件更换
# TEMPLATE = InspectionRecordGraph      # 巡检记录图：提取设备和巡检项
# TEMPLATE = FailureCaseGraph          # 故障案例图：提取故障现象、原因、措施和教训
# TEMPLATE = FailureKnowledgeHypergraph # 故障知识超图：建模故障现象、根因、部件、解决方案
# TEMPLATE = PartReplacementList        # 备件消耗清单：提取零件型号、数量、原因

# 5. HSE事故报告 (Incident Reports) - 事故调查、原因分析
# TEMPLATE = IncidentCausalityMap  # 事故因果链超图：建模隐患、触发条件、违章行为、事故后果（用于事故推演）
# TEMPLATE = SafetyTimeline        # 事故时序图：还原事故发生前后的操作与响应序列（用于事故复盘）


# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("Industry 知识模板测试演示")
    print("=" * 60)

    # 加载环境变量
    load_dotenv()

    # 验证输入文件是否存在
    if not INPUT_FILE.exists():
        print(f"❌ 错误：找不到文件 {INPUT_FILE}")
        return

    print(f"\n📄 输入文件: {INPUT_FILE.name}")
    print(f"🎯 使用模板: {TEMPLATE.__name__}")

    # 初始化 LLM 客户端
    print("\n🔧 初始化 LLM 客户端...")
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        print("✅ LLM 客户端初始化成功")
    except Exception as e:
        print(f"❌ LLM 客户端初始化失败: {e}")
        print("💡 请确保您已经正确设置了 OPENAI_API_KEY 环境变量")
        return

    # 读取输入文件内容
    print("\n📖 读取文件内容...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ 读取成功，共 {len(content)} 字符")

    # 初始化模板并进行知识提取
    print("\n🧠 开始知识提取...")
    try:
        # 初始化模板
        template = TEMPLATE(
            llm_client=llm,
            embedder=embedder,
            verbose=True,
        )

        # 喂入文本
        template.feed_text(content)
        print("✅ 知识提取完成")

        # 展示结果
        template.build_index()
        print("\n" + "=" * 60)
        print("📊 提取结果展示")
        print("=" * 60)
        template.show()

    except Exception as e:
        print(f"❌ 知识提取失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
