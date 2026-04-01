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
name: 公司新闻摘要
description: 从新闻文章中提取关键财务事件
type: TemporalGraph
schema:
  nodes:
    - type: Company
      properties:
        - name: name
          type: string
        - name: ticker
          type: string
    - type: FinancialEvent
      properties:
        - name: description
          type: string
        - name: amount
          type: number
        - name: category
          type: string
  edges:
    - type: ANNOUNCED
      source: Company
      target: FinancialEvent
```

## 第三步：提取知识（CLI）

```bash
he parse document.txt -o output/ -t template.yaml
```

## 第四步：提取知识（Python API）

```python
from hyperextract import Template

# 从 YAML 创建模板
ka = Template.from_yaml("template.yaml")

# 解析文档
result = ka.parse("Apple Inc. 报告创纪录的季度收入...")

# 访问结果
print(result.nodes)
print(result.edges)
```

## 第五步：查看结果

提取的知识将保存在您的输出目录中。您可以使用搜索命令：

```bash
he search output/ "有哪些财务事件？"
```

## 下一步

- 了解 [8 种自动类型](../concepts/auto-types.md)
- 探索 [提取方法](../concepts/methods.md)
- 浏览 [预设模板](../concepts/templates.md)
