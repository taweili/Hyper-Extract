# Python API

本指南介绍如何在 Python 应用程序中使用 Hyper-Extract。

## 安装

```bash
pip install hyper-extract
```

## 基本用法

### 导入和初始化

```python
from hyperextract import Template

# 加载预设模板
ka = Template.create("general/biography")

# 解析文档
result = ka.parse(text)
```

### 使用自定义模板

```python
from hyperextract import Template

# 从 YAML 加载
ka = Template.from_yaml("template.yaml")

# 解析文档
result = ka.parse(document_text)

# 访问结果
print(result.nodes)
print(result.edges)
```

## 自动类型

### AutoModel

```python
from hyperextract import AutoModel
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

extractor = AutoModel(schema=Person)
result = extractor.parse("John 是一位 30 岁的工程师。")
```

### AutoList

```python
from hyperextract import AutoList

extractor = AutoList(item_type="string")
result = extractor.parse("配料包括面粉、糖和鸡蛋。")
print(result.items)  # ["面粉", "糖", "鸡蛋"]
```

### AutoGraph

```python
from hyperextract import AutoGraph

extractor = AutoGraph(
    node_types=["Person", "Organization"],
    edge_types=["WORKS_AT"]
)
result = extractor.parse("Alice 在 Google 工作。")
```

### AutoHypergraph

```python
from hyperextract import AutoHypergraph

extractor = AutoHypergraph()
result = extractor.parse("Alice、Bob 和 Carol 合作了。")
```

## 提取方法

### 使用 atom

```python
from hyperextract.methods import atom

result = atom.extract(text, schema=MySchema)
```

### 使用 graph_rag

```python
from hyperextract.methods import graph_rag

result = graph_rag.extract(
    text,
    node_types=["Person", "Company"],
    edge_types=["WORKS_AT"]
)
```

### 使用 cog_rag

```python
from hyperextract.methods import cog_rag

result = cog_rag.extract(
    text,
    task="提取因果关系"
)
```

## 配置

### LLM 配置

```python
from hyperextract import Config

config = Config(
    llm_provider="openai",
    llm_model="gpt-4o",
    api_key="your-api-key"
)

ka = Template.create("general/biography", config=config)
```

### Embedding 配置

```python
config = Config(
    embedding_provider="openai",
    embedding_model="text-embedding-3-small"
)
```

## 处理结果

### 访问节点

```python
result = ka.parse(text)

for node in result.nodes:
    print(f"{node.type}: {node.properties}")
```

### 访问边

```python
for edge in result.edges:
    print(f"{edge.source} --[{edge.type}]--> {edge.target}")
```

### 序列化

```python
# 保存为 JSON
result.to_json("output.json")

# 保存为 YAML
result.to_yaml("output.yaml")

# 从文件加载
loaded = Result.from_json("output.json")
```

## 高级用法

### 自定义解析器

```python
from hyperextract import Template
from hyperextract.parsers import CustomParser

class MyParser(CustomParser):
    def parse(self, text):
        # 自定义解析逻辑
        return processed_result

ka = Template(parser=MyParser())
```

### 批量处理

```python
from hyperextract import Template

ka = Template.create("general/biography")

documents = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = ka.batch_parse(documents)
```

## 下一步

- 探索 [CLI](cli.md)
- 浏览 [领域模板](domain-templates/index.md)
- 查看 [参考](../reference/index.md)
