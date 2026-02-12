[English](README.md) | [中文](README_zh.md)

# GUI Formatter

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skill that formats Agent responses into structured **JSON UI Trees** for frontend rendering.

## Overview

GUI Formatter converts Agent output intents (text replies, forms, alerts, media, etc.) into a standardized UITree JSON format. The frontend renders these trees using a whitelist of **12 component types**, ensuring consistent and predictable UI output.

**Output format:**

```json
{
  "intro": "Brief summary of this response",
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

## Components (12 types)

| Category | Components | Usage |
|----------|-----------|-------|
| Display | `Markdown`, `Collapse` | Rich text (GFM), collapsible panels |
| Card | `AppCard` | App/work display cards |
| Form | `Form` | User input (fields + actions inline) |
| Media | `VideoPlayer`, `AudioPlayer`, `ImageGallery` | Video, audio, image gallery |
| Feedback | `Alert`, `Progress` | Alerts (info/warning/error/success), progress bars |
| Layout | `Card`, `Modal` | Card containers, modals/drawers |
| Embed | `WebView` | Iframe embedding |

## Intent Mapping

The formatter automatically selects the appropriate component based on the detected user intent:

| User Intent | Component | Description |
|-------------|-----------|-------------|
| Text reply | `Markdown` | Plain text, lists, tables |
| Code display | `Markdown` + codeOptions | Syntax-highlighted code blocks |
| User input | `Form` | Form fields with submit actions |
| Confirmation | `Card` + actions | Confirm/cancel dialogs |
| Selection | `Form` + radio/select | Single or multi-select options |
| Alert/Warning/Error/Success | `Alert` | Status notifications with icons |
| Data display | `Markdown` table | Tabular data |
| Collapsible content | `Collapse` | Expandable/collapsible sections |
| Media | `ImageGallery` / `VideoPlayer` / `AudioPlayer` | Rich media |
| Progress | `Progress` | Linear or circular progress bars |
| Web embed | `WebView` | Iframe embedding |
| App/work display | `AppCard` | App/work cards |

## Directory Structure

```
GUI-formatter/
├── SKILL.md                          # Skill definition (loaded by Claude)
├── README.md                         # English documentation
├── README_zh.md                      # Chinese documentation
├── LICENSE                           # MIT License
├── .gitignore
├── scripts/
│   ├── formatter.py                  # Core formatting engine
│   ├── catalog.py                    # Component catalog (whitelist registry)
│   ├── validator.py                  # Schema validator (3-round retry + fallback)
│   └── actions.py                    # Action schema definitions (6 action types)
└── references/
    ├── component-catalog.md          # Detailed component props and examples
    ├── action-schema.md              # Action types reference
    ├── validation-rules.md           # Form validation rules reference
    └── fallback-strategies.md        # Fallback/degradation strategies
```

## Getting Started

### As a Claude Code Skill

Place this directory under your Claude Code skills path:

```bash
# Clone directly into your skills directory
git clone https://github.com/ClawApps/GUI-formatter-skill.git ~/.claude/skills/GUI-formatter
```

Claude will automatically load `SKILL.md` and follow the formatting rules when responding.

### As a Python Library

```python
from scripts.formatter import UIFormatter, format_reply, format_form

# Simple text reply
result = format_reply("Hello **world**!")
print(result.tree)

# Form with fields
result = format_form([
    {"name": "email", "type": "email", "label": "Email", "required": True},
    {"name": "password", "type": "password", "label": "Password"}
])
print(result.tree)

# Full formatter with custom config
from scripts.formatter import FormatterConfig
config = FormatterConfig(enable_fallback=True, strict_validation=False)
formatter = UIFormatter(config)
result = formatter.format({"intent": "alert", "message": "Operation successful"})
```

### CLI

```bash
# From stdin
echo '{"intent": "reply", "content": "Hello"}' | python scripts/formatter.py

# From file
python scripts/formatter.py input.json -o output.json

# Strict mode (no fallback)
python scripts/formatter.py input.json --strict --no-fallback
```

## Validation & Fallback

The validator performs **3-round validation** before giving up:

1. **Schema validation** - Component type whitelist (12 types)
2. **Field validation** - Property types and required fields
3. **Tree validation** - Reference integrity and cycle detection

If all 3 rounds fail, the output is automatically degraded to a `Markdown` component containing the extracted text content. This ensures the frontend always receives renderable output.

## Form Field Types (12)

`text`, `email`, `password`, `number`, `textarea`, `select`, `radio`, `checkbox`, `date`, `switch`, `slider`, `file`

## Action Types (6)

`api_call`, `navigate`, `emit_event`, `open_modal`, `close_modal`, `reset`

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT License - see [LICENSE](LICENSE) for details.
