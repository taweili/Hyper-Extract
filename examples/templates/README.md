# Templates 目录

本目录包含 Hyper-Extract 预设模板的测试工具。

## 文件说明

| 文件 | 说明 |
|------|------|
| `templates_mapping.yaml` | 模板与测试数据的映射配置 |
| `list_templates.py` | 列出所有可用的预设模板 |
| `run_template.py` | 执行指定模板的测试 |

## 使用方法

### 列出所有模板

```bash
python examples/templates/list_templates.py
```

输出示例：
```
【FINANCE 领域】 (5 templates)
  • earnings_summary
    Type: model
    Description: 财报电话会议摘要
    Template: finance/earnings_summary.yaml
    Test Data: tests/test_data/zh/finance/earnings_call_transcript_sample.md
```

### 运行模板测试

```bash
python examples/templates/run_template.py -d <domain> -t <template>
```

参数说明：
- `-d, --domain`: 领域名称 (finance, general, industry, legal, medicine, tcm)
- `-t, --template`: 模板名称

示例：
```bash
python examples/templates/run_template.py -d finance -t earnings_summary
python examples/templates/run_template.py -d general -t base_graph
python examples/templates/run_template.py -d tcm -t formula_composition
```

### 文件内配置

编辑 `run_template.py` 顶部的 `CONFIG` 字典设置默认的 domain 和 template：

```python
CONFIG = {
    "domain": "general",
    "template": "base_graph",
}
```

然后直接运行：
```bash
python examples/templates/run_template.py
```

## 支持的领域

| 领域 | 模板数量 | 描述 |
|------|---------|------|
| finance | 5 | 金融领域：财报摘要、股权结构、风险因子等 |
| general | 11 | 通用领域：基础图谱、传记、工作流程等 |
| industry | 5 | 工业领域：设备拓扑、应急响应、故障分析等 |
| legal | 5 | 法律领域：案例引用、合规清单、合同义务等 |
| medicine | 5 | 医学领域：解剖图谱、药物相互作用、治疗方案等 |
| tcm | 5 | 中医领域：方剂组成、经络图、证候推理等 |

## 模板类型

| 类型 | 对应 AutoType |
|------|--------------|
| graph | AutoGraph |
| hypergraph | AutoHypergraph |
| list | AutoList |
| model | AutoModel |
| set | AutoSet |
| temporal_graph | AutoTemporalGraph |
| spatial_graph | AutoSpatialGraph |
| spatio_temporal_graph | AutoSpatioTemporalGraph |
