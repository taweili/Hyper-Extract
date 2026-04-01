# 安装

本指南介绍如何安装 Hyper-Extract 及其依赖项。

## 系统要求

- Python 3.9+
- pip 或 uv 包管理器
- OpenAI API 密钥（或兼容的 LLM API）

## 安装方法

### 使用 pip

```bash
pip install hyper-extract
```

### 使用 uv

```bash
uv pip install hyper-extract
```

## 额外依赖安装

针对特定用例安装额外依赖：

```bash
# 安装所有集成
pip install hyper-extract[all]

# 安装 OpenAI 支持
pip install hyper-extract[openai]

# 安装开发工具
pip install hyper-extract[dev]
```

## 验证安装

安装后，验证是否正常工作：

```bash
he --version
```

您应该看到版本号。

## 设置 API 密钥

Hyper-Extract 需要 LLM 服务的 API 密钥。设置方法：

### 使用环境变量

```bash
export OPENAI_API_KEY=your-api-key-here
```

### 使用 CLI

```bash
he config init -k your-api-key-here
```

## 下一步

- 继续学习[快速教程](quickstart.md) 运行您的第一次提取
- 或在[配置](configuration.md)中配置高级选项
