"""
Food 知识模板测试演示

这个文件用于测试 hyperextract 美食餐饮领域的所有知识模板。
只需要选择模板，程序会自动匹配对应的输入文件。

使用方法：
1. 选择知识模板（修改 TEMPLATE 变量）
2. 运行文件：python examples/template_food_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入所有美食餐饮知识模板
from hyperextract.templates.zh.food import (
    # 标准化食谱
    RecipeCollection,
    StandardRecipeCard,
    IngredientCompositionHypergraph,
    # 美食评论与感官评价
    DishReviewSummary,
    SensoryEvaluationGraph,
)

# 导入必要的 LLM 客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置：模板与输入文件自动映射
# ==========================================

# 测试文件根目录
TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "fixtures" / "test_samples" / "zh" / "food"

# 模板到输入文件的映射关系（根据 README 中的典型应用场景）
TEMPLATE_TO_INPUT = {
    # 标准化食谱 -> 餐厅菜单
    RecipeCollection: TEST_SAMPLES_ROOT / "restaurant_menu.md",
    # 标准化食谱 -> 标准食谱卡片
    StandardRecipeCard: TEST_SAMPLES_ROOT / "recipe_standard_card.md",
    IngredientCompositionHypergraph: TEST_SAMPLES_ROOT / "recipe_standard_card.md",
    # 美食评论与感官评价 -> 食评文章
    DishReviewSummary: TEST_SAMPLES_ROOT / "food_review_article.md",
    SensoryEvaluationGraph: TEST_SAMPLES_ROOT / "food_review_article.md",
}


# ==========================================
# 选择知识模板（只需要修改这一行）
# ==========================================

# 标准化食谱
# TEMPLATE = RecipeCollection  # 菜谱名录
# TEMPLATE = StandardRecipeCard  # 单品标准食谱
# TEMPLATE = IngredientCompositionHypergraph  # 食材配伍超图

# 美食评论与感官评价
TEMPLATE = DishReviewSummary  # 食评摘要清单
# TEMPLATE = SensoryEvaluationGraph  # 感官评价图谱

# 自动获取对应的输入文件
INPUT_FILE = TEMPLATE_TO_INPUT[TEMPLATE]


def main():
    """
    主函数：执行知识提取和展示流程
    """
    print("=" * 60)
    print("Food 知识模板测试演示")
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
