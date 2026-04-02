# Python API

Hyper-Extract 提供 Python API 用于程序化提取。

## 安装

```bash
pip install hyperextract
```

## 基础用法

### 加载预设模板

```python
from hyperextract import Template

# 加载预设模板
ka = Template.create("general/graph", "zh")

# 解析文档
result = ka.parse(document_text)

# 访问结果
print(result.entities)
print(result.relations)
```

### 加载自定义模板

```python
from hyperextract import Template

# 从 YAML 文件加载
ka = Template.create("template.yaml", "zh")

# 从字符串加载
yaml_content = """
language: zh
name: 自定义模板
type: graph
tags: [custom]
description: '...'
output:
  entities:
    fields:
    - name: name
      type: str
      description: '名称'
  relations:
    fields:
    - name: source
      type: str
      description: '源'
    - name: target
      type: str
      description: '目标'
    - name: type
      type: str
      description: '类型'
guideline:
  target: '...'
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
"""

ka = Template.create(yaml_content, "zh")
```

### 批量处理

```python
from hyperextract import Template

ka = Template.create("general/graph", "zh")

documents = ["文档1内容...", "文档2内容...", "文档3内容..."]

results = []
for doc in documents:
    result = ka.parse(doc)
    results.append(result)
```

### 结果导出

```python
from hyperextract import Template

ka = Template.create("general/graph", "zh")
result = ka.parse(document_text)

# 导出为 JSON
json_output = result.to_json()

# 导出为 Dict
dict_output = result.to_dict()

# 导出为三元组
triples = result.to_triples()
```

## 模板创建

### 创建新模板

```python
from hyperextract import Template

template = Template.create("template.yaml", "zh")
```

### 保存模板

```python
from hyperextract import Template

ka = Template.create("general/graph", "zh")
ka.save("my_template.yaml")
```

## 配置选项

### 设置语言

```python
from hyperextract import Template

# 单语言
ka = Template.create("general/graph", "zh")

# 多语言
ka = Template.create("general/graph", ["zh", "en"])
```

### 设置模型

```python
from hyperextract import Template

# 使用指定模型
ka = Template.create("general/graph", "zh", model="gpt-4")

# 使用本地模型
ka = Template.create("general/graph", "zh", model="local-model")
```

## 错误处理

```python
from hyperextract import Template

try:
    ka = Template.create("template.yaml", "zh")
    result = ka.parse(document_text)
except Exception as e:
    print(f"提取失败: {e}")
```

## 下一步

- 浏览 [预设模板](../concepts/templates.md)
- 查看 [领域模板](./domain-templates/index.md)
