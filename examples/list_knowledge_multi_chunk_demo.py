"""
ListKnowledge 多 Chunk 提取示例

演示如何使用 ListKnowledge 处理长文本，测试多 chunk 并发提取和列表合并功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.knowledge.generic import ListKnowledge


# 定义单个新闻事件的 Schema
class NewsEvent(BaseModel):
    """新闻事件结构"""

    event_id: Optional[str] = Field(default=None, description="事件唯一标识")
    title: str = Field(description="事件标题")
    date: str = Field(description="事件发生日期")
    location: str = Field(description="事件发生地点")
    description: str = Field(description="事件描述")
    participants: list[str] = Field(default_factory=list, description="参与者")
    impact: str = Field(default="", description="事件影响")


def generate_long_news_text() -> str:
    """生成包含多个新闻事件的长文本"""
    return """
# 2024年全球科技新闻回顾

## 一月份重大事件

### 事件1: OpenAI发布GPT-5
2024年1月15日，OpenAI在旧金山总部举行发布会，正式推出GPT-5大语言模型。该模型在推理能力、
多模态理解和长文本处理方面实现了重大突破。CEO Sam Altman在发布会上表示，GPT-5的参数量
达到5万亿，训练数据量是GPT-4的10倍。此次发布引起了全球AI行业的广泛关注，多家科技公司
股价应声上涨。微软、谷歌等竞争对手纷纷表态将加速自家AI产品的迭代。业界普遍认为，
这标志着人工智能进入了新的发展阶段。

### 事件2: 特斯拉自动驾驶重大更新
2024年1月22日，特斯拉在德克萨斯州奥斯汀发布了FSD(Full Self-Driving) V12版本。
Elon Musk宣称这是第一个完全基于端到端神经网络的自动驾驶系统，不再依赖人工规则。
新版本在城市道路、高速公路和停车场景中的表现都有显著提升。超过100万名测试用户
参与了Beta测试。此次更新获得了美国交通部的临时许可，预计将在3月份向所有车主推送。
这一进展被认为是自动驾驶技术的里程碑事件。

## 二月份重大事件

### 事件3: 苹果发布MR头显Apple Vision Pro 2
2024年2月1日，苹果公司在库比蒂诺Apple Park发布了第二代混合现实头显Vision Pro 2。
新产品重量减轻30%，续航时间提升至8小时，售价降至2499美元。CEO Tim Cook表示，
Vision Pro 2集成了更强大的M3芯片和先进的眼动追踪技术。首发市场包括美国、中国、
日本和欧洲主要国家。预购首日订单量突破50万台，远超第一代产品。分析师预测，
2024年MR头显市场将迎来爆发式增长。

### 事件4: 量子计算突破：IBM实现1000量子比特
2024年2月14日，IBM在纽约约克城研究中心宣布成功研制出1000量子比特的量子计算机Condor Plus。
这是全球首台突破千量子比特的实用型量子计算机。IBM研究副总裁Jay Gambetta介绍，
新系统的量子错误率降低了50%，可以稳定运行复杂的量子算法。合作伙伴包括MIT、
哈佛大学和多家制药公司。该系统已开始应用于药物研发和材料科学研究。
这一突破使量子计算离商业化应用又近了一步。

## 三月份重大事件

### 事件5: Meta推出脑机接口设备BrainLink
2024年3月5日，Meta在加州门洛帕克总部发布了消费级脑机接口设备BrainLink。
Mark Zuckerberg演示了如何通过思维控制虚拟现实环境。该设备采用非侵入式设计，
佩戴简便，价格定为999美元。Meta与多家医疗机构合作进行了临床试验，
参与者超过5000人。应用场景包括游戏、医疗康复和辅助残障人士。
业界认为这将开启人机交互的新时代。

### 事件6: 中国发射首个商业空间站
2024年3月20日，中国在海南文昌航天发射场成功发射"天宫商业1号"空间站核心舱。
这是全球首个完全由私营企业主导的商业空间站项目。参与公司包括航天科技集团、
华为和腾讯。空间站设计容纳6名宇航员，将主要用于微重力科学实验和太空旅游。
首批商业宇航员预计在6月份进驻。该项目总投资达200亿元人民币，
标志着中国商业航天进入新阶段。

## 四月份重大事件

### 事件7: 谷歌推出AI芯片TPU v6
2024年4月10日，谷歌在加州山景城发布了第六代张量处理单元TPU v6。
新芯片采用3纳米工艺，AI计算性能比上一代提升5倍，能效提升3倍。
Sundar Pichai宣布将在全球数据中心部署超过100万颗TPU v6芯片。
谷歌云客户将优先获得使用权。英伟达、AMD等竞争对手面临巨大压力。
市场分析认为，这将重塑AI芯片行业格局。

### 事件8: 生物技术突破：CRISPR治愈镰状细胞病
2024年4月25日，美国FDA正式批准首个基于CRISPR基因编辑技术的镰状细胞病疗法。
临床试验在波士顿儿童医院等10家医疗中心进行，45名患者接受治疗后全部康复。
研究团队由诺贝尔奖得主Jennifer Doudna领导。这是CRISPR技术首次在遗传性疾病
治疗中取得成功。医疗费用预计为每人100万美元。此突破为其他基因疾病的治疗
开辟了新路径。

## 五月份重大事件

### 事件9: 亚马逊推出送货无人机Fleet X
2024年5月8日，亚马逊在西雅图宣布正式商用送货无人机Fleet X。
Jeff Bezos在发布会上表示，新一代无人机可承载5公斤货物，飞行距离达30公里。
首批服务城市包括西雅图、洛杉矶和纽约。超过1000架无人机已完成部署。
配送时间可缩短至30分钟内。联邦航空局为此制定了专门的空域管理规则。
这标志着无人机配送进入规模化应用阶段。

### 事件10: 核聚变实验取得重大进展
2024年5月30日，美国劳伦斯利弗莫尔国家实验室宣布在核聚变实验中实现了3倍能量增益。
这是继去年首次实现净能量增益后的又一突破。实验团队由200多名科学家组成，
使用世界最强激光系统NIF。能源部长表示，这使商业化核聚变发电的目标更近一步。
多家能源公司已投入数十亿美元研发商用核聚变反应堆。专家预测，
清洁能源革命可能在10年内到来。

## 总结

2024年上半年，科技领域呈现出百花齐放的局面。人工智能、量子计算、生物技术、
航天科技等多个领域都取得了突破性进展。这些创新不仅推动了技术进步，
也将深刻改变人类社会的未来发展方向。
"""


def main():
    print("=" * 80)
    print("ListKnowledge 多 Chunk 提取示例")
    print("=" * 80)

    # 1. 生成长文本
    print("\n[1] 生成测试新闻文本...")
    news_text = generate_long_news_text()
    print(f"   文本长度: {len(news_text)} 字符")
    print(f"   预计分块数: {len(news_text) // 200 + 1} 块 (chunk_size=200)")

    # 2. 初始化 LLM 和 Embedder
    print("\n[2] 初始化 LLM 和 Embedder...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. 创建 ListKnowledge 实例 (使用小的 chunk_size 测试多 chunk)
    print("\n[3] 创建 ListKnowledge 实例 (chunk_size=200)...")
    knowledge = ListKnowledge(
        item_schema=NewsEvent,
        llm_client=llm,
        embedder=embedder,
        chunk_size=300,  # 设置小的 chunk_size 来测试多 chunk 提取
        chunk_overlap=50,
        max_workers=5,
        show_progress=True,
    )

    # 4. 提取知识 (替换模式)
    print("\n[4] 提取新闻事件列表 (替换模式)...")
    print("-" * 80)
    events = knowledge.extract(news_text, merge_mode=False)
    print("-" * 80)

    # 5. 显示提取结果
    print(f"\n[5] 提取到 {len(events)} 个新闻事件:")
    for i, event in enumerate(events[:5], 1):  # 只显示前5个
        print(f"\n   事件 {i}:")
        print(f"      标题: {event.title}")
        print(f"      日期: {event.date}")
        print(f"      地点: {event.location}")
        print(f"      描述: {event.description[:80]}...")
        print(f"      参与者: {', '.join(event.participants[:3])}")
        if event.impact:
            print(f"      影响: {event.impact[:60]}...")

    if len(events) > 5:
        print(f"\n   ... 还有 {len(events) - 5} 个事件未显示")

    # 6. 测试列表大小
    print(f"\n[6] 知识列表大小: {knowledge.size()} 个事件")

    # 7. 构建索引
    print("\n[7] 构建向量索引...")
    knowledge.build_index()

    # 8. 测试搜索
    print("\n[8] 测试事件搜索...")
    queries = [
        "人工智能相关的事件",
        "美国发生的科技事件",
        "与航天相关的新闻",
    ]

    for query in queries:
        print(f"\n   查询: '{query}'")
        results = knowledge.search(query, top_k=3)
        for i, event in enumerate(results, 1):
            print(f"      [{i}] {event.title} ({event.date})")
            print(f"          地点: {event.location}")

    # 9. 测试增量提取（合并模式）
    print("\n[9] 测试增量提取（合并模式）...")
    additional_news = """
    ### 事件11: 华为发布6G测试网络
    2024年6月15日，华为在深圳总部宣布建成全球首个6G技术测试网络。
    该网络覆盖深圳市区，传输速率达到每秒1TB。参与测试的包括华为、中国移动和多家大学。
    预计6G将在2028年开始商用。这标志着中国在6G技术研发中处于领先地位。
    """

    print("   添加补充新闻...")
    before_count = knowledge.size()
    knowledge.extract(additional_news, merge_mode=True)
    after_count = knowledge.size()
    print(f"   合并前: {before_count} 个事件")
    print(f"   合并后: {after_count} 个事件")
    print(f"   新增: {after_count - before_count} 个事件")

    # 10. 显示最新添加的事件
    if after_count > before_count:
        print("\n   最新添加的事件:")
        for event in knowledge.items[-3:]:
            print(f"      - {event.title} ({event.date})")

    # 11. 保存知识
    print("\n[10] 保存知识到文件...")
    save_path = Path(__file__).parent.parent / "tmp" / "list_knowledge_multi_chunk"
    knowledge.dump(str(save_path))
    print(f"   已保存到: {save_path}")

    # 12. 重新加载测试
    print("\n[11] 测试知识加载...")
    new_knowledge = ListKnowledge(
        item_schema=NewsEvent,
        llm_client=llm,
        embedder=embedder,
    )
    new_knowledge.load(str(save_path))
    print(f"   加载成功! 事件数: {new_knowledge.size()}")
    print(f"   第一个事件: {new_knowledge.items[0].title}")

    # 13. 测试清空功能
    print("\n[12] 测试清空功能...")
    print(f"   清空前: {new_knowledge.size()} 个事件")
    new_knowledge.clear()
    print(f"   清空后: {new_knowledge.size()} 个事件")

    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
