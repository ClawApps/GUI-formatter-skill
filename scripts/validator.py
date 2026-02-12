"""
UI Validator v0.8.0 - Schema Validator

Three-layer validation:
1. Schema layer - Component type whitelist (12 types)
2. Field layer - Property type and value validation
3. Tree structure layer - Reference integrity and cycle detection

Supports all 12 component types, 3-round validation retry + Markdown fallback.
"""

import re
import json
from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass, field
from enum import Enum
from catalog import get_catalog, FormFieldType


# ==================== Validation Rule Definitions ====================

class ValidationType(str, Enum):
    """Built-in validator types (11)"""
    REQUIRED = "required"
    EMAIL = "email"
    MIN_LENGTH = "minLength"
    MAX_LENGTH = "maxLength"
    PATTERN = "pattern"
    MIN = "min"
    MAX = "max"
    NUMERIC = "numeric"
    URL = "url"
    MATCHES = "matches"
    CUSTOM = "custom"


@dataclass
class ValidationError:
    """Validation error"""
    path: str
    message: str
    error_type: str = "error"


@dataclass
class ValidationResult:
    """Validation result"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    attempt: int = 1  # Current validation round

    def add_error(self, path: str, message: str):
        self.errors.append(ValidationError(path=path, message=message))
        self.is_valid = False

    def add_warning(self, path: str, message: str):
        self.warnings.append(ValidationError(path=path, message=message, error_type="warning"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "attempt": self.attempt,
            "errors": [{"path": e.path, "message": e.message} for e in self.errors],
            "warnings": [{"path": w.path, "message": w.message} for w in self.warnings]
        }


# ==================== Validator Class ====================

class UIValidator:
    """
    UI Validator v0.8.0

    Supports 3-round validation retry, falls back to Markdown on failure
    """

    MAX_ATTEMPTS = 3  # Maximum validation rounds

    def __init__(self):
        self.catalog = get_catalog()

    def validate_tree(self, tree_data: Dict[str, Any], attempt: int = 1) -> ValidationResult:
        """Validate entire UI tree"""
        result = ValidationResult(is_valid=True, attempt=attempt)

        # Basic structure check
        if "root" not in tree_data:
            result.add_error("root", "Missing root element ID")
            return result

        if "elements" not in tree_data:
            result.add_error("elements", "Missing elements dictionary")
            return result

        elements = tree_data.get("elements", {})
        root_id = tree_data.get("root")

        if root_id not in elements:
            result.add_error("root", f"Root element '{root_id}' not found")
            return result

        # Validate each element
        for elem_id, elem_data in elements.items():
            self._validate_element(elem_data, f"elements.{elem_id}", elements, result)

        # Validate child reference integrity
        all_ids = set(elements.keys())
        for elem_id, elem_data in elements.items():
            for child_id in elem_data.get("children", []):
                if child_id not in all_ids:
                    result.add_error(f"elements.{elem_id}.children", f"References non-existent child: {child_id}")

        # Detect circular references
        self._detect_cycles(root_id, elements, result)

        # Detect orphan elements
        self._detect_orphans(root_id, elements, result)

        return result

    def _validate_element(self, element: Dict[str, Any], path: str,
                          elements: Dict[str, Any], result: ValidationResult):
        """Validate a single element"""
        elem_type = element.get("type")

        if not elem_type:
            result.add_error(f"{path}.type", "Missing component type")
            return

        if not self.catalog.is_valid_type(elem_type):
            result.add_error(f"{path}.type",
                f"Unknown component type: {elem_type}, valid types: {', '.join(self.catalog.get_all_types())}")
            return

        # Validate props
        schema = self.catalog.get(elem_type)
        props = element.get("props", {})

        # Check required properties
        for required_prop in schema.required_props:
            if required_prop not in props:
                result.add_error(f"{path}.props.{required_prop}", f"Missing required property: {required_prop}")

        # Validate children
        if element.get("children") and not schema.supports_children:
            result.add_warning(f"{path}.children", f"Component {elem_type} does not support children")

        # Form-specific validation
        if elem_type == "Form":
            self._validate_form_fields(props, path, result)

    def _validate_form_fields(self, props: Dict[str, Any], path: str, result: ValidationResult):
        """Validate Form.fields inline field definitions"""
        fields = props.get("fields", [])
        field_names = set()

        for i, field_def in enumerate(fields):
            field_path = f"{path}.props.fields[{i}]"

            # Check name
            name = field_def.get("name")
            if not name:
                result.add_error(f"{field_path}.name", "Field must specify a name")
            elif name in field_names:
                result.add_error(f"{field_path}.name", f"Duplicate field name: {name}")
            else:
                field_names.add(name)

            # Check type
            field_type = field_def.get("type", "text")
            if not self.catalog.is_valid_field_type(field_type):
                result.add_error(f"{field_path}.type",
                    f"Invalid type: {field_type}, valid values: {', '.join(self.catalog.get_field_type_values())}")

            # Validate select/radio must have options
            if field_type in ["select", "radio"]:
                if not field_def.get("options"):
                    result.add_error(f"{field_path}.options", f"type={field_type} requires options")

            # Validate slider min/max
            if field_type == "slider":
                min_val = field_def.get("min")
                max_val = field_def.get("max")
                if min_val is not None and max_val is not None and min_val >= max_val:
                    result.add_error(f"{field_path}", "Slider min must be less than max")

    def _detect_cycles(self, root_id: str, elements: Dict[str, Any], result: ValidationResult):
        """Detect circular references"""
        visited = set()
        path_stack = []

        def has_cycle(elem_id: str) -> bool:
            if elem_id in path_stack:
                cycle = " -> ".join(path_stack[path_stack.index(elem_id):] + [elem_id])
                result.add_error("tree", f"Circular reference: {cycle}")
                return True
            if elem_id in visited or elem_id not in elements:
                return False

            visited.add(elem_id)
            path_stack.append(elem_id)

            for child_id in elements[elem_id].get("children", []):
                if has_cycle(child_id):
                    return True

            path_stack.pop()
            return False

        has_cycle(root_id)

    def _detect_orphans(self, root_id: str, elements: Dict[str, Any], result: ValidationResult):
        """Detect orphan elements"""
        reachable = set()

        def mark_reachable(elem_id: str):
            if elem_id in reachable or elem_id not in elements:
                return
            reachable.add(elem_id)
            for child_id in elements[elem_id].get("children", []):
                mark_reachable(child_id)

        mark_reachable(root_id)

        for orphan_id in set(elements.keys()) - reachable:
            result.add_warning(f"elements.{orphan_id}", "Orphan element, unreachable from root")

    def validate_with_retry(self, tree_data: Dict[str, Any],
                            fix_callback=None) -> tuple[ValidationResult, Dict[str, Any]]:
        """
        Validation with retry

        Args:
            tree_data: UI tree to validate
            fix_callback: Fix callback function (errors) -> fixed_tree_data

        Returns:
            (ValidationResult, final_tree_data)
            - Validation passed: returns original or fixed tree
            - 3 rounds failed: returns Markdown fallback
        """
        current_data = tree_data

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            result = self.validate_tree(current_data, attempt)

            if result.is_valid:
                return result, current_data

            # Last round still failed, fallback to Markdown
            if attempt == self.MAX_ATTEMPTS:
                fallback_tree = self._create_markdown_fallback(current_data, result)
                fallback_result = ValidationResult(is_valid=True, attempt=attempt)
                fallback_result.add_warning("fallback",
                    f"Validation failed after {self.MAX_ATTEMPTS} rounds, degraded to Markdown output")
                return fallback_result, fallback_tree

            # Attempt fix
            if fix_callback:
                current_data = fix_callback(result.errors, current_data)

        # Should not reach here
        return result, current_data

    def _create_markdown_fallback(self, tree_data: Dict[str, Any],
                                   result: ValidationResult) -> Dict[str, Any]:
        """Create Markdown fallback output"""
        # Try to extract useful content from original data
        content_parts = []

        elements = tree_data.get("elements", {})
        for elem_id, elem in elements.items():
            props = elem.get("props", {})

            # Extract text content
            if props.get("content"):
                content_parts.append(props["content"])
            if props.get("title"):
                content_parts.append(f"## {props['title']}")
            if props.get("message"):
                content_parts.append(props["message"])
            if props.get("description"):
                content_parts.append(props["description"])

        # Add validation error info
        if result.errors:
            content_parts.append("\n---\n**Validation errors:**")
            for err in result.errors[:5]:  # Show at most 5 errors
                content_parts.append(f"- {err.message}")

        fallback_content = "\n\n".join(content_parts) if content_parts else "Content generation failed"

        return {
            "root": "fallback_md",
            "elements": {
                "fallback_md": {
                    "id": "fallback_md",
                    "type": "Markdown",
                    "props": {"content": fallback_content}
                }
            },
            "metadata": {
                "version": "v0.8.0",
                "validation_status": "warning",
                "warnings": ["Validation failed, degraded to Markdown output"],
                "original_errors": [e.message for e in result.errors]
            }
        }


# ==================== Convenience Functions ====================

_validator: Optional[UIValidator] = None


def get_validator() -> UIValidator:
    global _validator
    if _validator is None:
        _validator = UIValidator()
    return _validator


def validate(tree_data: Dict[str, Any]) -> ValidationResult:
    """Quick validation function"""
    return get_validator().validate_tree(tree_data)


def validate_with_fallback(tree_data: Dict[str, Any]) -> tuple[ValidationResult, Dict[str, Any]]:
    """Validation with fallback"""
    return get_validator().validate_with_retry(tree_data)


if __name__ == "__main__":
    validator = get_validator()

    # Test valid tree
    print("=" * 50)
    print("Test valid Form component")
    print("=" * 50)

    valid_tree = {
        "root": "form_0",
        "elements": {
            "form_0": {
                "id": "form_0",
                "type": "Form",
                "props": {
                    "title": "User Login",
                    "fields": [
                        {"name": "email", "type": "email", "label": "Email", "required": True},
                        {"name": "password", "type": "password", "label": "Password"}
                    ],
                    "actions": [{"label": "Login", "type": "submit", "variant": "primary"}]
                }
            }
        }
    }

    result = validator.validate_tree(valid_tree)
    print(f"Result: valid={result.is_valid}")

    # Test invalid component type
    print("\n" + "=" * 50)
    print("Test invalid component type (should fallback)")
    print("=" * 50)

    invalid_tree = {
        "root": "widget_0",
        "elements": {
            "widget_0": {
                "id": "widget_0",
                "type": "CustomWidget",  # Invalid type
                "props": {"title": "Test"}
            }
        }
    }

    result, final_tree = validator.validate_with_retry(invalid_tree)
    print(f"Result: valid={result.is_valid}")
    print(f"Final output type: {final_tree['elements'][final_tree['root']]['type']}")
    if result.warnings:
        print(f"Warnings: {[w.message for w in result.warnings]}")
