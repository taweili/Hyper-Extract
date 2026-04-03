# Python 快速入门

使用 Python API 进行知识提取。

---

## 前置要求

- Hyper-Extract 已安装
- API 密钥已配置

→ 如果尚未完成，请查看[安装指南](installation.md)

---

## 基本示例

### 1. 创建模板

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", language="en")
```

### 2. 提取知识

```python
with open("document.md") as f:
    result = ka.parse(f.read())
```

### 3. 访问数据

```python
print(f"实体数量: {len(result.data.entities)}")
print(f"关系数量: {len(result.data.relations)}")
```

### 4. 可视化

```python
result.show()
```

---

## 完整示例

```python
from hyperextract import Template

# 创建模板
ka = Template.create("general/biography_graph", language="en")

# 提取知识
with open("tesla.md") as f:
    result = ka.parse(f.read())

# 访问数据
print(f"实体: {len(result.data.entities)}")
print(f"关系: {len(result.data.relations)}")

# 构建搜索索引
result.build_index()

# 搜索
results = result.search("AC motor")
print(results)

# 聊天
response = result.chat("What were Tesla's major inventions?")
print(response.content)

# 保存
result.dump("./output/")

# 加载
result.load("./output/")
```

---

## 增量更新

向现有知识库添加更多文档：

```python
# 初始提取
kb = ka.parse(doc1_text)

# 添加更多文档
kb.feed_text(doc2_text)
kb.feed_text(doc3_text)

# 保存
kb.dump("./my_kb/")
```

---

## 使用不同模板

```python
# 财务报告
ka = Template.create("finance/earnings_summary", language="en")
report = ka.parse(earnings_text)
print(report.data.revenue)

# 法律文档
ka = Template.create("legal/contract_obligation", language="en")
contract = ka.parse(contract_text)

# 医疗记录
ka = Template.create("medicine/symptom_list", language="en")
symptoms = ka.parse(medical_text)
```

---

## 下一步

- 阅读 [Python SDK 文档](../python/index.md)
- 探索 [模板库](../templates/index.md)
- 理解 [核心概念](../concepts/index.md)
