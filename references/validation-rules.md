# Validation Rules Reference v0.8

This document describes the validation rules supported by Form component fields.

## Overview

Validation rules are configured via Form.fields[].validation, supporting 11 built-in validators.

## Validation Configuration Structure

```json
{
  "type": "Form",
  "props": {
    "fields": [
      {
        "name": "email",
        "type": "email",
        "label": "Email",
        "required": true,
        "validation": [
          {"type": "required", "message": "Email is required"},
          {"type": "email", "message": "Invalid email format"}
        ]
      }
    ]
  }
}
```

---

## Built-in Validators (11)

### required - Required Field

```json
{"type": "required", "message": "This field is required"}
```

Empty value criteria: `null`, `""`, `[]`

### email - Email

```json
{"type": "email", "message": "Please enter a valid email"}
```

Pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

### minLength - Minimum Length

```json
{"type": "minLength", "value": 6, "message": "At least 6 characters"}
```

### maxLength - Maximum Length

```json
{"type": "maxLength", "value": 100, "message": "At most 100 characters"}
```

### pattern - Regex

```json
{"type": "pattern", "value": "^[a-zA-Z0-9]+$", "message": "Only letters and numbers allowed"}
```

Common patterns:
| Usage | Pattern |
|-------|---------|
| Phone (US) | `^\+1\d{10}$` |
| Phone (CN) | `^1[3-9]\d{9}$` |
| Username | `^[a-zA-Z0-9_]{3,20}$` |

### min - Minimum Value

```json
{"type": "min", "value": 0, "message": "Cannot be negative"}
```

### max - Maximum Value

```json
{"type": "max", "value": 100, "message": "Cannot exceed 100"}
```

### numeric - Numeric

```json
{"type": "numeric", "message": "Please enter a number"}
```

### url - URL

```json
{"type": "url", "message": "Please enter a valid URL"}
```

Pattern: `^https?://[^\s/$.?#].[^\s]*$`

### matches - Field Match

Used for password confirmation and similar scenarios:

```json
{"type": "matches", "value": "password", "message": "Passwords do not match"}
```

`value` is the target field's name.

### custom - Custom

```json
{"type": "custom", "value": "validateUsername", "message": "Invalid username"}
```

The frontend must register a corresponding validation function.

---

## Shorthand Property Auto-Conversion

Form.fields properties are automatically converted to validation rules:

| Property | Auto-generated Rule |
|----------|-------------------|
| `required: true` | `{"type": "required"}` |
| `type: "email"` | `{"type": "email"}` |
| `type: "number"` | `{"type": "numeric"}` |
| `minLength: 6` | `{"type": "minLength", "value": 6}` |
| `maxLength: 100` | `{"type": "maxLength", "value": 100}` |
| `min: 0` | `{"type": "min", "value": 0}` |
| `max: 100` | `{"type": "max", "value": 100}` |
| `pattern: "..."` | `{"type": "pattern", "value": "..."}` |

---

## Conditional Visibility (visibleWhen)

Fields can be dynamically shown/hidden based on other field values.

```json
{
  "name": "company",
  "type": "text",
  "label": "Company Name",
  "visibleWhen": {
    "field": "userType",
    "operator": "equals",
    "value": "business"
  }
}
```

### Operators

| Operator | Description |
|----------|-------------|
| `equals` | Equals |
| `notEquals` | Not equals |
| `contains` | Contains |
| `isEmpty` | Is empty |
| `isNotEmpty` | Is not empty |
| `in` | In list |

---

## Complete Example

```json
{
  "type": "Form",
  "props": {
    "title": "User Registration",
    "fields": [
      {
        "name": "username",
        "type": "text",
        "label": "Username",
        "required": true,
        "minLength": 3,
        "maxLength": 20,
        "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
        "helperText": "3-20 characters, starts with a letter"
      },
      {
        "name": "email",
        "type": "email",
        "label": "Email",
        "required": true
      },
      {
        "name": "password",
        "type": "password",
        "label": "Password",
        "required": true,
        "minLength": 8,
        "showToggle": true
      },
      {
        "name": "confirmPassword",
        "type": "password",
        "label": "Confirm Password",
        "required": true,
        "validation": [
          {"type": "required"},
          {"type": "matches", "value": "password", "message": "Passwords do not match"}
        ]
      },
      {
        "name": "userType",
        "type": "radio",
        "label": "User Type",
        "options": [
          {"value": "personal", "label": "Personal"},
          {"value": "business", "label": "Business"}
        ]
      },
      {
        "name": "company",
        "type": "text",
        "label": "Company Name",
        "visibleWhen": {"field": "userType", "operator": "equals", "value": "business"}
      }
    ],
    "actions": [
      {"label": "Register", "type": "submit", "variant": "primary"}
    ],
    "submitAction": {
      "type": "api_call",
      "api": {"endpoint": "/api/register", "method": "POST"}
    }
  }
}
```
