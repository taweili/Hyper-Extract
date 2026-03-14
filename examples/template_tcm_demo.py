"""
TCM 知识模板测试演示

这个文件用于测试 hyperextract 中医领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_tcm_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有中医知识模板
from hyperextract.templates.legacy.zh.tcm import (
    # 本草典籍
    HerbPropertyModel,
    ProcessingMethod,
    CompatibilityNet,
    # 方剂规范
    FormulaComposition,
    FunctionIndicationMap,
    # 经络腧穴专著
    MeridianFlowGraph,
    AcupointLocationMap,
    # 名医医案
    SyndromeReasoningGraph,
    PrescriptionModification,
    PulseTongueRecord,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "test_data" / "test_samples" / "zh" / "tcm"

# 模板到输入文件的映射关系（根据 README 中的典型应用场景）
TEMPLATE_TO_INPUT = {
    # 本草典籍 -> 多味药 / 单味药
    HerbPropertyModel: TEST_SAMPLES_ROOT / "herb_property_single.md", 
    ProcessingMethod: TEST_SAMPLES_ROOT / "herbal_compendium_sample.md",
    CompatibilityNet: TEST_SAMPLES_ROOT / "herbal_compendium_sample.md",
    # 方剂规范 -> 伤寒论
    FormulaComposition: TEST_SAMPLES_ROOT / "prescription_formulary_sample.md",
    FunctionIndicationMap: TEST_SAMPLES_ROOT / "prescription_formulary_sample.md",
    # 经络腧穴专著 -> 黄帝内经十二经脉
    MeridianFlowGraph: TEST_SAMPLES_ROOT / "meridian_treatise_sample.md",
    AcupointLocationMap: TEST_SAMPLES_ROOT / "meridian_treatise_sample.md",
    # 名医医案
    SyndromeReasoningGraph: TEST_SAMPLES_ROOT / "medical_case_record_sample.md",
    PrescriptionModification: TEST_SAMPLES_ROOT / "prescription_modification_sample.md",
    PulseTongueRecord: TEST_SAMPLES_ROOT / "medical_case_record_sample.md",
}

# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# 本草典籍
# TEMPLATE = HerbPropertyModel  # 药物性味归经
# TEMPLATE = ProcessingMethod  # 炮制方法列表
# TEMPLATE = CompatibilityNet  # 七情配伍网络

# 方剂规范
# TEMPLATE = FormulaComposition  # 君臣佐使结构图
TEMPLATE = FunctionIndicationMap  # 主治功效映射

# 经络腧穴专著
# TEMPLATE = MeridianFlowGraph  # 经络流注图
# TEMPLATE = AcupointLocationMap  # 腧穴空间定位

# 名医医案
# TEMPLATE = SyndromeReasoningGraph  # 辨证论治逻辑图
# TEMPLATE = PrescriptionModification  # 处方加减逻辑
# TEMPLATE = PulseTongueRecord  # 舌脉特征提取

# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("TCM 知识模板测试演示")
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
