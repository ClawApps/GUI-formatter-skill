# Fallback Strategies Reference v0.8

This document describes the UI Formatter's degradation strategies, ensuring renderable output even when validation fails.

## Overview

The fallback mechanism automatically repairs or degrades input data that doesn't fully conform to the spec, rather than failing outright.

**Design goals:**
- Generate renderable output whenever possible
- Preserve the core information of the original intent
- Provide clear warning reports

## Enabling/Disabling Fallback

```python
from scripts.formatter import UIFormatter, FormatterConfig

# Enabled by default
config = FormatterConfig(enable_fallback=True)

# Disable fallback (strict mode)
config = FormatterConfig(enable_fallback=False, strict_validation=True)
```

CLI:
```bash
python scripts/formatter.py input.json --no-fallback
python scripts/formatter.py input.json --strict
```

---

## Fallback Strategies

### 1. Unknown Component Type Degradation

Unknown component types are degraded to Card:

| Input Type | Degradation Target |
|------------|-------------------|
| Unknown display type | `Markdown` |
| Unknown form type | `Form` |
| Unknown layout type | `Card` |
| Other unknown | `Card` |

**Example:**
```json
// Input
{"type": "CustomWidget", "props": {"title": "Title"}}

// After degradation
{"type": "Card", "props": {"title": "Title"}}
```

Warning: `Component custom_0 degraded from CustomWidget to Card`

### 2. Missing Required Property Filling

Automatically fills missing required properties with default values.

**Example:**
```json
// Input (missing name)
{"name": "email", "type": "email", "label": "Email"}

// After filling
{"name": "field_0", "type": "email", "label": "Email"}
```

### 3. Data Type Mismatch Handling

| Expected Type | Actual Type | Handling |
|---------------|-------------|----------|
| number | string | parseFloat |
| boolean | string | "true" → true |
| string | number | Convert to string |
| array | string | Wrap in array |

### 4. Invalid Child Reference Removal

Automatically removes children that reference non-existent IDs.

```json
// Input
{"children": ["valid_id", "nonexistent_id"]}

// After processing
{"children": ["valid_id"]}
```

### 5. Circular Reference Detection

Detects and reports circular reference paths without interrupting processing.

```
Error: Circular reference detected: a -> b -> c -> a
```

### 6. Orphan Element Warning

Detects elements unreachable from the root node, generates warning but preserves them.

```
Warning: Orphan element, unreachable from root: orphan_field
```

---

## Validation Status

The `metadata.validation_status` field in the output:

| Status | Description |
|--------|-------------|
| `valid` | Passed all validations |
| `warning` | Has warnings but auto-repaired |
| `invalid` | Critical errors, fallback cannot repair |

**Output example:**
```json
{
  "root": "card_0",
  "elements": {...},
  "metadata": {
    "version": "v0.8.0",
    "validation_status": "warning",
    "errors": [],
    "warnings": ["Component widget_0 degraded from CustomWidget to Card"]
  }
}
```

---

## Error Codes

| Error Type | Description | Degradable |
|------------|-------------|------------|
| `UNKNOWN_TYPE` | Unknown component type | ✅ |
| `MISSING_REQUIRED` | Missing required property | ✅ |
| `TYPE_MISMATCH` | Type mismatch | ✅ |
| `INVALID_REFERENCE` | Invalid reference | ✅ |
| `CIRCULAR_REFERENCE` | Circular reference | ✅ (removed) |
| `MISSING_ROOT` | Missing root element | ❌ |
| `MISSING_ELEMENTS` | Missing elements dictionary | ❌ |
| `ROOT_NOT_FOUND` | Root element not found | ❌ |

---

## Best Practices

1. **Use strict mode during development:** `--strict`
2. **Enable fallback in production:** Ensure users always see rendered output
3. **Monitor warnings:** Regularly check `metadata.warnings`
4. **Use whitelisted components:** Only use the 12 standard components

**v0.8 Component List (12):**
- Markdown, Collapse
- AppCard
- Form
- VideoPlayer, AudioPlayer, ImageGallery
- Alert, Progress
- Card, Modal
- WebView
