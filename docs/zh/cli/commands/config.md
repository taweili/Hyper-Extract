# he config

管理 Hyper-Extract 的 LLM 和嵌入模型配置。

---

## 概要

```bash
he config [COMMAND] [OPTIONS]
```

## 命令

| 命令 | 描述 |
|---------|-------------|
| `init` | 初始化配置（懒人模式默认使用 `gpt-4o-mini` + `text-embedding-3-small`） |
| `show` | 显示当前配置 |
| `llm` | 配置 LLM 设置 |
| `embedder` | 配置嵌入模型设置 |

---

## he config init

初始化配置。这是**懒人一键配置** —— 只要传入 `-k`，就会自动使用内置默认值，无需任何交互：

- **LLM**: `gpt-4o-mini`
- **嵌入模型**: `text-embedding-3-small`

```bash
he config init [OPTIONS]
```

### 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--api-key` | `-k` | LLM 和嵌入模型的 API 密钥 |
| `--base-url` | `-u` | 自定义 API 基础 URL（可选） |

### 示例

#### 懒人一键配置（推荐）

```bash
he config init -k sk-your-api-key-here
```

执行后会自动保存默认模型 `gpt-4o-mini` 和 `text-embedding-3-small`。

#### 使用自定义基础 URL

```bash
he config init -k sk-your-key -u https://api.openai.com/v1
```

#### 交互式初始化

```bash
he config init
# 按步骤交互式输入模型名称和 API 密钥
```

---

## he config show

显示当前配置。

```bash
he config show
```

**输出示例：**

```
┌─────────────────────────────────────────────────────────┐
│         Hyper-Extract Configuration                     │
├──────────┬─────────────────────┬─────────────┬──────────┤
│ Service  │ Model               │ API Key     │ Base URL │
├──────────┼─────────────────────┼─────────────┼──────────┤
│ LLM      │ gpt-4o-mini         │ sk-xxxxx... │ (default)│
│ Embedder │ text-embedding-3... │ sk-xxxxx... │ (default)│
└──────────┴─────────────────────┴─────────────┴──────────┘
```

---

## he config llm

单独配置 LLM 设置。

```bash
he config llm [OPTIONS]
```

### 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--api-key` | `-k` | LLM API 密钥 |
| `--model` | `-m` | LLM 模型名称 |
| `--base-url` | `-u` | 自定义 API 基础 URL |
| `--show` | — | 查看当前 LLM 配置 |
| `--unset` | — | 清除 LLM 配置 |

### 示例

```bash
# 查看 LLM 配置
he config llm --show

# 修改 LLM 模型
he config llm --model gpt-4o

# 修改 LLM API 密钥和接口地址
he config llm --api-key sk-your-key --base-url https://api.openai.com/v1

# 重置 LLM 配置
he config llm --unset
```

---

## he config embedder

单独配置嵌入模型设置。

```bash
he config embedder [OPTIONS]
```

### 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--api-key` | `-k` | 嵌入模型 API 密钥 |
| `--model` | `-m` | 嵌入模型名称 |
| `--base-url` | `-u` | 自定义 API 基础 URL |
| `--show` | — | 查看当前嵌入模型配置 |
| `--unset` | — | 清除嵌入模型配置 |

### 示例

```bash
# 查看嵌入模型配置
he config embedder --show

# 使用更大的嵌入模型
he config embedder --model text-embedding-3-large

# 重置嵌入模型配置
he config embedder --unset
```

---

## 配置文件

配置存储在：

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### 配置示例

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = ""  # 空字符串表示继承 llm.api_key
base_url = ""  # 空字符串表示继承 llm.base_url
```

## 环境变量

| 变量 | 描述 |
|----------|-------------|
| `OPENAI_API_KEY` | LLM 和嵌入模型的 API 密钥备用方案 |
| `OPENAI_BASE_URL` | 自定义 API 基础 URL 备用方案 |

**优先级（从高到低）：** 命令行参数 → 环境变量 → 配置文件 → 默认值。

---

## 故障排除

### "未找到 API 密钥"

```bash
he config init -k your-api-key
```

或：

```bash
export OPENAI_API_KEY=your-api-key
```

### "未找到配置文件"

```bash
he config init -k your-api-key
```

---

## 另请参见

- [配置参考](../configuration.md) — 详细配置选项说明
- [安装指南](../../getting-started/installation.md) — 初始安装步骤
