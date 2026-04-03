# 步骤 1：设置

项目结构和模板选择。

---

## 目标

为维护领域特定知识库建立稳健的项目结构。

---

## 项目结构

创建以下目录结构：

```bash
mkdir -p my_knowledge_base/{documents,kb,backups,logs}
cd my_knowledge_base
```

结构：
```
my_knowledge_base/
├── config.yaml         # 项目配置
├── documents/          # 源文档
│   ├── raw/           # 原始文件
│   └── processed/     # 处理日志
├── kb/                # 知识库版本
│   └── current/       # 当前版本（符号链接）
├── backups/           # 版本备份
├── logs/              # 操作日志
└── kb_manager.py      # 管理脚本
```

---

## 配置

### config.yaml

```yaml
# 知识库配置
name: "Company Knowledge Base"
domain: "legal"  # 或 finance、medical 等

# 模板设置
template: "legal/contract_obligation"  # 根据领域选择
language: "en"

# 处理设置
chunk_size: 2048
max_workers: 10

# 版本控制
version_format: "v{major}.{minor}"
auto_backup: true

# 路径
documents_dir: "./documents/raw"
kb_dir: "./kb"
backup_dir: "./backups"
```

### 模板选择指南

| 领域 | 推荐模板 | 自动类型 |
|------|---------|---------|
| 法律 | `legal/contract_obligation` | list |
| 金融 | `finance/earnings_summary` | model |
| 医疗 | `medicine/anatomy_graph` | graph |
| 通用 | `general/knowledge_graph` | graph |
| 研究 | `general/concept_graph` | graph |

---

## 管理脚本

### kb_manager.py（入门版）

```python
"""知识库管理器。"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from hyperextract import Template

@dataclass
class KBConfig:
    name: str
    domain: str
    template: str
    language: str
    documents_dir: str
    kb_dir: str
    backup_dir: str

class KnowledgeBaseManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.ka = None
        self.current_kb = None
        
    def _load_config(self, path: str) -> KBConfig:
        """从 YAML 加载配置。"""
        with open(path) as f:
            data = yaml.safe_load(f)
        return KBConfig(**data)
    
    def initialize(self):
        """初始化知识库。"""
        print(f"初始化: {self.config.name}")
        
        # 创建目录
        Path(self.config.documents_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.kb_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建模板
        self.ka = Template.create(
            self.config.template,
            language=self.config.language
        )
        
        print("✓ 初始化完成")
        
    def get_version_path(self, version: Optional[str] = None) -> Path:
        """获取特定版本的路径。"""
        if version is None:
            version = datetime.now().strftime("v%Y%m%d_%H%M%S")
        return Path(self.config.kb_dir) / version
    
    def save_version(self, kb_instance, version: Optional[str] = None):
        """保存知识库版本。"""
        path = self.get_version_path(version)
        kb_instance.dump(str(path))
        
        # 更新当前符号链接
        current_link = Path(self.config.kb_dir) / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(path, target_is_directory=True)
        
        print(f"✓ 已保存版本: {path.name}")
        return path

# 使用
if __name__ == "__main__":
    manager = KnowledgeBaseManager()
    manager.initialize()
```

---

## 初始化

### 1. 创建配置

```bash
cat > config.yaml << 'EOF'
name: "My Knowledge Base"
domain: "general"
template: "general/knowledge_graph"
language: "en"
documents_dir: "./documents/raw"
kb_dir: "./kb"
backup_dir: "./backups"
EOF
```

### 2. 运行设置

```bash
python kb_manager.py
```

预期输出：
```
初始化: My Knowledge Base
✓ 初始化完成
```

### 3. 验证结构

```bash
tree my_knowledge_base/
```

---

## 模板测试

在导入文档之前，测试您的模板：

```python
# test_template.py
from hyperextract import Template

# 加载配置
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# 测试模板
ka = Template.create(config["template"], config["language"])

# 使用样本文本测试
test_text = "This is a test document for template validation."
result = ka.parse(test_text)

print(f"模板: {config['template']}")
print(f"节点: {len(result.data.nodes)}")
print(f"边: {len(result.data.edges)}")
```

---

## 下一步

→ [步骤 2：导入文档](step2-ingest.md)
