# CLI 指南

Hyper-Extract CLI 提供了强大的命令行界面用于知识提取。

## 安装

CLI 已包含在主包中：

```bash
pip install hyper-extract
```

## 基本用法

### 初始化配置

```bash
he config init -k YOUR_API_KEY
```

### 解析文档

```bash
he parse document.txt -o output/
```

### 搜索提取的知识

```bash
he search output/ "关键事件有哪些？"
```

### 添加新文档

```bash
he feed output/ new_document.txt
```

## 命令

### config

管理配置：

```bash
# 初始化
he config init -k API_KEY

# 显示当前配置
he config show

# 更新配置
he config set llm.model gpt-4o-mini

# 列出可用模板
he config list-templates
```

### parse

从文档中提取知识：

```bash
# 基本用法
he parse input.txt -o output/

# 使用模板
he parse input.txt -t finance/earnings_summary -o output/

# 指定语言
he parse input.txt -l zh -o output/

# 批量处理
he parse ./documents/ -o output/ --batch
```

### search

查询提取的知识：

```bash
# 基本搜索
he search output/ "发生了什么？"

# 使用过滤器
he search output/ "财务事件" --filter type=Event

# 限制结果数量
he search output/ "公司" --limit 10
```

### feed

向现有知识库添加新文档：

```bash
# 添加单个文档
he feed output/ new_doc.txt

# 添加多个文档
he feed output/ ./new_docs/
```

### list

列出可用模板和预设：

```bash
# 列出所有模板
he list

# 按类别列出
he list --category finance

# 列出领域模板
he list --domain general
```

## 选项

### 全局选项

| 选项 | 描述 |
|------|------|
| `--help` | 显示帮助信息 |
| `--version` | 显示版本号 |
| `--verbose` | 启用详细输出 |
| `--config PATH` | 使用自定义配置文件 |

### Parse 选项

| 选项 | 描述 |
|------|------|
| `-o, --output PATH` | 输出目录 |
| `-t, --template NAME` | 要使用的模板 |
| `-l, --language CODE` | 文档语言（en、zh 等）|
| `--batch` | 启用批量处理 |

## 示例

### 金融文档提取

```bash
he parse annual_report.pdf -t finance/earnings_summary -o ./results/
```

### 法律文档提取

```bash
he parse contract.txt -t legal/case_facts -o ./legal_output/
```

### 多语言支持

```bash
he parse chinese_doc.txt -l zh -o ./output/
```

## 下一步

- 探索 [Python API](python-api.md)
- 浏览 [领域模板](domain-templates/index.md)
- 查看 [CLI 参考](../reference/cli-reference.md)
