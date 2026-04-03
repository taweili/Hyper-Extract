# Python SDK

Hyper-Extract Python API。

## 安装

```bash
pip install hyper-extract
```

## 快速开始

```python
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

from hyperextract import Template

# 创建模板
ka = Template.create("general/biography_graph", "zh")

# 解析文档
with open("examples/zh/sushi.md", "r", encoding="utf-8") as f:
    text = f.read()
result = ka.parse(text)

# 访问结果
print(result.entities)
print(result.relations)
```

## 核心 API

| API | 用途 |
|-----|------|
| `Template.create()` | 创建模板实例 |
| `ka.parse()` | 解析文档 |
| `ka.feed()` | 增量补充 |
| `ka.search()` | 查询知识库 |

## 配置

[→ Python SDK 配置指南](./config.md)

## 详细指南

[→ Python API 详解](./python-api.md)

## 使用示例

- [金融领域模板](../templates/finance.md)
- [法律领域模板](../templates/legal.md)
- [医学领域模板](../templates/medicine.md)
