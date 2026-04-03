# Python API

## 安装

```bash
pip install hyper-extract
```

## 配置

使用 dotenv 设置 API key：

```python
from dotenv import load_dotenv
load_dotenv()
```

创建 `.env` 文件：
```bash
OPENAI_API_KEY=your-api-key
```

## 快速开始

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "zh")
result = ka.parse(document_text)
```

---

## AutoTypes

AutoTypes 定义了知识提取的**输出数据结构**。共有 8 种类型：

### AutoModel - 结构化数据

使用 AutoModel 提取结构化摘要：

```python
from pydantic import BaseModel, Field
from hyperextract import AutoModel
from langchain_openai import ChatOpenAI

class BiographySummary(BaseModel):
    title: str = Field(description="传记标题")
    subject: str = Field(description="主题名称")
    summary: str = Field(description="简要摘要")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

model = AutoModel(
    data_schema=BiographySummary,
    llm_client=llm,
)
model.feed_text(text)
print(model.data.title)
```

### AutoList - 列表数据

提取列表项：

```python
from hyperextract.types import AutoList

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

lst = AutoList[str](
    item_schema=str,
    llm_client=llm,
    embedder=embedder,
)
lst.feed_text(text)
print(lst.items)  # 提取的列表项
```

### AutoSet - 去重集合

提取唯一项（去重）：

```python
from hyperextract.types import AutoSet

s = AutoSet[str](
    item_schema=str,
    llm_client=llm,
    embedder=embedder,
)
s.feed_text(text)
print(s.items)  # 去重后的列表
```

### AutoGraph - 知识图谱

提取实体和关系：

```python
from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph

class Entity(BaseModel):
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型")

class Relation(BaseModel):
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    type: str = Field(description="关系类型")

graph = AutoGraph[Entity, Relation](
    node_schema=Entity,
    edge_schema=Relation,
    node_key_extractor=lambda x: x.name,
    edge_key_extractor=lambda x: f"{x.source}-{x.type}-{x.target}",
    llm_client=llm,
    embedder=embedder,
)
graph.feed_text(text)
print(f"节点: {len(graph.nodes)}, 边: {len(graph.edges)}")
```

### AutoHypergraph - 超图

用于多元关系（n元关系）：

```python
from hyperextract.types import AutoHypergraph
# 参考 examples/zh/autotypes/hypergraph_demo.py
```

### AutoTemporalGraph - 时序图

用于时间相关的关嗧：

```python
from hyperextract.types import AutoTemporalGraph
# 参考 examples/zh/autotypes/temporal_graph_demo.py
```

### AutoSpatialGraph - 空间图

用于位置相关的关嗧：

```python
from hyperextract.types import AutoSpatialGraph
# 参考 examples/zh/autotypes/spatial_graph_demo.py
```

### AutoSpatioTemporalGraph - 时空图

用于时间和位置同时相关的关嗧：

```python
from hyperextract.types import AutoSpatioTemporalGraph
# 参考 examples/zh/autotypes/spatio_temporal_graph_demo.py
```

---

## Methods vs Templates

Hyper-Extract 提供了两种提取知识的方式：

### Methods（底层方法）

Methods 提供对提取过程的**完全控制**。在以下情况下使用：
- 需要自定义提取逻辑
- 需要特定的算法调优
- 高级用例

```python
from hyperextract.methods.typical import KG_Gen

ka = KG_Gen(llm_client=llm, embedder=embedder)
ka.feed_text(text)
result = ka.chat("主要成就有哪些？")
```

可用的 Methods：
- **典型方法**：KG_Gen、iText2KG、iText2KG*
- **RAG增强方法**：GraphRAG、LightRAG、HyperRAG、HypergraphRAG、CogRAG

### Templates（高层配置）

Templates 是常见用例的**预配置 schema**。在以下情况下使用：
- 快速得到结果
- 领域特定的提取
- 零代码设置

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "zh")
result = ka.parse(text)
```

### 何时使用哪个？

| 场景 | 推荐 |
|------|------|
| 快速原型 | Templates |
| 领域特定提取 | Templates |
| 自定义提取逻辑 | Methods |
| 实时交互 | Methods |
| 批量处理 | 两者皆可 |

---

## 高级用法

### 批量处理

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "zh")
documents = ["doc1.txt", "doc2.txt", "doc3.txt"]

results = []
for doc in documents:
    with open(doc, encoding="utf-8") as f:
        result = ka.parse(f.read())
        results.append(result)
```

### 增量补充（feed）

```python
ka = Template.create("general/biography_graph", "zh")
result = ka.parse(text1)

# 添加更多知识
ka.feed(result, text2)
```

### 知识问答（chat）

```python
ka.build_index()
answer = ka.chat("有哪些关键事件？")
print(answer.content)
```

### 错误处理

```python
from hyperextract import Template

try:
    ka = Template.create("template_name", "zh")
    result = ka.parse(text)
except Exception as e:
    print(f"错误: {e}")
    # 处理错误
```

### 结果导出

```python
# 导出为 JSON
json_output = result.to_json()

# 导出为 Dict
dict_output = result.to_dict()

# 导出为三元组
triples = result.to_triples()
```

---

## 下一步

- [预设模板](../templates/index.md)
- [领域模板](../templates/index.md)
- [探索示例](https://github.com/yifanfeng97/hyper-extract/tree/main/examples/zh)
