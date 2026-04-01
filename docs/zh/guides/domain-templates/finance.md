# 金融模板

Hyper-Extract 提供专门的金融文档提取模板。

## 可用模板

### 财报摘要

从财报中提取关键财务指标：

```yaml
name: earnings_summary
type: TemporalGraph
schema:
  nodes:
    - type: FinancialMetric
    - type: Company
  edges:
    - type: REPORTED
```

### 风险因素

从金融文档中提取风险因素：

```yaml
name: risk_factors
type: List
schema:
  item:
    - name: category
      type: string
    - name: description
      type: string
```

### 所有权图

提取所有权关系：

```yaml
name: ownership_graph
type: Graph
schema:
  nodes:
    - type: Entity
    - type: Company
  edges:
    - type: OWNS
```

## 使用示例

### CLI

```bash
# 提取财报摘要
he parse earnings_report.pdf -t finance/earnings_summary -o output/

# 提取风险因素
he parse 10k_filing.txt -t finance/risk_factors -o output/
```

### Python API

```python
from hyperextract import Template

# 加载金融模板
ka = Template.create("finance/earnings_summary")

# 从文档提取
result = ka.parse(earnings_text)

# 访问财务指标
for metric in result.get_nodes("FinancialMetric"):
    print(f"{metric.name}: {metric.value}")
```

## 支持的文档类型

- 年度报告
- 季度财报
- 10-K/10-Q 文件
- 股权研究报告
- 财经新闻
- IPO 招股说明书
- 供应链分析

## 下一步

- [法律模板](legal.md)
- [医学模板](medicine.md)
- [模板库](../../reference/template-gallery.md)
