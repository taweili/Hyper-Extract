# 故障排除

Hyper-Extract 的常见问题和解决方案。

## 安装问题

### 包安装失败

**问题**: `pip install hyper-extract` 失败

**解决方案**:
1. 升级 pip：
   ```bash
   pip install --upgrade pip
   ```

2. 使用虚拟环境：
   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   pip install hyper-extract
   ```

### 依赖冲突

**问题**: 与其他包的依赖冲突

**解决方案**: 创建干净的虚拟环境：
```bash
python -m venv hyper-extract-env
source hyper-extract-env/bin/activate
pip install hyper-extract
```

## API 问题

### API 密钥无效

**问题**: "API 密钥无效" 错误

**解决方案**:
1. 验证您的 API 密钥是否正确
2. 检查密钥是否已过期
3. 确保有足够的额度/配额

### 速率限制

**问题**: "超出速率限制" 错误

**解决方案**:
1. 在请求之间添加延迟
2. 使用批量处理
3. 在配置中减少 `max_workers`

### 超时错误

**问题**: 请求超时

**解决方案**:
1. 在配置中增加超时时间：
   ```yaml
   extraction:
     timeout: 120
   ```
2. 使用更小的文档块
3. 检查网络连接

## 提取问题

### 空结果

**问题**: 提取返回无结果

**解决方案**:
1. 验证文档包含可提取的内容
2. 检查模板是否匹配文档类型
3. 查看提取日志中的错误

### 提取不正确

**问题**: 提取的数据不正确或不完整

**解决方案**:
1. 使用更具体的模板
2. 在模板描述中添加提取提示
3. 尝试不同的提取方法
4. 调整置信度阈值

### 内存问题

**问题**: 内存不足错误

**解决方案**:
1. 以更小的批次处理文档
2. 减少批量大小
3. 定期清除缓存

## 性能问题

### 提取缓慢

**问题**: 提取非常慢

**解决方案**:
1. 使用更快的提取方法：
   ```python
   result = atom.extract(text)  # 最快
   ```

2. 启用并行处理：
   ```python
   results = ka.batch_parse(docs, parallel=True)
   ```

3. 使用更轻量的模型加快处理速度

## CLI 问题

### 命令未找到

**问题**: 找不到 `he` 命令

**解决方案**:
1. 重新安装包：
   ```bash
   pip uninstall hyper-extract
   pip install hyper-extract
   ```

2. 直接使用 Python 模块：
   ```bash
   python -m hyperextract parse document.txt
   ```

### 未找到配置

**问题**: CLI 找不到配置

**解决方案**: 初始化配置：
```bash
he config init -k <your-api-key>
```

## 仍然有问题？

如果您仍然遇到问题：
1. 查看[常见问题](faq.md)
2. 搜索现有的 [GitHub Issues](https://github.com/yifanfeng97/hyper-extract/issues)
3. 创建包含详细信息的新问题
