"""
Life Event Timeline 知识模板测试演示

这个文件用于测试 hyperextract 中 life_event_timeline 知识模板。
使用祖冲之传记作为输入数据，实现提取、问答、搜索和可视化功能。

使用方法：
python examples/life_event_timeline_demo.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

# 导入必要的模块
from hyperextract.utils.template_engine import Template, Gallery
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ==========================================
# 配置
# ==========================================

# 模板文件路径
TEMPLATE_FILE = Path(__file__).parent.parent / "hyperextract" / "templates" / "presets" / "general" / "life_event_timeline.yaml"

# 输入文件路径
INPUT_FILE = Path(__file__).parent.parent / "tests" / "test_data" / "templates" / "biography_scientist.md"


def main():
    """
    主函数：执行知识提取、问答、搜索和可视化流程
    """
    print("=" * 60)
    print("Life Event Timeline 知识模板测试演示")
    print("=" * 60)

    # 加载环境变量
    load_dotenv()

    # 验证文件是否存在
    if not TEMPLATE_FILE.exists():
        print(f"❌ 错误：找不到模板文件 {TEMPLATE_FILE}")
        return
    
    if not INPUT_FILE.exists():
        print(f"❌ 错误：找不到输入文件 {INPUT_FILE}")
        return

    print(f"\n📄 输入文件: {INPUT_FILE.name}")
    print(f"🎯 使用模板: life_event_timeline.yaml")

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
        # 添加自定义模板文件到 Gallery
        Gallery.add(str(TEMPLATE_FILE))
        print("✅ 模板文件添加成功")

        # 从模板名称创建模板实例
        template = Template.create(
            "LifeEventTimeline",
            llm_client=llm,
            embedder=embedder,
            observation_time="2026-03-14"
        )
        print("✅ 模板初始化成功")

        # 喂入文本
        template.feed_text(content)
        print("✅ 知识提取完成")

        # 构建索引
        template.build_index()
        print("✅ 索引构建完成")

        # 展示提取结果
        print("\n" + "=" * 60)
        print("📊 提取结果展示")
        print("=" * 60)
        template.show()

        # 问答功能
        print("\n" + "=" * 60)
        print("❓ 问答功能测试")
        print("=" * 60)
        questions = [
            "祖冲之出生于哪一年？",
            "祖冲之在数学方面有什么成就？",
            "《大明历》是在哪一年编成的？",
            "祖冲之发明了哪些机械装置？",
            "祖冲之去世于哪一年？"
        ]
        
        for question in questions:
            print(f"\n问题: {question}")
            try:
                answer = template.ask(question)
                print(f"回答: {answer}")
            except Exception as e:
                print(f"❌ 问答失败: {e}")

        # 搜索功能
        print("\n" + "=" * 60)
        print("🔍 搜索功能测试")
        print("=" * 60)
        search_queries = [
            "圆周率",
            "大明历",
            "指南车",
            "462年"
        ]
        
        for query in search_queries:
            print(f"\n搜索: {query}")
            try:
                results = template.search(query, k=3)
                print(f"找到 {len(results)} 个结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['content'][:100]}...")
            except Exception as e:
                print(f"❌ 搜索失败: {e}")

        # 可视化功能
        print("\n" + "=" * 60)
        print("📈 可视化功能测试")
        print("=" * 60)
        try:
            # 生成可视化
            visualization = template.visualize()
            print("✅ 可视化生成成功")
            print("\n提示: 可视化结果已保存到临时文件")
        except Exception as e:
            print(f"❌ 可视化失败: {e}")

    except Exception as e:
        print(f"❌ 知识提取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
