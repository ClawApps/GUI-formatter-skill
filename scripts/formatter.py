#!/usr/bin/env python3
"""
Output Formatter v0.8.0 - Core Formatting Engine

Converts Agent output intents into UITree JSON format.
12 components: Markdown, Collapse, AppCard, Form, Card, Modal, Alert, Progress, VideoPlayer, AudioPlayer, ImageGallery, WebView

Pipeline:
Agent output intent -> Intent parsing -> Component generation -> Tree building -> Validation -> Fallback -> UITree JSON
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from catalog import get_catalog, ComponentCategory, FormFieldType
from validator import get_validator, ValidationResult, validate_with_fallback


class IntentType(Enum):
    """Intent types"""
    REPLY = "reply"              # Text reply -> Markdown
    CODE = "code"                # Code reply -> Markdown (with codeOptions)
    FORM = "form"                # Form -> Form (contains fields + actions)
    CONFIRM = "confirm"          # Confirmation -> Card (with actions)
    SELECT = "select"            # Selection -> Form (fields: radio/select)
    ALERT = "alert"              # Info alert -> Alert (info)
    WARN = "warn"                # Warning -> Alert (warning)
    ERROR = "error"              # Error -> Alert (error)
    SUCCESS = "success"          # Success -> Alert (success)
    DATA = "data"                # Data display -> Markdown table
    MEDIA = "media"              # Media display -> ImageGallery/VideoPlayer/AudioPlayer
    PROGRESS = "progress"        # Progress display -> Progress
    APP = "app"                  # App/work display -> AppCard
    UNKNOWN = "unknown"


@dataclass
class FormatterConfig:
    """Formatter configuration"""
    enable_fallback: bool = True
    strict_validation: bool = False
    auto_generate_ids: bool = True
    id_prefix: str = ""
    version: str = "v0.8.0"


@dataclass
class FormatterResult:
    """Formatting result"""
    success: bool
    tree: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fallback_applied: bool = False
    intent: Optional[str] = None


class UIFormatter:
    """
    UI Formatter v0.8.0

    Core features:
    1. Intent parsing - Identify input intent type
    2. Component generation - Generate matching component
    3. Tree building - Build flat tree (Card/Form as root container)
    4. Validation + Fallback - Degrade to Markdown after 3 failed validation rounds
    """

    def __init__(self, config: Optional[FormatterConfig] = None):
        self.config = config or FormatterConfig()
        self.catalog = get_catalog()
        self.validator = get_validator()
        self._id_counter: Dict[str, int] = {}

    def _generate_id(self, component_type: str) -> str:
        """Generate unique ID"""
        if component_type not in self._id_counter:
            self._id_counter[component_type] = 0
        idx = self._id_counter[component_type]
        self._id_counter[component_type] += 1
        prefix = self.config.id_prefix
        type_lower = component_type.lower()
        return f"{prefix}{type_lower}_{idx}" if prefix else f"{type_lower}_{idx}"

    def _reset_id_counter(self):
        self._id_counter = {}

    # ========== Intent Parsing ==========

    def _parse_intent(self, input_data: Dict[str, Any]) -> IntentType:
        """Parse input intent"""
        intent_str = input_data.get("intent", "").lower()

        intent_map = {
            "reply": IntentType.REPLY, "text": IntentType.REPLY, "message": IntentType.REPLY,
            "code": IntentType.CODE,
            "form": IntentType.FORM, "input": IntentType.FORM,
            "confirm": IntentType.CONFIRM,
            "select": IntentType.SELECT, "choose": IntentType.SELECT,
            "alert": IntentType.ALERT, "info": IntentType.ALERT,
            "warn": IntentType.WARN, "warning": IntentType.WARN,
            "error": IntentType.ERROR,
            "success": IntentType.SUCCESS,
            "data": IntentType.DATA,
            "media": IntentType.MEDIA,
            "progress": IntentType.PROGRESS,
            "app": IntentType.APP, "skill": IntentType.APP,
            "work": IntentType.APP, "ai_work": IntentType.APP,
        }

        if intent_str in intent_map:
            return intent_map[intent_str]

        # Infer from content
        if "content" in input_data and isinstance(input_data["content"], str):
            if "```" in input_data["content"] or input_data.get("language"):
                return IntentType.CODE
            return IntentType.REPLY

        if "fields" in input_data:
            return IntentType.FORM
        if "question" in input_data and "options" in input_data:
            return IntentType.SELECT
        if "title" in input_data and "actions" in input_data:
            return IntentType.CONFIRM
        if "message" in input_data and input_data.get("type") in ["info", "warning", "error", "success"]:
            return IntentType.ALERT

        return IntentType.UNKNOWN

    # ========== Intent Handlers ==========

    def _handle_reply(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Markdown component"""
        content = input_data.get("content", "")
        return {
            "type": "Markdown",
            "props": {"content": content}
        }

    def _handle_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code Markdown component"""
        code = input_data.get("code", input_data.get("content", ""))
        language = input_data.get("language", "text")

        # Extract from markdown code block
        if "```" in code:
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("```"):
                    lang = line[3:].strip()
                    if lang:
                        language = lang
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("```"):
                            code = "\n".join(lines[i + 1:j])
                            break
                    break

        return {
            "type": "Markdown",
            "props": {
                "content": f"```{language}\n{code}\n```",
                "codeOptions": {
                    "copyable": input_data.get("copyable", True),
                    "showLineNumbers": input_data.get("showLineNumbers", True)
                }
            }
        }

    def _handle_form(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Form component (inline fields + actions)"""
        fields = input_data.get("fields", [])
        actions = input_data.get("actions", [{"label": "Submit", "type": "submit", "variant": "primary"}])

        # Normalize fields
        normalized_fields = []
        for f in fields:
            field_def = {
                "name": f.get("name", f"field_{len(normalized_fields)}"),
                "type": f.get("type", f.get("type", "text")),
                "label": f.get("label", ""),
            }
            # Copy additional properties
            for key in ["placeholder", "defaultValue", "required", "disabled", "helperText",
                        "options", "min", "max", "minLength", "maxLength", "pattern",
                        "multiple", "searchable", "rows", "showToggle", "validation", "visibleWhen"]:
                if key in f:
                    field_def[key] = f[key]
            normalized_fields.append(field_def)

        # Normalize actions
        normalized_actions = []
        for a in actions:
            action_def = {
                "label": a.get("label", "Submit"),
                "type": a.get("type", "submit"),
                "variant": a.get("variant", "primary" if a.get("type") in ["submit", "confirm"] else "secondary")
            }
            if "action" in a:
                action_def["action"] = a["action"]
            if a.get("disabled"):
                action_def["disabled"] = True
            normalized_actions.append(action_def)

        return {
            "type": "Form",
            "props": {
                "title": input_data.get("title", ""),
                "description": input_data.get("description", ""),
                "layout": input_data.get("layout", "vertical"),
                "fields": normalized_fields,
                "actions": normalized_actions,
                "submitAction": input_data.get("submitAction")
            }
        }

    def _handle_confirm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate confirmation Card component (Card with actions)"""
        title = input_data.get("title", "Confirm")
        content = input_data.get("description", input_data.get("content", ""))
        actions = input_data.get("actions", [
            {"label": "Confirm", "variant": "primary"},
            {"label": "Cancel", "variant": "outline"}
        ])

        # Normalize actions
        normalized_actions = []
        for a in actions:
            action_type = a.get("type", "")
            variant = a.get("variant")
            if not variant:
                if action_type in ["confirm", "submit"]:
                    variant = "primary"
                elif action_type in ["danger", "delete"]:
                    variant = "danger"
                else:
                    variant = "outline"

            action_def = {"label": a.get("label", ""), "variant": variant}
            if "action" in a:
                action_def["action"] = a["action"]
            normalized_actions.append(action_def)

        return {
            "type": "Card",
            "props": {
                "title": title,
                "content": content,
                "actions": normalized_actions,
                "bordered": True
            }
        }

    def _handle_select(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate selection Form component (Form with radio/select field)"""
        question = input_data.get("question", "Please select")
        options = input_data.get("options", [])
        multiple = input_data.get("multiple", False)

        # Determine field type based on option count and multi-select
        if multiple:
            field_type = "checkbox"
        elif len(options) <= 5:
            field_type = "radio"
        else:
            field_type = "select"

        field_def = {
            "name": "selection",
            "type": field_type,
            "label": question,
            "options": options,
            "required": True
        }

        if field_type == "select" and len(options) > 10:
            field_def["searchable"] = True

        return {
            "type": "Form",
            "props": {
                "fields": [field_def],
                "actions": input_data.get("actions", [{"label": "OK", "type": "submit", "variant": "primary"}])
            }
        }

    def _handle_alert(self, input_data: Dict[str, Any], alert_type: str = "info") -> Dict[str, Any]:
        """Generate Alert component"""
        message = input_data.get("message", input_data.get("content", ""))
        description = input_data.get("description", "")
        actions = input_data.get("actions", [])

        return {
            "type": "Alert",
            "props": {
                "type": alert_type,
                "message": message,
                "description": description,
                "showIcon": input_data.get("showIcon", True),
                "closable": input_data.get("closable", False),
                "actions": actions
            }
        }

    def _handle_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Progress component"""
        return {
            "type": "Progress",
            "props": {
                "value": input_data.get("value", 0),
                "max": input_data.get("max", 100),
                "type": input_data.get("type", "linear"),
                "label": input_data.get("label", ""),
                "showValue": input_data.get("showValue", True),
                "status": input_data.get("status", "normal")
            }
        }

    def _handle_media(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate media component"""
        media_type = input_data.get("media_type", "image").lower()
        src = input_data.get("src", "")
        sources = input_data.get("sources", [src] if src else [])

        if media_type == "video":
            return {
                "type": "VideoPlayer",
                "props": {
                    "src": sources[0] if sources else "",
                    "poster": input_data.get("poster", ""),
                    "controls": input_data.get("controls", True),
                    "title": input_data.get("title", "")
                }
            }
        elif media_type == "audio":
            return {
                "type": "AudioPlayer",
                "props": {
                    "src": sources[0] if sources else "",
                    "controls": input_data.get("controls", True),
                    "title": input_data.get("title", "")
                }
            }
        else:  # image
            images = []
            for s in sources:
                if isinstance(s, str):
                    images.append({"src": s})
                else:
                    images.append(s)
            return {
                "type": "ImageGallery",
                "props": {
                    "images": images,
                    "columns": input_data.get("columns", 1 if len(images) == 1 else 3),
                    "enableLightbox": input_data.get("enableLightbox", True)
                }
            }

    def _handle_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data display Markdown table"""
        data = input_data.get("data", [])
        columns = input_data.get("columns", [])
        title = input_data.get("title", "")

        if not data or not columns:
            return {"type": "Markdown", "props": {"content": title or "No data"}}

        # Build Markdown table
        headers = [c.get("title", c.get("key", "")) for c in columns]
        keys = [c.get("key", "") for c in columns]

        lines = []
        if title:
            lines.append(f"## {title}\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in data:
            cells = [str(row.get(k, "")) for k in keys]
            lines.append("| " + " | ".join(cells) + " |")

        return {
            "type": "Markdown",
            "props": {"content": "\n".join(lines)}
        }

    def _handle_app(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AppCard component"""
        return {
            "type": "AppCard",
            "props": {
                "id": input_data.get("id", ""),
                "title": input_data.get("title", ""),
                "url": input_data.get("url", ""),
                "description": input_data.get("description", ""),
                "avatar": input_data.get("avatar", ""),
                "thumbnail": input_data.get("thumbnail", ""),
                "author_name": input_data.get("author_name", ""),
                "type": input_data.get("type", ""),
                "view_count": input_data.get("view_count", 0),
                "like_count": input_data.get("like_count", 0)
            }
        }

    # ========== Tree Building ==========

    def _build_tree(self, component: Dict[str, Any], intent: IntentType) -> Dict[str, Any]:
        """Build flat tree structure"""
        self._reset_id_counter()

        comp_type = component.get("type", "Markdown")
        comp_id = self._generate_id(comp_type)

        element = {
            "id": comp_id,
            "type": comp_type,
            "props": component.get("props", {}),
            "children": []
        }

        tree = {
            "root": comp_id,
            "elements": {comp_id: element},
            "metadata": {
                "version": self.config.version,
                "intent": intent.value,
                "validation_status": "valid",
                "errors": [],
                "warnings": [],
                "generated_at": datetime.now().astimezone().isoformat()
            }
        }

        return tree

    # ========== Main Format Method ==========

    def format(self, input_data: Dict[str, Any]) -> FormatterResult:
        """
        Main formatting method

        Supported input formats:
        - {"intent": "reply", "content": "text content"}
        - {"intent": "code", "code": "code", "language": "python"}
        - {"intent": "form", "fields": [...], "actions": [...]}
        - {"intent": "confirm", "title": "Confirm", "description": "...", "actions": [...]}
        - {"intent": "select", "question": "Question", "options": [...]}
        - {"intent": "alert|warn|error|success", "message": "message"}
        - {"intent": "data", "columns": [...], "data": [...]}
        - {"intent": "media", "src": "...", "media_type": "image|video|audio"}
        - {"intent": "progress", "value": 50, "max": 100}
        - {"intent": "app", "id": "uuid", "title": "App name", "avatar": "...", ...}
        - {"intent": "work", "id": "uuid", "title": "Work name", "thumbnail": "...", ...}  (maps to AppCard)
        """
        result = FormatterResult(success=True)

        try:
            # 1. Parse intent
            intent = self._parse_intent(input_data)
            result.intent = intent.value

            # 2. Generate component based on intent
            if intent == IntentType.REPLY:
                component = self._handle_reply(input_data)
            elif intent == IntentType.CODE:
                component = self._handle_code(input_data)
            elif intent == IntentType.FORM:
                component = self._handle_form(input_data)
            elif intent == IntentType.CONFIRM:
                component = self._handle_confirm(input_data)
            elif intent == IntentType.SELECT:
                component = self._handle_select(input_data)
            elif intent == IntentType.ALERT:
                component = self._handle_alert(input_data, "info")
            elif intent == IntentType.WARN:
                component = self._handle_alert(input_data, "warning")
            elif intent == IntentType.ERROR:
                component = self._handle_alert(input_data, "error")
            elif intent == IntentType.SUCCESS:
                component = self._handle_alert(input_data, "success")
            elif intent == IntentType.PROGRESS:
                component = self._handle_progress(input_data)
            elif intent == IntentType.MEDIA:
                component = self._handle_media(input_data)
            elif intent == IntentType.DATA:
                component = self._handle_data(input_data)
            elif intent == IntentType.APP:
                component = self._handle_app(input_data)
            else:
                # Unknown intent, treat as text
                content = input_data.get("content", str(input_data))
                component = {"type": "Markdown", "props": {"content": content}}

            # 3. Build tree
            tree = self._build_tree(component, intent)

            # 4. Validate + Fallback
            if self.config.enable_fallback:
                validation_result, final_tree = validate_with_fallback(tree)
                if validation_result.warnings:
                    result.warnings.extend([w.message for w in validation_result.warnings])
                    result.fallback_applied = True
                tree = final_tree
            else:
                validation_result = self.validator.validate_tree(tree)
                if not validation_result.is_valid:
                    if self.config.strict_validation:
                        result.success = False
                        result.errors.extend([e.message for e in validation_result.errors])
                        return result

            result.tree = tree

        except Exception as e:
            result.success = False
            result.errors.append(f"Formatting failed: {str(e)}")

        return result

    def format_json(self, input_json: str) -> str:
        """Format from JSON string"""
        try:
            input_data = json.loads(input_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "errors": [f"JSON parse error: {str(e)}"]
            }, ensure_ascii=False, indent=2)

        result = self.format(input_data)

        output = {
            "success": result.success,
            "intent": result.intent,
            "tree": result.tree,
            "errors": result.errors,
            "warnings": result.warnings
        }

        if result.fallback_applied:
            output["fallback_applied"] = True

        return json.dumps(output, ensure_ascii=False, indent=2)


# ========== Convenience Functions ==========

def format_output(input_data: Dict[str, Any], **config_kwargs) -> FormatterResult:
    config = FormatterConfig(**config_kwargs)
    return UIFormatter(config).format(input_data)


def format_reply(content: str) -> FormatterResult:
    return format_output({"intent": "reply", "content": content})


def format_code(code: str, language: str = "text") -> FormatterResult:
    return format_output({"intent": "code", "code": code, "language": language})


def format_form(fields: List[Dict], actions: List[Dict] = None) -> FormatterResult:
    return format_output({"intent": "form", "fields": fields, "actions": actions})


def format_confirm(title: str, description: str = "", actions: List[Dict] = None) -> FormatterResult:
    return format_output({"intent": "confirm", "title": title, "description": description, "actions": actions})


def format_select(question: str, options: List[Dict], multiple: bool = False) -> FormatterResult:
    return format_output({"intent": "select", "question": question, "options": options, "multiple": multiple})


def format_alert(message: str, alert_type: str = "info") -> FormatterResult:
    return format_output({"intent": alert_type, "message": message})


# ========== CLI Entry Point ==========

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Output Formatter v0.8.0")
    parser.add_argument("input", nargs="?", help="Input JSON file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--strict", action="store_true", help="Strict mode")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback")

    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_json = f.read()
    else:
        input_json = sys.stdin.read()

    config = FormatterConfig(
        enable_fallback=not args.no_fallback,
        strict_validation=args.strict
    )

    result = UIFormatter(config).format_json(input_json)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        print(result)


if __name__ == "__main__":
    print("=" * 50)
    print("Test Output Formatter v0.8.0")
    print("=" * 50)

    formatter = UIFormatter()

    # Test 1: Text reply
    print("\n[1] Text reply:")
    result = formatter.format({"intent": "reply", "content": "This is a **Markdown** reply"})
    print(f"Success: {result.success}, Root component: {result.tree['elements'][result.tree['root']]['type']}")

    # Test 2: Code
    print("\n[2] Code reply:")
    result = formatter.format({"intent": "code", "code": "print('hello')", "language": "python"})
    print(f"Success: {result.success}")

    # Test 3: Form (inline fields)
    print("\n[3] Form (Form.fields):")
    result = formatter.format({
        "intent": "form",
        "title": "User Login",
        "fields": [
            {"name": "email", "type": "email", "label": "Email", "required": True},
            {"name": "password", "type": "password", "label": "Password"}
        ],
        "actions": [{"label": "Login", "type": "submit"}]
    })
    form_props = result.tree['elements'][result.tree['root']]['props']
    print(f"Success: {result.success}, fields count: {len(form_props.get('fields', []))}")

    # Test 4: Selection
    print("\n[4] Selection:")
    result = formatter.format({
        "intent": "select",
        "question": "Choose a color",
        "options": [{"value": "red", "label": "Red"}, {"value": "blue", "label": "Blue"}]
    })
    form_props = result.tree['elements'][result.tree['root']]['props']
    print(f"Success: {result.success}, type: {form_props['fields'][0]['type']}")

    # Test 5: Confirmation
    print("\n[5] Confirmation:")
    result = formatter.format({
        "intent": "confirm",
        "title": "Delete Confirmation",
        "description": "Are you sure you want to delete?"
    })
    print(f"Success: {result.success}, Component: {result.tree['elements'][result.tree['root']]['type']}")

    # Test 6: Alert
    print("\n[6] Warning alert:")
    result = formatter.format({"intent": "warn", "message": "Insufficient balance"})
    print(f"Success: {result.success}, Alert type: {result.tree['elements'][result.tree['root']]['props']['type']}")

    print("\n" + "=" * 50)
    print("Tests complete")
