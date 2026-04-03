# he build-index

为知识库构建或重建向量搜索索引。

---

## 概要

```bash
he build-index KA_PATH [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |

## 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--force` | `-f` | 即使索引存在也强制重建 |

---

## 描述

为语义搜索和聊天功能构建向量搜索索引：

1. **读取所有实体/关系** — 从知识库数据中
2. **生成嵌入** — 使用配置的嵌入模型
3. **构建 FAISS 索引** — 用于快速相似度搜索
4. **保存到磁盘** — 在 `index/` 子目录中

**必需用于**：`he search` 和 `he talk` 命令。

---

## 示例

### 构建索引

```bash
he build-index ./output/
```

**输出：**
```
Template: general/biography_graph
Language: en

Success! Index built for ./output/

Now you can:
  he search ./output/ "keyword"  # Semantic search
  he talk ./output/ -i           # Interactive chat
```

### 强制重建

如果索引损坏或您想重建：

```bash
he build-index ./output/ -f
```

---

## 何时构建索引

### Parse 后（默认）

默认情况下，`he parse` 会自动构建索引：

```bash
he parse doc.md -t general/biography_graph -o ./kb/ -l en
# 索引自动构建
```

如果不需要搜索/聊天，使用 `--no-index` 跳过：

```bash
he parse doc.md -t general/biography_graph -o ./kb/ -l en --no-index
```

### Feed 后

喂养新文档后始终重建：

```bash
he feed ./kb/ new_doc.md
he build-index ./kb/
```

### 手动更改后

如果您手动修改了 `data.json`：

```bash
he build-index ./kb/ -f
```

---

## 索引存储

索引存储在知识库目录中：

```
./kb/
├── data.json
├── metadata.json
└── index/              # 索引目录
    ├── index.faiss     # FAISS 向量索引
    └── docstore.json   # 文档存储映射
```

---

## 性能

### 构建时间

| 知识库大小 | 预计构建时间 |
|---------------------|----------------------|
| 小型（< 100 项） | < 5 秒 |
| 中型（100-1000） | 5-30 秒 |
| 大型（1000+） | 30+ 秒 |

### 搜索速度

一旦构建完成，搜索非常快：

```bash
he search ./kb/ "query"  # 通常 < 1 秒
```

---

## 最佳实践

1. **Feed 后构建** — `he feed` 后索引会变旧
2. **批量处理使用 `--no-index`** — 所有解析后统一构建一次
3. **有问题时强制重建** — 如果搜索返回意外结果，使用 `-f`
4. **备份大型索引** — `index/` 目录可能很大

---

## 批量工作流程

高效处理多个文档：

```bash
# 解析所有文件，不构建索引
he parse doc1.md -t general/biography_graph -o ./kb/ -l en --no-index
he feed ./kb/ doc2.md
he feed ./kb/ doc3.md

# 最后统一构建索引
he build-index ./kb/

# 现在可以进行搜索/聊天
he search ./kb/ "query"
he talk ./kb/ -q "question"
```

---

## 故障排除

### "索引已存在"

使用 `-f` 强制重建：

```bash
he build-index ./kb/ -f
```

### "索引构建失败"

检查：
1. 知识库有数据：`he info ./kb/`
2. API 密钥已配置：`he config show`
3. 有足够的磁盘空间存储索引

### 搜索仍然不工作

尝试强制重建：

```bash
he build-index ./kb/ -f
```

---

## 另请参见

- [`he parse`](parse.md) — 可选索引构建的解析
- [`he feed`](feed.md) — 添加文档（需要重建）
- [`he search`](search.md) — 搜索索引
- [`he talk`](talk.md) — 使用索引聊天
