# 方法 API

提取方法的 API 参考。

---

## 注册表函数

::: hyperextract.methods.registry
    options:
      members:
        - register_method
        - get_method
        - list_methods
        - get_method_cfg
        - list_method_cfgs

---

## 方法配置

::: hyperextract.methods.registry.MethodCfg
    options:
      members: true

---

## 基于 RAG 的方法

### LightRAG

::: hyperextract.methods.rag.Light_RAG
    options:
      members: true

### GraphRAG

::: hyperextract.methods.rag.Graph_RAG
    options:
      members: true

### HyperRAG

::: hyperextract.methods.rag.Hyper_RAG
    options:
      members: true

### HyperGraphRAG

::: hyperextract.methods.rag.HyperGraph_RAG
    options:
      members: true

### CogRAG

::: hyperextract.methods.rag.Cog_RAG
    options:
      members: true

---

## 典型方法

### iText2KG

::: hyperextract.methods.typical.iText2KG
    options:
      members: true

### iText2KG_Star

::: hyperextract.methods.typical.iText2KG_Star
    options:
      members: true

### KG_Gen

::: hyperextract.methods.typical.KG_Gen
    options:
      members: true

### Atom

::: hyperextract.methods.typical.Atom
    options:
      members: true

---

## 直接使用方法

```python
from hyperextract.methods import Light_RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 创建方法实例
llm = ChatOpenAI()
emb = OpenAIEmbeddings()

method = Light_RAG(
    llm_client=llm,
    embedder=emb
)

# 提取知识
result = method.parse(text)
```

---

## 注册自定义方法

```python
from hyperextract.methods import register_method

class MyCustomMethod:
    def __init__(self, llm_client, embedder, **kwargs):
        self.llm_client = llm_client
        self.embedder = embedder
    
    def parse(self, text):
        # 您的提取逻辑
        pass

# 注册方法
register_method(
    name="my_method",
    method_class=MyCustomMethod,
    autotype="graph",
    description="我的自定义提取方法"
)

# 通过模板 API 使用
from hyperextract import Template
ka = Template.create("method/my_method")
```
