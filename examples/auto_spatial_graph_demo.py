"""
AutoSpatialGraph Demo: 深海惊魂 - "阿特拉斯"号的幽灵 🌊👻

场景背景：
一名深海打捞专家进入失联的科研站"阿特拉斯"号。由于电力系统故障，导航地图失效。
主角必须通过观察周围环境、阅读墙壁标识和逻辑推理来确定自己在空间站的具体位置。

难点：
1. 3D 空间结构：不仅有东南西北，还有"上层甲板"、"下层动力舱"、"垂直维修井"。
2. 相对位置推理："这里的阀门控制着楼下的..."、"头顶传来了..."。
3. 空间作为属性：位置不再是节点，而是实体（尸体、设备、怪物）的固有属性。
4. 观察点注入：所有相对描述（"这里"）必须解析为主角当前的观察点。
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.graphs import AutoSpatialGraph
from ontomem import MergeStrategy

load_dotenv()

# ==================== 1. 定义空间感知知识结构 (Schema) ====================


class DeepSeaEntity(BaseModel):
    """深海空间站实体节点"""

    name: str = Field(description="实体名称（人名、设备名、怪物代号、房间名）")
    category: str = Field(
        description="实体类型：'船员', '怪物', '关键设备', '房间/区域', '物品'",
        default="未知",
    )
    location: Optional[str] = Field(
        description="【关键字段】实体所处的具体位置。必须将相对位置解析为绝对位置。",
        default=None,
    )
    status: str = Field(
        description="当前状态（例如：已死亡、损坏、锁定、活跃）", default="正常"
    )
    description: str = Field(description="实体的详细描述")  

    def __repr__(self):
        loc_display = self.location if self.location else "位置未知"
        return f"📍 [{loc_display}] {self.name} ({self.status})"


class InteractionEdge(BaseModel):
    """实体间的互动关系"""

    source: str = Field(description="发起者")
    target: str = Field(description="对象")
    relation: str = Field(description="关系或动作（例如：'位于...内部'，'攻击'，'修复'）")
    details: str = Field(description="互动的详细描述")

    def __repr__(self):
        return f"{self.source} --[{self.relation}]--> {self.target}"


# ==================== 2. 深海探险日志文本 ====================

DEEP_SEA_LOG = """
【自动日志转录 - 救援队员编号：R-09】
【任务：阿特拉斯(Atlas)轨道工厂 - 重启冷却系统】
【当前环境：重力异常，高温警报】
【初始观察点：主气闸舱 (Airlock Alpha)】

08:00
气闸舱的警示灯在闪烁。我刚对接进入「主气闸舱」。这里的空气中弥漫着烧焦的臭氧味。
在我面前（气闸舱正中央）是两台处于休眠状态的安保机器人，型号分别是 "Sentinel-01" 和 "Loader-Bot Beta"。
Sentinel-01 的机械臂严重扭曲，似乎是被某种巨大的力量强行折断的，而 Loader-Bot Beta 的抓手里紧紧握着一张蓝色的 "工程维护卡"。

08:15
维护卡显示拥有「高能物理实验室-B区」的权限。
我看向气闸舱的左侧，那里的重型隔离门上喷着 "To Crew Quarters (船员休眠区)" 的字样，门禁面板显示"封锁中"。
右侧的舱门半开着，门楣上写着 "To Central Hub (中央枢纽)"。地上有一道明显的机油泄露痕迹，延伸进右侧的黑暗走廊中。

08:30
我穿过右侧舱门，进入了「中央枢纽」。这是一个巨大的圆形大厅，占据了空间站的主层。
这里的上方是网格状的金属地板。透过网格，我能看到头顶上方（上层甲板）悬挂着巨大的「备用冷却罐」。那个冷却罐表面覆盖着厚厚的冰霜，显然发生了泄露。
大厅的正中央是一座全息控制台，现在正不断弹出红色的错误代码。

08:45
顺着中央枢纽的地板格栅往下看，我能隐约看到下方的「动力反应堆舱」。那里闪烁着危险的橙色光芒。
突然，反应堆舱那个方向传来了一声金属爆裂的巨响。有什么设备炸了。
我想去找通往下层的梯子，但在枢纽的北侧墙壁上，我发现了一张破损的结构图。如果图纸没更新，那里正是「核心控制阀」所在的位置。

09:00
我决定先去寻找备用电源。根据记忆，就在这个大厅（中央枢纽）的东侧回廊尽头。
我走进东侧回廊。路过「维修车间」时，自动门突然卡住了。
通过门缝，我看到维修车间的一张工作台上，放着被称为 "Prototype-X" 的实验型外骨骼。它看起来像是被拆解了……外壳被暴力撕开。
最关键的是，在这台外骨骼的胸腔核心位置，插着一枚闪烁的「系统引导盘」。

09:10
我试图撬开门取出引导盘。
这时，工作台旁边的阴影里窜出了一只小型的 "Scavenger-Drone (清道夫无人机)"。它处于失控暴走状态。
它向我发射了激光切割束。我举起电磁脉冲盾，将它弹飞到旁边的工具柜上。这里的工具柜被撞得粉碎。

09:20
拿到系统引导盘后，我必须去恢复电力才能重启冷却。
回到中央枢纽，我找到了通往顶部的维修梯。我爬上了头顶的「上层甲板」。
这里的重力系统失效了，冷却液凝结成的冰晶在空中漂浮。
在上层甲板的最南端，就是「主控室」。透过破碎的观察窗，我看到里面的情况很糟。
站长AI终端 "Master Computer" 的屏幕完全碎裂。
终端机的数据接口上插着一根不明来源的数据线，一直连接到地板下的线路中。

09:30
我走进主控室。Master Computer 发出了断断续续的合成音，声音从四周的扬声器（位于主控室墙壁）里传出来：
"警告……核心温度临界……无法控制……"
我看了一眼备用屏幕。监控显示，刚才发出爆炸声的「核心控制阀」（位于我们正下方的底层/反应堆舱）已经被熔化的金属覆盖。
而那种高温熔融物，正通过通风管道，从底层慢慢向上层的各个房间蔓延。

09:45
我必须做出选择。是立刻撤离，还是尝试手动关闭反应堆？
无论如何，我现在的位置（主控室）温度正在急剧升高。通风管道里吹出了灼热的风。

09:50
我冲出主控室，回到上层甲板。这时我发现了一个关键信息——在备用冷却罐下方贴着一份维护日志：
"实验机体 Prototype-X 的核心电池极不稳定。原计划移送至 高能物理实验室-B区 进行拆解，暂存维修车间。"
这意味着，Prototype-X 原本是要送去「高能物理实验室-B区」的。而那间实验室的权限卡，正在主气闸舱里 Loader-Bot Beta 的手中。

10:00
我需要获取那张维护卡，但这意味着我要冒着高温熔穿地板的风险，返回主气闸舱。
在我犹豫的时候，我听到了休眠区的方向传来了结构断裂的声音。
通过内部通讯系统，我听到了一段自动广播：
"注意……高能物理实验室-B区……结构性……崩溃……电池组……连锁反应……"

10:15
我的决定已经定了。我必须到达「高能物理实验室-B区」切断电池组。
为了到达那里，我有两条路：
一是返回主气闸舱取维护卡（路径较远但温度较低）。
二是通过维修通道的紧急截断阀（位于底层的动力反应堆舱侧面）绕过门禁系统（不仅路远，而且是高温核心区，危险系数极大）。
"""

# ==================== 3. 运行提取 ====================


def run_demo():
    print("=" * 70)
    print("🌊 深海惊魂 - 空间感知分析模块启动")
    print("=" * 70)

    # 初始化 LLM
    print("\n🔧 初始化 LLM 和嵌入模型...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    # 创建 AutoSpatialGraph
    print("📊 构建 AutoSpatialGraph 实例...\n")
    # 关键：使用 location_in_node_extractor 解析位置属性
    graph = AutoSpatialGraph[DeepSeaEntity, InteractionEdge](
        node_schema=DeepSeaEntity,
        edge_schema=InteractionEdge,
        # Split extractors: base name and location separately
        node_key_extractor=lambda x: x.name,
        location_in_node_extractor=lambda x: x.location,
        edge_key_extractor=lambda x: f"{x.source}|{x.relation}|{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm,
        embedder=embedder,
        observation_location="Atlas深海科研站",  # 设定总的地理围栏
        extraction_mode="two_stage",
        node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger=MergeStrategy.LLM.BALANCED,
        prompt_for_node_extraction=(
            "提取深海空间站中的所有实体。\n"
            "关键空间规则：\n"
            "1. **位置注入**：仔细分析文本中的相对位置描述。例如，如果主角在'中央枢纽'，那么'头顶上方'应被解析为'上层甲板'。\n"
            "2. **属性化**：不要提取'上层'、'左边'、'地下'作为节点。将它们解析为实体具体的 location 属性。\n"
            "3. **3D结构**：注意区分甲板层级（上层甲板、主层、底层/动力舱）。\n"
            "4. **实体类型**：如果是尸体，状态标为'死亡'但仍需提取为实体（携带关键物品）。\n"
        ),
        prompt_for_edge_extraction=(
            "提取实体之间所有有意义的互动与关联关系。由于位置已作为实体属性记录，**请勿提取简单的'位于...内部'关系**。\n\n"
            "重点提取以下类型的关系：\n"
            "1. **动作与交互**：例如 '攻击'、'修复'、'操作'、'持有/携带'、'观察到'。\n"
            "2. **物理连接与阻挡**：例如 '连接着'（线缆）、'阻挡了'（门/障碍物）、'覆盖'。\n"
            "3. **控制与功能**：例如 '门禁卡->开启->门'、'阀门->控制->管道'。\n"
            "4. **因果与逻辑**：例如 '爆炸->导致->泄露'、'日志->提及->怪物'、'任务->目标是->设备'。\n"
        ),
        verbose=True,  # 开启日志以便观察提取过程
        chunk_size=2048,
    )

    print(f"\n📖 正在加载深海探险日志...")
    print("=" * 70)
    print(DEEP_SEA_LOG[:300] + "...")
    print("=" * 70)

    # 执行提取
    print("\n⚙️  执行空间感知提取（解析相对方位词）...\n")
    graph.feed_text(DEEP_SEA_LOG)

    # ==================== 4. 空间分析结果 ====================

    print("\n" + "=" * 70)
    print(f"✅ 空间结构分析完成！")
    print("=" * 70)
    print(f"   提取的实体: {len(graph.nodes)} 个")
    print(f"   记录的互动关系: {len(graph.edges)} 个")

    print("\n" + "-" * 70)
    print("📍 空间站实体分布 (Nodes - 按位置分组)")
    print("-" * 70)

    # 按位置简单的分组打印
    nodes_by_location = {}
    for node in graph.nodes:
        # 简单处理一下位置字符串，取前几个字作为粗略分组
        loc_key = node.location or "位置未知"
        if loc_key not in nodes_by_location:
            nodes_by_location[loc_key] = []
        nodes_by_location[loc_key].append(node)

    for loc, entities in sorted(nodes_by_location.items()):
        print(f"\n🏢 区域: {loc}")
        for entity in entities:
            print(f"   - {entity.name} [{entity.category}]: {entity.status}")

    print("\n" + "-" * 70)
    print("🔗 关键互动关系 (Edges)")
    print("-" * 70)
    for i, edge in enumerate(graph.edges[:15]):  # 只打印前15个
        print(f"   {i+1}. {edge}")
    if len(graph.edges) > 15:
        print(f"   ... (还有 {len(graph.edges) - 15} 条关系)")

    # ==================== 5. 空间情报检索 (Search 阶段) ====================

    print("\n" + "=" * 70)
    print("🔍 空间站导航系统 - 向量检索阶段")
    print("=" * 70)

    # 建立索引
    print("\n🏗️  构建向量索引...")
    graph.build_index()

    # 场景1：找怪物
    q1 = "空间站里有哪些怪物或威胁？它们在哪？"
    print(f"\n❓ Search Query: {q1}")
    try:
        nodes, edges = graph.search(q1, top_k=5)
        if nodes:
            print(f"  📍 相关实体:")
            for n in nodes:
                print(f"    - {n}")
        if edges:
            print(f"  🔗 相关关系:")
            for e in edges:
                print(f"    - {e}")
        if not nodes and not edges:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  检索失败: {e}")

    # 场景2：找关键物品
    q2 = "黑匣子在哪里找到的？"
    print(f"\n❓ Search Query: {q2}")
    try:
        nodes, edges = graph.search(q2, top_k=3)
        if nodes:
            print(f"  📍 相关实体:")
            for n in nodes:
                print(f"    - {n}")
        if edges:
            print(f"  🔗 相关关系:")
            for e in edges:
                print(f"    - {e}")
        if not nodes and not edges:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  检索失败: {e}")

    # 场景3：3D 空间理解
    q3 = "动力反应堆舱（底层）里有什么东西？"
    print(f"\n❓ Search Query: {q3}")
    try:
        nodes, edges = graph.search(q3, top_k=5)
        if nodes:
            print(f"  📍 相关实体:")
            for n in nodes:
                print(f"    - {n}")
        if edges:
            print(f"  🔗 相关关系:")
            for e in edges:
                print(f"    - {e}")
        if not nodes and not edges:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  检索失败: {e}")

    # 场景4：权限卡位置
    q4 = "权限卡在哪里？"
    print(f"\n❓ Search Query: {q4}")
    try:
        nodes, edges = graph.search(q4, top_k=3)
        if nodes:
            print(f"  📍 相关实体:")
            for n in nodes:
                print(f"    - {n}")
        if edges:
            print(f"  🔗 相关关系:")
            for e in edges:
                print(f"    - {e}")
        if not nodes and not edges:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  检索失败: {e}")


    # ==================== 6. 交互式情报问答 (Chat 阶段) ====================

    print("\n" + "=" * 70)
    print("💬 深海空间站 - 交互式情报分析终端")
    print("=" * 70)
    print("系统提示: 您现在可以直接用自然语言询问关于空间结构、实体关系和危险评估的复杂问题。\n")

    chat_queries = [
        "这个空间站里发生了什么悲剧？请根据现场的尸体、伤口和位置信息推断事件的发展顺序。",
        "Subject X 是如何逃出医务室的？它现在可能在空间站的哪些地方？",
        "潜水员如果要从医务室安全抵达生物实验室-B区，应该如何规划路线？需要注意哪些危险？",
    ]

    for i, q in enumerate(chat_queries, 1):
        print(f"👤 [深海调查官 {i}]: {q}")
        print("🤖 [AI 空间分析引擎]: 正在检索空间拓扑结构并生成情报分析报告...")
        
        try:
            # 使用 chat 接口进行 RAG 问答
            response = graph.chat(q)
            print(f"📄 [情报简报]:\n{response.content}\n")
        except Exception as e:
            print(f"⚠️  系统响应异常: {e}\n")

    # ==================== 7. 保存 ====================

    print("\n" + "=" * 70)
    print("💾 保存空间知识图谱...")
    print("=" * 70)
    save_path = project_root / "temp" / "auto_spatial_graph_demo"
    try:
        graph.dump(str(save_path))
        print(f"   已保存至: {save_path}")
    except Exception as e:
        print(f"   保存失败: {e}")

    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
