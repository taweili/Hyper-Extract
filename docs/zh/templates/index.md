# Templates

Hyper-Extract 为各行业和用例提供专用模板。

## 可用领域

- [金融](domain/finance.md) - 金融文档提取
- [法律](domain/legal.md) - 法律文档提取
- [医学](domain/medicine.md) - 医疗文档提取
- [中医](domain/tcm.md) - 中医模板

## 快速开始

### 使用领域模板

```bash
# CLI
he parse document.txt -t finance/earnings_summary

# Python API
ka = Template.create("finance/earnings_summary")
result = ka.parse(document_text)
```

## 模板类别

### 金融模板

从各种文档类型中提取财务信息：

- 财报
- 财经新闻
- IPO 招股书
- 券商研报
- 供应链分析

### 法律模板

提取法律信息：

- 判决书
- 合同
- 合规文件
- 法律专著

### 医学模板

提取医学信息：

- 临床指南
- 出院小结
- 药品说明书
- 病理报告
- 医学教材

### 中医模板

中医专用模板：

- 中药属性
- 方剂组成
- 经络图谱
- 证候推理

## 快速链接

- [Concepts](../concepts/index.md) - 了解 AutoTypes 和 Methods
