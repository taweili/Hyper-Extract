# CLI

Hyper-Extract 命令行界面。

## 安装

```bash
uv pip install hyper-extract
```

## 快速开始

```bash
# 配置 API Key
he config init -k YOUR_OPENAI_API_KEY

# 提取知识
he parse document.txt -t general/biography_graph -o ./output/

# 查询知识库
he search ./output/ "有哪些关键事件？"

# 可视化知识图谱
he show ./output/
```

## 核心命令

| 命令 | 用途 |
|------|------|
| `he config init` | 配置 API Key |
| `he parse` | 提取知识 |
| `he search` | 查询知识库 |
| `he show` | 可视化图谱 |
| `he feed` | 增量补充 |
| `he list` | 列出模板 |

## 配置

[→ CLI 配置指南](./config.md)

## 详细指南

[→ CLI 命令详解](./cli.md)

## 使用示例

- [金融领域模板](../templates/finance.md)
- [法律领域模板](../templates/legal.md)
- [医学领域模板](../templates/medicine.md)
