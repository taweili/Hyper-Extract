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

from hyperextract.methods.typical import KG_Gen

load_dotenv()

# ==============================================================================
# 示例文本 - 来自真实场景的数据
# ==============================================================================

EXAMPLE_TEXT = """
【818】星辰阁公会昨晚解散的真相！团长黑装备还骂人！这简直是最大的内讧事件！

楼主：匿名玩家（ID已隐藏）
发帖时间：今天 23:45

我是星辰阁的一个普通成员，昨晚目睹了整个悲剧的发生。我觉得必须把真相告诉大家。

首先介绍一下我们的团队阵容：
- 会长兼主坦克：雷霆之怒（真实ID：张三，40级战士，装备评分9999）
- 副坦克：坚如磐石（真实ID：李四，38级盾战士，评分8800，人很老实）
- 主奶妈（治疗）：小甜甜（真实ID：王五，38级圣骑士，评分8600）
- 副奶妈：月光治愈者（真实ID：赵六，35级德鲁伊，评分7500）
- DPS输出1（弓箭手）：暗影刺客（真实ID：孙七，39级猎手，评分9200）
- DPS输出2（法师）：火球术一级（真实ID：周八，37级法师，评分8400）
- DPS输出3（剑客）：风云剑侠（真实ID：吴九，36级剑士，评分7800）
- 远程法师：冰霜法咒（真实ID：郑十，35级冰法，评分7600）

昨晚晚上8点，我们集合在副本入口。这是星辰阁第三次挑战"深渊魔龙"这个最终BOSS。
前两次都失败了，主要是因为配合不够默契。但是昨晚会长雷霆之怒发誓说一定要拿下这个BOSS。

副本开始，一切似乎很顺利。前5个小怪都被我们轻松秒杀。
然后大家来到了BOSS房间——深渊魔龙的巢穴。这是一个超级庞大的紫龙，满血时候气势相当恐怖。

战斗一开始，雷霆之怒（会长）冲上去拉住了仇恨值。坚如磐石（副坦克）站在侧翼进行补充。
小甜甜不断给雷霆之怒刷HOT（持续恢复）。月光治愈者给坚如磐石加盾。
前期看起来非常完美，大家的DPS输出也打得相当漂亮。

但是，大约打了5分钟，问题出现了。

坚如磐石（副坦克）突然掉线了！这太糟糕了。我们在公会频道里看到他的在线状态变成了灰色。
公会会长雷霆之怒看到这一幕，血压瞬间上升（我可以想象他的脸色）。

为什么副坦会掉线呢？大家后来才明白——坚如磐石的家里停电了。这真的是太不走运了。

没有副坦克的补充，所有的伤害都集中在了雷霆之怒身上。
但是这个时候，事情开始变得诡异。

小甜甜（主奶妈）本应该全力治疗会长，但是我通过伤害统计面板发现，她的治疗量明显不足。
更奇怪的是，她把大量的治疗都给了暗影刺客（弓箭手）。

这很不正常。暗影刺客作为DPS，血量本不应该这么低。我仔细看了一下暗影刺客的走位——
哎哟，这哥们为了最大化伤害输出，站位超级靠前，几乎要贴到BOSS身上了。
结果BOSS的爪子扫过来，一下子就把暗影刺客的血条扫到了20%以下。

关键时刻，小甜甜却把大治疗术给了暗影刺客。这让会长雷霆之怒的血量开始急速下降。

我当时就在YY频道里喊："小甜甜，快给会长加血！"

月光治愈者也在拼命给会长加盾，但是她的输出能力有限，根本抵挡不住BOSS的伤害。

而且我还发现，月光治愈者的治疗也有一部分莫名其妙地给了其他人。看起来公会里有人在划水。

等等，我再看一下。哦天哪，火球术一级（法师）和冰霜法咒在BOSS的AoE范围内站了太长时间，
导致他们频繁掉血。但是，更夸张的是，暗影刺客和小甜甜之间似乎有什么默契——
每当暗影刺客掉血，小甜甜就立马给他加。

这时候，我想到了一个可能性。我在游戏论坛里看过一些帖子，有人提到暗影刺客和小甜甜好像是现实中的情侣！

妈呀，这下问题大了。在这么关键的时刻，小甜甜竟然偏心给她的男朋友加血，而忽视了作为团队大脑的会长！

大约在15分钟的时候，BOSS放出了一个大招——"魔龙吐息"。
这个技能造成的伤害足以秒杀任何一个DPS。但是坦克（雷霆之怒）应该能扛住。

可是，小甜甜的治疗没有及时跟上。雷霆之怒的血条瞬间掉到了0。

会长倒地了！

随后，失去了坦克的护佑，暗影刺客也被BOSS的普通攻击打成了残血，然后被秒杀。
紧接着是风云剑侠，然后是火球术一级。整个团队在短短30秒内全灭了。

副本失败。大家都复活在了副本入口。

这个时候，雷霆之怒（会长）的脾气彻底炸裂了。

他在YY频道里破口大骂："小甜甜，你是干什么呢？！你是团队奶妈，不是暗影刺客的私人医生！
治疗职业就是要保坦克，你这样的治疗我见过，但从没见过这么烂的！"

小甜甜试图辩解："我……我只是……"

雷霆之怒直接打断她："别给我狡辩！我决定了，你从今天起被踢出公会！
而且暗影刺客这个摸鱼的家伙，我也要把他赶出去。两个人都别在星辰阁待着！"

但就在这个时候，事情发生了急转弯。

暗影刺客一句话都没说，只见他的角色突然冲向了BOSS房间。
而就在这时，副本的第二个阶段秘密掉落物品——传说级别的武器"魔龙之牙"出现了！

这是一把超级稀有的武器，全服务器可能只有两三把。价值高达几百万金币。

没等任何人反应过来，暗影刺客就冲上去，一把拿起了"魔龙之牙"！

我们都懵了。"魔龙之牙"本来应该由队长（雷霆之怒）来分配，决定给谁。
但是暗影刺客直接黑吃黑，把这把传说武器直接塞进了自己的背包里！

会长还在语音里骂人，根本没注意到这一幕。

紧接着，更狠的来了——暗影刺客在游戏里按下了"退出公会"的按钮。
他直接，光速，毫不犹豫地退出了星辰阁！

然后他的角色在世界频道发了一句话："拜拜，各位。我去找个真正尊重我的公会。"

说完，这哥们直接下线了。

我们的公会频道顿时炸锅了。

小甜甜也没做任何辩解，直接退出了公会。她甚至没有说一句话。

会长雷霆之怒这时候才意识到发生了什么。他看到了掉落物品的分配记录——
"魔龙之牙"被暗影刺客拿走了，而不是团队共有。

他疯了。直接在世界频道开始刷屏：
"各位玩家，我要举报星辰阁的暗影刺客和小甜甜这两条狗！他们合谋黑装备！
不要信任他们！全服通缉这两个垃圾！"

火球术一级（法师）现在也开始助威。他在世界频道里连发了十多条信息：
"赞同！这两个人太过分了！狗男女！不要和他们做交易！"

"冰霜法咒在副本里的表现也不太理想，看起来他好像和那对情侣有什么关系，
因为我注意到在暗影刺客掉线的时候，冰霜法咒也莫名其妙地不进行输出了。"

有人开始怀疑冰霜法咒是不是也是那对情侣的朋友。

坚如磐石（副坦）这时候才上线。他看到了聊天记录，一脸懵逼。
他在公会频道里问："发生什么了？我家里停电了……"

没有人回答他。因为大家都在看这场大戏。

月光治愈者试图调和一下，她说："大家冷静……这件事可能有误会……"

但是没有人听她的。因为这个时候，世界频道上的玩家也开始评论这件事。

有人说："这就是为什么我不玩大公会。大公会水太深。"

还有人说："我早就听说暗影刺客这个人在游戏里名声不太好。多次被指控在副本里贪图装备。"

有人挖出了暗影刺客的历史记录。原来他曾经在另一个公会里，也因为类似的事情被踢出来过。

这哥们简直就是个"装备贪心鬼"。

风云剑侠开始反思："也许我们团队的问题不只是小甜甜。我们可能选错人了。"

火球术一级继续在世界频道里刷屏："各位，我建议大家抵制这两个玩家。不要和他们一个队。"

这时候，一个名字叫做"游戏管理员001"的官方账号出现了。
他说："我们收到了关于玩家暗影刺客的举报。我们正在调查这件事。如果确认违规，将给予封号处理。"

暗影刺客的名字从世界频道消失了——他已经下线了。而且下线之前把"魔龙之牙"从背包里转移到了仓库。
没人知道他把这把武器藏在了哪里。

最后，星辰阁的会长雷霆之怒在公会频道里宣布：
"各位成员，我决定了。星辰阁正式解散。这个公会不适合我继续管理。
我会转移到一个小公会，和志同道合的朋友重新开始。"

很多成员试图挽留他。但是他的决心已定。

现在，星辰阁已经成为了一个"死公会"。只有一些离不开这个ID的成员还在。

这就是昨晚发生的一切。我作为一个旁观者，见证了这场游戏江湖的大戏。

最后的最后，我想说：游戏就是游戏。团队合作最重要。装备是身外之物。
但是，为了装备而背叛队友，这绝对是游戏玩家中最可耻的行为。

希望游戏官方能够严肃处理暗影刺客的违规行为。
也希望星辰阁的所有成员能够吸取教训，在各自的新公会里找到快乐。

---

【回复楼层】

1楼：网络大侠
妈呀，这比小说还精彩。我已经截图保存，等着看后续。

2楼：游戏评论家
我注意到"冰霜法咒"在这件事里也有可疑之处。为什么他突然停止输出？
楼主，能不能深入调查一下他和暗影刺客的关系？

3楼：前星辰阁成员（风云剑侠）
我想出来说两句话。昨晚我在现场。
真相是：小甜甜确实有偏心。但是暗影刺客黑装备这件事更过分。
会长的反应虽然情绪化，但也能理解。
我已经离开了星辰阁，现在申请加入"日月神教"这个新兴公会。

4楼：月光治愈者（副奶妈）
我想为自己辩解一下。我在昨晚的治疗中没有任何划水行为。
是小甜甜的治疗分配有问题，不是我。
顺便说一下，我现在还在星辰阁，因为我对公会有感情。
但是我也不太确定会不会继续留下来。

5楼：装备交易商
这就是为什么装备交易需要系统中间作为担保的原因。
建议官方加强对装备分配的监管。

6楼：游戏社区版主
这个帖子已经标记为"关键事件记录"。
我们会持续关注这件事的后续发展。
请各位不要进行人身攻击和骚扰。相关玩家可以选择转服。
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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
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
    # Chat with Knowledge Graph
    # ============================================================================
    print("\n" + "=" * 70)
    print("💬 Knowledge Graph Intelligence")
    print("=" * 70)
    print("Interactive dialogue based on extracted relationships...\n")

    kg_questions = [
        "What are the main conflicts mentioned in this text?",
        "Which characters played the most important roles in the guild drama?",
        "What lessons can be learned from this event?"
    ]

    kg.build_index()
    for q in kg_questions:
        print(f"❓ Question: {q}")
        try:
            response = kg.chat(q)
            print(f"🤖 Answer: {response.content}\n")
        except Exception as e:
            print(f"⚠️ Chat error: {e}\n")

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
