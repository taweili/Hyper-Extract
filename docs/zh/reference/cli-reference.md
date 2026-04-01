# CLI 参考

Hyper-Extract 所有 CLI 命令的完整参考。

## 命令概览

| 命令 | 描述 |
|------|------|
| `he config` | 管理配置 |
| `he parse` | 从文档提取知识 |
| `he search` | 查询提取的知识 |
| `he feed` | 向知识库添加新文档 |
| `he list` | 列出可用模板 |

## config

管理 Hyper-Extract 配置。

### 语法

```bash
he config <action> [options]
```

### 操作

#### init

初始化配置：

```bash
he config init -k API_KEY [--provider PROVIDER]
```

#### show

显示当前配置：

```bash
he config show [--format json|yaml]
```

#### set

更新配置选项：

```bash
he config set KEY VALUE
```

#### list-templates

列出可用模板：

```bash
he config list-templates [--category CATEGORY]
```

## parse

从文档中提取知识。

### 语法

```bash
he parse <input> [options]
```

### 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出目录 | 必需 |
| `-t, --template` | 模板名称 | 自动检测 |
| `-l, --language` | 文档语言 | 自动检测 |
| `--method` | 提取方法 | 默认 |
| `--batch` | 批量处理 | False |
| `--format` | 输出格式 | json |

## search

查询提取的知识。

### 语法

```bash
he search <knowledge_base> <query> [options]
```

### 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--filter` | 按节点/边类型过滤 | 无 |
| `--limit` | 最大结果数 | 10 |
| `--format` | 输出格式 | json |

## feed

向现有知识库添加新文档。

### 语法

```bash
he feed <knowledge_base> <documents...> [options]
```

## list

列出可用模板。

### 语法

```bash
he list [options]
```

### 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--category` | 按类别过滤 | 全部 |
| `--domain` | 按领域过滤 | 全部 |
| `--format` | 输出格式 | table |

## 全局选项

| 选项 | 描述 |
|------|------|
| `--help` | 显示帮助信息 |
| `--version` | 显示版本号 |
| `--verbose` | 启用详细输出 |
| `--debug` | 启用调试模式 |
| `--config PATH` | 自定义配置文件 |
