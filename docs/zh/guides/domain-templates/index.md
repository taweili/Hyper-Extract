# 领域模板

Hyper-Extract 为各行业和用例提供专用模板。

## 可用领域

- [金融](finance.md) - 金融文档提取
- [法律](legal.md) - 法律文档提取
- [医学](medicine.md) - 医疗文档提取
- [中医](tcm.md) - 中医模板

## 快速开始

### 使用领域模板

```bash
# CLI
he parse document.txt -t finance/earnings_summary

# Python API
ka = Template.create("finance/earnings_summary")
result = ka.parse(document_text)
```

## 创建自定义领域模板

请参阅[模板设计指南](../../concepts/templates.md)了解如何创建您自己的领域特定模板。
