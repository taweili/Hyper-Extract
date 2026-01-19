"""
AutoModel 多 Chunk 提取示例

演示如何使用 AutoModel 处理长文本，测试多 chunk 并发提取和合并功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract import AutoModel


# 定义文档知识 Schema
class DocumentSchema(BaseModel):
    """文档综合知识结构"""

    title: str = Field(default="", description="文档标题")
    author: str = Field(default="", description="作者姓名")
    publish_date: str = Field(default="", description="发布日期")
    category: str = Field(default="", description="文档类别")
    summary: str = Field(default="", description="文档摘要")
    main_topics: List[str] = Field(default_factory=list, description="主要话题")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    methodology: str = Field(default="", description="研究方法")
    conclusion: str = Field(default="", description="结论")
    keywords: List[str] = Field(default_factory=list, description="关键词")


def generate_long_document() -> str:
    """生成一个长文档用于测试多 chunk 提取"""
    return """
# 人工智能在医疗诊断中的应用研究报告

作者: 张伟博士
发布日期: 2024年3月15日
类别: 医疗科技研究

## 摘要

本研究报告深入探讨了人工智能技术在现代医疗诊断领域的广泛应用。通过分析大量临床数据和案例研究，
我们发现AI技术在提高诊断准确率、降低医疗成本、优化治疗方案等方面展现出巨大潜力。

## 第一部分：引言与背景

人工智能(AI)技术的快速发展正在深刻改变医疗行业的面貌。特别是在医疗诊断领域，AI展示了超越传统
方法的潜力。深度学习、计算机视觉和自然语言处理等技术的结合，使得AI系统能够从海量医疗数据中
学习并识别疾病模式。

随着电子健康记录(EHR)的普及和医学影像数字化，医疗数据呈现爆炸式增长。这为AI技术的应用提供了
丰富的训练素材。同时，计算能力的提升和算法的优化，使得复杂的医学诊断任务变得更加可行。

## 第二部分：研究方法与数据收集

本研究采用了多种研究方法相结合的方式：

1. **文献综述**: 系统性回顾了2015-2024年间发表的相关学术论文超过500篇
2. **案例分析**: 深入分析了15家医院实施AI诊断系统的实际案例
3. **实验研究**: 在合作医院进行了为期18个月的临床试验
4. **专家访谈**: 采访了50位医疗专家和AI研究人员

数据收集方面，我们使用了包括X光片、CT扫描、MRI影像在内的超过100,000份医学影像数据，
以及相应的诊断报告和患者病历。所有数据均经过严格的隐私保护处理，符合医疗数据使用规范。

## 第三部分：主要发现

### 3.1 诊断准确率显著提升

研究发现，AI辅助诊断系统在多个疾病领域的准确率达到了专家级水平：
- 肺癌早期检测准确率达到94.5%，比传统方法提高12%
- 糖尿病视网膜病变识别准确率达到96.8%
- 皮肤癌分类准确率达到91.2%

### 3.2 诊断效率大幅提高

AI系统能够在数秒内完成原本需要医生数小时才能完成的影像分析工作。平均诊断时间从45分钟
缩短至3分钟，效率提升了15倍。

### 3.3 成本效益分析

实施AI诊断系统后，医院的诊断成本平均降低了35%。主要节省来自于：
- 减少了不必要的复诊
- 降低了误诊率
- 优化了医疗资源配置

### 3.4 早期疾病检测

AI系统在早期疾病检测方面表现出色，能够识别出人眼难以察觉的微小病变。这对于提高治疗成功率
和患者生存率具有重要意义。

## 第四部分：技术实现与挑战

### 4.1 核心技术

研究涉及的主要AI技术包括：
- 卷积神经网络(CNN)用于医学影像分析
- 循环神经网络(RNN)用于处理时序医疗数据
- 迁移学习技术加速模型训练
- 联邦学习保护患者隐私

### 4.2 面临的挑战

尽管AI在医疗诊断中展现出巨大潜力，但仍面临诸多挑战：
1. 数据质量和标注问题
2. 模型可解释性不足
3. 医疗法规和伦理问题
4. 医生接受度和信任问题
5. 系统集成和部署成本

## 第五部分：结论与展望

通过本研究，我们得出以下结论：

1. AI技术已经在医疗诊断领域取得了显著成果，能够有效提高诊断准确率和效率
2. AI不是要替代医生，而是作为强有力的辅助工具，帮助医生做出更准确的诊断
3. 数据质量、算法透明度和医疗伦理是未来需要重点关注的问题
4. 跨学科合作（医学专家+AI研究人员）是推动该领域发展的关键

展望未来，我们预期AI在医疗诊断领域将继续深化应用，特别是在个性化医疗、远程诊断、
罕见病识别等方面将发挥更大作用。同时，随着可解释AI和联邦学习等技术的成熟，
AI医疗诊断系统的可信度和安全性将进一步提升。

## 关键词

人工智能、医疗诊断、深度学习、医学影像分析、诊断准确率、医疗AI、计算机辅助诊断、
临床应用、机器学习、医疗科技
"""


def main():
    print("=" * 80)
    print("AutoModel 多 Chunk 提取示例")
    print("=" * 80)

    # 1. 生成长文档
    print("\n[1] 生成测试文档...")
    document = generate_long_document()
    print(f"   文档长度: {len(document)} 字符")
    print(f"   预计分块数: {len(document) // 200 + 1} 块 (chunk_size=200)")

    # 2. 初始化 LLM 和 Embedder
    print("\n[2] 初始化 LLM 和 Embedder...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. 创建 AutoModel 实例 (使用小的 chunk_size 测试多 chunk)
    print("\n[3] 创建 AutoModel 实例 (chunk_size=200)...")
    a_document_model = AutoModel(
        data_schema=DocumentSchema,
        llm_client=llm,
        embedder=embedder,
        chunk_size=200,  # 设置小的 chunk_size 来测试多 chunk 提取
        chunk_overlap=50,
        max_workers=5,
        show_progress=True,
    )

    # 4. 提取知识 (使用 feed 模式)
    print("\n[4] 提取知识 (使用 feed 模式)...")
    print("-" * 80)
    a_document_model.feed(document)
    extracted_data = a_document_model.data
    print("-" * 80)

    # 5. 显示提取结果
    print("\n[5] 提取结果:")
    print(f"   标题: {extracted_data.title}")
    print(f"   作者: {extracted_data.author}")
    print(f"   发布日期: {extracted_data.publish_date}")
    print(f"   类别: {extracted_data.category}")
    print(f"   摘要: {extracted_data.summary[:100]}...")
    print(f"   主要话题: {extracted_data.main_topics}")
    print(f"   关键发现数量: {len(extracted_data.key_findings)}")
    print(f"   方法论: {extracted_data.methodology[:100]}...")
    print(f"   结论: {extracted_data.conclusion[:100]}...")
    print(f"   关键词数量: {len(extracted_data.keywords)}")

    # 6. 测试字段数量
    print(f"\n[6] 知识字段数: {len(a_document_model)}")

    # 7. 构建索引
    print("\n[7] 构建向量索引...")
    a_document_model.build_index()

    # 8. 测试搜索
    print("\n[8] 测试知识搜索...")
    queries = [
        "研究的主要发现是什么",
        "使用了哪些研究方法",
        "AI的准确率如何",
    ]

    for query in queries:
        print(f"\n   查询: '{query}'")
        results = a_document_model.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            field_name = list(result.keys())[0]
            field_value = result[field_name]
            print(f"      [{i}] {field_name}: {str(field_value)[:80]}...")

    # 9. 测试增量提取（feed 模式）
    print("\n[9] 测试增量提取（feed 模式）...")
    additional_text = """
    补充信息：
    本研究获得了国家自然科学基金支持，项目编号：NSFC-2023-12345。
    研究团队来自清华大学医学院和北京协和医院。
    """
    print("   添加补充文本...")
    a_document_model.feed(additional_text)  # 使用 feed 自动合并
    print(f"   更新后的作者信息: {a_document_model.data.author}")

    # 10. 保存知识
    print("\n[10] 保存知识到文件...")
    save_path = Path(__file__).parent.parent / "temp" / "auto_model_demo"
    a_document_model.dump(str(save_path))
    print(f"   已保存到: {save_path}")

    # 11. 重新加载测试
    print("\n[11] 测试知识加载...")
    a_loaded_document_model = AutoModel(
        data_schema=DocumentSchema,
        llm_client=llm,
        embedder=embedder,
    )
    a_loaded_document_model.load(str(save_path))
    print(f"   加载成功! 字段数: {len(a_loaded_document_model)}")
    print(f"   标题: {a_loaded_document_model.data.title}")

    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
