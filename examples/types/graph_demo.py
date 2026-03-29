"""
AutoGraph Demo: MMORPG Guild Drama (游戏公会恩仇录) 🎮⚔️

场景背景：
在一个名为《永恒之境》的游戏中，顶尖公会"星辰阁"在攻略最终BOSS时发生了严重的内讧。
这段文本是一篇游戏论坛的"818"（八卦爆料）帖子。

难点：
1. 术语混杂：ID、职业代称（主T、奶妈）、外号混用。
2. 关系复杂：涉及治疗、仇恨（Aggro）、装备分配（Loot）、公会管理。
3. 讽刺与隐喻：LLM 需要理解"划水"、"黑装备"等游戏黑话。

使用方法：
    python examples/types/graph_demo.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.types import AutoGraph
from ontomem import MergeStrategy

import dotenv

dotenv.load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "mmorpg_guild_drama.md"

# ==================== 1. 定义游戏知识结构 (Schema) ====================


class GameEntity(BaseModel):
    """游戏实体节点（包含玩家、BOSS、NPC、公会等）"""

    name: str = Field(description="实体名称或ID，例如玩家ID、BOSS名、'星辰阁'")
    category: str = Field(
        description="实体类型，例如：'玩家', 'BOSS', '公会', '群体'", default="玩家"
    )
    info: str = Field(
        description="职业、描述或状态，如'战神'、'最终BOSS'、'解散'", default="未知"
    )

    def __repr__(self):
        return f"🎮 [{self.category}] {self.name} <{self.info}>"


class GameInteraction(BaseModel):
    """游戏互动边"""

    source: str = Field(description="发起互动的实体名称")
    target: str = Field(description="互动的对象名称（可以是玩家、BOSS或公会）")
    action_type: str = Field(
        description="互动类型：'治疗', '攻击', '抢装备', '辱骂', '踢出队伍', '拉入队伍'"
    )
    details: str = Field(description="具体的互动描述或原因")

    def __repr__(self):
        return (
            f"⚡ {self.source} --[{self.action_type}]--> {self.target} ({self.details})"
        )


# ==================== 2. 运行提取 ====================

def run_demo():
    print("=" * 60)
    print("🕹️  正在加载游戏日志分析模块...")
    print("=" * 60)

    # 读取输入文件
    print(f"\n📖 正在阅读游戏论坛爆料帖: {INPUT_FILE}")
    print("=" * 60)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        game_forum_post = f.read()
    print(game_forum_post[:200] + "...")
    print("=" * 60)

    # 初始化 LLM
    print("\n🔧 初始化 LLM 和嵌入模型...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    # 创建 AutoGraph
    print("📊 构建 AutoGraph 实例...\n")
    graph = AutoGraph[GameEntity, GameInteraction](
        node_schema=GameEntity,
        edge_schema=GameInteraction,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}_{x.action_type}_{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm,
        embedder=embedder,
        extraction_mode="two_stage",
        node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
        prompt_for_node_extraction=(
            "提取文本中的所有游戏实体作为节点。关键：必须提取BOSS（如深渊魔龙）、公会（如星辰阁）以及关键玩家。"
            "如果文中提到'全团'或'所有人'，也将其作为一个群体实体提取。"
            "注意识别ID和别名，将别名（如'团长'）标准化为具体ID。\n\n"
            "## 源文本:\n"
            "{source_text}"
        ),
        prompt_for_edge_extraction=(
            "提取实体之间的互动行为。"
            "重要规则：互动中的 source 和 target 必须是你刚才提取过的实体名称。"
            "例如，如果之前提取了节点'深渊魔龙'，那么攻击BOSS的互动 target 必须填'深渊魔龙'。"
            "### 已知的实体列表\n"
            "{known_nodes}\n\n"
            "## 源文本:\n"
            "{source_text}\n\n"
        ),
    )

    # 执行提取
    print("\n⚙️  执行两阶段提取...\n")
    graph.feed_text(game_forum_post)

    # ==================== 4. 战报分析 ====================

    print("\n" + "=" * 60)
    print(f"✅ 分析完成!")
    print("=" * 60)
    print(f"   找到玩家/BOSS: {len(graph.nodes)} 个")
    print(f"   记录的互动事件: {len(graph.edges)} 个")

    print("\n" + "-" * 60)
    print("🛡️ 角色面板 (Nodes)")
    print("-" * 60)
    for i, p in enumerate(graph.nodes, 1):
        print(f"{i}. {p}")

    print("\n" + "-" * 60)
    print("⚔️  战斗和互动记录 (Edges)")
    print("-" * 60)
    for i, e in enumerate(graph.edges, 1):
        print(f"{i}. {e}")

    # ==================== 5. 语义搜索 (查内鬼) ====================

    print("\n" + "=" * 60)
    print("🔍 游戏管理员(GM)调查查询模块")
    print("=" * 60)

    # 建立索引（默认同时索引节点和边，无需指定参数）
    graph.build_index()

    # 场景1: 找谁拿了装备？
    q1 = "谁拿走了传说武器？"
    print(f"\n❓ Query: {q1}")
    try:
        # 默认同时搜索节点和边，返回 Tuple[nodes, edges]
        nodes, edges = graph.search(q1, top_k_nodes=3, top_k_edges=3)
        interactions = edges
        if interactions:
            for i in interactions:
                print(f"  🚨 {i}")
        else:
            print("  (没有找到相关记录)")
    except Exception as e:
        print(f"  (搜索出错: {e})")

    # 场景2: 找特定的职业
    q2 = "谁是治疗职业的？"
    print(f"\n❓ Query: {q2}")
    try:
        nodes, edges = graph.search(q2, top_k_nodes=3, top_k_edges=3)
        healers = nodes
        if healers:
            for h in healers:
                print(f"  🚑 {h}")
        else:
            print("  (没有找到治疗职业)")
    except Exception as e:
        print(f"  (搜索出错: {e})")

    # 场景3: 找矛盾中心
    q3 = "谁和谁发生了冲突？"
    print(f"\n❓ Query: {q3}")
    try:
        nodes, edges = graph.search(q3, top_k_nodes=3, top_k_edges=3)
        conflicts = edges
        if conflicts:
            for c in conflicts:
                print(f"  🔥 {c}")
        else:
            print("  (没有找到冲突记录)")
    except Exception as e:
        print(f"  (搜索出错: {e})")

    # 场景4: 找坦克
    q4 = "谁是主坦克？"
    print(f"\n❓ Query: {q4}")
    try:
        nodes, edges = graph.search(q4, top_k_nodes=3, top_k_edges=3)
        tanks = nodes
        if tanks:
            for t in tanks:
                print(f"  🛡️  {t}")
        else:
            print("  (没有找到坦克)")
    except Exception as e:
        print(f"  (搜索出错: {e})")

    # ==================== 6. 交互式对话 (Chat RAG) ====================

    print("\n" + "=" * 60)
    print("💬 进入交互式对话模式")
    print("=" * 60)
    print("🤖 正在基于提取的知识图谱回答复杂问题...\n")

    chat_queries = [
        "请总结这个公会冲突的核心原因。",
        "暗影刺客和小甜甜的行为对团队造成了什么影响？",
        "从这个事件中，我们学到了什么关于公会管理的经验？",
    ]

    for q in chat_queries:
        print(f"👤 提问: {q}")
        try:
            response = graph.chat(q)
            print(f"🤖 回答: {response.content}\n")
        except Exception as e:
            print(f"⚠️ 对话异常: {e}\n")

    # ==================== 7. 保存知识图谱 ====================

    print("\n" + "=" * 60)
    print("💾 保存知识图谱到本地...")
    print("=" * 60)
    save_path = project_root / "temp" / "auto_graph_demo"
    try:
        graph.dump(save_path)
        print(f"✅ 图谱已保存到: {save_path}")
    except Exception as e:
        print(f"⚠️  保存失败: {e}")

    graph.show(
        node_label_extractor=lambda n: f"{n.name} ({n.category})",
        edge_label_extractor=lambda e: e.action_type,
    )


if __name__ == "__main__":
    run_demo()
