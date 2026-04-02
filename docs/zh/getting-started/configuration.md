# 配置

Hyper-Extract 使用 TOML 配置文件。默认位置：`~/.he/config.toml`

## 快速配置

```bash
# 使用 API 密钥初始化（推荐）
he config init -k YOUR_API_KEY

# 或者分别配置 LLM 和 Embedder
he config llm --api-key YOUR_API_KEY
he config embedder --api-key YOUR_API_KEY
```

## 配置选项

### LLM 设置

```bash
he config llm --api-key YOUR_KEY --model gpt-4o-mini
```

| 选项 | 说明 | 默认值 |
|------|------|---------|
| `--api-key`, `-k` | LLM API 密钥 | 必需 |
| `--model`, `-m` | 模型名称 | gpt-4o-mini |
| `--base-url`, `-u` | 自定义 API 基础 URL | (默认) |

### Embedder 设置

```bash
he config embedder --api-key <your-api-key> --model text-embedding-3-small
```

| 选项 | 说明 | 默认值 |
|------|------|---------|
| `--api-key`, `-k` | Embedder API 密钥 | 必需 |
| `--model`, `-m` | 模型名称 | text-embedding-3-small |
| `--base-url`, `-u` | 自定义 API 基础 URL | (默认) |

## 查看配置

```bash
he config show
```

## 命令

| 命令 | 说明 |
|------|------|
| `he config init -k KEY` | 使用 API 密钥初始化 LLM 和 Embedder |
| `he config llm` | 配置 LLM 设置 |
| `he config embedder` | 配置 Embedder 设置 |
| `he config show` | 显示当前配置 |

## 下一步

- 了解[模板](../concepts/templates.md)
- 浏览[预设模板](../concepts/templates.md#preset-templates)
