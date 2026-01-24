"""
AutoList 多 Chunk 提取示例

演示如何使用 AutoList 处理长文本，测试多 chunk 并发提取和列表合并功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract import AutoList

import dotenv

dotenv.load_dotenv()

# 定义单个新闻事件的 Schema
class NewsEvent(BaseModel):
    """新闻事件结构"""

    title: str = Field(description="事件标题")
    date: str = Field(description="事件发生日期")
    location: str = Field(description="事件发生地点")
    description: str = Field(description="事件描述")
    participants: list[str] = Field(default_factory=list, description="参与者")
    impact: str = Field(default="", description="事件影响")


def generate_long_news_text() -> str:
    """生成包含多个新闻事件的长文本"""
    return """
2024年的科技圈可谓是风起云涌，一个接一个的突破性进展改变着世界。这一切始于一月份，当时旧金山的全球目光都被吸引到了OpenAI的总部。
1月15日，OpenAI正式发布了备受期待的GPT-5大语言模型，这无疑是一个足以震撼业界的时刻。CEO Sam Altman在发布会上自信地宣布，新模型的参数量达到了
惊人的5万亿，训练数据量是GPT-4的整整10倍。这套堪称最强的语言模型在推理能力、多模态理解和长文本处理方面实现了重大突破。此次发布引起了全球AI
行业的广泛关注，纳斯达克上那些科技公司股价应声上涨，分析师纷纷调高评级。而微软、谷歌这些竞争对手一看这架势坐不住了，立即宣布将加速自家AI
产品的迭代。业界的共识是，这不仅仅是一个产品发布，而是标志着人工智能进入了一个全新的发展阶段。

仅仅一周后，又一个科技大事件在德克萨斯州的奥斯汀上演。特斯拉在1月22日正式发布了FSD(Full Self-Driving) V12版本，
Elon Musk亲自宣布这是第一个完全基于端到端神经网络的自动驾驶系统，彻底摒弃了传统的人工规则编码。这套新系统在城市道路、高速公路和复杂停车
场景中的表现都有了显著提升，而且已经有超过100万名测试用户参与了Beta测试并提交了反馈。美国交通部也很给面子，迅速批准了临时许可，预计将在
3月份向所有车主推送这个更新。整个业界都认为这是自动驾驶技术向商业化迈进的一个里程碑事件。

到了二月份，硬件领域也开始发力。2月1日，苹果在其加州库比蒂诺的Apple Park总部举行了盛大发布会，推出了第二代混合现实头显Vision Pro 2。
与第一代相比，这款新产品经过了精心的工业设计优化，重量足足减轻了30%，续航时间提升至8小时，售价也从天价的3499美元降至2499美元，虽然依然
不便宜但相对"亲民"了许多。CEO Tim Cook在舞台上演示了搭载的更强大M3芯片和革新性的眼动追踪技术的完美配合。首发市场覆盖美国、中国、日本
和欧洲主要国家，预购首日的订单量就突破了50万台，远远超过了第一代产品的预期。分析师普遍预测，2024年的MR头显市场将迎来一场爆发式增长。

就在Vision Pro 2发布两周后，量子计算领域传来了同样振奋人心的消息。2月14日，IBM在纽约约克城研究中心宣布成功研制出了1000量子比特的
量子计算机Condor Plus，这是全球历史上首台突破千量子比特大关的实用型量子计算机。IBM研究副总裁Jay Gambetta详细介绍了这套系统如何将量子
错误率降低了50%，使其能够稳定运行复杂的量子算法。这个项目汇聚了MIT、哈佛大学和众多知名制药公司的力量。该系统已经开始在药物研发和材料
科学研究中发挥作用，这一突破无疑将量子计算离商业化应用的距离又拉近了好几步。

春天的到来似乎预示着人类要探索更多的新边界。3月5日，Meta在加州门洛帕克总部举行了一场颠覆性的产品发布，推出了消费级脑机接口设备
BrainLink。Mark Zuckerberg在发布会上亲自演示了如何通过思维意念来控制虚拟现实环境中的对象，这场景看起来就像是从科幻大片里走出来的。
该设备采用了非侵入式的前沿设计，佩戴简便舒适，价格定为999美元。Meta与包括Harvard Medical School在内的多家医疗机构深度合作进行了临床试验，
参与者超过5000人。应用场景涵盖游戏、医疗康复和为残障人士提供生活辅助，业界普遍认为这将开启人机交互的全新时代。

把目光投向太空的同一个月，中国在3月20日于海南文昌航天发射场成功发射了"天宫商业1号"空间站核心舱。这是全球首个完全由私营企业主导的
商业空间站项目，打破了长期以来太空领域被国家宇航局垄断的局面。参与企业包括航天科技集团、华为和腾讯这样的科技巨头。该空间站设计容纳6名
宇航员，主要用于微重力科学实验和高端太空旅游体验。首批商业宇航员预计在6月份进驻。这个项目总投资达到了200亿元人民币，标志着中国商业航天
真正迈入了一个全新的发展阶段。

进入四月，硅谷的算力竞争开始白热化。谷歌在4月10日于加州山景城推出了第六代张量处理单元TPU v6，这款芯片采用了前沿的3纳米工艺。与上一代
相比，AI计算性能提升了5倍，能源效率提升了3倍。Sundar Pichai雄心勃勃地宣布计划在全球数据中心部署超过100万颗TPU v6芯片。谷歌云的客户
将获得优先使用权。这个举措给英伟达、AMD等竞争对手施加了巨大的压力，市场分析人士纷纷预测，整个AI芯片行业的竞争格局可能将被重新洗牌。

同月下旬的4月25日，生物医疗领域传来了令人欣喜的突破。美国FDA正式批准了首个基于CRISPR基因编辑技术的镰状细胞病疗法上市。临床试验在
包括波士顿儿童医院在内的10家权威医疗中心进行，参与的45名患者在接受治疗后全部康复。这个研究团队由诺贝尔奖得主Jennifer Doudna亲自领导。
这是CRISPR技术首次在遗传性疾病治疗中取得如此完美的成功。虽然每人的治疗费用预计为100万美元，但这个突破意义重大，为其他遗传性疾病的治疗
开辟了崭新的光明前景。

五月份的科技新闻继续让人应接不暇。亚马逊在5月8日于西雅图宣布了其送货无人机Fleet X的正式商用。Jeff Bezos在发布会上表示，新一代无人机
可以承载5公斤的货物，飞行距离达到30公里，超越了之前的所有技术指标。首批服务城市包括西雅图、洛杉矶和纽约这样的大都市，目前已经有超过
1000架无人机完成部署。通过这套系统，配送时间可以缩短至30分钟以内，这无疑将彻底改变最后一公里的物流体验。联邦航空局甚至为此制定了专门的
空域管理规则。这标志着无人机配送终于进入了规模化应用阶段。

月底的5月30日，能源领域传来了同样振奋的消息。美国劳伦斯利弗莫尔国家实验室宣布在核聚变实验中实现了3倍的能量增益，这是继去年首次实现
净能量增益之后的又一次重大突破。这个由200多名顶级科学家组成的研究团队利用世界上最强大的激光系统NIF取得了这一成就。能源部长亲自出来为这个
突破站台，表示这使商业化核聚变发电的目标更加近在咫尺。多家能源巨头已经投入数十亿美元来研发商用核聚变反应堆，而专家们普遍预测，一场清洁
能源革命可能在十年内就会到来，这将彻底改变全球能源格局。

"""


def main():
    print("=" * 80)
    print("AutoList 多 Chunk 提取示例")
    print("=" * 80)

    # 1. 生成长文本
    print("\n[1] 生成测试新闻文本...")
    news_text = generate_long_news_text()
    print(f"   文本长度: {len(news_text)} 字符")
    print(f"   预计分块数: {len(news_text) // 500 + 1} 块 (chunk_size=500)")

    # 2. 初始化 LLM 和 Embedder
    print("\n[2] 初始化 LLM 和 Embedder...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. 创建 AutoList 实例 (使用小的 chunk_size 测试多 chunk)
    print("\n[3] 创建 AutoList 实例 (chunk_size=500)...")
    a_event_list = AutoList(
        item_schema=NewsEvent,
        llm_client=llm,
        embedder=embedder,
        chunk_size=500,  # 设置小的 chunk_size 来测试多 chunk 提取
        chunk_overlap=50,
        max_workers=5,
        verbose=True,
    )

    # 4. 提取知识 (使用 feed_text 模式)
    print("\n[4] 提取新闻事件列表 (使用 feed_text 模式)...")
    print("-" * 80)
    a_event_list.feed_text(news_text)
    print("-" * 80)

    # 5. 显示提取结果
    print(f"\n[5] 提取到 {len(a_event_list.items)} 个新闻事件:")
    for i, event in enumerate(a_event_list.items[:5], 1):  # 只显示前5个
        print(f"\n   事件 {i}:")
        print(f"      标题: {event.title}")
        print(f"      日期: {event.date}")
        print(f"      地点: {event.location}")
        print(f"      描述: {event.description[:80]}...")
        print(f"      参与者: {', '.join(event.participants[:3])}")
        if event.impact:
            print(f"      影响: {event.impact[:60]}...")

    if len(a_event_list) > 5:
        print(f"\n   ... 还有 {len(a_event_list) - 5} 个事件未显示")

    # 6. 测试列表大小
    print(f"\n[6] 知识列表大小: {len(a_event_list)} 个事件")

    # 7. 构建索引
    print("\n[7] 构建向量索引...")
    a_event_list.build_index()

    # 8. 测试搜索
    print("\n[8] 测试事件搜索...")
    queries = [
        "人工智能相关的事件",
        "美国发生的科技事件",
        "与航天相关的新闻",
    ]

    for query in queries:
        print(f"\n   查询: '{query}'")
        results = a_event_list.search(query, top_k=3)
        for i, event in enumerate(results, 1):
            print(f"      [{i}] {event.title} ({event.date})")
            print(f"          地点: {event.location}")

    # 9. 测试增量提取（feed 模式）
    print("\n[9] 测试增量提取（feed 模式）...")
    additional_news = """
    六月中旬的时候，通信领域又有了一个重磅消息。在深圳华为总部的一场技术发布大会上，华为的高管们宣布公司已经建成了全球首个6G技术
    测试网络，这消息一出来整个业界都沸腾了。这套测试网络覆盖了深圳市区的多个区域，实测传输速率达到了令人瞪目结舌的每秒1TB。这个项目
    汇聚了华为、中国移动和来自北大、清华等多家顶尖大学的研究力量。业界的普遍预测是，基于这样的技术进展，6G有望在2028年左右开始商用，
    这意味着全球通信技术的下一代竞争已经提前打响了。华为在这一轮竞争中处于相当领先的地位，这对中国的技术产业来说无疑是个重大利好消息。
    """

    print("   添加补充新闻...")
    before_count = len(a_event_list)
    a_event_list.feed_text(additional_news)  # 使用 feed_text 自动合并
    after_count = len(a_event_list)
    print(f"   合并前: {before_count} 个事件")
    print(f"   合并后: {after_count} 个事件")
    print(f"   新增: {after_count - before_count} 个事件")

    # 10. 显示最新添加的事件
    if after_count > before_count:
        print("\n   最新添加的事件:")
        for event in a_event_list.items[-3:]:
            print(f"      - {event.title} ({event.date})")

    a_event_list.build_index()
    # 11. 保存知识
    print("\n[10] 保存知识到文件...")
    save_path = Path(__file__).parent.parent / "temp" / "auto_list_demo"
    a_event_list.dump(str(save_path))
    print(f"   已保存到: {save_path}")

    # 12. 重新加载测试
    print("\n[11] 测试知识加载...")
    a_loaded_event_list = AutoList(
        item_schema=NewsEvent,
        llm_client=llm,
        embedder=embedder,
    )
    a_loaded_event_list.load(str(save_path))
    print(f"   加载成功! 事件数: {len(a_loaded_event_list)}")
    print(f"   第一个事件: {a_loaded_event_list.items[0].title}")

    # 13. 测试清空功能
    print("\n[12] 测试清空功能...")
    print(f"   清空前: {len(a_loaded_event_list)} 个事件")
    a_loaded_event_list.clear()
    print(f"   清空后: {len(a_loaded_event_list)} 个事件")

    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
