"""集合知识示例 - 从冒险者日志中提取和去重怪物信息

这个示例演示了AutoSet如何基于唯一键字段自动去重提取的项目。
使用RPG怪物图鉴场景展示LLM_MERGE策略如何智能合并来自多个来源的冲突信息。
"""

# import os

# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ontomem.merger import MergeStrategy


# 添加项目根目录到 Python 路径
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hyperextract import AutoSet

import dotenv

dotenv.load_dotenv()


# 定义怪物信息的数据模型
class MonsterEntry(BaseModel):
    """RPG游戏中的怪物信息"""

    name: str = Field(description="怪物的名称（例如：'地精小卒'、'洞穴巨魔'）")
    species: str | None = Field(
        None,
        description="怪物的种族分类（例如：'类人型'、'巨人'、'野兽'）",
    )
    danger_level: int | None = Field(
        None,
        description="危险等级（1-10），用于评估战斗难度",
    )
    habitats: str | None = Field(None, description="怪物常见的栖息地或活动场所")
    characteristics: str | None = Field(
        None, description="怪物的外观特征和行为习性描述"
    )
    weaknesses: str | None = Field(
        None, description="怪物对特定伤害类型或攻击方式的弱点"
    )
    loot_drops: str | None = Field(None, description="击败怪物可能掉落的物品和资源")


def main():
    # 初始化LLM和嵌入模型
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # 创建AutoSet，使用LLM_MERGE策略
    # 当同一个怪物在多个日志中出现时，LLM会智能合并冲突的信息
    monster_codex = AutoSet(
        item_schema=MonsterEntry,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,  # 基于怪物名称去重
        strategy_or_merger=MergeStrategy.LLM.PREFER_INCOMING,
        prompt="""从冒险者的日志记录中提取所有怪物的相关信息。

对于每只怪物，请提供：
- name: 怪物的确切名称
- species: 怪物的种族分类（类人型、野兽、不死生物等）
- danger_level: 战斗危险等级（1-10）
- habitats: 常见的栖息地或地理位置
- characteristics: 详细的外观特征和行为描述
- weaknesses: 已知的弱点和克制方法
- loot_drops: 击败后可能掉落的物品

要尽可能准确和详细，包括所有提到的怪物和它们的属性。如果信息不完整，请基于已有信息做出合理推断。""",
        verbose=True,
    )

    # 来自冒险者的日志 - 包含重复的怪物但信息略有不同
    adventurer_logs = [
        """
        【第一个冒险日记 - 林地远征】
        日期：秋月15日
        
        今天在幽暗森林中遭遇了几种怪物。首先遇到了一群地精小卒，他们大约有3-4英尺高，绿皮肤，
        穿着破烂的皮盔甲。这些家伙相当狡猾，喜欢群体狩猎。危险等级大概是2-3。它们掉落了
        一些铜币和破旧的匕首。
        
        在森林深处，我还遇到了一只洞穴巨魔。这个家伙大约8英尺高，皮肤呈灰褐色，力量惊人。
        对火焰特别敏感——我用火焰咒语成功地逼退了它。危险等级至少是7。它的巢穴里有一些金币。
        
        还有森林狼群，非常聪明的野兽，它们似乎有高度的群体智能。危险等级4-5。
        """,
        """
        【第二个冒险日记 - 深矿探险】
        日期：秋月18日
        
        在深矿洞中进行了危险的探险。地精小卒在这里也有出现！看来他们在地下还有殖民地。
        这次的地精穿着更好的装备，显然这是地精的精英部队。他们配备了铁制短剑，训练更充分。
        危险等级可能达到了3-4。掉落了更多的铜币和一些魔晶。
        
        还有一种我之前没遇过的怪物——地下爬行虫。这些生物有分节的身体，长约2-3米，
        用触须来感知周围环境。它们不是很聪明，但速度很快。危险等级3。掉落虫壳碎片。
        
        巨魔在深处也出现了，但这次的巨魔看起来比森林里的那只更大更凶悍。
        它对寒冰魔法有抵抗力，但仍然惧怕火焰。危险等级估计8级。
        """,
        """
        【第三个冒险日记 - 废墟遗迹】
        日期：秋月22日
        
        在古老遗迹的探索中发现了新的敌人类型。最常见的是地精小卒的变种——遗迹守卫。
        他们看起来是被之前的文明改造过的，具有更强的战斗能力。有人说他们被魔法增强过。
        危险等级跳到了4-5。这些怪物掉落了古代金币和遗迹碎片。
        
        还有一个更大的怪物——遗迹看守者，是一只3米高的怪物。它有三只眼睛，可能具有某种魔法能力。
        非常危险！危险等级至少9级。击败它时获得了一个古老的魔晶。
        
        巨魔在这里也有据点，防守非常严密。这些可能是智商更高的个体。
        它们使用简单的工具和陷阱来狩猎冒险者。危险等级8-9。
        """,
    ]

    print("=" * 80)
    print("集合知识演示：从冒险者日志中构建怪物图鉴")
    print("=" * 80)

    # 从所有日志中提取怪物信息
    print("\n[*] 正在处理冒险者日志...")
    for i, log in enumerate(adventurer_logs, 1):
        print(f"\n  处理日志 {i}...")
        monster_codex.feed_text(log)  # 喂养数据
        print(f"  √ 目前已识别的怪物数量：{len(monster_codex)}")

    # 显示所有提取的怪物
    print("\n" + "=" * 80)
    print(f"[*] 提取的怪物统计：共 {len(monster_codex)} 种不同的怪物")
    print("=" * 80)

    # 按危险等级分组显示
    monsters_by_danger = {}
    for monster in monster_codex.items:
        level = monster.danger_level or 0
        if level not in monsters_by_danger:
            monsters_by_danger[level] = []
        monsters_by_danger[level].append(monster)

    # 从低到高显示怪物
    print("\n[怪物按危险等级分类]\n")
    for level in sorted(monsters_by_danger.keys()):
        level_monsters = monsters_by_danger[level]
        print(f"[!] 危险等级 {level}:")
        for monster in sorted(level_monsters, key=lambda m: m.name):
            print(f"\n  ● 怪物名称：{monster.name}")
            if monster.species:
                print(f"    种族：{monster.species}")
            if monster.habitats:
                print(f"    栖息地：{monster.habitats}")
            if monster.characteristics:
                print(f"    特征：{monster.characteristics}")
            if monster.weaknesses:
                print(f"    弱点：{monster.weaknesses}")
            if monster.loot_drops:
                print(f"    掉落物：{monster.loot_drops}")

    # 演示集合操作
    print("\n" + "=" * 80)
    print("[*] 演示集合操作和语义搜索")
    print("=" * 80)

    # 构建向量索引以支持语义搜索
    print("\n正在构建向量索引...")
    monster_codex.build_index()
    print("√ 索引构建成功")

    # 语义搜索示例
    print("\n[1] 语义搜索 - 寻找掉落金币的怪物：")
    treasure_monsters = monster_codex.search("掉落金币财宝", top_k=5)
    for monster in treasure_monsters:
        print(f"  • {monster.name}")
        if monster.loot_drops:
            print(f"    掉落物：{monster.loot_drops}")

    print("\n[2] 语义搜索 - 寻找怕火焰的怪物：")
    fire_weak_monsters = monster_codex.search("害怕火焰弱点火", top_k=5)
    for monster in fire_weak_monsters:
        print(f"  • {monster.name}")
        if monster.weaknesses:
            print(f"    弱点：{monster.weaknesses}")

    print("\n[3] 语义搜索 - 寻找在地下出现的怪物：")
    underground_monsters = monster_codex.search("地下洞穴矿井", top_k=5)
    for monster in underground_monsters:
        print(f"  • {monster.name}")
        if monster.habitats:
            print(f"    栖息地：{monster.habitats}")

    # 检查特定怪物是否存在
    print("\n[4] 成员检验 - 检查特定怪物是否在图鉴中：")
    check_monsters = ["地精小卒", "洞穴巨魔", "龙", "骷髅战士"]
    for monster_name in check_monsters:
        exists = monster_codex.contains(monster_name)
        status = "√" if exists else "×"
        print(f"  {status} {monster_name}：{'已记录' if exists else '未记录'}")

    # 获取特定怪物的详细信息
    print("\n[5] 查询特定怪物详情：")
    goblin = monster_codex.get("地精小卒")
    if goblin:
        print(f"  怪物名称：{goblin.name}")
        print(f"  种族：{goblin.species or '未知'}")
        print(f"  危险等级：{goblin.danger_level or '未知'}/10")
        print(f"  栖息地：{goblin.habitats or '未知'}")
        print(f"  特征：{goblin.characteristics or '无'}")
        print(f"  弱点：{goblin.weaknesses or '无已知弱点'}")
        print(f"  掉落物：{goblin.loot_drops or '无'}")

    # 保存提取的知识
    print("\n" + "=" * 80)
    print("[*] 保存怪物图鉴")
    print("=" * 80)

    save_path = project_root / "temp" / "auto_set_demo"
    monster_codex.dump(save_path)
    print(f"√ 已保存到：{save_path}")
    print("  - state.json（结构化数据）")
    print("  - faiss_index/（向量索引）")

    # 演示加载功能
    print("\n[*] 加载已保存的怪物图鉴...")
    loaded_codex = AutoSet(
        item_schema=MonsterEntry,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )
    loaded_codex.load(save_path)
    print(f"√ 加载成功！图鉴中有 {len(loaded_codex)} 只怪物")

    # 显示已加载的怪物列表
    print("\n[已加载怪物列表]")
    for monster in loaded_codex.items:
        print(f"  • {monster.name} (危险等级：{monster.danger_level}/10)")

    # 总结
    print("\n" + "=" * 80)
    print("[*] 演示总结")
    print("=" * 80)
    print(f"  提取的不同怪物数量：{len(monster_codex)}")
    print(f"  处理的冒险者日志数：{len(adventurer_logs)}")
    print("  去重策略：LLM_MERGE（智能合并）")
    print("  去重键：lambda x: x.name")
    print("\n  √ 基于怪物名称自动去重")
    print("  √ 智能合并多个来源的冲突信息")
    print("  √ 支持所有怪物的语义搜索")
    print("  √ 持久化存储和加载")
    print("=" * 80)


if __name__ == "__main__":
    main()
