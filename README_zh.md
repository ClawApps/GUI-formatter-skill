[English](README.md) | [中文](README_zh.md)

# GUI Formatter

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skill，将 Agent 回复格式化为结构化的 **JSON UI Tree**，供前端渲染。

## 概述

GUI Formatter 将 Agent 的输出意图（文本回复、表单、提示、媒体等）转换为标准化的 UITree JSON 格式。前端通过白名单机制渲染 **12 种组件类型**，确保 UI 输出一致且可预测。

**输出格式：**

```json
{
  "intro": "本次回复的简要说明",
  "ui_tree": {
    "root": "element_id",
    "elements": {
      "element_id": {
        "type": "Markdown",
        "props": { "content": "Hello **world**" },
        "children": []
      }
    }
  }
}
```

## 组件清单（12 种）

| 类别 | 组件 | 用途 |
|------|------|------|
| 展示 | `Markdown`, `Collapse` | 富文本 (GFM)、折叠面板 |
| 卡片 | `AppCard` | 应用/作品卡片 |
| 表单 | `Form` | 用户输入（内联 fields + actions） |
| 媒体 | `VideoPlayer`, `AudioPlayer`, `ImageGallery` | 视频、音频、图片画廊 |
| 反馈 | `Alert`, `Progress` | 提示（info/warning/error/success）、进度条 |
| 布局 | `Card`, `Modal` | 卡片容器、弹窗/抽屉 |
| 嵌入 | `WebView` | 网页嵌入（iframe） |

## 意图映射

格式化器根据识别到的用户意图自动选择对应组件：

| 用户意图 | 组件 | 说明 |
|---------|------|------|
| 文本回复 | `Markdown` | 纯文本、列表、表格 |
| 代码展示 | `Markdown` + codeOptions | 语法高亮代码块 |
| 需要用户输入 | `Form` | 带提交动作的表单 |
| 确认操作 | `Card` + actions | 确认/取消对话框 |
| 选择操作 | `Form` + radio/select | 单选或多选 |
| 警告/错误/成功 | `Alert` | 带图标的状态通知 |
| 数据展示 | `Markdown` 表格 | 表格数据 |
| 折叠内容 | `Collapse` | 可展开/收起的分组 |
| 媒体展示 | `ImageGallery` / `VideoPlayer` / `AudioPlayer` | 富媒体内容 |
| 进度展示 | `Progress` | 线性或环形进度条 |
| 嵌入网页 | `WebView` | iframe 嵌入 |
| 应用/作品展示 | `AppCard` | 应用/作品卡片 |

## 目录结构

```
GUI-formatter/
├── SKILL.md                          # Skill 定义（Claude 自动加载）
├── README.md                         # 英文文档
├── README_zh.md                      # 中文文档
├── LICENSE                           # MIT License
├── .gitignore
├── scripts/
│   ├── formatter.py                  # 核心格式化引擎
│   ├── catalog.py                    # 组件目录（白名单注册表）
│   ├── validator.py                  # Schema 验证器（3 轮重试 + 降级）
│   └── actions.py                    # Action 定义（6 种动作类型）
└── references/
    ├── component-catalog.md          # 组件详细属性和示例
    ├── action-schema.md              # Action 类型参考
    ├── validation-rules.md           # 表单验证规则参考
    └── fallback-strategies.md        # 降级策略参考
```

## 快速开始

### 作为 Claude Code Skill 使用

将此目录放到 Claude Code 的 skills 路径下：

```bash
# 直接克隆到 skills 目录
git clone https://github.com/ClawApps/GUI-formatter-skill.git ~/.claude/skills/GUI-formatter
```

Claude 会自动加载 `SKILL.md`，在回复时遵循格式化规则。

### 作为 Python 库使用

```python
from scripts.formatter import UIFormatter, format_reply, format_form

# 简单文本回复
result = format_reply("Hello **world**!")
print(result.tree)

# 表单
result = format_form([
    {"name": "email", "type": "email", "label": "邮箱", "required": True},
    {"name": "password", "type": "password", "label": "密码"}
])
print(result.tree)

# 自定义配置
from scripts.formatter import FormatterConfig
config = FormatterConfig(enable_fallback=True, strict_validation=False)
formatter = UIFormatter(config)
result = formatter.format({"intent": "alert", "message": "操作成功"})
```

### 命令行

```bash
# 从 stdin 输入
echo '{"intent": "reply", "content": "Hello"}' | python scripts/formatter.py

# 从文件输入
python scripts/formatter.py input.json -o output.json

# 严格模式（禁用降级）
python scripts/formatter.py input.json --strict --no-fallback
```

## 验证与降级

验证器执行 **3 轮验证**：

1. **Schema 验证** — 组件类型白名单（12 种）
2. **字段验证** — 属性类型和必填检查
3. **树结构验证** — 引用完整性和循环依赖检测

如果 3 轮验证全部失败，输出会自动降级为 `Markdown` 组件，包含提取的文本内容。这确保前端始终能收到可渲染的输出。

## 表单字段类型（12 种）

`text`, `email`, `password`, `number`, `textarea`, `select`, `radio`, `checkbox`, `date`, `switch`, `slider`, `file`

## 动作类型（6 种）

`api_call`, `navigate`, `emit_event`, `open_modal`, `close_modal`, `reset`

## 环境要求

- Python 3.8+
- 无外部依赖

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。
