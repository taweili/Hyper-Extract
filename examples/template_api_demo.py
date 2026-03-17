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

from hyperextract.utils.template_engine import Template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings


INPUT_FILE = Path(__file__).parent.parent / "tests" / "test_data" / "templates" / "biography_scientist.md"


def main():
    print("=" * 60)
    print("Template API 测试")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"❌ 找不到输入文件: {INPUT_FILE}")
        return

    print(f"\n📄 输入文件: {INPUT_FILE.name}")
    print(f"🎯 使用模板: general/life_event_timeline")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n[1] Template.list() - 列出所有模板")
    names = Template.list()
    print(f"共 {len(names)} 个模板")

    print("\n[2] Template.list_domains() - 列出所有领域")
    domains = Template.list_domains()
    print(f"共 {len(domains)} 个领域: {domains}")

    print("\n[3] Template.get() - 获取配置")
    config = Template.get("general/life_event_timeline")
    if config:
        print(f"找到: {config.name}, type: {config.type}")
    else:
        print("未找到")

    print("\n[4] Template.search(type='list') - 按类型搜索")
    results = Template.search(type="list")
    print(f"找到 {len(results)} 个 list 类型模板")

    print("\n[5] Template.create() - 通过文件路径创建实例")
    template = Template.create(
        'life_event_timeline',
        llm_client=llm,
        embedder=embedder,
        language="zh",
    )
    print(f"创建成功: {type(template).__name__}")

    print("\n[6] 读取输入文件")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"读取成功，共 {len(content)} 字符")

    print("\n[7] template.feed_text() - 喂入文本")
    template.feed_text(content)
    print("✅ 知识提取完成")

    print("\n[8] template.build_index() - 构建索引")
    template.build_index()
    print("✅ 索引构建完成")

    print("\n[9] template.show() - 展示结果")
    template.show()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
