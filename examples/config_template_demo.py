"""
YAML配置模板测试演示

这个文件用于测试通过YAML配置文件生成的模板。
测试LifeEventTimeline (temporal_graph) 模板。

使用方法：
1. 运行文件：python examples/config_template_demo.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


TEST_SAMPLES_ROOT = Path(__file__).parent.parent / "tests" / "fixtures" / "test_samples" / "zh" / "general"
INPUT_FILE = TEST_SAMPLES_ROOT / "biography_scientist.md"


def main():
    print("=" * 60)
    print("YAML配置模板测试 - LifeEventTimeline")
    print("=" * 60)

    load_dotenv()

    if not INPUT_FILE.exists():
        print(f"错误：找不到文件 {INPUT_FILE}")
        return

    print(f"\n输入文件: {INPUT_FILE.name}")

    print("\n初始化LLM客户端...")
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        print("LLM客户端初始化成功")
    except Exception as e:
        print(f"LLM客户端初始化失败: {e}")
        return

    print("\n读取文件内容...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"读取成功，共 {len(content)} 字符")

    print("\n加载YAML配置...")
    config = Gallery.get("LifeEventTimeline")
    if not config:
        print("错误：找不到LifeEventTimeline配置")
        return
    print(f"配置加载成功: {config.name}, autotype: {config.autotype}")

    print("\n从配置创建模板...")
    try:
        template = TemplateFactory.create(
            config, 
            llm, 
            embedder,
        )
        print("模板创建成功")
    except Exception as e:
        print(f"模板创建失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n开始知识提取...")
    try:
        template.feed_text(content)
        print("知识提取完成")

        template.build_index()
        print("\n" + "=" * 60)
        print("提取结果展示")
        print("=" * 60)
        template.show()

    except Exception as e:
        print(f"知识提取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
