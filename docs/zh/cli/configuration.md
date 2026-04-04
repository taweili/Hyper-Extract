# CLI 配置参考

Hyper-Extract CLI 的配置指南，从快速入门到高级设置。

---

## 快速开始

只需 3 步完成配置。

### 1. 初始化配置

```bash
he config init -k YOUR_API_KEY
```

这会创建 `~/.he/config.toml` 配置文件，使用以下默认值：
- **LLM**: `gpt-4o-mini`
- **嵌入模型**: `text-embedding-3-small`

### 2. 验证配置

```bash
he config show
```

看到类似输出即配置成功：

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

### 3. 修改配置（如需）

```bash
# 更换 LLM 模型
he config llm --model gpt-4o

# 使用不同的嵌入模型
he config embedder --model text-embedding-3-large

# 配置自定义 API 端点
he config llm --base-url https://your-api-endpoint.com/v1
```

---

## CLI 命令参考

### 命令概览

| 命令 | 常用参数 | 描述 |
|------|---------|------|
| `he config init` | `-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址 | 初始化配置（首次使用） |
| `he config llm` | `-m, --model` — 模型名称<br>`-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址<br>`--show` — 查看当前配置<br>`--unset` — 清除配置 | 配置 LLM |
| `he config embedder` | `-m, --model` — 模型名称<br>`-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址<br>`--show` — 查看当前配置<br>`--unset` — 清除配置 | 配置嵌入模型 |
| `he config show` | — | 查看完整配置 |

### 常见用法示例

**交互式初始化（推荐首次使用）：**
```bash
he config init
# 按提示输入模型名、API 密钥等信息
```

**非交互式初始化（脚本中使用）：**
```bash
he config init -k sk-your-api-key
```

**查看 LLM 配置：**
```bash
he config llm --show
```

**单独配置嵌入模型（使用不同密钥）：**
```bash
he config embedder --api-key sk-embedder-key --model text-embedding-3-large
```

**清除配置（重置为默认值）：**
```bash
he config llm --unset
he config embedder --unset
```

---

## 配置文件详解

当你运行 `he config init` 时，会自动创建 `~/.he/config.toml` 文件。

### 文件位置

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### 配置格式

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

### 配置项说明

| 节 | 键 | 描述 | 默认值 |
|---|-----|------|--------|
| `[llm]` | `model` | LLM 模型名称 | `gpt-4o-mini` |
| `[llm]` | `api_key` | OpenAI API 密钥 | 必填 |
| `[llm]` | `base_url` | API 基础 URL | `https://api.openai.com/v1` |
| `[embedder]` | `model` | 嵌入模型名称 | `text-embedding-3-small` |
| `[embedder]` | `api_key` | API 密钥（留空继承 llm） | — |
| `[embedder]` | `base_url` | API 基础 URL（留空继承 llm） | — |

### 支持的模型

**LLM 模型：**
- `gpt-4o-mini` — 快速、成本效益高（默认）
- `gpt-4o` — 高质量
- `gpt-4-turbo` — 最佳质量
- 其他 OpenAI 兼容模型

**嵌入模型：**
- `text-embedding-3-small` — 快速、成本效益高（默认）
- `text-embedding-3-large` — 更好的质量
- `text-embedding-ada-002` — 传统模型

---

## 环境变量

以下环境变量可作为配置的备选方案：

| 变量 | 映射到 | 示例 |
|------|--------|------|
| `OPENAI_API_KEY` | `llm.api_key`, `embedder.api_key` | `sk-...` |
| `OPENAI_BASE_URL` | `llm.base_url` | `https://api.openai.com/v1` |

**优先级说明：** 环境变量优先级高于配置文件，低于命令行参数。

**使用场景：**
- 临时切换 API 密钥
- CI/CD 环境中注入密钥
- 不想在配置文件中硬编码密钥

---

## 高级配置

### 使用 OpenAI 兼容 API

对于 Azure、本地模型等 OpenAI 兼容 API：

```toml
[llm]
model = "your-model-name"
api_key = "your-key"
base_url = "https://your-api-endpoint.com/v1"

[embedder]
model = "your-embedding-model"
```

### LLM 和嵌入器使用不同密钥和不同 base_url

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-llm-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-large"
api_key = "sk-embedder-key"
base_url = "https://your-embedder-provider.com/v1"
```

---

## 故障排除

### "API key not found"

**原因**: 未配置 API 密钥

**解决**:

```bash
he config init -k YOUR_API_KEY
```

### "Failed to connect to API"

**原因**: 网络问题或 base_url 配置错误

**解决**:

```bash
# 检查配置
he config llm --show

# 重新设置 base_url
he config llm --base-url https://api.openai.com/v1
```

### 权限被拒绝

**解决**:

```bash
chmod 600 ~/.he/config.toml
```

### 无效的 TOML 格式

**验证配置**:

```bash
python3 -c "import tomllib; tomllib.load(open('$HOME/.he/config.toml', 'rb'))"
```

**常见问题**:

- 字符串缺少引号
- 多余的逗号
- 错误的节标题（如使用中文标点）

---

## 另请参见

- [`he config`](commands/config.md) — 详细的配置命令说明
- [安装指南](../getting-started/installation.md) — 初始安装步骤
