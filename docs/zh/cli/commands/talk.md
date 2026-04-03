# he talk

使用自然语言与您的知识库对话。

---

## 概要

```bash
he talk KA_PATH [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |

## 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--query` | `-q` | 要问的单个问题 |
| `--top-k` | `-n` | 要检索的上下文项目数量 | 3 |
| `--interactive` | `-i` | 进入交互式聊天模式 |

---

## 描述

`talk` 命令让您与知识库进行对话：

1. **检索相关上下文** — 搜索与您问题相关的信息
2. **生成答案** — 使用 LLM 综合自然语言响应
3. **显示来源** — 显示用于生成答案的项目

**要求**：必须构建搜索索引。

---

## 示例

### 单个问题

```bash
he talk ./output/ -q "特斯拉的主要成就是什么？"
```

**输出：**
```
Query: 特斯拉的主要成就是什么？
Knowledge Abstract: ./output/
Top K: 3

Nikola Tesla made numerous groundbreaking contributions to electrical 
engineering. His major achievements include:

1. Development of the alternating current (AC) electrical system, which 
   became the dominant method of power transmission worldwide.

2. Invention of the Tesla coil, used in radio technology and electrical 
   resonant circuits.

3. Contributions to the development of X-ray imaging and wireless 
   communication technologies.

Retrieved context:
1. Nikola Tesla: Serbian-American inventor, electrical engineer...
2. AC Power System: Type: invention, Description: System for alternating...
3. Tesla Coil: Type: invention, Description: Resonant transformer circuit...
```

### 交互模式

```bash
he talk ./output/ -i
```

**会话：**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

Knowledge Abstract: ./output/
Template: general/biography_graph
Top K: 3

> 谁是 Nikola Tesla？
Nikola Tesla was a Serbian-American inventor, electrical engineer, 
mechanical engineer, and futurist best known for his contributions 
to the design of the modern alternating current (AC) electricity 
supply system.

> 他什么时候出生的？
Nikola Tesla 于 1856 年 7 月 10 日出生在克罗地亚的 Smiljan。

> 他与爱迪生的关系如何？
Tesla 于 1884 年在纽约市为 Thomas Edison 工作。由于在直流电（DC）
和交流电（AC）电力系统方面的不同观点，他们的关系存在争议。

> exit
Goodbye!

Other useful commands:
  he show ./output/              # 可视化
  he search ./output/ "keyword"  # 搜索
  he info ./output/              # 查看信息
```

### 使用更多上下文

为复杂问题增加上下文：

```bash
he talk ./output/ -q "解释电流战争" -n 10
```

---

## 交互命令

在交互模式（`-i`）中：

| 命令 | 操作 |
|---------|--------|
| `exit`, `quit`, `q` | 退出交互模式 |
| `help` | 显示可用命令 |

---

## 用例

### 研究助手

```bash
he talk ./paper_kb/ -q "总结本文的主要贡献"
```

### 法律分析

```bash
he talk ./contract_kb/ -q "终止条件是什么？"
```

### 历史研究

```bash
he talk ./bio_kb/ -q "哪些事件导致了特斯拉的经济困难？"
```

---

## 工作原理

1. **语义搜索** — 在知识库中找到相关项目
2. **上下文组装** — 将检索到的项目组合成上下文
3. **LLM 生成** — 使用上下文生成答案
4. **来源归属** — 显示哪些项目提供了答案

---

## 更好答案的技巧

1. **要具体** — "特斯拉创造了什么发明？" vs "告诉我关于特斯拉的事"
2. **追问** — 通过对话构建上下文
3. **调整 top-k** — 对于复杂问题使用 `-n 5` 或更高
4. **检查来源** — 审查 "Retrieved context" 的准确性

---

## 与 `he search` 的比较

| 功能 | `he search` | `he talk` |
|---------|-------------|-----------|
| 输出 | 原始实体/关系 | 自然语言 |
| 最适合 | 查找特定数据 | 理解/解释 |
| 速度 | 快 | 更慢（LLM 调用） |
| 来源可见性 | 直接 | 在上下文中引用 |

---

## 故障排除

### "未找到索引"

```bash
he build-index ./output/
```

### "没有相关信息"

- 尝试重新表述您的问题
- 使用 `-n 10` 增加上下文
- 验证知识库有相关数据：`he info ./output/`

---

## 另请参见

- [`he search`](search.md) — 搜索特定项目
- [`he build-index`](build-index.md) — 构建搜索索引
- [`he show`](show.md) — 可视化知识图谱
