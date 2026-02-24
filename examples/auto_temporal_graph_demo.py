"""
AutoTemporalGraph Demo: 谍战惊悚 - 柏林的48小时 🕵️‍♀️💣

场景背景：
在冷战时期的东柏林，一名CIA特工Elias必须在48小时内阻止恐怖分子的炸弹计划。
时间信息隐含在叙述中，通过人物对话、观察和行动序列自然出现。

难点：
1. 时间隐藏在对话中："看了一眼手表"、"两分钟后"等自然表述
2. 并发事件：同一时间多个地点的不同行动
3. 时间精度：需要提取到分钟级别（HH:MM）
4. 实体合并：同一个人的不同代称需要被识别和合并
"""

import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.types import AutoTemporalGraph
from ontomem import MergeStrategy

import dotenv

dotenv.load_dotenv()

# ==================== 1. 定义时间感知知识结构 (Schema) ====================


class SpyEntity(BaseModel):
    """谍战实体节点（特工、地点、组织等）"""

    name: str = Field(description="实体名称，例如特工ID、地点名、组织名")
    category: str = Field(
        description="实体类型：'特工', '地点', '组织', '物品', '事件'", default="未知"
    )
    description: str = Field(
        description="实体的详细描述或身份背景", default=""
    )

    def __repr__(self):
        return f"🕵️ [{self.category}] {self.name} - {self.description}"


class TemporalAction(BaseModel):
    """时间感知的行动边"""

    source: str = Field(description="行动发起者")
    target: str = Field(description="行动对象（可以是人、地点或物品）")
    action: str = Field(description="具体行动内容")
    timestamp: Optional[str] = Field(
        description="行动发生的具体时间点（YYYY-MM-DD HH:MM 格式，精确到分钟）", default=None
    )
    description: str = Field(
        description="行动的详细描述、上下文或发生地点", default=""
    )

    def __repr__(self):
        time_str = f" @ {self.timestamp}" if self.timestamp else ""
        desc_str = f" ({self.description})" if self.description else ""
        return f"⚡ {self.source} --[{self.action}]--> {self.target}{time_str}{desc_str}"


# ==================== 2. 谍战叙述文本 ====================

SPY_THRILLER_NARRATIVE = """
【CIA 绝密档案：代号"日蚀"行动日志】
【日期：2024-03-15】
【地点：柏林】
【特工：Elias】

08:30，柏林的晨雾还未散去。特工 Elias 穿着一身灰色风衣，在勃兰登堡门附近的 Tiergarten 公园长椅上坐下。他在喂鸽子，看似悠闲，实则警惕地观察四周。

五分钟后（08:35），联络员 Sarah 骑着自行车经过，故意丢下了一份报纸。夹在报纸里的是一张加密纸条："Viktor 在东区活动。第一枚炸弹已部署在 Friedrichstraße 车站。"

Elias 迅速离开。09:00，他在安全屋换装完毕，携带了干扰器和开锁工具。

09:15，Elias 抵达 Friedrichstraße 车站。车站人流如织。他在月台的自动售票机旁，发现了 Viktor 的助手 Bond。Bond 手提一个沉重的黑色公文包，神色慌张，正在频繁看表。

此时（09:15），在城市的另一端，废弃工厂的地下室里，Viktor 正在通过无线电向所有战斗小组下达指令："不用等了，现在就启动倒计时。"

09:42，Bond 走向了车站深处的地下维修通道入口。Elias 悄无声息地跟了进去。通道里光线昏暗，只有滴水的声音。

突然，Bond 猛地转身，手里多了一把消音手枪。两人展开了近身搏斗。09:44，Bond 试图按下公文包上的红色按钮。

09:45，随着一声沉闷的枪响，Elias 击中了 Bond 的手腕，起爆器滑落到铁轨旁。此时公文包上的红色 LED 灯亮起，显示倒计时剩余时间：15分钟。

Elias 开始拆弹。这其实是一个复杂的诱饵装置。他在切断第一根红线时，发现电路逻辑不对。现在是 09:50。

"真的炸弹在哪里？" Elias 踩住 Bond 的伤口逼问。
Bond 疼得满头大汗，狞笑道："你来不及了。真家伙在威廉皇帝纪念教堂。定时 10:30 引爆，那里现在全是游客。"

10:05，Elias 冲出车站，抢了一辆停在路边的杜卡迪摩托车。他在早高峰的车流中狂飙，连闯三个红灯。
与此同时（10:05），Sarah 收到了 Elias 的警报，带领 CIA 战术小队开始疏散教堂外围的人群。

10:15，Elias 冲进教堂。他在螺旋楼梯上被两名雇佣兵拦截。经过一番激烈的枪战，他解决了守卫，冲上钟楼顶部。

10:20，他在钟楼顶层发现了 Viktor。Viktor 手里抓着扩音器，似乎正准备发表某种宣言。看到 Elias，Viktor 拔出了匕首。

10:25，Elias 与 Viktor 在狭窄的钟楼平台展开肉搏。Viktor 试图将不知情的游客作为人质，Elias 抓住破绽，一记重拳将 Viktor 击倒，随后将其拷在栏杆上。

10:26，Elias 找到了藏在大钟底座下的生化炸弹。显示屏跳动着：00:03:59。
这不是普通的定时炸弹，还有倾斜传感器。

10:28，Elias 满头大汗。他通过耳机连接了 Sarah 传来的蓝图指示。"剪蓝线，还是黄线？"
"等等！" Sarah 在耳机里喊道，"图纸有更新，是红蓝相间的那根地线！"
Elias 深吸一口气，剪断了那根不起眼的细线。

计时器定格在 00:01:30。危机解除。

11:00，警方封锁线建立。Viktor 和 Bond 被押上囚车。Elias 在混乱的人群中压低帽檐，转身走进了一条小巷，消失在柏林的喧嚣中。
"""

# ==================== 3. 运行提取 ====================


def run_demo():
    print("=" * 70)
    print("🕵️  柏林谍战行动 - 时间线分析模块启动")
    print("=" * 70)

    # 初始化 LLM
    print("\n🔧 初始化 LLM 和嵌入模型...")
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    # 创建 AutoTemporalGraph
    print("📊 构建 AutoTemporalGraph 实例...\n")
    graph = AutoTemporalGraph[SpyEntity, TemporalAction](
        node_schema=SpyEntity,
        edge_schema=TemporalAction,
        # 1. 实体ID提取规则
        node_key_extractor=lambda x: x.name,
        # 2. 时间感知的行动唯一性规则（分离 edge key 和 time）
        edge_key_extractor=lambda x: f"{x.source}|{x.action}|{x.target}",
        time_in_edge_extractor=lambda x: x.timestamp or "",
        # 3. 行动双方映射规则
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm,
        embedder=embedder,
        # 观察时间：故事背景
        observation_time="2024-03-15",
        # 两阶段提取
        extraction_mode="two_stage",
        # 智能合并：能识别"Elias" = "特工" 等
        node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger=MergeStrategy.LLM.BALANCED,
        # 针对谍战的特化提示词
        prompt_for_node_extraction=(
            "提取文本中的所有关键实体作为节点。包括：特工/人物、地点、组织、物品、事件。\n"
            "关键要求：\n"
            "1. 提取所有人名（Elias、Viktor、Bond、Katya、Sarah等）及其别称或代称\n"
            "2. 提取所有地点（柏林、Black Swan酒吧、Charlottenburg Palace等）\n"
            "3. 提取组织（CIA、KGB等）和物品（炸弹、枪、起爆器等）\n"
            "4. 将代称和别名标准化为主要名称"
        ),
        prompt_for_edge_extraction=(
            "提取人物之间和与物品/地点之间的**时间感知的行动**。\n"
            "关键要求：\n"
            "1. 时间信息可能隐含在叙述中，如'看了一眼手表——秒针刚好划过十二点。现在是 18:42'\n"
            "2. 相对时间表达如'两分钟后'、'十分钟过去了'需要根据前文推算具体时间\n"
            "3. 并发事件（'与此同时'）需提取相同的时间戳\n"
            "4. 提取精确到分钟级别（HH:MM格式），日期使用 YYYY-MM-DD\n"
            "5. 在 description 字段中记录行动发生的地点或其他上下文信息\n"
            "6. 如果时间不明确，填写空值而不是猜测"
        ),
        verbose=True,
        chunk_size=2048,
    )

    print(f"\n📖 正在加载谍战行动日志...")
    print("=" * 70)
    print(SPY_THRILLER_NARRATIVE[:300] + "...")
    print("=" * 70)

    # 执行提取
    print("\n⚙️  执行两阶段时间感知提取...\n")
    graph.feed_text(SPY_THRILLER_NARRATIVE)

    # ==================== 4. 时间线分析 ====================

    print("\n" + "=" * 70)
    print(f"✅ 时间线分析完成！")
    print("=" * 70)
    print(f"   提取的实体: {len(graph.nodes)} 个")
    print(f"   记录的行动事件: {len(graph.edges)} 个")

    print("\n" + "-" * 70)
    print("🕵️  实体信息 (Nodes)")
    print("-" * 70)
    for i, entity in enumerate(graph.nodes, 1):
        print(f"{i}. {entity}")

    print("\n" + "-" * 70)
    print("⚡ 时间感知行动时间表 (Edges)")
    print("-" * 70)
    
    # 排序有时间的边
    all_sorted_edges = sorted(graph.edges, key=lambda x: x.timestamp or "9999-12-31")
    for i, action in enumerate(all_sorted_edges, 1):
        print(f"{i}. {action}")

    # ==================== 5. 情报检索系统 ====================

    print("\n" + "=" * 70)
    print("🔍 CIA 情报检索系统")
    print("=" * 70)

    # 建立索引
    graph.build_index()

    # 检索场景1: 找关键人物
    q1 = "Elias做了什么？"
    print(f"\n❓ Query: {q1}")
    try:
        nodes, edges = graph.search(q1, top_k_nodes=5, top_k_edges=5)
        if edges:
            for e in edges:
                print(f"  ⚡ {e}")
        else:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  (检索出错: {e})")

    # 检索场景2: 找地点
    q2 = "发生在地铁站的事件有哪些？"
    print(f"\n❓ Query: {q2}")
    try:
        nodes, edges = graph.search(q2, top_k_nodes=5, top_k_edges=5)
        if edges:
            for e in edges:
                print(f"  📍 {e}")
        else:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  (检索出错: {e})")

    # 检索场景3: 找对抗
    q3 = "Viktor和Elias之间的冲突"
    print(f"\n❓ Query: {q3}")
    try:
        nodes, edges = graph.search(q3, top_k_nodes=5, top_k_edges=5)
        if edges:
            for e in edges:
                print(f"  🔥 {e}")
        else:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  (检索出错: {e})")

    # 检索场景4: 找时间关键点
    q4 = "下午的行动"
    print(f"\n❓ Query: {q4}")
    try:
        nodes, edges = graph.search(q4, top_k_nodes=5, top_k_edges=5)
        if edges:
            for e in edges:
                print(f"  ⏰ {e}")
        else:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  (检索出错: {e})")

    # 检索场景5: 找组织
    q5 = "CIA和KGB分别做了什么？"
    print(f"\n❓ Query: {q5}")
    try:
        nodes, edges = graph.search(q5, top_k_nodes=5, top_k_edges=5)
        if nodes:
            print(f"  🏢 相关实体:")
            for n in nodes:
                print(f"    - {n}")
        if edges:
            print(f"  📋 相关行动:")
            for e in edges:
                print(f"    - {e}")
        if not nodes and not edges:
            print("  (无相关记录)")
    except Exception as e:
        print(f"  (检索出错: {e})")

    # ==================== 6. 交互式情报问答 (Chat) ====================

    print("\n" + "=" * 70)
    print("💬 正在切换至：CIA 交互式情报分析终端")
    print("=" * 70)
    print("系统提示: 您现在可以直接用自然语言询问关于行动的细节、动机或因果关系。\n")

    chat_queries = [
        "Viktor的炸弹袭击计划最终是如何失败的？请按时间顺序列出导致他失败的关键转折点。",
        "Elias在整个行动中使用了哪些交通工具？请结合时间点说明。",
        "这次行动中，哪些人物的决策改变了事件的进程？"
    ]

    for q in chat_queries:
        print(f"👤 [高级分析师]: {q}")
        print("🤖 [系统核心]: 正在检索关联情报节点并生成分析报告...")
        
        try:
            # 使用 chat 接口进行 RAG 问答
            response = graph.chat(q)
            print(f"📄 [情报简报]:\n{response.content}\n")
        except Exception as e:
            print(f"⚠️ 系统响应异常: {e}\n")

    # ==================== 7. 保存知识图谱 ====================

    print("\n" + "=" * 70)
    print("💾 保存时间感知知识图谱到本地...")
    print("=" * 70)
    save_path = project_root / "temp" / "auto_temporal_graph_demo"
    try:
        graph.dump(save_path)
        print(f"✅ 图谱已保存到: {save_path}")
    except Exception as e:
        print(f"⚠️  保存失败: {e}")

    print("\n" + "=" * 70)
    print("✅ 演示完成！时间线已成功提取并分析。")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
