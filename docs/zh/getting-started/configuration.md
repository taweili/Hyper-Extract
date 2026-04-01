# 配置

本指南介绍 Hyper-Extract 的高级配置选项。

## 配置文件

Hyper-Extract 使用 YAML 配置文件。默认位置：`~/.hyper-extract/config.yaml`

## 配置选项

### LLM 设置

```yaml
llm:
  provider: openai  # openai, anthropic, azure 等
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}  # 或使用环境变量
  temperature: 0.0
  max_tokens: 4096
```

### Embedding 设置

```yaml
embedding:
  provider: openai  # openai, huggingface 等
  model: text-embedding-3-small
  api_key: ${OPENAI_API_KEY}
```

### 提取设置

```yaml
extraction:
  default_type: AutoGraph
  max_retries: 3
  timeout: 60
  batch_size: 10
```

### 存储设置

```yaml
storage:
  type: local  # local, s3 等
  path: ./output
  format: json  # json, yaml, parquet
```

## 环境变量

| 变量 | 描述 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `HYPER_EXTRACT_CONFIG` | 配置文件路径 |

## CLI 配置

通过 CLI 初始化配置：

```bash
# 使用 OpenAI 初始化
he config init -k your-api-key

# 显示当前配置
he config show

# 更新特定选项
he config set llm.model gpt-4o-mini
```

## 下一步

- 探索[核心概念](../concepts/index.md) 了解提取类型
- 查看 [CLI 参考](../reference/cli-reference.md) 了解所有命令
