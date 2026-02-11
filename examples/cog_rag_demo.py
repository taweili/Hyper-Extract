"""
Cog_RAG Demo: Theme-based Knowledge Extraction + Entity-Relation Detail Retrieval

This demo demonstrates the unified Cog_RAG System Wrapper:
1.  **Macro Layer (Theme Layer)**: Extracts Narrative Arcs (Themes) and their Participant Entities.
2.  **Micro Layer (Detail Layer)**: Extracts Entities and their Semantic Relationships.
3.  **Process**:
    -   Feeds the same story to the Unified System.
    -   The system automatically distributes extraction tasks to both layers.
    -   Performs a Dual-Layer Chat/Search.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to load dotenv, ignoring if not installed

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.types.cog_rag import Cog_RAG

# ============================================================================
# Sample Story for Extraction
# ============================================================================

STORY = """
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


if __name__ == "__main__":
    # ============================================================================
    # Initialize the Cog_RAG system
    # ============================================================================
    print("=" * 80)
    print("Initializing Unified Cog_RAG System...")
    print("=" * 80)

    # Use a capable model for extraction
    llm_client = ChatOpenAI(
        model="gpt-4o-mini",
        extra_body={
            "system": "You are a helpful assistant. Always respond in Chinese."
        },
        temperature=0,
    )
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # Initialize the Unified System Wrapper
    rag = Cog_RAG(
        llm_client=llm_client,
        embedder=embedder,
        chunk_size=1000,
        verbose=True
    )

    # ============================================================================
    # Feed text to the system
    # ============================================================================
    print("\nFeeding story to the Cog_RAG System (Dual-Layer Extraction)...")
    rag.feed_text(STORY)
    print("✓ Story processed successfully\n")

    # ============================================================================
    # Display Extracted Data (Unified View)
    # ============================================================================
    print("=" * 80)
    print("EXTRACTED KNOWLEDGE")
    print("=" * 80)

    # 1. Macro Themes
    print("\n--- MACRO LAYER: Themes (Narrative Arcs) ---")
    for i, edge in enumerate(rag.theme_layer.edges, 1):
        print(f"\nTheme {i}: {edge.description}")
        print(f"   Participants: {', '.join(edge.participants)}")

    print(f"\n✓ Total Themes extracted: {len(rag.theme_layer.edges)}")

    # 2. Micro Relations
    print(f"\n--- MICRO LAYER: Entity Relations ---")
    
    low_order_edges = [e for e in rag.detail_layer.edges if len(e.participants) == 2]
    high_order_edges = [e for e in rag.detail_layer.edges if len(e.participants) > 2]

    print(f"\nMicro Relations (Pairwise):")
    for i, edge in enumerate(low_order_edges[:5], 1): # Show top 5
        print(f"{i}. {edge.description} (Entities: {', '.join(edge.participants)})")
    if len(low_order_edges) > 5:
        print(f"... and {len(low_order_edges) - 5} more.")

    print(f"\nMicro Relations (Hyperedges):")
    for i, edge in enumerate(high_order_edges[:5], 1): # Show top 5
        print(f"{i}. {edge.description} (Entities: {', '.join(edge.participants)})")
    if len(high_order_edges) > 5:
        print(f"... and {len(high_order_edges) - 5} more.")

    print(f"\n✓ Total Micro Relations extracted: {len(rag.detail_layer.edges)}")

    # 3. Entities
    print(f"\n--- UNIQUE ENTITIES (Combined) ---")
    print(f"Total Unique Entities: {len(rag.nodes)}")
    
    # Display top 5 entities
    for i, node in enumerate(rag.nodes[:5], 1):
        print(f"{i}. 【{node.name}】 ({node.type})")
    if len(rag.nodes) > 5:
        print(f"... and {len(rag.nodes) - 5} more.")

    # ============================================================================
    # Build Semantic Index
    # ============================================================================
    print("\n" + "=" * 80)
    print("Building Semantic Indexes...")
    print("=" * 80)

    rag.build_index()
    print("✓ Semantic indexes built successfully\n")

    # ============================================================================
    # Q&A: Dual-Layer Search
    # ============================================================================
    print("=" * 80)
    print("Q&A: DUAL-LAYER SEMANTIC SEARCH")
    print("=" * 80)

    queries = [
        "虚空水晶现在在哪里?",
        "黑蛇和议员Valerius有什么阴谋?",
        "谁参与了泰坦空间站的秘密会议?",
        "Leona目前的状况如何?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n【问题 {i}】{query}")
        print("-" * 60)
        
        # Search BOTH layers
        results = rag.search(query, top_k_themes=2, top_k_entities=2)
        
        print("  [Macro Themes Found]:")
        if results['themes']:
            for t in results['themes']:
                print(f"    - {t.description}")
        else:
            print("    (None)")

        print("  [Micro Entities Found]:")
        if results['entities']:
            for e in results['entities']:
                print(f"    - {e.name}: {e.description[:50]}...")
        else:
            print("    (None)")


    # ============================================================================
    # Chat with Cog_RAG
    # ============================================================================
    print("\n" + "=" * 80)
    print("💬 Interactive Chat with Cog_RAG")
    print("=" * 80)
    print("Engaging in multi-turn dialogue based on Dual-Layer Knowledge...\n")

    for q in queries:
        print(f"❓ User: {q}")
        try:
            response = rag.chat(q)
            print(f"🤖 Cog_RAG: {response.content}\n")
        except Exception as e:
            print(f"⚠️ Chat error: {e}\n")

    # ============================================================================
    # Save Results
    # ============================================================================
    print("\n" + "=" * 80)
    print("Saving Results...")
    print("=" * 80)

    try:
        output_dir = "temp/cog_rag_demo"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        rag.dump(output_dir)
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

    print("\n" + "=" * 80 + "\n")

