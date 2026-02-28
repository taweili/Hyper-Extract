"""
Finance 知识模板测试演示

这个文件用于测试 hyperextract 中金融领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_finance_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有金融知识模板
from hyperextract.templates.zh.finance import (
    # SEC 文件 (10-K / 10-Q / 8-K)
    FilingFinancialSnapshot,
    MDANarrativeGraph,
    FilingRiskFactorSet,
    MaterialEventTimeline,
    SegmentPerformanceList,
    FinancialDataTemporalGraph,
    RiskAssessmentGraph,
    SupplyChainGraph,
    # 股票研究报告
    ResearchNoteSummary,
    FinancialForecast,
    ValuationLogicMap,
    FactorInfluenceHypergraph,
    RiskFactorList,
    # 招股说明书 / IPO 文件 (S-1)
    ShareholderStructure,
    ProceedsUsage,
    CompanyHistoryTimeline,
    # 财报电话会议记录
    EarningsCallSummary,
    ManagementGuidanceList,
    DiscussionGraph,
    CallSentimentHypergraph,
    # 金融新闻与市场评论
    MarketSentimentModel,
    FinancialEventCausalGraph,
    MultiSourceSentimentHypergraph,
    MarketNarrativeTimeline,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "fixtures" / "test_samples" / "zh" / "finance"

# 模板到输入文件的映射关系
TEMPLATE_TO_INPUT = {
    # SEC 文件
    FilingFinancialSnapshot: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    MDANarrativeGraph: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    FilingRiskFactorSet: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    MaterialEventTimeline: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    SegmentPerformanceList: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    FinancialDataTemporalGraph: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    RiskAssessmentGraph: TEST_SAMPLES_ROOT / "annual_report_sample.md",
    SupplyChainGraph: TEST_SAMPLES_ROOT / "supply_chain_analysis_sample.md",
    # 股票研究报告
    ResearchNoteSummary: TEST_SAMPLES_ROOT / "equity_research_report_sample.md",
    FinancialForecast: TEST_SAMPLES_ROOT / "equity_research_report_sample.md",
    ValuationLogicMap: TEST_SAMPLES_ROOT / "equity_research_report_sample.md",
    FactorInfluenceHypergraph: TEST_SAMPLES_ROOT / "equity_research_report_sample.md",
    RiskFactorList: TEST_SAMPLES_ROOT / "equity_research_report_sample.md",
    # 招股说明书 / IPO
    ShareholderStructure: TEST_SAMPLES_ROOT / "ipo_prospectus_sample.md",
    ProceedsUsage: TEST_SAMPLES_ROOT / "ipo_prospectus_sample.md",
    CompanyHistoryTimeline: TEST_SAMPLES_ROOT / "ipo_prospectus_sample.md",
    # 财报电话会议
    EarningsCallSummary: TEST_SAMPLES_ROOT / "earnings_call_transcript_sample.md",
    ManagementGuidanceList: TEST_SAMPLES_ROOT / "earnings_call_transcript_sample.md",
    DiscussionGraph: TEST_SAMPLES_ROOT / "earnings_call_transcript_sample.md",
    CallSentimentHypergraph: TEST_SAMPLES_ROOT / "earnings_call_transcript_sample.md",
    # 金融新闻
    MarketSentimentModel: TEST_SAMPLES_ROOT / "financial_news_sample.md",
    FinancialEventCausalGraph: TEST_SAMPLES_ROOT / "financial_news_sample.md",
    MultiSourceSentimentHypergraph: TEST_SAMPLES_ROOT / "financial_news_sample.md",
    MarketNarrativeTimeline: TEST_SAMPLES_ROOT / "financial_news_sample.md",
}

# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# SEC 文件
# TEMPLATE = MDANarrativeGraph  # MD&A 因果图
# TEMPLATE = FilingFinancialSnapshot  # 财务报表快照
# TEMPLATE = FilingRiskFactorSet  # 风险因子集合
# TEMPLATE = MaterialEventTimeline  # 重大事件时间线
# TEMPLATE = SegmentPerformanceList  # 业务分部业绩列表
TEMPLATE = FinancialDataTemporalGraph  # 财务数据时序图
# TEMPLATE = RiskAssessmentGraph  # 风险评估图谱
# TEMPLATE = SupplyChainGraph  # 供应链图谱

# 股票研究报告
# TEMPLATE = ResearchNoteSummary  # 研究报告摘要
# TEMPLATE = FinancialForecast  # 业绩预测
# TEMPLATE = ValuationLogicMap  # 估值逻辑图
# TEMPLATE = FactorInfluenceHypergraph  # 因子影响超图
# TEMPLATE = RiskFactorList  # 风险因子列表

# 招股说明书 / IPO
# TEMPLATE = ShareholderStructure  # 股东结构图
# TEMPLATE = ProceedsUsage  # 募集资金用途
# TEMPLATE = CompanyHistoryTimeline  # 公司历史时间线

# 财报电话会议
# TEMPLATE = EarningsCallSummary  # 财报电话会议摘要
# TEMPLATE = ManagementGuidanceList  # 管理层业绩指引
# TEMPLATE = DiscussionGraph  # 分析师问答图
# TEMPLATE = CallSentimentHypergraph  # 电话会议情绪超图

# 金融新闻
# TEMPLATE = MarketSentimentModel  # 市场情绪模型
# TEMPLATE = FinancialEventCausalGraph  # 金融事件因果图
# TEMPLATE = MultiSourceSentimentHypergraph  # 多源情绪超图
# TEMPLATE = MarketNarrativeTimeline  # 市场叙事时间线

# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("Finance 知识模板测试演示")
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
