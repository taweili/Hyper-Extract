# 法律模板

法律文档处理和分析。

---

## 概述

法律模板专为从法律文档中提取结构化信息而设计。

---

## 模板

### contract_obligation

**类型**：list

**用途**：提取合同义务和条款

**最适合**：
- 服务协议
- 雇佣合同
- 采购协议
- 许可协议

**字段**：
| 字段 | 类型 | 描述 |
|------|------|------|
| `party` | str | 义务方 |
| `obligation` | str | 义务描述 |
| `deadline` | str | 截止日期/时间线 |
| `conditions` | str | 条件或限制 |

**示例：**
```bash
he parse contract.md -t legal/contract_obligation -l en
```

**Python：**
```python
ka = Template.create("legal/contract_obligation", "en")
result = ka.parse(contract_text)

for obl in result.data.items:
    print(f"{obl.party}: {obl.obligation}")
    if obl.deadline:
        print(f"  截止: {obl.deadline}")
```

---

### case_citation

**类型**：graph

**用途**：提取法律案例引用和关系

**最适合**：
- 法律摘要
- 法庭意见
- 研究备忘录
- 案例分析

**实体**：
- 案例
- 法规
- 条例
- 法院

**关系**：
- `cited_by` — 引用关系
- `overruled` — 推翻关系
- `distinguished` — 区分关系

**示例：**
```bash
he parse brief.md -t legal/case_citation -l en
```

---

### case_fact_timeline

**类型**：temporal_graph

**用途**：提取按时间排列的案件事实

**最适合**：
- 案件摘要
- 调查报告
- 诉讼时间线

**特性**：
- 事件日期
- 事实描述
- 相关方

**示例：**
```bash
he parse case_summary.md -t legal/case_fact_timeline -l en
```

---

### compliance_list

**类型**：list

**用途**：提取合规要求

**最适合**：
- 监管文档
- 合规手册
- 政策文档

**字段**：
| 字段 | 类型 | 描述 |
|------|------|------|
| `requirement` | str | 合规要求 |
| `regulation` | str | 来源条例 |
| `priority` | str | 优先级 |

**示例：**
```bash
he parse compliance.md -t legal/compliance_list -l en
```

---

### defined_term_set

**类型**：set

**用途**：提取定义术语及其含义

**最适合**：
- 带定义章节的合同
- 技术法律文档
- 词汇表提取

**示例：**
```bash
he parse agreement.md -t legal/defined_term_set -l en
```

**输出：**
```python
{
    "items": [
        "保密信息：指所有非公开的...",
        "生效日期：指签署日期...",
        "当事方：指任一签字方..."
    ]
}
```

---

## 用例

### 合同审查

```python
from hyperextract import Template

ka = Template.create("legal/contract_obligation", "en")
obligations = ka.parse(contract)

# 查找所有截止日期
deadlines = [o for o in obligations.data.items if o.deadline]
for d in sorted(deadlines, key=lambda x: x.deadline):
    print(f"{d.deadline}: {d.party} - {d.obligation}")
```

### 案例分析

```python
ka = Template.create("legal/case_citation", "en")
case_graph = ka.parse(brief)

# 查找引用最多的案例
citations = {}
for rel in case_graph.data.relations:
    if rel.type == "cited_by":
        citations[rel.target] = citations.get(rel.target, 0) + 1

top_cases = sorted(citations.items(), key=lambda x: x[1], reverse=True)
```

### 尽职调查

```python
# 提取义务
ka = Template.create("legal/contract_obligation", "en")
obligations = ka.parse(agreement)

# 提取风险
ka2 = Template.create("finance/risk_factor_set", "en")
risks = ka2.parse(agreement)

# 分析
high_risk_obligations = [
    o for o in obligations.data.items
    if any(r in o.obligation.lower() for r in risks.data.items)
]
```

---

## 提示

1. **contract_obligation 用于截止期限** — 跟踪合同义务
2. **case_citation 用于研究** — 构建引用网络
3. **defined_term_set 用于明确性** — 提取关键定义
4. **结合搜索使用** — 使用 `he search` 查找特定条款

---

## 参见

- [浏览所有模板](browse.md)
- [金融模板](finance.md)
