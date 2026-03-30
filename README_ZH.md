# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

将文档转化为**知识摘要** —— 一行命令即可。

![Hero](docs/assets/hero-v2.jpg)

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

---

## ⚡ 快速开始

```bash
pip install hyper-extract

he config init -k YOUR_API_KEY

he parse document.md -o ./knowledge_abstract/ -l zh
```

> 🔗 详细使用说明请查看 [CLI 指南](./hyperextract/cli/README.md)

---

## ✨ 核心特性

| 🤖 8种知识类型 | 🌍 38+领域模板 | 💻 交互式CLI | 🔍 语义检索 |
|:---:|:---:|:---:|:---:|
| 从列表到时空图谱 | 金融医疗法律开箱即用 | 一行命令完成全流程 | FAISS向量相似度 |

> 🔗 了解 [8种知识类型](#知识类型) | [领域模板](#领域模板)

---

## 📊 知识类型

![8种类型](docs/assets/8-types-v2.jpg)

| 类型 | 适用场景 | 示例 |
|------|----------|------|
| AutoModel | 结构化报告 | 财报摘要 |
| AutoList | 有序列表 | 会议要点 |
| AutoSet | 去重集合 | 产品目录 |
| AutoGraph | 二元关系 | 社交网络 |
| AutoHypergraph | 多元事件 | 合同纠纷 |
| AutoTemporalGraph | 时序关系 | 新闻时间线 |
| AutoSpatialGraph | 空间关系 | 配送路线 |
| AutoSpatioTemporalGraph | 时空事件 | 历史战役 |

> 🔗 查看 [完整类型文档](./hyperextract/types/) | [模板设计指南](./hyperextract/templates/DESIGN_GUIDE.md)

---

## 🌍 领域模板

![领域概览](docs/assets/domains-v2.png)

| 领域 | 模板数 | 典型场景 |
|------|--------|----------|
| General | 13 | 工作流、传记、概念图 |
| Finance | 5 | 财报分析、风险因子 |
| Medicine | 5 | 临床记录、药物相互作用 |
| TCM | 5 | 方剂配伍、经络走向 |
| Industry | 5 | 设备拓扑、事故分析 |
| Legal | 5 | 合同条款、判例引用 |

> 🔗 查看 [完整模板库](./hyperextract/templates/) | [模板设计指南](./hyperextract/templates/DESIGN_GUIDE.md)

---

## 🎯 Python API 示例

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary")
result = ka.parse(financial_report_text)
# result.operating_revenue = "1000亿元"
```

> 🔗 查看更多 [示例代码](./examples/)

---

## 📈 与同类项目对比

| 特性 | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
|------|:---:|:---:|:---:|:---:|:---:|
| 知识图谱 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 时序图谱 | ✅ | ❌ | ❌ | ✅ | ✅ |
| 空间图谱 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 超图 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 领域模板 | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI工具 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 多语言 | 部分 | ❌ | ❌ | ❌ | ✅ |
| 可视化 | 部分 | ❌ | ❌ | ❌ | ✅ |

---

## 💻 CLI 参考

### 解析文档

```bash
he parse document.md -o ./knowledge_abstract/ -l zh
he parse earnings.md -o ./finance_report/ -t finance/earnings_summary -l zh
```

### 搜索与问答

```bash
he search ./finance_report/ "营收增长了多少？"
he talk ./finance_report/ -i  # 交互式问答
```

### 可视化

```bash
he show ./finance_report/  # 图形化展示
he info ./finance_report/  # 显示统计信息
```

> 🔗 完整的 CLI 文档请查看 [CLI 指南](./hyperextract/cli/README.md)

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

Apache-2.0

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [CLI 指南](./hyperextract/cli/README.md) | 命令行工具完整参考 |
| [模板库](./hyperextract/templates/) | 38+ 领域模板 |
| [示例代码](./examples/) | Python API 使用示例 |
| [完整文档](./docs/) | 架构设计与实现细节 |
