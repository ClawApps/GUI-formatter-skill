[English](CONTRIBUTING.md) | [中文](CONTRIBUTING_zh.md)

# 贡献指南

感谢你对 GUI Formatter 的关注！以下指南将帮助你快速参与贡献。

## 如何贡献

### 报告 Bug

1. 先搜索[现有 Issue](https://github.com/ClawApps/GUI-formatter-skill/issues)，避免重复
2. 使用 **Bug Report** 模板创建新 Issue
3. 包含：复现步骤、预期行为、实际行为、运行环境

### 功能建议

1. 使用 **Feature Request** 模板提交 Issue
2. 描述使用场景和价值
3. 尽量提供输入/输出示例

### 提交 Pull Request

1. Fork 仓库
2. 从 `main` 创建功能分支：
   ```bash
   git checkout -b feat/your-feature
   ```
3. 按照下方代码规范进行修改
4. 测试：
   ```bash
   python scripts/formatter.py    # 格式化器自测
   python scripts/validator.py    # 验证器自测
   python scripts/catalog.py      # 组件目录自测
   ```
5. 使用清晰的 commit message（见下方提交规范）
6. Push 并向 `main` 发起 PR

## 开发环境

```bash
# 克隆
git clone https://github.com/ClawApps/GUI-formatter-skill.git
cd GUI-formatter-skill

# 无需安装依赖 — 纯 Python 3.8+ 标准库

# 运行自测
python scripts/formatter.py
python scripts/validator.py
python scripts/catalog.py
```

## 项目结构

```
scripts/
├── formatter.py    # 核心格式化引擎（意图 → UITree）
├── catalog.py      # 组件注册表（白名单）
├── validator.py    # 3 轮验证 + Markdown 降级
└── actions.py      # Action 类型定义

references/         # 组件属性、Action、验证规则的详细文档
SKILL.md            # Claude Code Skill 定义
```

## 代码规范

- 兼容 Python 3.8+（不使用海象运算符、`match` 语句等）
- 函数签名使用类型注解
- 类和公共方法使用 docstring
- 仅使用标准库，不引入外部依赖
- 遵循现有命名风格：函数/变量用 `snake_case`，类用 `PascalCase`

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 添加新组件类型
fix: 修复 Form 字段验证
docs: 更新 component-catalog 示例
refactor: 简化意图解析逻辑
test: 添加验证器边界用例
```

## 添加新组件的步骤

1. 在 `scripts/catalog.py` 中注册组件（`_register_builtin_components`）
2. 如需要，在 `scripts/formatter.py` 中添加意图处理器
3. 更新 `SKILL.md` — 组件列表、意图映射表、组件数量
4. 更新 `references/component-catalog.md` — 完整属性表和示例
5. 更新 `references/fallback-strategies.md` — 组件列表
6. 更新 `README.md` 和 `README_zh.md` — 组件表格和数量

## 有问题？

提交 Issue 并添加 **Question** 标签，我们很乐意帮助。
