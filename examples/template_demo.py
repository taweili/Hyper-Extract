"""Template API 测试演示

这个文件用于测试 hyperextract 的统一 Template API。

使用方法：
    python examples/template_api_demo.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from hyperextract import Template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# INPUT_FILE = (
#     Path(__file__).parent.parent
#     / "tests"
#     / "test_data"
#     / "templates"
#     / "biography_scientist.md"
# )

INPUT_FILE = (
    Path(__file__).parent.parent
    / "tests"
    / "kg.md"
)

# name = "general/life_event_timeline"
name = "general/knowledge_graph"


def main():

    print(f"\n📄 输入文件: {INPUT_FILE.name}")
    print(f"🎯 使用模板: {name}")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n[1] Template.create() - 通过文件路径创建实例")
    template = Template.create(
        name,
        language="zh",
        llm_client=llm,
        embedder=embedder,
    )
    print(f"创建成功: {type(template).__name__}")

    print("\n[2] 读取输入文件")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"读取成功，共 {len(content)} 字符")

    print("\n[3] template.feed_text() - 喂入文本")
    template.feed_text(content)
    print("✅ 知识提取完成")

    print("\n[4] template.build_index() - 构建索引")
    template.build_index()
    print("✅ 索引构建完成")

    print("\n[5] template.show() - 展示结果")
    template.show()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
