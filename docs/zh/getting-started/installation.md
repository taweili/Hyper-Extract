# 安装

Hyper-Extract 需要 **Python 3.11+**。

---

## 从 PyPI 安装

=== "pip"

    ```bash
    pip install hyper-extract
    ```

=== "uv (推荐)"

    ```bash
    uv pip install hyper-extract
    ```

=== "conda"

    ```bash
    pip install hyper-extract
    ```

---

## 验证安装

```bash
he --version
```

您应该看到类似输出：

```
Hyper-Extract CLI version 0.1.0
```

---

## 可选依赖

=== "Anthropic Claude 支持"

    ```bash
    pip install hyper-extract[anthropic]
    ```

=== "Google Gemini 支持"

    ```bash
    pip install hyper-extract[google]
    ```

=== "所有可选依赖"

    ```bash
    pip install hyper-extract[all]
    ```

---

## 配置

在使用 Hyper-Extract 之前，您需要配置 LLM API 凭证。

### 选项 1：使用 CLI（推荐）

```bash
he config init -k YOUR_OPENAI_API_KEY
```

这将在 `~/.he/config.toml` 创建配置文件。

### 选项 2：使用环境变量

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
```

### 选项 3：使用 .env 文件（仅限 Python）

在项目根目录创建 `.env` 文件：

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

然后在 Python 代码中加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 开发安装

如果您想贡献或修改源代码：

```bash
# 克隆仓库
git clone https://github.com/yifanfeng97/hyper-extract.git
cd hyper-extract

# 以可编辑模式安装开发依赖
pip install -e ".[dev]"
```

---

## 接下来做什么？

- [:octicons-arrow-right-24: CLI 快速入门](cli-quickstart.md) — 从终端进行首次提取
- [:octicons-arrow-right-24: Python 快速入门](python-quickstart.md) — 使用 Python 进行首次提取
