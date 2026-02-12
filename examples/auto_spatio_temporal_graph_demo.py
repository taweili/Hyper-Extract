"""
AutoSpatioTemporalGraph Demo: 谍战惊悚 - 柏林的48小时 (时空增强版) 🕵️‍♀️🏙️

场景背景：
在冷战时期的东柏林，特工 Elias 的行动不仅在时间线上推进，其地理位置的变化也至关重要。
本 Demo 演示如何同时提取和处理：
1. 时间信息 (Timestamp)
2. 空间信息 (Location/Coordinates)
3. 时空上下文注入 (Observation Time & Location)

核心特性：
- 分离的时间/空间提取器 (Time & Location Extractors)
- 自动融合的时空唯一键 (Composite Spatio-Temporal Key)
- 相对时空消歧 (Relative Spatio-Temporal Resolution)
"""

import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.types import AutoSpatioTemporalGraph

import dotenv

dotenv.load_dotenv()

# ==================== 1. 定义时空感知知识结构 (Schema) ====================

class SpyEntity(BaseModel):
    """谍战实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：'特工', '地点', '组织', '物品'", default="未知")
    description: str = Field(description="实体的详细描述", default="")

    def __repr__(self):
        return f"🕵️ [{self.category}] {self.name}"

class SpatioTemporalAction(BaseModel):
    """时空感知的行动边"""
    source: str = Field(description="行动发起者")
    target: str = Field(description="行动对象")
    action: str = Field(description="具体行动")
    time: Optional[str] = Field(description="发生的具体时间 (YYYY-MM-DD HH:MM)", default=None)
    location: Optional[str] = Field(description="发生的具体地点", default=None)
    details: str = Field(description="行动细节描述", default="")

    def __repr__(self):
        ctx = []
        if self.time: ctx.append(f"⏰ {self.time}")
        if self.location: ctx.append(f"📍 {self.location}")
        ctx_str = f" [{' '.join(ctx)}]" if ctx else ""
        return f"⚡ {self.source} --[{self.action}]--> {self.target}{ctx_str}"

# ==================== 2. 叙述文本 (包含丰富的时空信息) ====================

ST_NARRATIVE = """
【任务简报：代号"碎冰"】
【当前基准：2024-03-15，柏林勃兰登堡门】

08:30，Elias 抵达了勃兰登堡门。他在广场西侧的长椅上坐下，距离标志性建筑仅50米。他正在等待接头指令。
五分钟后（08:35），Sarah 骑车从他身边经过，故意丢下一份夹着代码的《柏林日报》。

09:00，Elias 穿过街道，进入了位于 Friedrichstraße 车站附近的一个隐藏安全屋。他在地下室的一层准备了电子干扰器。
与此同时（09:00），主要目标 Viktor 出现在亚历山大广场（Alexanderplatz）。他在电视塔底层的咖啡馆购买了一杯拿铁，并与一名身份不明的男子交谈了五分钟。

09:15，Viktor 离开了亚历山大广场，乘出租车前往查理检查站（Checkpoint Charlie）。他的公文包里显然装着危险品。

09:45，冲突在 Friedrichstraße 车站的地下维修通道正式爆发。Elias 追上了 Bond（Viktor 的副手）。在一阵密集的交火后，Elias 成功击落了 Bond 手中的无线起爆器。
起爆器掉落在 3 号站台生锈的导轨上，距离带电轨道仅几厘米。

10:10，Viktor 出现在查理检查站附近的马路旁，他正准备与那里的地下组织会合。Sarah 的监视小组记录下了他与另一名接头人交换了一个蓝色的U盘。

10:30，真炸弹的最终位置被确认为威廉皇帝纪念教堂（Kaiser Wilhelm Memorial Church）。
Elias 在 10:28 冲上了教堂钟楼的最顶层平台，冒着巨大的生命危险剪断了那根决定生死的红线。

11:00，警方封锁了教堂周围的所有街道。Elias 悄无声息地从后门撤离，回到了勃兰登堡门附近的接头点。
"""

# ==================== 3. 运行提取 ====================

def run_demo():
    print("=" * 80)
    print("🕵️  AutoSpatioTemporalGraph 演示：冷战柏林行动")
    print("=" * 80)

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    embedder = OpenAIEmbeddings()

    # 创建 AutoSpatioTemporalGraph 实例
    graph = AutoSpatioTemporalGraph[SpyEntity, SpatioTemporalAction](
        node_schema=SpyEntity,
        edge_schema=SpatioTemporalAction,
        node_key_extractor=lambda x: x.name,
        # 基础边 Key: (谁, 做了什么, 对谁)
        edge_key_extractor=lambda x: f"{x.source}|{x.action}|{x.target}",
        # 分离提取：时间
        time_in_edge_extractor=lambda x: x.time or "",
        # 分离提取：空间
        location_in_edge_extractor=lambda x: x.location or "",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm,
        embedder=embedder,
        # 时空上下文注入
        observation_time="2024-03-15",
        observation_location="Brandenburg Gate, Berlin",
        # 提示词微调
        prompt_for_edge_extraction=(
            "精确捕获行动发生的时间和地点。\n"
            "特别是：\n"
            "- 如果提到'这里'，指 Brandenburg Gate\n"
            "- 提取具体的车站名、建筑物名或房间号"
        ),
        verbose=True
    )

    print("\n⚙️  执行时空感知提取流程...")
    graph.feed_text(ST_NARRATIVE)

    # ==================== 4. 结果展示 ====================

    print("\n" + "=" * 80)
    print(f"📊 提取结果统计：{len(graph.nodes)} 节点, {len(graph.edges)} 边")
    print("=" * 80)

    print("\n📍 关键时空事件表 (Edges)：")
    # 按时间排序展示
    sorted_edges = sorted(graph.edges, key=lambda x: (x.time or "9999", x.location or ""))
    for i, edge in enumerate(sorted_edges, 1):
        print(f"{i}. {edge}")

    # ==================== 5. 增强检索测试 ====================
    print("\n" + "=" * 80)
    print("🔍 多维时空检索测试")
    print("=" * 80)
    graph.build_index()

    print("\n📍 检索场景 1: 地点相关检索")
    q1 = "在亚历山大广场（Alexanderplatz）发生了什么？"
    _, edges1 = graph.search(q1, top_k_edges=3)
    for e in edges1: print(f"  ✅ {e}")

    print("\n💼 检索场景 2: 关键物品流转")
    q2 = "Viktor 的公文包和蓝色 U 盘在哪里出现的？"
    _, edges2 = graph.search(q2, top_k_edges=3)
    for e in edges2: print(f"  ✅ {e}")

    print("\n⏰ 检索场景 3: 时间同步检索")
    q3 = "早上 09:00 这一刻，Elias 和 Viktor 分别在内存中留下了什么记录？"
    _, edges3 = graph.search(q3, top_k_edges=5)
    for e in edges3: print(f"  ✅ {e}")

    # ==================== 6. 交互式分析 (Chat) ====================
    print("\n" + "=" * 80)
    print("💬 时空感知交互式情报分析 (Chat)")
    print("=" * 80)

    chat_queries = [
        "请按时间顺序列出 Elias 在这次行动中的所有地理位置变化轨迹。",
        "描述 Viktor 在亚历山大广场和查理检查站的具体活动细节及其时间点。",
        "对比分析 Elias 和 Viktor 在 09:00 时的动作，他们是否在同一地点？"
    ]

    for cq in chat_queries:
        print(f"\n👤 [高级分析师]: {cq}")
        response = graph.chat(cq)
        print(f"🤖 [情报分析系统]:\n{response.content}")

    # ==================== 7. 保存图谱 ====================
    print("\n" + "=" * 80)
    save_path = project_root / "temp" / "auto_spatio_temporal_demo"
    graph.dump(save_path)
    print(f"💾 完整时空知识图谱已持久化至: {save_path}")

if __name__ == "__main__":
    run_demo()
