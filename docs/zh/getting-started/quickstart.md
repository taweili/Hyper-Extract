# 快速教程

本教程将引导您在 5 分钟内完成从文档中提取知识。

## 第一步：准备文档

从一个简单的文本文档开始。创建名为 `document.txt` 的文件：

```text
Apple Inc. 报告 2024 年第一季度创纪录的季度收入 1239 亿美元。
CEO Tim Cook 宣布公司实现了史上最强的 iPhone 销量。
董事会宣布每股 0.24 美元的现金股息。
服务业务收入达到历史新高的 223 亿美元。
```

## 第二步：创建提取模板

Hyper-Extract 使用 YAML 模板来定义要提取的内容。创建 `template.yaml`：

```yaml
language: zh

name: 公司新闻摘要
type: graph
tags: [finance]

description: '从新闻文章中提取关键财务事件和实体关系。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称'
    - name: type
      type: str
      description: '实体类型（公司/人物/事件/金额）'
  relations:
    fields:
    - name: source
      type: str
      description: '源实体'
    - name: target
      type: str
      description: '目标实体'
    - name: type
      type: str
      description: '关系类型'

guideline:
  target: '从新闻中提取实体和关系。'
  rules_for_entities:
    - '提取公司、人物、金额等实体'
    - '保持命名一致'
  rules_for_relations:
    - '仅在文本明确表达时创建关系'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

## 第三步：提取知识（CLI）

![CLI](../assets/cli.png)

```bash
he parse document.txt -o output/ -t template.yaml
```

## 第四步：提取知识（Python API）

```python
from hyperextract import Template

# 从 YAML 创建模板
ka = Template.create("template.yaml", "zh")

# 解析文档
result = ka.parse("Apple Inc. 报告创纪录的季度收入...")

# 访问结果
print(result.entities)
print(result.relations)
```

## 第五步：查看结果

提取的知识将保存在您的输出目录中。您可以使用搜索命令：

```bash
he search output/ "有哪些财务事件？"
```

**AutoGraph 可视化示例：**

![AutoGraph 可视化](../assets/zh_show.png)

## 下一步

- 了解 [8 种自动类型](../concepts/auto-types.md)
- 探索 [提取方法](../concepts/methods.md)
- 浏览 [预设模板](../concepts/templates.md)
