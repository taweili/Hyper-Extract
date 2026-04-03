# CLI 工作流程指南

本指南通过实际案例带您完成完整的知识提取工作流程。

---

## 场景：研究论文分析

假设您是一位研究人员，想要从学术论文中提取和交互知识。以下是使用 Hyper-Extract 的方法。

---

## 步骤 1：准备文档

首先，确保您的文档是支持的格式（`.md`、`.txt`）：

```bash
# 示例：将 PDF 转换为文本（使用外部工具）
pdftotext paper.pdf paper.md
```

或创建一个示例文档：

```bash
cat > transformer_paper.md << 'EOF'
# Attention Is All You Need

## Abstract
The dominant sequence transduction models are based on complex recurrent or 
convolutional neural networks that include an encoder and a decoder. The best 
performing models also connect the encoder and decoder through an attention 
mechanism. We propose a new simple network architecture, the Transformer, 
based solely on attention mechanisms.

## Authors
- Ashish Vaswani
- Noam Shazeer
- Niki Parmar
- Jakob Uszkoreit
- Llion Jones
- Aidan N. Gomez
- Lukasz Kaiser
- Illia Polosukhin

## Key Innovation
The Transformer eschews recurrence and instead relies entirely on an attention 
mechanism to draw global dependencies between input and output sequences.

## Performance
On the WMT 2014 English-to-German translation task, our model achieves a 
BLEU score of 28.4, outperforming all existing models.
EOF
```

---

## 步骤 2：提取知识

使用 `parse` 命令提取知识：

```bash
he parse transformer_paper.md -t general/concept_graph -o ./transformer_kb/ -l en
```

**发生了什么：**
1. 读取文档并分块（如文档较长）
2. LLM 提取实体和关系
3. 结果保存到 `./transformer_kb/`

**输出结构：**
```
./transformer_kb/
├── data.json       # 提取的知识
├── metadata.json   # 提取元数据
└── index/          # 向量搜索索引（如已构建）
```

---

## 步骤 3：探索知识

### 查看统计信息

```bash
he info ./transformer_kb/
```

**输出：**
```
Knowledge Abstract Info

Path          ./transformer_kb/
Template      general/concept_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:30:00
Nodes         12
Edges         15
Index         Built
```

### 可视化

```bash
he show ./transformer_kb/
```

这将在浏览器中打开交互式图谱，显示：
- **节点**：作者、概念、模型、指标
- **边**：它们之间的关系

---

## 步骤 4：搜索信息

### 语义搜索

即使关键词不完全匹配也能查找信息：

```bash
he search ./transformer_kb/ "neural network architecture"
```

**结果：**
```
Found 3 result(s):

Result 1:
{
  "name": "Transformer",
  "type": "model",
  "description": "A neural network architecture based solely on attention mechanisms"
}

Result 2:
{
  "name": "Attention Mechanism",
  "type": "concept",
  "description": "Mechanism to draw global dependencies between sequences"
}
...
```

### 特定查询

```bash
he search ./transformer_kb/ "performance metrics" -n 5
```

---

## 步骤 5：与知识对话

### 单个问题

```bash
he talk ./transformer_kb/ -q "本文的主要贡献是什么？"
```

**响应：**
```
主要贡献是引入了 Transformer 架构，它在机器翻译任务上实现了最先进的成果，
同时比循环或卷积架构更易于并行化，训练时间也显著减少。
```

### 交互模式

```bash
he talk ./transformer_kb/ -i
```

**会话：**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

> 作者是谁？
本文作者是 Ashish Vaswani、Noam Shazeer、Niki Parmar、Jakob Uszkoreit、
Llion Jones、Aidan N. Gomez、Lukasz Kaiser 和 Illia Polosukhin。

> 他们取得了什么 BLEU 分数？
该模型在 WMT 2014 英德翻译任务上取得了 28.4 的 BLEU 分数。

> exit
Goodbye!
```

---

## 步骤 6：扩展知识库

### 添加另一个文档

```bash
# 下载另一篇论文
curl -o bert_paper.md https://example.com/bert.md

# 添加到现有知识库
he feed ./transformer_kb/ bert_paper.md
```

### 验证更新

```bash
he info ./transformer_kb/
```

注意节点/边数增加和时间戳更新。

---

## 步骤 7：重建索引（如需要）

添加文档后，重建搜索索引：

```bash
he build-index ./transformer_kb/
```

或强制完全重建：

```bash
he build-index ./transformer_kb/ -f
```

---

## 完整脚本示例

以下是一个自动化整个工作流程的 bash 脚本：

```bash
#!/bin/bash

# 配置
INPUT_FILE="paper.md"
OUTPUT_DIR="./paper_kb/"
TEMPLATE="general/concept_graph"
LANGUAGE="en"

echo "=== Hyper-Extract Workflow ==="
echo

# 步骤 1: 解析
echo "Step 1: Extracting knowledge..."
he parse "$INPUT_FILE" -t "$TEMPLATE" -o "$OUTPUT_DIR" -l "$LANGUAGE"
echo

# 步骤 2: 信息
echo "Step 2: Knowledge base info:"
he info "$OUTPUT_DIR"
echo

# 步骤 3: 搜索示例
echo "Step 3: Sample search:"
he search "$OUTPUT_DIR" "main contributions" -n 2
echo

# 步骤 4: 打开可视化
echo "Step 4: Opening visualization..."
he show "$OUTPUT_DIR"

echo "=== Workflow Complete ==="
```

---

## 高级：批量处理

一次处理多个文档：

```bash
# 创建输出目录
mkdir -p ./kb/paper1 ./kb/paper2 ./kb/paper3

# 处理每个
he parse papers/paper1.md -t general/concept_graph -o ./kb/paper1/ -l en
he parse papers/paper2.md -t general/concept_graph -o ./kb/paper2/ -l en
he parse papers/paper3.md -t general/concept_graph -o ./kb/paper3/ -l en

# 或使用循环
for file in papers/*.md; do
    name=$(basename "$file" .md)
    he parse "$file" -t general/concept_graph -o "./kb/$name/" -l en
done
```

---

## 常见模式

### 模式 1：持续构建知识

```bash
# 初始提取
he parse initial_doc.md -t general/biography_graph -o ./kb/ -l en

# 每周更新
he feed ./kb/ week1_update.md
he feed ./kb/ week2_update.md
he feed ./kb/ week3_update.md

# 每月重建
he build-index ./kb/ -f
```

### 模式 2：多领域项目

```bash
# 技术文档
he parse api_docs.md -t general/concept_graph -o ./project_kb/tech/ -l en

# 法律合同
he parse contract.pdf -t legal/contract_obligation -o ./project_kb/legal/ -l en

# 财务报告
he parse q4_report.md -t finance/earnings_summary -o ./project_kb/finance/ -l en
```

### 模式 3：比较文档

```bash
# 提取两个版本
he parse draft_v1.md -t general/concept_graph -o ./kb/v1/ -l en
he parse draft_v2.md -t general/concept_graph -o ./kb/v2/ -l en

# 通过聊天比较
he talk ./kb/v1/ -q "主要主题是什么？"
he talk ./kb/v2/ -q "主要主题是什么？"
```

---

## 故障排除提示

| 问题 | 解决方案 |
|-------|----------|
| 提取速度慢 | 长文档会被分块；使用 `--no-index` 在解析时跳过索引 |
| 搜索无结果 | 确保索引已构建：`he build-index ./kb/` |
| 模板未找到 | 列出可用模板：`he list template` |
| 内存不足 | 减少配置中的块大小或处理较小的文档 |

---

## 下一步

- 了解[所有 CLI 命令](commands/parse.md)
- 探索[模板库](../templates/index.md)
- 阅读[选择正确的自动类型](../concepts/autotypes.md)
