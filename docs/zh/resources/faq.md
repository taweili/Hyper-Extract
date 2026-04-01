# 常见问题

关于 Hyper-Extract 的常见问题。

## 概述

### 什么是 Hyper-Extract？

Hyper-Extract 是一个智能的、基于 LLM 的知识提取框架，可将非结构化文档转换为结构化知识表示。

### Hyper-Extract 可以处理哪些类型的文档？

Hyper-Extract 可以处理各种文档类型，包括：
- 纯文本文件
- PDF
- Markdown 文件
- HTML 文档
- Word 文档

### 支持哪些语言？

Hyper-Extract 支持多种语言，包括英语、中文、日语、韩语等。

## 安装

### 如何安装 Hyper-Extract？

```bash
pip install hyper-extract
```

### 系统要求是什么？

- Python 3.9 或更高版本
- OpenAI API 密钥（或兼容的 LLM API）

## 使用

### 如何从文档中提取知识？

使用 CLI：
```bash
he parse document.txt -o output/
```

使用 Python API：
```python
from hyperextract import Template
ka = Template.create("general/biography")
result = ka.parse(document_text)
```

### 如何选择正确的模板？

根据以下条件选择模板：
1. 文档类型（金融、法律、医学等）
2. 提取目标（实体、关系、列表等）
3. 所需输出格式（图、列表、模型等）

### 如何创建自定义模板？

请参阅[模板设计指南](../concepts/templates.md)了解如何创建自定义模板。

## 故障排除

### API 密钥问题

**错误："未找到 API 密钥"**

解决方案：使用以下方式设置 API 密钥：
```bash
he config init -k YOUR_API_KEY
```

### 提取质量问题

**提取质量低**

改进提示：
1. 使用领域特定模板
2. 提供清晰的提取说明
3. 使用更长的上下文窗口
4. 调整温度设置

### 性能问题

**提取速度慢**

优化提示：
1. 使用 `light_rag` 方法加快提取速度
2. 批量处理多个文档
3. 使用适当的批量大小

## 贡献

### 如何贡献？

请参阅[贡献指南](contributing.md)了解如何贡献。

### 如何报告错误？

请在我们的 GitHub 仓库上提交问题，包括：
- 错误的详细描述
- 重现步骤
- 预期与实际行为
- 环境信息
