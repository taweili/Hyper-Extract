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
print(f"实体数: {len(result.data.entities)}")
print(f"关系数: {len(result.data.relations)}")

# 打印第一个实体
if result.data.entities:
    entity = result.data.entities[0]
    print(f"\n第一个: {entity.name} ({entity.type})")
    print(f"描述: {entity.description}")
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
# 打开交互式可视化
result.show()
```

### 4. 搜索

```python
# 构建搜索索引
result.build_index()

# 搜索
results = result.search("Nobel Prize", top_k=3)
for item in results:
    print(item)
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
    print(f"\nExtraction Results:")
    print(f"  Entities: {len(result.data.entities)}")
    print(f"  Relations: {len(result.data.relations)}")
    
    # 列出实体
    print("\nEntities found:")
    for entity in result.data.entities:
        print(f"  - {entity.name} ({entity.type})")
    
    # 构建索引和搜索
    print("\nBuilding search index...")
    result.build_index()
    
    search_results = result.search("computer programming", top_k=2)
    print(f"\nSearch results: {len(search_results)} items")
    
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
