"""
Medical 知识模板测试演示

这个文件用于测试 hyperextract 中医学领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_medicine_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有医学知识模板
from hyperextract.templates.zh.medicine import (
    # 医学教科书与专著
    PathologyHypergraph,
    MedicalConceptNet,
    PharmacologyGraph,
    AnatomyHierarchy,
    SymptomDifferential,
    # 临床诊疗指南
    TreatmentRegimenMap,
    ClinicalPathway,
    LevelOfEvidence,
    # 出院小结
    SurgicalEventGraph,
    HospitalCourseTimeline,
    DischargeInstruction,
    # 病理报告
    TumorStagingItem,
    MicroscopicFeatureSet,
    # 药品说明书
    ComplexInteractionNet,
    ContraindicationList,
    AdverseReactionStats,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "fixtures" / "test_samples" / "zh" / "medicine"

# 模板到输入文件的映射关系（根据 README 中的典型应用场景）
TEMPLATE_TO_INPUT = {
    # 医学教科书与专著 -> 病理学教材
    PathologyHypergraph: TEST_SAMPLES_ROOT / "textbook_sample.md",
    MedicalConceptNet: TEST_SAMPLES_ROOT / "textbook_sample.md",
    PharmacologyGraph: TEST_SAMPLES_ROOT / "textbook_sample.md",
    AnatomyHierarchy: TEST_SAMPLES_ROOT / "textbook_sample.md",
    SymptomDifferential: TEST_SAMPLES_ROOT / "textbook_sample.md",
    # 临床诊疗指南 -> 临床指南
    TreatmentRegimenMap: TEST_SAMPLES_ROOT / "clinical_guideline_sample.md",
    ClinicalPathway: TEST_SAMPLES_ROOT / "clinical_guideline_sample.md",
    LevelOfEvidence: TEST_SAMPLES_ROOT / "clinical_guideline_sample.md",
    # 出院小结 -> 出院小结
    SurgicalEventGraph: TEST_SAMPLES_ROOT / "discharge_summary_sample.md",
    HospitalCourseTimeline: TEST_SAMPLES_ROOT / "discharge_summary_sample.md",
    DischargeInstruction: TEST_SAMPLES_ROOT / "discharge_summary_sample.md",
    # 病理报告 -> 病理报告
    TumorStagingItem: TEST_SAMPLES_ROOT / "pathology_report_sample.md",
    MicroscopicFeatureSet: TEST_SAMPLES_ROOT / "pathology_report_sample.md",
    # 药品说明书 -> 药品说明书
    ComplexInteractionNet: TEST_SAMPLES_ROOT / "package_insert_sample.md",
    ContraindicationList: TEST_SAMPLES_ROOT / "package_insert_sample.md",
    AdverseReactionStats: TEST_SAMPLES_ROOT / "package_insert_sample.md",
}

# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# 医学教科书与专著
# TEMPLATE = PathologyHypergraph  # 多因素病理机制图
# TEMPLATE = MedicalConceptNet  # 医学概念网络
# TEMPLATE = PharmacologyGraph  # 药理机制图
# TEMPLATE = AnatomyHierarchy  # 解剖层级树
# TEMPLATE = SymptomDifferential  # 鉴别诊断表

# 临床诊疗指南
# TEMPLATE = TreatmentRegimenMap  # 综合治疗方案图
# TEMPLATE = ClinicalPathway  # 临床路径图
# TEMPLATE = LevelOfEvidence  # 证据评级表

# 出院小结
# TEMPLATE = SurgicalEventGraph  # 手术事件超图
TEMPLATE = HospitalCourseTimeline  # 住院病程时间轴
# TEMPLATE = DischargeInstruction  # 出院医嘱摘要

# 病理报告
# TEMPLATE = TumorStagingItem  # TNM 分期表
# TEMPLATE = MicroscopicFeatureSet  # 微观特征集

# 药品说明书
# TEMPLATE = ComplexInteractionNet  # 条件性相互作用网
# TEMPLATE = ContraindicationList  # 禁忌症清单
# TEMPLATE = AdverseReactionStats  # 不良反应统计

# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("Medical 知识模板测试演示")
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
            model="gpt-5-mini",
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
