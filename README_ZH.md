# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**
>
> *"告别文档焦虑，让信息一目了然"*

将文档转化为**知识摘要** —— 一行命令即可。

![Hero](docs/assets/hero-v2.jpg)

[📖 English Version](./README.md) · [中文版](#)

---

## ⚡ 快速开始

```bash
pip install hyper-extract

he config init
he parse document.md -o ka -l zh
he talk ka -i
```

![CLI 配置指南](docs/assets/cli.png)

---

## ⚙️ 快速配置

**推荐配置**：gpt-4o-mini（快速稳定，适合结构化提取）+ text-embedding-3-small

```bash
he config init -k YOUR_API_KEY
# 或指定自定义接口
he config init -k YOUR_KEY -u https://api.openai.com/v1
```

查看配置：`he config show`

---

## 💡 使用示例

```bash
he parse document.md -o ka -l zh
he show ka
he search ka "关键信息"
```

---

## 🧩 知识摘要类型

![8 种类型](docs/assets/8-types-v2.jpg)

8 种知识结构，满足不同文档类型：

**记录型（Record Types）：**
| 结构 | 适用场景 | 示例 |
|------|----------|------|
| AutoModel | 结构化报告 | 财务报表 |
| AutoList | 要点列表 | 会议记录 |
| AutoSet | 实体集合 | 产品目录 |

**图型（Graph Types）：**
| 结构 | 适用场景 | 示例 |
|------|----------|------|
| AutoGraph | 二元关系 | 社交网络 |
| AutoHypergraph | 多方事件 | 法律纠纷 |
| AutoTemporalGraph | 事件序列 | 新闻时间线 |
| AutoSpatialGraph | 地理位置 | 配送路线 |
| AutoSpatioTemporalGraph | 时空事件 | 历史战役 |

### 与其他库的对比

| 功能 | KG-Gen | ATOM | Graphiti | LightRAG | Hyper-Extract |
|------|--------|------|----------|----------|---------------|
| 知识图谱 | ✅ | ✅ | ❌ | ✅ | ✅ |
| 时序图谱 | ❌ | ✅ | ✅ | ❌ | ✅ |
| 空间图谱 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 超图 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 模板 | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI 工具 | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🌍 领域模板

![领域概览](docs/assets/domains-v2.png)

开箱即用的领域模板：

| 领域 | 模板数 | 典型场景 |
|------|--------|----------|
| General | 13 | 工作流、传记、概念图 |
| Finance | 5 | 财报分析、风险因子 |
| Medicine | 5 | 临床记录、药物相互作用 |
| TCM | 5 | 方剂配伍、经络走向 |
| Industry | 5 | 设备拓扑、事故分析 |
| Legal | 5 | 合同条款、判例引用 |

**总计：6 大领域 · 37 个模板**

查看 [模板库](hyperextract/templates/) 获取所有模板。

---

## 💻 CLI 参考

### 解析文档

```bash
he parse document.md -o my_ka -l zh
he parse document.md -o my_ka -t general/knowledge_graph -l zh
```

### 构建搜索索引

```bash
he build-index my_ka
```

### 搜索知识摘要

```bash
he search my_ka "关键发现是什么？"
he search my_ka "关键信息" -n 5
```

### 可视化

```bash
he show my_ka
he info my_ka
```

完整的 CLI 文档请查看 [CLI 指南](hyperextract/cli/README.md)。

---

## 📚 文档

- [📖 完整文档](docs/)
- [💻 示例代码](examples/)
- [🏷️ 模板库](hyperextract/templates/)
- [🖥️ CLI 指南](hyperextract/cli/README.md)
