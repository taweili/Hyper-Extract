# Methods API

API reference for extraction methods.

---

## Registry Functions

::: hyperextract.methods.registry
    options:
      members:
        - register_method
        - get_method
        - list_methods
        - get_method_cfg
        - list_method_cfgs

---

## Method Configuration

::: hyperextract.methods.registry.MethodCfg
    options:
      members: true

---

## RAG-Based Methods

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

## Typical Methods

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

## Using Methods Directly

```python
from hyperextract.methods import Light_RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Create method instance
llm = ChatOpenAI()
emb = OpenAIEmbeddings()

method = Light_RAG(
    llm_client=llm,
    embedder=emb
)

# Extract knowledge
result = method.parse(text)
```

---

## Registering Custom Methods

```python
from hyperextract.methods import register_method

class MyCustomMethod:
    def __init__(self, llm_client, embedder, **kwargs):
        self.llm_client = llm_client
        self.embedder = embedder
    
    def parse(self, text):
        # Your extraction logic
        pass

# Register the method
register_method(
    name="my_method",
    method_class=MyCustomMethod,
    autotype="graph",
    description="My custom extraction method"
)

# Use via Template API
from hyperextract import Template
ka = Template.create("method/my_method")
```
