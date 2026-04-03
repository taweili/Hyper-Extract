# Python SDK 配置

## 环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制示例 env 文件
cp .env.example .env
```

编辑 `.env` 文件：

```bash
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

## 加载环境变量

使用 `python-dotenv` 加载环境变量：

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()
```

## 程序化配置

你也可以通过代码设置环境变量：

```python
import os

os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
```

## 配置选项

### LLM 选项

| 选项 | 环境变量 | 默认值 |
|------|---------|--------|
| API Key | `OPENAI_API_KEY` | 必填 |
| Base URL | `OPENAI_BASE_URL` | OpenAI 默认 |
| Model | `LLM_MODEL` | `gpt-4o-mini` |
| Temperature | `LLM_TEMPERATURE` | `0.0` |

### Embedder 选项

| 选项 | 环境变量 | 默认值 |
|------|---------|--------|
| Model | `EMBEDDER_MODEL` | `text-embedding-3-small` |
| Batch Size | `EMBEDDER_BATCH_SIZE` | `100` |

## 示例 .env 文件

```bash
# 必填
OPENAI_API_KEY=sk-your-api-key

# 可选
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
EMBEDDER_MODEL=text-embedding-3-small
```
