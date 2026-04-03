# CLI 配置

## 配置文件

CLI 配置文件位于 `~/.he/config.toml`。

## 初始化配置

```bash
# 使用 API Key 初始化（推荐首次用户）
he config init -k YOUR_OPENAI_API_KEY

# 交互式设置（会提示输入 LLM 和 Embedder 配置）
he config init
```

## 查看配置

```bash
# 显示当前配置
he config show
```

## 配置 LLM

```bash
# 设置 LLM API key 和模型
he config llm --api-key YOUR_KEY --model gpt-4o-mini

# 显示当前 LLM 配置
he config llm --show

# 设置自定义 base URL
he config llm --api-key YOUR_KEY --base-url https://api.openai.com/v1

# 清除 LLM 配置
he config llm --unset
```

## 配置 Embedder

```bash
# 设置 Embedder API key 和模型
he config embedder --api-key YOUR_KEY --model text-embedding-3-small

# 显示当前 Embedder 配置
he config embedder --show

# 设置自定义 base URL
he config embedder --api-key YOUR_KEY --base-url https://api.openai.com/v1

# 清除 Embedder 配置
he config embedder --unset
```

## 配置选项

### LLM 选项

| 选项 | 标志 | 描述 | 默认值 |
|------|------|------|--------|
| API Key | `--api-key`, `-k` | LLM API key | 必填 |
| Model | `--model`, `-m` | LLM 模型名称 | `gpt-4o-mini` |
| Base URL | `--base-url`, `-u` | 自定义 API base URL | OpenAI 默认 |

### Embedder 选项

| 选项 | 标志 | 描述 | 默认值 |
|------|------|------|--------|
| API Key | `--api-key`, `-k` | Embedder API key | 必填 |
| Model | `--model`, `-m` | Embedder 模型名称 | `text-embedding-3-small` |
| Base URL | `--base-url`, `-u` | 自定义 API base URL | OpenAI 默认 |

## 环境变量

你也可以使用环境变量作为替代方案：

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1
```

当配置文件中未设置时，将使用环境变量。
