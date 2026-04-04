# 安装

Hyper-Extract 需要 **Python 3.11+**。

---

## 从 PyPI 安装

=== "uv (推荐)"

    ```bash
    uv pip install hyper-extract
    ```

=== "pip"

    ```bash
    pip install hyper-extract
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
