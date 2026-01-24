"""
KGGenGraph 演示：知识图谱生成

这个演示展示了如何使用 KGGenGraph 从非结构化文本中提取简单的三元组知识图谱。
KGGenGraph 是对 AutoGraph 的专用包装，优化了提示词和数据结构以支持三元组提取。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.graphs import KG_Gen

load_dotenv()

# ==============================================================================
# 示例文本 - 来自真实场景的数据
# ==============================================================================

EXAMPLE_TEXT = """
【MMORPG 公会纠纷事件】

星辰阁是一个在《永恒之境》游戏中排名前三的公会。公会会长是一位名叫雷霆之怒的资深玩家。
副会长包括坚如磐石和月光治愈者两位。

三年前，雷霆之怒创立了星辰阁。他邀请了许多朋友加入，其中包括主要DPS输出暗影刺客。
暗影刺客以他的高伤害输出而闻名，经常在公会的副本团队中表现突出。

公会的治疗负责人是一名叫小甜甜的圣骑士，她与暗影刺客是现实中的一对情侣。
这导致了许多问题，因为在关键的BOSS战中，小甜甜会偏心给暗影刺客加血。

最终的冲突发生在深渊魔龙副本中。在这场战斗中：
- 雷霆之怒担任主坦克，吸收大部分伤害
- 坚如磐石作为副坦克进行补充
- 小甜甜负责主要治疗
- 月光治愈者负责辅助治疗
- 暗影刺客、火球术一级、风云剑侠等担任DPS

在战斗中，坚如磐石不幸掉线。此时小甜甜没有全力治疗会长，反而将大部分治疗给了暗影刺客。
结果导致雷霆之怒（会长）血量下降过快，最终倒地。

战斗失败后，雷霆之怒非常愤怒。他当众指责小甜甜的治疗不负责任。
随后，暗影刺客和小甜甜相继退出了公会。

更糟糕的是，在战斗中掉落的传说级武器"魔龙之牙"被暗影刺客私吞了。
这个武器本来应该由会长分配给整个公会。

最终，雷霆之怒宣布星辰阁解散。许多成员转向其他公会，包括火球术一级加入了日月神教。
这个事件成为了游戏社区的一个著名丑闻，许多玩家开始警惕加入有腐败管理的大公会。
"""

# ==============================================================================
# 主程序
# ==============================================================================

def main():
    print("=" * 70)
    print("🎮 KGGenGraph 演示：从游戏事件提取知识图谱")
    print("=" * 70)
    print()

    # 1. 初始化
    print("📦 初始化组件...")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    embedder = OpenAIEmbeddings()

    print("🚀 创建 KGGenGraph 实例...")
    kg = KG_Gen(
        llm_client=llm,
        embedder=embedder,
        verbose=True,
    )

    # 2. 提取
    print(f"\n📄 处理文本（长度：{len(EXAMPLE_TEXT)} 字符）...")
    print()
    kg.feed_text(EXAMPLE_TEXT)

    print(f"\n🧩 提取初始结果: {len(kg.nodes)} 个节点, {len(kg.edges)} 条边")

    # 显示去重前的节点
    print("\n" + "-" * 70)
    print(f"📝 去重前的实体列表 ({len(kg.nodes)} 个):")
    print("-" * 70)
    nodes_before = sorted([node.name for node in kg.nodes])
    for i, name in enumerate(nodes_before, 1):
        print(f"  {i:2d}. {name}")

    # 3. 去重演示
    print("\n" + "=" * 70)
    print("🔄 执行语义去重 (Self-Deduplication)...")
    print("=" * 70)
    print("说明: 去重会通过语义相似度合并近似的实体名称")
    print("阈值越高 (0.0-1.0)，匹配条件越严格，合并越少")
    print()
    # 使用较为宽松的阈值 (0.9) 来演示合并效果
    # 注意：首次运行时会自动下载 sentence-transformers 模型
    kg.self_deduplicate(threshold=0.9)

    # 显示去重后的节点
    print("\n" + "-" * 70)
    print(f"✨ 去重后的实体列表 ({len(kg.nodes)} 个):")
    print("-" * 70)
    nodes_after = sorted([node.name for node in kg.nodes])
    for i, name in enumerate(nodes_after, 1):
        print(f"  {i:2d}. {name}")
    
    if len(nodes_before) != len(nodes_after):
        print(f"\n📊 去重效果: {len(nodes_before)} → {len(nodes_after)} ({len(nodes_before) - len(nodes_after)} 个实体被合并)")

    # 4. 显示结果
    print("\n" + "=" * 70)
    print("✅ 最终结果（去重后）！")
    print("=" * 70)

    # 统计信息
    print(f"\n📊 统计信息:")
    print(f"   节点数量: {len(kg.nodes)}")
    print(f"   关系数量: {len(kg.edges)}")
    unique_predicates = len(set(e.predicate for e in kg.edges))
    avg_edges = len(kg.edges) / max(len(kg.nodes), 1)
    print(f"   唯一谓词数: {unique_predicates}")
    print(f"   平均每个节点的关系数: {avg_edges:.2f}")

    # 显示所有节点
    print("\n" + "-" * 70)
    print(f"🏷️  提取的实体 ({len(kg.nodes)} 个):")
    print("-" * 70)
    for i, node in enumerate(kg.nodes, 1):
        print(f"  {i:2d}. {node.name}")

    # 显示所有三元组
    print("\n" + "-" * 70)
    print(f"🔗 提取的关系 ({len(kg.edges)} 个):")
    print("-" * 70)
    for i, edge in enumerate(kg.edges, 1):
        print(f"  {i:2d}. {edge.subject} --[{edge.predicate}]--> {edge.object}")

    # 按谓词分组显示
    print("\n" + "-" * 70)
    print("📋 按关系类型分类:")
    print("-" * 70)
    
    from collections import defaultdict
    relations_by_type = defaultdict(list)
    for edge in kg.edges:
        relations_by_type[edge.predicate].append((edge.subject, edge.object))
    
    for pred in sorted(relations_by_type.keys()):
        pairs = relations_by_type[pred]
        print(f"\n  ✓ {pred} ({len(pairs)} 条)")
        for s, o in pairs:
            print(f"     • {s} -> {o}")

    # 实体连接度分析
    print("\n" + "-" * 70)
    print("⭐ 高关联度实体 (Top 5):")
    print("-" * 70)
    
    from collections import Counter
    entity_degree = Counter()
    for edge in kg.edges:
        entity_degree[edge.subject] += 1
        entity_degree[edge.object] += 1
    
    for entity, count in entity_degree.most_common(5):
        print(f"  • {entity}: 参与 {count} 个关系")

    # ============================================================================
    # Save Results
    # ============================================================================
    print("\n" + "=" * 70)
    print("Saving Results...")
    print("=" * 70)

    try:
        import os
        output_dir = "temp/kg_gen_demo"
        kg.dump(output_dir)
        print(f"✓ Results saved to {output_dir}/")
        
        # List saved files
        saved_files = []
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    saved_files.append(rel_path)
        
        if saved_files:
            print("\n  Saved files:")
            for f in saved_files:
                print(f"    - {f}")
    except Exception as e:
        print(f"⚠ Warning: Could not save results: {str(e)}")

    print("\n" + "=" * 70)
    print("✨ 演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
