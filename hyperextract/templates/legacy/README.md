# Legacy Templates (废弃模板)

> ⚠️ **警告**: 此目录下的所有 Python 模板文件已被废弃，将在未来版本中删除。

## 说明

此目录包含旧版本的 Python 类模板，已被 YAML 配置文件模板取代。

## 迁移指南

### 旧的使用方式（已废弃）
```python
from hyperextract.templates.legacy.zh.general import LifeEventTimeline

template = LifeEventTimeline(llm_client=llm, embedder=embedder)
```

### 新的使用方式（推荐）
```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory

# 直接获取模板（自动加载 presets 和 customs）
config = Gallery.get("LifeEventTimeline")

# 创建模板
template = TemplateFactory.create(config, llm_client, embedder)
```

## 删除时间线

- **当前版本**: 标记为废弃，但仍可使用
- **下个版本**: 在文档中明确推荐使用 YAML 配置方式
- **未来版本 (v2.0)**: 删除此目录

## 相关文档

- [PYTHON转YAML配置指南](../PYTHON转YAML配置指南.md)
- [模板使用说明](../README.md)
