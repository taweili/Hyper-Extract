"""
General 知识模板测试演示

这个文件用于测试 hyperextract 中 general 领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_general_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有 general 知识模板
from hyperextract.templates.zh.general import (
    # 第一波：基础知识提取
    KnowledgeGraph,
    EntityRegistry,
    KeywordList,
    # 第二波：百科条目
    EncyclopediaItem,
    ConceptHierarchy,
    CrossReferenceNet,
    # 第三波：人物传记
    PersonalProfile,
    SocialNetwork,
    LifeEventTimeline,
    # 第四波：规章制度
    RegulationProfile,
    ClauseList,
    PenaltyRegistry,
    OperationalProcedure,
    PenaltyMapping,
    ComplianceLogic,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "fixtures" / "test_samples" / "zh" / "general"

# 模板到输入文件的映射关系（根据 README 中的典型应用场景）
TEMPLATE_TO_INPUT = {
    # 基础知识提取 -> 科技新闻
    KnowledgeGraph: TEST_SAMPLES_ROOT / "arbitrary_tech_news.md",
    EntityRegistry: TEST_SAMPLES_ROOT / "arbitrary_tech_news.md",
    KeywordList: TEST_SAMPLES_ROOT / "arbitrary_tech_news.md",
    # 百科条目 -> 机器学习百科
    EncyclopediaItem: TEST_SAMPLES_ROOT / "encyclopedia_machine_learning.md",
    ConceptHierarchy: TEST_SAMPLES_ROOT / "encyclopedia_machine_learning.md",
    CrossReferenceNet: TEST_SAMPLES_ROOT / "encyclopedia_machine_learning.md",
    # 人物传记 -> 科学家传记
    PersonalProfile: TEST_SAMPLES_ROOT / "biography_scientist.md",
    SocialNetwork: TEST_SAMPLES_ROOT / "biography_scientist.md",
    LifeEventTimeline: TEST_SAMPLES_ROOT / "biography_scientist.md",
    # 规章制度 -> 公司制度
    RegulationProfile: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
    ClauseList: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
    PenaltyRegistry: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
    OperationalProcedure: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
    PenaltyMapping: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
    ComplianceLogic: TEST_SAMPLES_ROOT / "regulation_company_policy.md",
}

# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# 基础知识提取
# TEMPLATE = KnowledgeGraph  # 知识图谱
# TEMPLATE = EntityRegistry  # 实体集合
# TEMPLATE = KeywordList  # 关键词列表

# 百科条目
# TEMPLATE = EncyclopediaItem  # 百科条目
# TEMPLATE = ConceptHierarchy  # 概念层级图
# TEMPLATE = CrossReferenceNet  # 引用网络

# 人物传记
# TEMPLATE = PersonalProfile  # 个人档案
# TEMPLATE = SocialNetwork  # 社会网络
TEMPLATE = LifeEventTimeline  # 生平时序图

# 规章制度
# TEMPLATE = RegulationProfile  # 规章元数据快照
# TEMPLATE = ClauseList  # 规章条文清单
# TEMPLATE = PenaltyRegistry  # 违规处罚对照表
# TEMPLATE = OperationalProcedure  # 执行程序流程图
# TEMPLATE = PenaltyMapping  # 违规处罚因果链
# TEMPLATE = ComplianceLogic  # 合规行为超图

# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("General 知识模板测试演示")
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
