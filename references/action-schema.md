# Action Schema Reference v0.8

This document describes how user interaction actions are defined.

## Overview

Action Schema defines the handling logic after user operations (button clicks, form submissions).

**Used in:**
- Form.submitAction
- Form.actions[].action
- Card.actions[].action
- Modal.footer[].action
- Alert.actions[].action

## Action Types (6)

| type | Description |
|------|-------------|
| `api_call` | Call an API |
| `navigate` | Page navigation |
| `emit_event` | Send event |
| `open_modal` | Open modal |
| `close_modal` | Close modal |
| `reset` | Reset form |

---

## ActionSchema Structure

```json
{
  "type": "api_call",
  "api": {...},
  "url": "...",
  "event": "...",
  "modalId": "...",
  "confirm": {...},
  "callbacks": {...}
}
```

---

## api_call - API Call

```json
{
  "type": "api_call",
  "api": {
    "endpoint": "/api/users",
    "method": "POST",
    "bodyMapping": "auto"
  },
  "callbacks": {
    "onSuccess": [{"type": "navigate", "url": "/list"}],
    "feedback": {"successText": "Saved successfully", "errorText": "Save failed"}
  }
}
```

### api Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | string | **Required** | API endpoint |
| `method` | string | `"POST"` | HTTP method |
| `bodyMapping` | string/object | `"auto"` | Request body mapping |

**bodyMapping:**
- `"auto"`: Automatically map form fields
- `{fieldName: targetKey}`: Manual mapping

---

## navigate - Page Navigation

```json
{
  "type": "navigate",
  "url": "/users/{id}",
  "target": "_blank"
}
```

| Field | Description |
|-------|-------------|
| `url` | Target URL, supports `{id}` template variables |
| `target` | `_self` (default) or `_blank` |

---

## emit_event - Send Event

```json
{
  "type": "emit_event",
  "event": "user_created",
  "payload": {"id": 123}
}
```

| Field | Description |
|-------|-------------|
| `event` | Event name |
| `payload` | Event data (optional) |

---

## open_modal / close_modal - Modal Control

```json
{"type": "open_modal", "modalId": "edit_modal"}
{"type": "close_modal", "modalId": "edit_modal"}
```

| Field | Description |
|-------|-------------|
| `modalId` | Modal component ID |

---

## reset - Reset Form

```json
{"type": "reset"}
```

Resets the current form to its initial state.

---

## confirm - Confirmation Dialog

Show a confirmation dialog before executing the action:

```json
{
  "type": "api_call",
  "api": {"endpoint": "/api/delete/{id}", "method": "DELETE"},
  "confirm": {
    "title": "Confirm Delete",
    "message": "This cannot be undone. Are you sure?",
    "type": "danger"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Dialog title |
| `message` | string | Confirmation message |
| `type` | string | info, warning, danger |

---

## callbacks - Callback Configuration

```json
{
  "callbacks": {
    "onSuccess": [
      {"type": "emit_event", "event": "saved"},
      {"type": "navigate", "url": "/list"}
    ],
    "onError": [
      {"type": "emit_event", "event": "error"}
    ],
    "feedback": {
      "successText": "Operation successful",
      "errorText": "Operation failed"
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `onSuccess` | Actions to execute on success |
| `onError` | Actions to execute on failure |
| `feedback.successText` | Success message text |
| `feedback.errorText` | Error message text |

---

## Complete Examples

### Form Submission

```json
{
  "type": "Form",
  "props": {
    "title": "User Registration",
    "fields": [
      {"name": "email", "type": "email", "required": true},
      {"name": "password", "type": "password", "required": true}
    ],
    "actions": [
      {"label": "Register", "type": "submit", "variant": "primary"}
    ],
    "submitAction": {
      "type": "api_call",
      "api": {"endpoint": "/api/register", "method": "POST", "bodyMapping": "auto"},
      "callbacks": {
        "onSuccess": [{"type": "navigate", "url": "/login"}],
        "feedback": {"successText": "Registration successful", "errorText": "Registration failed"}
      }
    }
  }
}
```

### Delete with Confirmation

```json
{
  "type": "Card",
  "props": {
    "title": "User Info",
    "actions": [
      {
        "label": "Delete",
        "variant": "danger",
        "action": {
          "type": "api_call",
          "api": {"endpoint": "/api/users/{id}", "method": "DELETE"},
          "confirm": {"title": "Confirm Delete", "message": "Are you sure?", "type": "danger"},
          "callbacks": {
            "onSuccess": [{"type": "navigate", "url": "/users"}],
            "feedback": {"successText": "Deleted"}
          }
        }
      }
    ]
  }
}
```

### Modal Operations

```json
{
  "type": "Card",
  "props": {
    "actions": [
      {"label": "Edit", "variant": "primary", "action": {"type": "open_modal", "modalId": "edit_modal"}}
    ]
  }
}
```

```json
{
  "type": "Modal",
  "props": {
    "title": "Edit",
    "footer": [
      {"label": "Cancel", "variant": "outline", "action": {"type": "close_modal", "modalId": "edit_modal"}},
      {"label": "Save", "variant": "primary", "action": {"type": "api_call", "api": {"endpoint": "/api/save"}}}
    ]
  }
}
```
