# 贡献

感谢您对 Hyper-Extract 贡献的兴趣！

## 贡献方式

### 报告错误

通过提交 GitHub issue 报告错误，包括：
- 错误的清晰描述
- 重现步骤
- 预期与实际行为
- 环境信息（Python 版本、操作系统等）

### 提出功能建议

我们欢迎功能建议！请：
1. 检查现有 issue 以避免重复
2. 清晰描述用例
3. 解释预期行为

### 贡献代码

#### 开发环境设置

1. Fork 仓库
2. 克隆您的 fork：
   ```bash
   git clone https://github.com/yifanfeng97/hyper-extract.git
   cd hyper-extract
   ```

3. 创建虚拟环境：
   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   ```

4. 安装开发依赖：
   ```bash
   pip install -e ".[dev]"
   ```

5. 安装预提交钩子：
   ```bash
   pre-commit install
   ```

#### 开发工作流程

1. 创建功能分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 进行更改
3. 运行测试：
   ```bash
   pytest tests/
   ```

4. 运行代码检查：
   ```bash
   ruff check .
   ```

5. 提交您的更改：
   ```bash
   git commit -m "Add your feature"
   ```

6. 推送并创建 Pull Request

#### 代码风格

- 遵循 PEP 8
- 使用类型提示
- 编写文档字符串
- 为新功能添加测试

### 贡献文档

文档改进始终受欢迎：
- 修复拼写错误或不清楚的解释
- 添加示例
- 改进翻译
- 更新过时内容

### 翻译贡献

我们欢迎翻译贡献：
1. 检查现有翻译
2. 通过 PR 提交翻译

## Pull Request 指南

1. 引用相关 issue
2. 为新功能包含测试
3. 根据需要更新文档
4. 遵循代码风格指南
5. 确保所有测试通过

## 开发资源

- [GitHub 仓库](https://github.com/hyper-extract/hyper-extract)
- [Issue 追踪器](https://github.com/hyper-extract/hyper-extract/issues)
- [讨论区](https://github.com/hyper-extract/hyper-extract/discussions)

## 行为准则

请在所有互动中保持尊重和建设性。我们遵循[贡献者公约](https://www.contributor-covenant.org/)。

## 许可证

通过贡献，您同意您的贡献将在 Apache 2.0 许可证下获得许可。
