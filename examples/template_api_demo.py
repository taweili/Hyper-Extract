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


def main():
    llm = ChatOpenAI(model="gpt-4o-mini")
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("=" * 60)
    print("Template API 测试")
    print("=" * 60)

    print("\n[1] Template.list() - 列出所有模板")
    names = Template.list()
    print(f"共 {len(names)} 个模板")
    print(f"前10个: {names[:10]}")

    print("\n[2] Template.list_domains() - 列出所有领域")
    domains = Template.list_domains()
    print(f"共 {len(domains)} 个领域: {domains}")

    print("\n[3] Template.get() - 通过路径获取配置")
    config = Template.get("general/knowledge_graph")
    if config:
        print(f"找到: {config.name}, type: {config.type}")
    else:
        print("未找到")

    print("\n[4] Template.search(type='graph') - 按类型搜索")
    results = Template.search(type="graph")
    print(f"找到 {len(results)} 个 graph 类型模板")
    if results:
        print(f"前5个: {[r.name for r in results[:5]]}")

    print("\n[5] Template.search(query='知识图谱') - 模糊搜索")
    results = Template.search(query="知识图谱")
    print(f"找到 {len(results)} 个匹配模板")
    if results:
        print(f"前5个: {[r.name for r in results[:5]]}")

    print("\n[6] Template.create() - 创建实例（通过路径）")
    template = Template.create("general/knowledge_graph", llm, embedder)
    print(f"创建成功: {type(template).__name__}")

    print("\n[7] 测试 parse")
    test_text = "苹果公司成立于1976年，总部位于加利福尼亚州库比蒂诺。"
    try:
        result = template.parse(test_text)
        print(f"解析结果: {result}")
    except Exception as e:
        print(f"解析出错（正常，API调用）: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
