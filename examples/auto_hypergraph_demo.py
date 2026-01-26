"""
AutoHypergraph 演示：星际外交危机的故事线分析

这个例子展示了如何使用 AutoHypergraph 从复杂的叙事文本中提取多类型的超边关系。
超边可以代表不同类型的故事单元：冲突、结盟、持有关系、会议等。
"""

import os
import sys
import collections
from typing import List
from pathlib import Path

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.hypergraphs import AutoHypergraph

load_dotenv()

# ==============================================================================
# 1. 定义 Schema：灵活的叙事结构
# ==============================================================================


class StoryEntity(BaseModel):
    """
    节点：故事中的基本元素。
    可以是：人物(Character), 地点(Location), 物品(Item), 派系(Faction)
    """

    name: str = Field(description="实体名称，如 'Neo', 'Matrix', 'Excalibur'")
    category: str = Field(
        description="实体类别: Character(人物), Location(地点), Item(物品), Faction(派系)",
    )
    description: str = Field(
        description="实体的详细描述，如 '黑蛇'(Character) 的角色是 Which Snake",
    )


class NarrativeUnit(BaseModel):
    """
    超边：一个叙事单元。

    这不仅仅是一个关系，它可以是一个发生的事件、一种复杂的联盟、或者一个状态。
    关键在于：它通过一个 'type' 字段来区分语义，但结构上都是连接多个实体的超边。
    """

    summary: str = Field(description="简短描述这个单元发生了什么，或者是什么关系")

    # 这里体现了"多类型"：LLM 会判断这具体是什么类型的连接
    edge_type: str = Field(description="超边类型: Conflict(冲突), Alliance(结盟), Possession(持有), Meeting(会议), State(状态)")

    # 核心：连接所有相关的实体
    participants: List[str] = Field(description="所有牵涉其中的实体名称列表")


# ==============================================================================
# 2. 故事文本：星际外交危机
# ==============================================================================

source_text = """
【银河纪元 3042年 - 赤红星云事件报告】

危机在这一周达到了顶峰。整个银河系似乎都陷入了暗流涌动的政治漩涡。

【第一阶段：秘密接触】
臭名昭著的星际海盗黑蛇驾驶着他的旗舰复仇号，在泰坦空间站秘密会见了银河联邦的背叛者议员 Valerius。
目击者称，两人在午夜时分登上了空间站的顶层禁区。据情报部门推测，这是一次肮脏的交易——
双方达成了针对皇室的同盟关系。参与此会议的还有 Valerius 手下的特务头目 Shadow，
他负责处理所有不可告人的细节。这个同盟的形成标志着大麻烦即将到来。

【第二阶段：叛变与夺权】
在这次会议的两天后，事态急剧恶化。黑蛇这种疯狂的家伙竟然在极光星区伏击了皇家护卫队。
这场突然的冲突中，皇家护卫队的队长 Leona 与副队长 Marcus 奋力抵抗，
但他们陷入了黑蛇手下的精锐战士的包围。这场激战导致队长 Leona 身受重伤。
而黑蛇的目标不是为了杀戮，而是为了夺取一件神圣的物品——传说中的虚空水晶。
这枚水晶散发着幽蓝的光芒，据说能够打开先祖之门的第一道密封。
黑蛇在战斗中成功夺取了水晶，但 Leona 在临终前用最后的力量将其重新夺回。

【第三阶段：流亡与隐藏】
Leona 被迫带着虚空水晶，从极光星区逃往荒凉的废土行星 Z-9。
在这个被遗忘的角落，她向仅有的几个信任者求救：还有副队长 Marcus 以及隐秘组织"地下抵抗军"的领导人 Cipher。
同时，议员 Valerius 非法持有了开启先祖之门的钥匙——这把钥匙本应被安全保管在皇家金库中。
他现在藏匿在浮空都市中，与黑蛇遥相呼应，计划着下一步的政变。

【第四阶段：势力重组】
银河联邦的最高委员会得知了这一系列事件，决定采取行动。
高级顾问 Artemis 被任命为特使，她与 Leona 在废土行星 Z-9 进行了秘密会晤，
讨论如何制止这场即将到来的危机。同时，地下抵抗军的 Cipher 也加入了这次会议，
三人共同制定了一个大胆的计划。

【第五阶段：最后的筹码】
虽然黑蛇未能获得虚空水晶，但他已经从 Valerius 那里获得了先祖之门钥匙的复制品。
根据情报，这个复制品目前被秘密运往到黑蛇的秘密基地——位于辐射荒漠中的要塞。
参与此次运送的还有 Shadow 和黑蛇手下的精锐战士群体。
与此同时，Leona 和 Marcus 正在准备一场反击，他们计划在虚空水晶的力量下重新夺回局势的控制权。

目前局势：
- 黑蛇：手持复制品钥匙，掌控旗舰复仇号，计划进行最终的攻击
- 议员 Valerius：躲在浮空都市中，与黑蛇保持联系
- Leona：守护虚空水晶，在废土行星 Z-9 养伤，准备反击
- 银河联邦：通过特使 Artemis 支持 Leona，正在调集力量
- 地下抵抗军：Cipher 领导，与 Leona 和 Marcus 联手，准备对抗黑蛇和 Valerius 的同盟

这场战争的走向仍不确定。虚空水晶、先祖之门、以及隐藏在这一切背后的秘密，
都将在接下来的日子里浮出水面。银河的命运，可能就在这些关键人物和物品的碰撞中决定。
"""


# ==============================================================================
# 3. 提取逻辑配置
# ==============================================================================


def main():
    """主函数：完整的 AutoHypergraph 提取与分析流程"""

    # 初始化 LLM 和嵌入模型
    llm_client = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    # 1. 节点指纹：用名字即可
    node_key_fn = lambda x: x.name

    # 2. 边指纹：类型 + 摘要 + 参与者（排序）
    #    这样即使是同一群人，如果发生了两件事，也会被视为两条边
    def edge_key_fn(x: NarrativeUnit) -> str:
        participants = sorted(x.participants)
        return f"{x.edge_type}|{'-'.join(participants)}"

    # 3. 参与者映射：告诉框架谁在这个超边里
    participants_fn = lambda x: tuple(x.participants)

    print("=" * 70)
    print("🚀 AutoHypergraph 演示：赤红星云事件分析")
    print("=" * 70)
    print()

    # 创建 AutoHypergraph 实例
    hypergraph = AutoHypergraph(
        node_schema=StoryEntity,
        edge_schema=NarrativeUnit,
        node_key_extractor=node_key_fn,
        edge_key_extractor=edge_key_fn,
        nodes_in_edge_extractor=participants_fn,
        llm_client=llm_client,
        embedder=embedder,
        extraction_mode="two_stage",  # 推荐：先识别实体，再梳理故事线
        verbose=True,
        # 使用中文 Prompt 引导 LLM
        prompt_for_node_extraction=(
            "你的任务是从故事文本中提取所有重要的实体节点。\n"
            "实体可以是以下类别之一：\n"
            "- Character（人物）：故事中出现的角色\n"
            "- Location（地点）：故事发生的地方\n"
            "- Item（物品）：故事中提到的重要物品或武器\n"
            "- Faction（派系）：故事中的组织或势力\n\n"
            "请确保提取所有重要的实体，并正确分类它们的类别。"
        ),
        prompt_for_edge_extraction=(
            "你的任务是从故事文本中提取复杂的叙事关系，将其建模为超边。\n"
            "超边可以连接任意数量的实体（Character、Location、Item、Faction）。\n\n"
            "请根据故事内容，识别并分类以下类型的超边：\n"
            "- Conflict（冲突）：两个或多个角色之间的战斗或对抗\n"
            "- Alliance（结盟）：角色或派系之间的同盟或合作关系\n"
            "- Possession（持有）：某个角色拥有或守护某件物品\n"
            "- Meeting（会议）：多个角色在某个地点进行的会面\n"
            "- State（状态）：描述某个角色或物品在某个地点的状态\n\n"
            "对于每个超边，请提供：\n"
            "1. summary：对这个叙事单元的简洁描述\n"
            "2. edge_type：上述分类之一\n"
            "3. participants：所有牵涉其中的实体名称列表\n\n"
            "确保 participants 列表包含故事中与该事件相关的所有实体。"
        ),
        chunk_size=1000,
    )

    print("📚 正在分析《赤红星云事件报告》...")
    print(f"   文本长度：{len(source_text)} 字符")
    print()

    # 执行提取
    hypergraph.feed_text(source_text)

    # ==============================================================================
    # 4. 结果展示：按类型分类
    # ==============================================================================

    print("\n" + "=" * 70)
    print(f"🎭 第一部分：登场角色与物品 ({len(hypergraph.nodes)} 个实体)")
    print("=" * 70)

    # 按类别打印
    nodes_by_cat = collections.defaultdict(list)
    for n in hypergraph.nodes:
        nodes_by_cat[n.category].append(n.name)

    category_emoji = {"Character": "👤", "Location": "📍", "Item": "⚔️", "Faction": "🏛️"}

    for cat in ["Character", "Location", "Item", "Faction"]:
        if cat in nodes_by_cat:
            emoji = category_emoji.get(cat, "•")
            names = ", ".join(nodes_by_cat[cat])
            print(
                f"\n   {emoji} {cat}（{cat == 'Character' and '人物' or cat == 'Location' and '地点' or cat == 'Item' and '物品' or '派系'}）:"
            )
            print(f"      {names}")

    # ==============================================================================
    # 5. 故事线展示：按超边类型分类
    # ==============================================================================

    print("\n" + "=" * 70)
    print(f"🎬 第二部分：故事线分析 ({len(hypergraph.edges)} 个叙事单元)")
    print("=" * 70)

    # 按类型分组
    edges_by_type = collections.defaultdict(list)
    for e in hypergraph.edges:
        edges_by_type[e.edge_type].append(e)

    type_emoji = {
        "Conflict": "⚔️",
        "Alliance": "🤝",
        "Possession": "🎁",
        "Meeting": "🤵",
        "State": "📊",
    }

    type_cn = {
        "Conflict": "冲突",
        "Alliance": "结盟",
        "Possession": "持有",
        "Meeting": "会议",
        "State": "状态",
    }

    for e_type in ["Conflict", "Alliance", "Meeting", "Possession", "State"]:
        if e_type in edges_by_type:
            emoji = type_emoji.get(e_type, "•")
            cn_name = type_cn.get(e_type, e_type)
            edges = edges_by_type[e_type]
            print(f"\n   {emoji} 【{cn_name}】类型 ({len(edges)} 个事件):")
            for i, e in enumerate(edges, 1):
                print(f"\n      {i}. 事件描述：{e.summary}")
                print(f"         🔗 参与方：{', '.join(e.participants)}")

    # ==============================================================================
    # 6. 实体中心性分析：哪个实体参与了最多的故事线
    # ==============================================================================

    print("\n" + "=" * 70)
    print("📊 第三部分：关键实体分析（超边参与度）")
    print("=" * 70)

    entity_participation = collections.defaultdict(int)
    for e in hypergraph.edges:
        for participant in e.participants:
            entity_participation[participant] += 1

    # 按参与度排序
    sorted_entities = sorted(
        entity_participation.items(), key=lambda x: x[1], reverse=True
    )

    print("\n   参与故事线最多的实体（中心性分析）：\n")
    for rank, (entity, count) in enumerate(sorted_entities[:10], 1):
        bar = "█" * count
        print(f"   {rank:2d}. {entity:12s}  {bar}  ({count} 个故事线)")

    # ==============================================================================
    # 7. 复杂查询演示
    # ==============================================================================

    print("\n" + "=" * 70)
    print("🔍 第四部分：语义搜索演示")
    print("=" * 70)

    # 建立索引
    print("\n   正在构建搜索索引...")
    hypergraph.build_index(index_nodes=True, index_edges=True)

    # 执行几个查询
    queries = [
        "虚空水晶在哪里？谁守护着它？",
        "Leona 发生了什么事？",
        "黑蛇的计划是什么？",
    ]

    for query in queries:
        print(f"\n   🎯 查询：{query}")
        results = hypergraph.search_edges(query, top_k=3)
        if results:
            for j, res in enumerate(results, 1):
                print(f"      → 结果 {j} [{res.edge_type}]：{res.summary}")
        else:
            print(f"      → 未找到相关信息")

    # ==============================================================================
    # 8. 关系图统计
    # ==============================================================================

    print("\n" + "=" * 70)
    print("📈 第五部分：图统计")
    print("=" * 70)

    print(f"\n   节点总数（实体）：{len(hypergraph.nodes)}")
    print(f"   边总数（叙事单元）：{len(hypergraph.edges)}")

    avg_participants = (
        sum(len(e.participants) for e in hypergraph.edges) / len(hypergraph.edges)
        if hypergraph.edges
        else 0
    )
    print(f"   平均每条边的参与度：{avg_participants:.2f} 个实体")

    max_participants_edge = (
        max(hypergraph.edges, key=lambda e: len(e.participants))
        if hypergraph.edges
        else None
    )
    if max_participants_edge:
        print(f"   最复杂的叙事单元：{max_participants_edge.summary}")
        print(f"      参与实体数：{len(max_participants_edge.participants)}")

    # ==============================================================================
    # 9. 保存超图到本地
    # ==============================================================================

    print("\n" + "=" * 70)
    print("💾 保存超图到本地")
    print("=" * 70)

    # 获取项目根目录
    project_root = Path(__file__).resolve().parent.parent
    save_path = project_root / "temp" / "auto_hypergraph_demo"

    try:
        hypergraph.dump(save_path)
        print(f"\n   ✅ 超图已保存到: {save_path}")
        print(f"      节点数: {len(hypergraph.nodes)}")
        print(f"      边数: {len(hypergraph.edges)}")
    except Exception as e:
        print(f"\n   ⚠️  保存失败: {e}")

    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
