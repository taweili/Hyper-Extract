# he config

管理 Hyper-Extract 配置。

---

## 概要

```bash
he config [COMMAND] [OPTIONS]
```

## 命令

| 命令 | 描述 |
|---------|-------------|
| `init` | 初始化配置 |
| `show` | 显示当前配置 |
| `set` | 设置配置值 |
| `get` | 获取配置值 |

---

## he config init

使用 API 凭证初始化配置。

```bash
he config init [OPTIONS]
```

### 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--key` | `-k` | OpenAI API 密钥 |
| `--base-url` | `-u` | API 基础 URL（可选） |
| `--model` | `-m` | 默认模型（默认：gpt-4o-mini） |
| `--embedder` | `-e` | 嵌入模型（默认：text-embedding-3-small） |

### 示例

#### 基本设置

```bash
he config init -k sk-your-api-key-here
```

#### 使用自定义基础 URL

```bash
he config init -k sk-your-key -u https://api.openai.com/v1
```

#### 使用自定义模型

```bash
he config init -k sk-your-key -m gpt-4o -e text-embedding-3-large
```

#### 交互模式

```bash
he config init
# 交互式提示输入 API 密钥
```

---

## he config show

显示当前配置。

```bash
he config show
```

**输出：**
```
Configuration (from ~/.he/config.toml):

[llm]
model = "gpt-4o-mini"
api_key = "sk-...***"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = "sk-...***"

[defaults]
language = "en"
chunk_size = 2048
max_workers = 10
```

---

## he config set

设置配置值。

```bash
he config set <KEY> <VALUE>
```

### 示例

```bash
# 更改默认模型
he config set llm.model gpt-4o

# 更改嵌入模型
he config set embedder.model text-embedding-3-large

# 设置默认语言
he config set defaults.language zh
```

---

## he config get

获取配置值。

```bash
he config get <KEY>
```

### 示例

```bash
he config get llm.model
# Output: gpt-4o-mini

he config get defaults.language
# Output: en
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
api_key = "sk-your-api-key"

[defaults]
language = "en"
chunk_size = 2048
chunk_overlap = 256
max_workers = 10
verbose = false
```

---

## 环境变量

也可以通过环境变量设置配置（更高优先级）：

| 变量 | 描述 |
|----------|-------------|
| `OPENAI_API_KEY` | LLM 和嵌入器的 API 密钥 |
| `OPENAI_BASE_URL` | 自定义 API 基础 URL |
| `HE_LLM_MODEL` | 默认 LLM 模型 |
| `HE_EMBEDDER_MODEL` | 默认嵌入模型 |

---

## 优先级顺序

配置按以下顺序解析（最高优先）：

1. 命令行参数
2. 环境变量
3. 配置文件
4. 内置默认值

---

## 故障排除

### "未找到 API 密钥"

初始化配置：

```bash
he config init -k your-api-key
```

或设置环境变量：

```bash
export OPENAI_API_KEY=your-api-key
```

### "API 密钥无效"

检查您的 API 密钥：

```bash
he config show
# 验证密钥是否正确
```

### "未找到配置文件"

运行 init 创建：

```bash
he config init -k your-api-key
```

---

## 另请参见

- [配置参考](../configuration.md) — 详细配置选项
- [安装指南](../../getting-started/installation.md) — 初始设置
