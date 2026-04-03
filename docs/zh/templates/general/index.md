# 通用模板

基础类型和常见提取任务。

---

## 概述

通用模板为各种文档提供基本的提取功能。

---

## 基础类型

### base_model

**用途**：基础结构化数据提取

**输出**：单个结构化对象

**用于**：简单摘要、表单类数据

**示例：**
```bash
he parse doc.md -t general/base_model -l en
```

**输出模式**：
```python
{
    "field1": "value1",
    "field2": "value2"
}
```

---

### base_list

**用途**：有序集合提取

**输出**：项目列表

**用于**：序列、排名

**示例：**
```bash
he parse doc.md -t general/base_list -l en
```

**输出模式**：
```python
{
    "items": ["item1", "item2", "item3"]
}
```

---

### base_set

**用途**：唯一集合提取

**输出**：唯一项目集合

**用于**：标签、类别、关键词

**示例：**
```bash
he parse doc.md -t general/base_set -l en
```

**输出模式**：
```python
{
    "items": {"unique1", "unique2", "unique3"}
}
```

---

### base_graph

**用途**：基础实体关系提取

**输出**：包含实体和关系的图谱

**用于**：知识图谱、网络

**示例：**
```bash
he parse doc.md -t general/base_graph -l en
```

**输出模式**：
```python
{
    "entities": [
        {"name": "Entity1", "type": "type1"},
        {"name": "Entity2", "type": "type2"}
    ],
    "relations": [
        {"source": "Entity1", "target": "Entity2", "type": "relates_to"}
    ]
}
```

---

## 专业模板

### biography_graph

**类型**：temporal_graph

**用途**：提取人物生平事件和时间线

**最适合**：传记、简介、回忆录

**示例使用：**
```bash
he parse tesla_bio.md -t general/biography_graph -l en
```

**特性**：
- 提取人物、地点、事件
- 捕获时间关系
- 时间线可视化

**示例输出**：
```python
{
    "entities": [
        {"name": "Nikola Tesla", "type": "person"},
        {"name": "AC Motor", "type": "invention"}
    ],
    "relations": [
        {
            "source": "Nikola Tesla",
            "target": "AC Motor",
            "type": "invented",
            "time": "1888"
        }
    ]
}
```

---

### concept_graph

**类型**：graph

**用途**：提取概念及其关系

**最适合**：研究论文、技术文档、文章

**示例使用：**
```bash
he parse paper.md -t general/concept_graph -l en
```

**特性**：
- 概念识别
- 关系映射
- 层次结构

---

### doc_structure

**类型**：model

**用途**：提取文档结构和大纲

**最适合**：长文档、报告、书籍

**示例使用：**
```bash
he parse report.md -t general/doc_structure -l en
```

**特性**：
- 章节识别
- 标题层次
- 每节要点

---

### workflow_graph

**类型**：graph

**用途**：提取流程工作流

**最适合**：程序、流程、工作流

**示例使用：**
```bash
he parse procedure.md -t general/workflow_graph -l en
```

**特性**：
- 步骤识别
- 流程关系
- 决策点

---

## 何时使用通用模板

### 何时使用：
- 文档不属于特定领域
- 需要基础提取
- 探索/文档类型未知
- 构建自定义工作流

### 何时不使用：
- 有领域特定模板可用（改用那个）
- 需要专业字段（创建自定义模板）

---

## 示例

### 示例 1：简单摘要

```python
from hyperextract import Template

ka = Template.create("general/base_model", "en")
result = ka.parse("""
会议记录：
日期：2024年1月15日
参会：Alice, Bob, Carol
主题：Q1 规划
决定：3月发布产品
""")

print(result.data)
```

### 示例 2：传记分析

```python
ka = Template.create("general/biography_graph", "en")
result = ka.parse(biography_text)

# 可视化生平事件
result.show()

# 提问
result.build_index()
response = result.chat("主要成就是什么？")
print(response.content)
```

### 示例 3：研究论文

```python
ka = Template.create("general/concept_graph", "en")
result = ka.parse(paper_text)

# 获取概念图
for node in result.data.nodes:
    print(f"概念: {node.name}")

for edge in result.data.edges:
    print(f"{edge.source} → {edge.target}")
```

---

## 参见

- [浏览所有模板](../browse.md)
- [如何选择](../how-to-choose.md)
- [自动类型](../../concepts/autotypes.md)
