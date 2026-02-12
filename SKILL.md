---
name: GUI-formatter
description: |
  Standardized frontend output formatting Skill. All responses are formatted as JSON UI Trees.
  Output format: { "intro": "summary", "ui_tree": { "root": "id", "elements": {...} } }
  Supports 12 components: Markdown, Collapse, AppCard, Form, Card, Modal, Alert, Progress, VideoPlayer, AudioPlayer, ImageGallery, WebView
---

# GUI Formatter v0.8.0

All Agent responses should be formatted as UITree JSON for frontend rendering.

## Core Rules

```
┌────────────────────────────────────────────────────────────────┐
│  1. Output JSON format (not plain text)                        │
│  2. Before each response, choose component based on intent     │
│  3. Only use the 12 standard components                        │
│  4. Use Card as layout container (not Container)               │
└────────────────────────────────────────────────────────────────┘
```

**Unsupported component types:** `Container`, `Button`, `Grid`, `GridItem`, `Tabs`, `TabPane`, `Drawer`, `Text`, `CodeBlock`, `TextField`, `Select`, `DatePicker`, `Checkbox`, `Radio`, `Switch`, `Slider`, `FileUpload`, `Table`, `DataGrid`, `Statistic`, `Chart`, `Badge`, `Tooltip`, `Tag`, `Avatar`, `Divider`, `Image`, `Link`

**Layout container:** When you need to wrap multiple components, use `Card` (not Container)

---

## Output Format

```json
{
  "intro": "Brief summary of this response (1-2 sentences)",
  "ui_tree": {
    "root": "element_id",
    "elements": {
      "element_id": {
        "type": "ComponentType",
        "props": { ... },
        "children": ["child_id"]
      }
    }
  }
}
```

**Field descriptions:**
- `intro`: Required. Brief summary of the output content (displayed as preview)
- `ui_tree.root`: Required. Root element ID
- `ui_tree.elements`: Required. Flat dictionary of all elements

---

## Intent → Component Mapping

**Before responding, determine the intent and choose the matching component:**

| User Intent | Intent | Component | Description |
|-------------|--------|-----------|-------------|
| General reply | `reply` | `Markdown` | Text, lists, tables |
| Code display | `code` | `Markdown` + codeOptions | Code blocks |
| User input needed | `form` | `Form` | Form fields + submit |
| Confirm action | `confirm` | `Card` + actions | Confirm/cancel buttons |
| Selection | `select` | `Form` + radio/select | Single/multi select |
| Warning/Error/Success | `alert` | `Alert` | Alert with icon |
| Data display | `data` | `Markdown` table | Statistics data |
| Grouped collapsible | `collapse` | `Collapse` | Expandable/collapsible groups |
| Media display | `media` | `ImageGallery`/`VideoPlayer`/`AudioPlayer` | Images/video/audio |
| Progress display | `progress` | `Progress` | Progress bar |
| Embed web page | `webview` | `WebView` | iframe embed |
| App/work display | `app` | `AppCard` | App/work card |

---

## Component List (12 types)

| Category | Component | Usage |
|----------|-----------|-------|
| Display | `Markdown` | Text, code, tables (GFM support) |
| Display | `Collapse` | Collapsible panels (expand/collapse content) |
| Card | `AppCard` | App/work display card |
| Form | `Form` | User input (inline fields + actions) |
| Media | `VideoPlayer`, `AudioPlayer`, `ImageGallery` | Video, audio, images |
| Feedback | `Alert`, `Progress` | Alerts, progress bars |
| Layout | `Card`, `Modal` | Cards, modals/drawers |
| Embed | `WebView` | Web page embed |

**Detailed properties and examples →** [component-catalog.md](references/component-catalog.md)

---

## Collapse vs Card Rules

```
┌────────────────────────────────────────────────────────────────┐
│  Collapse and Card are different components, do not mix them!  │
│                                                                │
│  Collapse: props.items[] → CollapseItem (collapsible panels)   │
│  Card:     children[]    → Child element ID refs (container)   │
│                                                                │
│  ✗ Wrong: type="Card" + props.items  (Card has no items)       │
│  ✗ Wrong: type="Collapse" + children (Collapse has no children)│
│  ✓ Right: type="Collapse" + props.items                        │
│  ✓ Right: type="Card" + children                               │
└────────────────────────────────────────────────────────────────┘
```

---

## Form Component Key Rules

```
┌────────────────────────────────────────────────────────────────┐
│  1. fields and actions must be inside props                    │
│  2. Field type property name is "type"                         │
│  3. Textarea row count property is "rows"                      │
└────────────────────────────────────────────────────────────────┘
```

### Field Types (12)

| type | Usage | Special Props |
|-----------|-------|---------------|
| `text` | Single-line text | maxLength |
| `email` | Email | - |
| `password` | Password | showToggle |
| `number` | Number | min, max, step |
| `textarea` | Multi-line text | rows |
| `select` | Dropdown | options, multiple |
| `radio` | Radio buttons | options |
| `checkbox` | Checkboxes | options |
| `date` | Date picker | minDate, maxDate |
| `switch` | Toggle switch | - |
| `slider` | Slider | min, max, step |
| `file` | File upload | accept, multiple |

**Selection component rules:**
- Options ≤ 5 → `radio`
- Options > 5 → `select`
- Multi-select → `checkbox` or `select` + `multiple: true`

**Detailed Form examples →** [component-catalog.md](references/component-catalog.md) Section 4

---

## Action Definitions

Actions triggered by button clicks or form submissions:

| type | Usage | Required Fields |
|------|-------|-----------------|
| `api_call` | Call API | api.endpoint |
| `navigate` | Page navigation | url |
| `emit_event` | Send event | event |
| `reset` | Reset form | - |
| `open_modal` | Open modal | modalId |
| `close_modal` | Close modal | modalId |

**Detailed reference →** [action-schema.md](references/action-schema.md)

---

## Validation Rules

Validators supported by FormField:

| Validator | Usage |
|-----------|-------|
| `required` | Required field |
| `email` | Email format |
| `minLength` | Minimum length |
| `maxLength` | Maximum length |
| `pattern` | Regex match |
| `min` | Minimum value |
| `max` | Maximum value |

**Detailed reference →** [validation-rules.md](references/validation-rules.md)

---

## Output Checklist

Before generating JSON, verify the following:

```
□ Determined user intent
□ Chose correct component type (see component-catalog.md)
□ Included intro field (brief summary)
□ ui_tree.root points to a valid element
□ All children references exist in elements
□ Form fields and actions are inside props
□ Form fields use "type" (not "fieldType")
□ JSON is well-formed (no trailing commas, correct quotes)
```

---

## Reference Documents

| Document | Content |
|----------|---------|
| [component-catalog.md](references/component-catalog.md) | **Detailed component properties and examples** |
| [action-schema.md](references/action-schema.md) | Action type reference |
| [validation-rules.md](references/validation-rules.md) | Validation rules |
| [fallback-strategies.md](references/fallback-strategies.md) | Fallback strategies |
