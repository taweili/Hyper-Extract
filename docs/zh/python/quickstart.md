# Python 快速入门

在 5 分钟内开始使用 Hyper-Extract Python SDK。

---

## 前置要求

- Python 3.11+
- OpenAI API 密钥

## 安装

```bash
pip install hyper-extract
```

## 基本用法

### 1. 配置 API 密钥

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

或使用 `.env` 文件：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. 提取知识

```python
from hyperextract import Template

# 创建模板
ka = Template.create("general/biography_graph", language="en")

# 您的文本
text = """
Marie Curie was a Polish-French physicist and chemist who conducted 
pioneering research on radioactivity. She was the first woman to win 
a Nobel Prize and the only person to win Nobel Prizes in two different 
scientific fields.
"""

# 提取
result = ka.parse(text)

# 访问结果
print(f"节点数: {len(result.nodes)}")
print(f"边数: {len(result.edges)}")

# 打印第一个节点
if result.nodes:
    node = result.nodes[0]
    print(f"\n第一个: {node.name} ({node.type})")
    print(f"描述: {node.description}")
```

**输出：**
```
Entities: 5
Relations: 4

First: Marie Curie (person)
Description: Polish-French physicist and chemist
```

### 3. 可视化

```python
# 构建索引以支持搜索/对话功能
result.build_index()

# 打开交互式可视化
result.show()
```

### 4. 搜索

```python
# 构建搜索索引
result.build_index()

# 搜索
nodes, edges = result.search("Nobel Prize", top_k=3)
for node in nodes:
    print(f"节点: {node.name}")
for edge in edges:
    print(f"边: {edge.source} -> {edge.target}")
```

### 5. 聊天

```python
# 提问
response = result.chat("Marie Curie 发现了什么？")
print(response.content)
```

### 6. 保存和加载

```python
# 保存到磁盘
result.dump("./curie_kb/")

# 之后加载
new_ka = Template.create("general/biography_graph", language="en")
new_ka.load("./curie_kb/")
```

---

## 完整示例

```python
"""完整示例：提取、探索和保存知识。"""

from dotenv import load_dotenv
load_dotenv()

from hyperextract import Template

def main():
    # 创建模板
    print("Creating template...")
    ka = Template.create("general/biography_graph", language="en")
    
    # 示例文本
    text = """
    Ada Lovelace was an English mathematician and writer, chiefly known 
    for her work on Charles Babbage's early mechanical general-purpose 
    computer, the Analytical Engine. She is often regarded as the first 
    computer programmer.
    """
    
    # 提取知识
    print("Extracting knowledge...")
    result = ka.parse(text)
    
    # 显示结果
    print(f"\n提取结果：")
    print(f"  节点数: {len(result.nodes)}")
    print(f"  边数: {len(result.edges)}")

    # 列出节点
    print("\n发现的节点：")
    for node in result.nodes:
        print(f"  - {node.name} ({node.type})")
    
    # 构建索引和搜索
    print("\nBuilding search index...")
    result.build_index()
    
    search_nodes, search_edges = result.search("computer programming", top_k=2)
    print(f"\n搜索结果: {len(search_nodes)} 个节点, {len(search_edges)} 条边")
    
    # 保存
    print("\nSaving knowledge base...")
    result.dump("./ada_kb/")
    
    print("\nDone! Try: he show ./ada_kb/")

if __name__ == "__main__":
    main()
```

---

## 下一步

- 学习[核心概念](core-concepts.md)
- 阅读[使用模板指南](guides/using-templates.md)
- 探索 [API 参考](api-reference/template.md)
