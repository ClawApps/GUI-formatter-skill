# Component Catalog v0.8.0

This document describes all 12 supported UI component types and their properties in detail.

## Component Overview

| Category | Component | Supports children | Supports actions |
|----------|-----------|-------------------|------------------|
| Display | Markdown | - | - |
| Display | Collapse | - | - |
| Card | AppCard | - | - |
| Form | Form | - | ✅ actions[], fields[] |
| Media | VideoPlayer | - | - |
| Media | AudioPlayer | - | - |
| Media | ImageGallery | - | - |
| Feedback | Alert | - | ✅ actions[] |
| Feedback | Progress | - | - |
| Layout | Card | ✅ | ✅ actions[] |
| Layout | Modal | ✅ | ✅ footer[] |
| Embed | WebView | - | - |

---

## 1. Markdown

Rich text rendering component, supports tables, code blocks, images, etc.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `content` | string | `""` | Markdown content |
| `allowHtml` | boolean | `false` | Allow HTML tags |
| `codeOptions` | object | - | Code block options |
| `imageOptions` | object | - | Image options |

**codeOptions:**
```json
{"copyable": true, "showLineNumbers": true, "highlightLines": []}
```

**imageOptions:**
```json
{"clickAction": "lightbox", "maxWidth": "100%"}
```

**Example:**
```json
{
  "type": "Markdown",
  "props": {
    "content": "## Title\n\n| Col 1 | Col 2 |\n|-------|-------|\n| A | B |",
    "codeOptions": {"copyable": true}
  }
}
```

---

## 2. Collapse

Collapsible panel component, supports expand/collapse content areas.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `items` | CollapseItem[] | `[]` | Panel item list |
| `accordion` | boolean | `false` | Accordion mode (only one open at a time) |
| `bordered` | boolean | `true` | Show border |
| `gap` | number | `0` | Gap between panels |

**CollapseItem:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `key` | string | - | **Required** Unique identifier |
| `title` | string | - | **Required** Panel title |
| `subtitle` | string | - | Subtitle |
| `icon` | string | - | Title icon (emoji or icon name) |
| `content` | string | - | Markdown content |
| `defaultExpanded` | boolean | `false` | Default expanded |
| `disabled` | boolean | `false` | Disable collapse |

**Example (task list collapse):**
```json
{
  "type": "Collapse",
  "props": {
    "accordion": false,
    "bordered": true,
    "items": [
      {
        "key": "active_tasks",
        "title": "Active Scheduled Tasks",
        "subtitle": "3 tasks",
        "icon": "📋",
        "defaultExpanded": true,
        "content": "| Task | Execution Time | Type | Status |\n|------|---------------|------|--------|\n| Meeting Reminder | Jan 25 16:00 | One-time | Pending |\n| Daily Exercise | Every day 09:00 | Recurring | Active |"
      },
      {
        "key": "completed",
        "title": "Completed Tasks",
        "subtitle": "5 tasks",
        "icon": "✅",
        "content": "| Task | Completed At | Result |\n|------|-------------|--------|\n| Morning Meeting | Jan 24 09:00 | Delivered |"
      }
    ]
  }
}
```

**Example (accordion mode):**
```json
{
  "type": "Collapse",
  "props": {
    "accordion": true,
    "items": [
      {"key": "q1", "title": "What are scheduled tasks?", "content": "Scheduled tasks are..."},
      {"key": "q2", "title": "How to create recurring tasks?", "content": "You can say..."}
    ]
  }
}
```

---

## 3. AppCard

App/work display card, used for showing apps or AI-generated works.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | string | - | **Required** Unique ID (UUID) |
| `title` | string | - | **Required** Title |
| `url` | string | `""` | Access URL |
| `description` | string | `""` | Description text |
| `avatar` | string | `""` | Icon URL |
| `thumbnail` | string | `""` | Thumbnail URL |
| `author_name` | string | `""` | Author name |
| `type` | string | `""` | Content type: image, video, audio, document, mixed |
| `view_count` | number | `0` | View count |
| `like_count` | number | `0` | Like count |

**Type reference:**

| type | Description | Icon |
|------|-------------|------|
| `image` | Image work | 🖼️ |
| `video` | Video work | 🎬 |
| `audio` | Audio work | 🎵 |
| `document` | Document/webpage/game | 📄 |
| `mixed` | Mixed type | 📦 |

**Example (App card):**
```json
{
  "type": "AppCard",
  "props": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Smart Translator",
    "avatar": "https://example.com/translate-icon.png",
    "description": "Real-time translation supporting 100+ languages",
    "url": "https://example.com/{workspace}/translate",
    "like_count": 5200,
    "view_count": 32000
  }
}
```

**Example (Work card):**
```json
{
  "type": "AppCard",
  "props": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Ink Landscape Painting",
    "thumbnail": "https://example.com/landscape.jpg",
    "author_name": "Alice",
    "type": "image",
    "like_count": 892,
    "view_count": 4500,
    "url": "https://example.com/{workspace}/works/abc-123.html"
  }
}
```

**Multi-card list example (using Card as container):**
```json
{
  "root": "card_container",
  "elements": {
    "card_container": {
      "type": "Card",
      "props": {
        "title": "Recommended",
        "layout": "grid",
        "gridColumns": 2,
        "gap": 16
      },
      "children": ["app_1", "app_2"]
    },
    "app_1": {
      "type": "AppCard",
      "props": {
        "id": "uuid-1",
        "title": "Smart Translator",
        "avatar": "https://...",
        "description": "Multi-language translation",
        "like_count": 5200,
        "view_count": 32000
      }
    },
    "app_2": {
      "type": "AppCard",
      "props": {
        "id": "uuid-2",
        "title": "Ink Landscape Painting",
        "thumbnail": "https://...",
        "author_name": "Alice",
        "type": "image",
        "like_count": 892,
        "view_count": 4500
      }
    }
  }
}
```

---

## 4. Form

Form container with inline field definitions and action buttons.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | string | - | Form title |
| `description` | string | - | Form description |
| `layout` | string | `"vertical"` | Layout: vertical, horizontal, inline |
| `labelWidth` | number | `100` | Label width for horizontal layout |
| `columns` | number | `1` | Number of columns |
| `gap` | number | `16` | Gap between fields |
| `fields` | FormFieldDef[] | `[]` | Field definition list |
| `actions` | FormAction[] | `[]` | Action button list |
| `actionsAlign` | string | `"right"` | Button alignment: left, center, right |
| `submitAction` | ActionSchema | - | Submit action |
| `validateOnChange` | boolean | `true` | Validate on input change |
| `validateOnBlur` | boolean | `true` | Validate on blur |

### FormFieldDef (Inline Field Definition)

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | **Required** Field name |
| `type` | string | **Required** Field type |
| `label` | string | Label |
| `placeholder` | string | Placeholder text |
| `defaultValue` | any | Default value |
| `required` | boolean | Whether required |
| `disabled` | boolean | Whether disabled |
| `helperText` | string | Helper text |
| `validation` | ValidationRule[] | Validation rules |
| `visibleWhen` | VisibilityCondition | Conditional visibility |

### Field Types (12)

| type | Usage | Special Props |
|-----------|-------|---------------|
| `text` | Single-line text | maxLength, minLength, pattern |
| `email` | Email | (built-in validation) |
| `password` | Password | showToggle |
| `number` | Number | min, max, step |
| `textarea` | Multi-line text | rows, maxLength |
| `select` | Dropdown | options, multiple, searchable |
| `date` | Date picker | minDate, maxDate, dateFormat, showTime |
| `checkbox` | Checkbox | - |
| `radio` | Radio buttons | options, direction |
| `switch` | Toggle switch | - |
| `slider` | Slider | min, max, step, marks |
| `file` | File upload | accept, maxSize, maxFiles |

### FormAction (Inline Button Definition)

```json
{"label": "Submit", "type": "submit", "variant": "primary"}
```

| Property | Type | Description |
|----------|------|-------------|
| `label` | string | Button text |
| `type` | string | submit, reset, button |
| `variant` | string | primary, secondary, outline, danger |
| `disabled` | boolean | Whether disabled |
| `action` | ActionSchema | Click action |

**Example:**
```json
{
  "type": "Form",
  "props": {
    "title": "User Login",
    "fields": [
      {"name": "email", "type": "email", "label": "Email", "required": true},
      {"name": "password", "type": "password", "label": "Password", "showToggle": true}
    ],
    "actions": [
      {"label": "Login", "type": "submit", "variant": "primary"}
    ],
    "submitAction": {"type": "api_call", "api": {"endpoint": "/api/login", "method": "POST"}}
  }
}
```

---

## 5. Card

Unified layout container, supports flex/grid layout, can contain any child components.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | string | - | Title |
| `subtitle` | string | - | Subtitle |
| `content` | string | - | Text content |
| `image` | string/ImageConfig | - | Header image |
| `layout` | string | `"flex"` | Layout: flex, grid |
| `direction` | string | `"column"` | Flex direction: row, column |
| `gap` | number | `16` | Gap |
| `padding` | number | `16` | Padding |
| `align` | string | `"stretch"` | Alignment: start, center, end, stretch |
| `justify` | string | `"start"` | Justification: start, center, end, between, around |
| `gridColumns` | number | `3` | Grid column count |
| `bordered` | boolean | `true` | Show border |
| `hoverable` | boolean | `false` | Hover effect |
| `shadow` | string | `"none"` | Shadow: none, sm, md, lg |
| `background` | string | - | Background color |
| `borderRadius` | number | `8` | Border radius |
| `actions` | ActionButton[] | - | Action buttons |
| `actionsPosition` | string | `"bottom"` | Button position: bottom, right |

**ImageConfig:**
```json
{"src": "url", "position": "top", "height": 200, "fit": "cover"}
```

**Example (Flex layout):**
```json
{
  "type": "Card",
  "props": {
    "layout": "flex",
    "direction": "row",
    "gap": 16,
    "align": "center"
  },
  "children": ["child_1", "child_2"]
}
```

**Example (Product card):**
```json
{
  "type": "Card",
  "props": {
    "title": "iPhone 15",
    "subtitle": "Apple Flagship",
    "content": "A17 Pro chip",
    "image": {"src": "url", "position": "top", "height": 150},
    "actions": [
      {"label": "Buy", "variant": "primary", "action": {"type": "navigate", "url": "/buy"}}
    ]
  }
}
```

---

## 6. Modal

Modal dialog / Drawer component, can contain any child components.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | string | - | Title |
| `mode` | string | `"modal"` | Mode: modal, drawer |
| `placement` | string | `"right"` | Drawer position: left, right, top, bottom |
| `width` | number | `520` | Width |
| `height` | number | - | Height |
| `closable` | boolean | `true` | Can be closed |
| `maskClosable` | boolean | `true` | Close on mask click |
| `footer` | ActionButton[] | - | Footer buttons |

**Example (Modal):**
```json
{
  "type": "Modal",
  "props": {
    "title": "Edit",
    "mode": "modal",
    "width": 600,
    "footer": [
      {"label": "Cancel", "variant": "outline", "action": {"type": "close_modal", "modalId": "m1"}},
      {"label": "Save", "variant": "primary"}
    ]
  },
  "children": ["form_1"]
}
```

**Example (Drawer):**
```json
{
  "type": "Modal",
  "props": {
    "title": "Sidebar",
    "mode": "drawer",
    "placement": "right",
    "width": 400
  },
  "children": ["content_1"]
}
```

---

## 7. Alert

Alert notification component.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `type` | string | `"info"` | Type: info, success, warning, error |
| `message` | string | - | Message content |
| `description` | string | - | Detailed description |
| `showIcon` | boolean | `true` | Show icon |
| `closable` | boolean | `false` | Can be closed |
| `actions` | ActionButton[] | - | Action buttons |

**Example:**
```json
{
  "type": "Alert",
  "props": {
    "type": "warning",
    "message": "Insufficient Balance",
    "description": "Please top up your account",
    "actions": [
      {"label": "Top Up", "variant": "primary", "action": {"type": "navigate", "url": "/recharge"}}
    ]
  }
}
```

---

## 8. Progress

Progress bar component.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `value` | number | `0` | Current value |
| `max` | number | `100` | Maximum value |
| `type` | string | `"linear"` | Type: linear, circle |
| `label` | string | - | Label |
| `showValue` | boolean | `true` | Show value |
| `size` | number | - | Size for circle type |
| `status` | string | `"normal"` | Status: normal, success, error |

**Example:**
```json
{
  "type": "Progress",
  "props": {"value": 75, "max": 100, "type": "circle", "label": "Completion"}
}
```

---

## 9. VideoPlayer

Video player component.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `src` | string | - | Video URL |
| `poster` | string | - | Poster image |
| `title` | string | - | Title |
| `controls` | boolean | `true` | Show controls |
| `autoplay` | boolean | `false` | Autoplay |
| `muted` | boolean | `false` | Muted |
| `loop` | boolean | `false` | Loop |
| `width` | string | `"100%"` | Width |
| `height` | number | - | Height |

---

## 10. AudioPlayer

Audio player component.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `src` | string | - | Audio URL |
| `title` | string | - | Title |
| `controls` | boolean | `true` | Show controls |
| `autoplay` | boolean | `false` | Autoplay |
| `loop` | boolean | `false` | Loop |

---

## 11. ImageGallery

Image gallery component.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `images` | ImageDef[] | `[]` | Image list |
| `layout` | string | `"grid"` | Layout: grid, carousel |
| `columns` | number | `3` | Column count |
| `gap` | number | `8` | Gap |
| `enableLightbox` | boolean | `true` | Enable lightbox preview |

**ImageDef:**
```json
{"src": "url", "alt": "description", "thumbnail": "thumb_url", "caption": "caption"}
```

**Example:**
```json
{
  "type": "ImageGallery",
  "props": {
    "images": [
      {"src": "1.jpg", "alt": "Image 1"},
      {"src": "2.jpg", "alt": "Image 2"}
    ],
    "columns": 2,
    "enableLightbox": true
  }
}
```

---

## 12. WebView

Web page embed component (iframe).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | string | - | Page URL |
| `html` | string | - | HTML content (mutually exclusive with url) |
| `width` | string | `"100%"` | Width |
| `height` | number | `400` | Height |
| `sandbox` | string[] | - | Sandbox permissions |

**Example:**
```json
{
  "type": "WebView",
  "props": {
    "url": "https://example.com",
    "height": 500,
    "sandbox": ["allow-scripts", "allow-same-origin"]
  }
}
```

---

## ActionButton Common Definition

Used in Card.actions, Modal.footer, Alert.actions.

| Property | Type | Description |
|----------|------|-------------|
| `label` | string | Button text |
| `variant` | string | primary, secondary, outline, text, danger, link |
| `size` | string | small, medium, large |
| `icon` | string | Icon |
| `disabled` | boolean | Whether disabled |
| `loading` | boolean | Loading state |
| `action` | ActionSchema | Click action |

---

## ActionSchema Common Definition

| type | Usage | Key Properties |
|------|-------|---------------|
| `api_call` | Call API | api.endpoint, api.method |
| `navigate` | Page navigation | url, target |
| `emit_event` | Send event | event, payload |
| `open_modal` | Open modal | modalId |
| `close_modal` | Close modal | modalId |
| `reset` | Reset form | - |

Detailed reference: [action-schema.md](action-schema.md)
