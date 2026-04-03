# he search

对知识库执行语义搜索。

---

## 概要

```bash
he search KA_PATH QUERY [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |
| `QUERY` | 搜索查询字符串 |

## 选项

| 选项 | 简写 | 描述 | 默认值 |
|--------|-------|-------------|---------|
| `--top-k` | `-n` | 返回结果数量 | 3 |

---

## 描述

语义搜索即使在关键词不完全匹配时也能找到相关信息。它使用：

1. **向量嵌入** — 将查询和内容转换为向量
2. **相似度匹配** — 找到语义相似的内容
3. **排名** — 返回最相关的结果

**要求**：必须构建搜索索引。如有需要，运行 `he build-index`。

---

## 示例

### 基本搜索

```bash
he search ./output/ "Tesla's inventions"
```

### 获取更多结果

```bash
he search ./output/ "electrical engineering" -n 10
```

### 自然语言查询

```bash
he search ./kb/ "主要成就是什么？"
he search ./kb/ "与爱迪生一起工作的人"
he search ./kb/ "时间线上的重要日期"
```

### 构建索引后

```bash
# 首先，确保索引存在
he build-index ./output/

# 然后搜索
he search ./output/ "innovation"
```

---

## 输出格式

```
Found 3 result(s):

Result 1:
{
  "name": "Nikola Tesla",
  "type": "person",
  "description": "Serbian-American inventor, electrical engineer..."
}

Result 2:
{
  "source": "Nikola Tesla",
  "target": "Thomas Edison",
  "type": "worked_with",
  "description": "Tesla worked for Edison in 1884"
}

Result 3:
...
```

---

## 工作原理

1. **查询嵌入** — 将您的查询转换为向量
2. **索引搜索** — 在知识库中找到最近的向量
3. **结果排名** — 返回 top-k 最相似的项目

---

## 更好搜索的技巧

1. **使用自然语言** — "电气工程方面的发明" vs "发明 电气"
2. **要具体** — "特斯拉在交流电方面的工作" vs "特斯拉 工作"
3. **尝试同义词** — 如果 "发明" 不行，尝试 "发现"
4. **增加 top-k** — 使用 `-n 10` 获取更广泛的结果

---

## 与 `he talk` 的比较

| 功能 | `he search` | `he talk` |
|---------|-------------|-----------|
| 返回 | 原始实体/关系 | 自然语言答案 |
| 用例 | 查找特定数据 | 获取解释 |
| 速度 | 更快 | 更慢（LLM 生成） |
| 精度 | 精确匹配 | 解释性 |

---

## 故障排除

### "未找到索引"

构建搜索索引：

```bash
he build-index ./output/
```

### "未找到结果"

尝试：
1. 更广泛的查询词
2. 增加 `-n` 获取更多结果
3. 不同的措辞
4. 检查 `he info ./output/` 验证数据存在

---

## 另请参见

- [`he talk`](talk.md) — 与知识库对话
- [`he build-index`](build-index.md) — 构建搜索索引
- [`he parse`](parse.md) — 带索引构建的提取
