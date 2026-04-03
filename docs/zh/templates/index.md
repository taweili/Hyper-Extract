# 模板库

浏览并选择 80+ 个领域特定的提取模板。

---

## 什么是模板？

模板是预先配置的提取设置，包含：
- **自动类型** — 输出数据结构
- **提示词** — 针对特定领域优化
- **模式** — 用例的字段定义
- **指南** — 提取规则

---

## 模板类别

<div class="grid cards" markdown>

-   :material-folder:{ .lg .middle } __通用__

    ---

    基础类型和常见提取任务
    
    - 传记图谱
    - 知识图谱
    - 概念提取
    
    [:octicons-arrow-right-24: 浏览](general/index.md)

-   :material-chart-line:{ .lg .middle } __金融__

    ---

    金融文档分析
    
    - 财报摘要
    - 风险因素
    - 股权结构
    
    [:octicons-arrow-right-24: 浏览](finance.md)

-   :material-scale-balance:{ .lg .middle } __法律__

    ---

    法律文档处理
    
    - 合同义务
    - 案例引用
    - 合规清单
    
    [:octicons-arrow-right-24: 浏览](legal.md)

-   :material-hospital:{ .lg .middle } __医疗__

    ---

    医学文本分析
    
    - 解剖图谱
    - 药物相互作用
    - 治疗方案
    
    [:octicons-arrow-right-24: 浏览](medicine.md)

-   :material-leaf:{ .lg .middle } __中医__

    ---

    中医药
    
    - 草药属性
    - 方剂组成
    - 经络图谱
    
    [:octicons-arrow-right-24: 浏览](tcm.md)

-   :material-factory:{ .lg .middle } __工业__

    ---

    工业文档
    
    - 设备拓扑
    - 安全控制
    - 操作流程
    
    [:octicons-arrow-right-24: 浏览](industry.md)

</div>

---

## 快速选择指南

| 我想提取... | 使用模板 |
|------------|---------|
| 人物生平 | `general/biography_graph` |
| 研究论文概念 | `general/concept_graph` |
| 公司财报 | `finance/earnings_summary` |
| 合同条款 | `legal/contract_obligation` |
| 医疗症状 | `medicine/symptom_list` |
| 中草药 | `tcm/herb_property` |
| 设备规格 | `industry/equipment_topology` |

---

## 如何选择

### 按文档类型

| 文档 | 模板类别 |
|------|---------|
| 传记、简介 | 通用 |
| 财报、10-K | 金融 |
| 合同、法律摘要 | 法律 |
| 医疗记录、论文 | 医疗 |
| 中医药文本、处方 | 中医 |
| 手册、流程 | 工业 |

### 按输出类型

| 需求 | 自动类型 | 示例模板 |
|------|---------|---------|
| 摘要报告 | AutoModel | `earnings_summary`, `discharge_instruction` |
| 项目列表 | AutoList | `compliance_list`, `symptom_list` |
| 唯一项目 | AutoSet | `risk_factor_set`, `defined_term_set` |
| 网络/图谱 | AutoGraph | `knowledge_graph`, `ownership_graph` |
| 时间线 | AutoTemporalGraph | `event_timeline`, `biography_graph` |

→ [完整选择指南](how-to-choose.md)

---

## 使用模板

### CLI

```bash
# 列出可用模板
he list template

# 使用模板
he parse doc.md -t general/biography_graph -o ./out/ -l en
```

### Python

```python
from hyperextract import Template

# 从预设创建
ka = Template.create("general/biography_graph", "en")

# 列出所有
all_templates = Template.list()

# 按领域筛选
finance = Template.list(filter_by_tag="finance")
```

---

## 模板属性

每个模板包含：

- **名称** — 唯一标识符
- **类型** — 自动类型（graph、list、model 等）
- **标签** — 领域分类
- **语言** — 支持的语言（zh、en）
- **描述** — 提取内容的说明

### 查看模板详情

```python
from hyperextract import Template

# 获取模板信息
cfg = Template.get("general/biography_graph")

print(cfg.name)           # biography_graph
print(cfg.type)           # temporal_graph
print(cfg.tags)           # ['general', 'biography']
print(cfg.description)    # 描述文本
```

---

## 浏览所有模板

→ [完整模板浏览器](browse.md)

---

## 创建自定义模板

需要特定的功能？创建您自己的模板：

→ [自定义模板指南](../python/guides/custom-templates.md)

---

## 模板格式参考

了解 YAML 结构：

→ [模板格式](../concepts/templates-format.md)
