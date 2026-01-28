"""
Atom 演示：产品历史中的时序知识图谱提取

这个演示展示了如何使用 Atom 从产品迭代历史中提取结构化知识。
重点展示：
1. 产品发布时间与版本信息的提取
2. 关键人物与产品的关联
3. 公司并购与产品策略变化
4. 时序关系的精确捕获（t_start, t_end）
5. 证据追踪与来源溯源
"""

import os
import sys
from collections import Counter, defaultdict

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.graphs import Atom

load_dotenv()

# ==============================================================================
# 示例文本：产品历史（技术产品迭代）
# ==============================================================================

# EXAMPLE_TEXT = """
#     2024年是李四职业生涯的转折点。6月15日，李四加入了Google，担任工程师一职。
#     他加入的是核心技术团队，主要从事后端服务开发。工作初期，李四表现出色，
#     与团队协作顺利，代码质量得到认可。
    
#     到了9月，由于李四在多个关键项目中的出色表现，Google决定将其提升为技术主管。
#     升职后，李四开始领导一个30人的技术团队，负责推荐系统的开发和优化。
#     他实施了多项技术改革，团队效率提升了40%。
    
#     然而，到了11月中旬，李四发现自己对当前的薪资待遇不满意。经过深思熟虑，
#     他决定寻求新的机会。最终，李四接受了字节跳动的邀约，并于11月25日正式加入。
#     在字节，李四担任高级工程师，继续从事推荐系统的研发工作。
#     """

EXAMPLE_TEXT = """
"CyberPhone"是未来科技（FutureTech）公司旗下的旗舰智能手机系列，代表了移动设备革新的前沿。

第一代CyberPhone于2010年6月发布，凭其全息投影屏幕震惊业界。当时的首席设计师是乔纳森·李，他与工程主管陈思共同主导了这次创新。
这款产品上市后迅速成为全球最受欢迎的高端手机，首年销售额达到了2亿美元。

2012年9月，FutureTech推出了CyberPhone 2。这一代产品引入了脑机接口（BMI）的雏形功能，允许用户通过脑电波进行基础交互。
设计师乔纳森·李继续领导设计团队，而陈思则被晋升为首席工程师。
然而，这次创新也带来了风险：由于集成度过高，CyberPhone 2的电池安全问题频频出现。

到了2013年，由于电池缺陷引发的多起安全事故，FutureTech不得不宣布全球召回所有CyberPhone 2。
这场危机导致公司股价大幅下跌，管理层面临巨大压力。
时任CEO的王芳为了挽回信誉，做出了一个大胆的决定：整个2014年不发布新产品，所有资源投入到底层系统和安全机制的重构。

直到2015年底，经过两年打磨，CyberPhone 3终于问世。虽然发布时间大幅推迟，但这一代产品搭载了革命性的AI助手"Luna"。
Luna是由FutureTech在2015年年中收购的初创公司"Moon AI"开发的核心算法。
Moon AI的创始人兼CEO李想因此加入了FutureTech，担任AI创新部门的副总裁，任期从2015年7月至2019年6月。
CyberPhone 3一经发布就获得了业界的广泛赞誉，被誉为"手机史上的里程碑"。

自此之后，FutureTech建立了稳定的产品节奏，基本保持每两年推出一代新品的策略。
2017年3月发布的CyberPhone 4进一步完善了AI助手功能，并加入了增强现实（AR）显示技术。
2019年9月发布的CyberPhone 5则在续航能力和计算性能上取得了突破。
在这个阶段，乔纳森·李仍然是首席设计师，陈思继续担任首席工程师。

但转折点来了。2021年4月，乔纳森·李在为FutureTech服务了整整12年后，宣布离职并加入竞品公司"QuantumTech"担任设计总监。
乔纳森的离职引发了业界热议，许多人认为这标志着CyberPhone系列即将走向衰落。
与此同时，新晋设计师韩雪接替了乔纳森的职位，但她的设计风格与乔纳森截然不同。

2021年底发布的CyberPhone 6展现了全新的设计语言——极简风格取代了之前的科技感。
业界对这一变化评价不一，许多长期粉丝甚至戏称这是"最不像CyberPhone的一代"。
销售数据也反映了这一点：CyberPhone 6的市场反应相比前几代明显不足。

在这个困难时期，陈思于2022年年底晋升为首席产品官（CPO），获得了更大的权力重新调整产品方向。
同时，李想在2022年中期转任为AI伦理委员会主席，虽然仍在公司但已远离产品一线。

去年（2023年）全年，FutureTech几乎没有推出任何重大产品更新。这个沉默期引发了市场猜测。
直到今年初，公司宣布了一个雄心勃勃的计划：将在今年晚些时候发布CyberPhone X。

本周，FutureTech官方确认了CyberPhone X的发布时间定在今年Q3，并透露这款产品将是对CyberPhone系列的根本性重新定义。
根据公司声明，CyberPhone X旨在纪念该系列诞生15周年，同时引入突破性的新技术。
韩雪确认将继续担任首席设计师，而陈思作为CPO将主导这次产品重塑项目。
令人惊喜的是，曾经的设计大师乔纳森·李也获邀作为顾问加盟这个项目，尽管他目前仍就职于QuantumTech。

业界普遍认为，CyberPhone X将成为检验FutureTech是否能重获竞争力的关键产品。
"""

# ==============================================================================
# 主程序
# ==============================================================================

def main():
    print("=" * 80)
    print("🕒 Atom 演示：产品历史中的时序知识图谱提取")
    print("=" * 80)
    print()

    # 1. 初始化
    print("📦 初始化组件...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    obs_time = "2024-12-15"
    print(f"🚀 创建 Atom 实例（观察时间：{obs_time}）...")
    kg = Atom(
        llm_client=llm,
        embedder=embedder,
        observation_time=obs_time,
        facts_per_chunk=10,
        verbose=True,
    )

    # 2. 提取
    print(f"\n📄 正在处理产品历史文本（长度：{len(EXAMPLE_TEXT)} 字符）...")
    print("状态: 正在进行两阶段提取...")
    print("  [Phase 1] 原子事实提取")
    print("  [Phase 2] 关系提取（带时序和证据追踪）")
    print()
    kg.feed_text(EXAMPLE_TEXT)

    # 3. 显示初步结果
    print("\n" + "=" * 80)
    print("✅ Phase 1-2 提取完成！")
    print("=" * 80)

    # 统计信息
    print(f"\n📊 提取统计:")
    print(f"   节点数量: {len(kg.nodes)}")
    print(f"   关系数量: {len(kg.edges)}")
    
    # 统计标签分布
    labels = Counter(n.label for n in kg.nodes)
    print(f"   实体类型分布: {dict(labels)}")

    # 显示所有节点
    print("\n" + "-" * 80)
    print(f"🏷️  提取的实体及其类型 ({len(kg.nodes)} 个):")
    print("-" * 80)
    for i, node in enumerate(kg.nodes, 1):
        print(f"  {i:2d}. {node.name:<30} [类型: {node.label}]")

    # 显示所有关系（包括时间和证据信息）
    print("\n" + "-" * 80)
    print(f"🔗 提取的关系 ({len(kg.edges)} 个):")
    print("-" * 80)
    
    # 按时间排序关系
    sorted_edges = sorted(
        kg.edges,
        key=lambda e: e.t_start[0] if e.t_start else "9999-12-31"
    )
    
    for i, edge in enumerate(sorted_edges, 1):
        # 基本关系
        rel_str = f"{edge.startNode.name} --[{edge.name}]--> {edge.endNode.name}"
        
        # 添加时间信息
        time_info = ""
        if edge.t_start:
            time_info += f"(从 {edge.t_start[0]}"
            if edge.t_end:
                time_info += f" 到 {edge.t_end[0]})"
            else:
                time_info += ")"
        elif edge.t_end:
            time_info += f"(截止 {edge.t_end[0]})"
        
        print(f"  {i:2d}. {rel_str:<65} {time_info}")
        
        # 显示证据（只显示第一条）
        if edge.atomic_facts:
            evidence = edge.atomic_facts[0].replace("\n", " ")
            if len(evidence) > 70:
                evidence = evidence[:70] + "..."
            print(f"       📌 证据: {evidence}")

    # 按谓词分组显示
    print("\n" + "-" * 80)
    print("📋 按关系类型分类:")
    print("-" * 80)
    
    relations_by_type = defaultdict(list)
    for edge in kg.edges:
        relations_by_type[edge.name].append((edge.startNode.name, edge.endNode.name))
    
    for pred in sorted(relations_by_type.keys()):
        pairs = relations_by_type[pred]
        print(f"\n  ✓ {pred} ({len(pairs)} 条)")
        for s, o in pairs[:8]:  # 显示前 8 条
            print(f"     • {s} → {o}")
        if len(pairs) > 8:
            print(f"     • ... 及 {len(pairs) - 8} 条其他关系")

    # 实体连接度分析
    print("\n" + "-" * 80)
    print("⭐ 高关联度实体 (Top 15):")
    print("-" * 80)
    
    entity_degree = Counter()
    for edge in kg.edges:
        entity_degree[edge.startNode.name] += 1
        entity_degree[edge.endNode.name] += 1
    
    for entity, count in entity_degree.most_common(15):
        print(f"  • {entity:<30} 参与 {count:2d} 个关系")

    # ============================================================================
    # Phase 3: 语义去重
    # ============================================================================
    print("\n" + "=" * 80)
    print("🔄 Phase 3: 语义去重 (使用 SemHash)")
    print("=" * 80)
    
    print(f"\n去重前: 节点 {len(kg.nodes)}, 关系 {len(kg.edges)}")
    print("  执行语义相似度匹配 (threshold=0.8)...")
    
    kg.match_nodes_and_update_edges(threshold=0.8)
    
    print(f"去重后: 节点 {len(kg.nodes)}, 关系 {len(kg.edges)}")
    
    # 对比统计
    print("\n📊 去重后统计:")
    
    # 更新标签分布
    labels_after = Counter(n.label for n in kg.nodes)
    print(f"   实体类型分布: {dict(labels_after)}")
    
    # 更新关系类型分布
    relations_after = defaultdict(int)
    for edge in kg.edges:
        relations_after[edge.name] += 1
    print(f"   关系类型: {len(relations_after)} 种")

    # 显示去重后的节点
    print("\n" + "-" * 80)
    print(f"🏷️  去重后的实体 ({len(kg.nodes)} 个):")
    print("-" * 80)
    for i, node in enumerate(kg.nodes, 1):
        print(f"  {i:2d}. {node.name:<30} [类型: {node.label}]")

    # 显示去重后的关系（简要版）
    print("\n" + "-" * 80)
    print(f"🔗 去重后的关系 ({len(kg.edges)} 个 - 简要版):")
    print("-" * 80)
    
    sorted_edges_after = sorted(
        kg.edges,
        key=lambda e: e.t_start[0] if e.t_start else "9999-12-31"
    )
    
    for i, edge in enumerate(sorted_edges_after, 1):
        rel_str = f"{edge.startNode.name} --[{edge.name}]--> {edge.endNode.name}"
        
        time_info = ""
        if edge.t_start:
            time_info += f"(从 {edge.t_start[0]}"
            if edge.t_end:
                time_info += f" 到 {edge.t_end[0]})"
            else:
                time_info += ")"
        elif edge.t_end:
            time_info += f"(截止 {edge.t_end[0]})"
        
        print(f"  {i:2d}. {rel_str:<65} {time_info}")

    # ============================================================================
    # 保存结果
    # ============================================================================
    print("\n" + "=" * 80)
    print("💾 保存结果...")
    print("=" * 80)

    try:
        output_dir = "temp/atom_demo"
        kg.dump(output_dir)
        print(f"✓ 结果已保存到 {output_dir}/")
        
        # 列出保存的文件
        import os
        saved_files = []
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    saved_files.append(rel_path)
        
        if saved_files:
            print("\n  保存的文件:")
            for f in sorted(saved_files):
                print(f"    - {f}")
    except Exception as e:
        print(f"⚠ 警告: 无法保存结果: {str(e)}")

    # ============================================================================
    # 智能对话 (Chat)
    # ============================================================================
    print("\n" + "=" * 80)
    print("💬 知识图谱智能问答")
    print("=" * 80)
    print("基于提取的知识进行深度对话...\n")

    chat_questions = [
        "CyberPhone 系列从第一代到最新一代的发展过程中，主要经历了哪些关键转折点和挑战？",
        "乔纳森·李和陈思在 FutureTech 公司的职业发展过程中扮演了什么角色，他们的离职和晋升对产品方向有什么影响？",
        "CyberPhone 2 的电池问题危机是如何发生的，FutureTech 公司采取了什么应对措施来恢复信誉？"
    ]

    kg.build_index()
    for q in chat_questions:
        print(f"❓ 提问: {q}")
        try:
            response = kg.chat(q)
            print(f"💡 回答: {response.content}\n")
        except Exception as e:
            print(f"⚠️ 对话异常: {e}\n")

    print("\n" + "=" * 80)
    print("✨ Atom 演示完成！")
    print("=" * 80)
    print("\n📌 演示要点:")
    print("  ✓ 两阶段提取：原子事实 → 关系提取")
    print("  ✓ 时序追踪：产品发布日期、人物任职期间")
    print("  ✓ 证据追踪：每条关系都关联到源事实")
    print("  ✓ 语义去重：自动合并同义实体")
    print("  ✓ 智能对话：基于知识图谱的 RAG 问答")


if __name__ == "__main__":
    main()
