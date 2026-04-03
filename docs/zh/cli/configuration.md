# CLI 配置参考

Hyper-Extract CLI 配置的完整参考。

---

## 配置文件位置

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

---

## 配置部分

### [llm] — 语言模型设置

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `model` | LLM 模型名称 | `gpt-4o-mini` |
| `api_key` | OpenAI API 密钥 | *必填* |
| `base_url` | API 基础 URL | `https://api.openai.com/v1` |

**示例：**
```toml
[llm]
model = "gpt-4o"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"
```

**支持的模型：**
- `gpt-4o-mini` — 快速、成本效益高
- `gpt-4o` — 高质量
- `gpt-4-turbo` — 最佳质量
- 其他 OpenAI 兼容模型

---

### [embedder] — 嵌入模型设置

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `model` | 嵌入模型名称 | `text-embedding-3-small` |
| `api_key` | API 密钥（默认为 llm.api_key） | — |

**示例：**
```toml
[embedder]
model = "text-embedding-3-large"
```

**支持的模型：**
- `text-embedding-3-small` — 快速、成本效益高
- `text-embedding-3-large` — 更好的质量
- `text-embedding-ada-002` — 传统模型

---

### [defaults] — 默认行为设置

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `language` | 默认语言（`en` 或 `zh`） | `en` |
| `chunk_size` | 处理文本的块大小 | `2048` |
| `chunk_overlap` | 块之间的重叠 | `256` |
| `max_workers` | 并行处理工作线程数 | `10` |
| `verbose` | 启用详细输出 | `false` |

**示例：**
```toml
[defaults]
language = "en"
chunk_size = 4096
chunk_overlap = 512
max_workers = 5
verbose = true
```

---

## 环境变量

所有配置选项都可以通过环境变量设置：

| 变量 | 映射到 | 示例 |
|----------|---------|---------|
| `OPENAI_API_KEY` | `llm.api_key`, `embedder.api_key` | `sk-...` |
| `OPENAI_BASE_URL` | `llm.base_url` | `https://api.openai.com/v1` |
| `HE_LLM_MODEL` | `llm.model` | `gpt-4o` |
| `HE_EMBEDDER_MODEL` | `embedder.model` | `text-embedding-3-large` |
| `HE_DEFAULT_LANGUAGE` | `defaults.language` | `zh` |
| `HE_CHUNK_SIZE` | `defaults.chunk_size` | `4096` |
| `HE_VERBOSE` | `defaults.verbose` | `true` |

---

## 完整示例

```toml
# ~/.he/config.toml

[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key-here"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
# api_key 默认为 llm.api_key

[defaults]
language = "en"
chunk_size = 2048
chunk_overlap = 256
max_workers = 10
verbose = false
```

---

## 配置优先级

设置按以下顺序解析（最高优先级优先）：

1. **命令行参数**（例如 `-l zh`）
2. **环境变量**（例如 `OPENAI_API_KEY`）
3. **配置文件**（`~/.he/config.toml`）
4. **内置默认值**

---

## 管理配置

### 初始化

```bash
he config init -k your-api-key
```

### 查看当前设置

```bash
he config show
```

### 更新设置

```bash
# 更新单个值
he config set llm.model gpt-4o

# 或直接编辑文件
nano ~/.he/config.toml
```

### 重置为默认值

```bash
rm ~/.he/config.toml
he config init -k your-api-key
```

---

## 高级配置

### 自定义 API 端点

对于 OpenAI 兼容 API（Azure、本地模型等）：

```toml
[llm]
model = "your-model-name"
api_key = "your-key"
base_url = "https://your-api-endpoint.com/v1"

[embedder]
model = "your-embedding-model"
```

### LLM 和嵌入器使用不同密钥

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-llm-key"

[embedder]
model = "text-embedding-3-small"
api_key = "sk-embedder-key"
```

---

## 故障排除

### 权限被拒绝

```bash
# 修复权限
chmod 600 ~/.he/config.toml
```

### 无效的 TOML 格式

验证配置：

```bash
# 使用 Python
python -c "import tomllib; tomllib.load(open('~/.he/config.toml', 'rb'))"
```

常见问题：
- 字符串缺少引号
- 尾部逗号
- 错误的节标题

---

## 另请参见

- [`he config`](commands/config.md) — 配置命令
- [安装指南](../getting-started/installation.md) — 初始设置
