"""
Action Schema v0.8.0 - User Interaction Action Definitions

Defines 6 action types for handling form submissions, button clicks, and other user interactions.

Action types:
- api_call: Call an API
- navigate: Page navigation
- emit_event: Send event
- open_modal: Open modal/drawer
- close_modal: Close modal/drawer
- reset: Reset form
"""

from typing import Dict, Any, Optional, List, Literal
from enum import Enum
from dataclasses import dataclass, field


class ActionType(str, Enum):
    """Action types (6)"""
    API_CALL = "api_call"
    NAVIGATE = "navigate"
    EMIT_EVENT = "emit_event"
    OPEN_MODAL = "open_modal"
    CLOSE_MODAL = "close_modal"
    RESET = "reset"


class HttpMethod(str, Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class ApiConfig:
    """API call configuration"""
    endpoint: str
    method: str = "POST"
    bodyMapping: str = "auto"  # "auto" | {fieldName: targetKey}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "bodyMapping": self.bodyMapping
        }


@dataclass
class ConfirmConfig:
    """Confirmation dialog configuration"""
    title: str = "Confirm Action"
    message: str = "Are you sure you want to proceed?"
    type: str = "warning"  # info | warning | danger

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "type": self.type
        }


@dataclass
class FeedbackConfig:
    """User feedback configuration"""
    successText: str = "Operation successful"
    errorText: str = "Operation failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "successText": self.successText,
            "errorText": self.errorText
        }


@dataclass
class CallbackConfig:
    """Callback configuration"""
    onSuccess: List[Dict[str, Any]] = field(default_factory=list)
    onError: List[Dict[str, Any]] = field(default_factory=list)
    feedback: Optional[FeedbackConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.onSuccess:
            result["onSuccess"] = self.onSuccess
        if self.onError:
            result["onError"] = self.onError
        if self.feedback:
            result["feedback"] = self.feedback.to_dict()
        return result


@dataclass
class ActionSchema:
    """
    Action Schema v0.8.0

    Example:
    {
        "type": "api_call",
        "api": {"endpoint": "/api/users", "method": "POST", "bodyMapping": "auto"},
        "confirm": {"title": "Confirm", "message": "Are you sure?", "type": "warning"},
        "callbacks": {
            "onSuccess": [{"type": "navigate", "url": "/list"}],
            "feedback": {"successText": "Saved successfully"}
        }
    }
    """
    type: ActionType

    # api_call config
    api: Optional[ApiConfig] = None

    # navigate config
    url: Optional[str] = None
    target: str = "_self"  # _self | _blank

    # emit_event config
    event: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    # open_modal / close_modal config
    modalId: Optional[str] = None

    # Common config
    confirm: Optional[ConfirmConfig] = None
    callbacks: Optional[CallbackConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type.value}

        if self.type == ActionType.API_CALL and self.api:
            result["api"] = self.api.to_dict()

        if self.type == ActionType.NAVIGATE and self.url:
            result["url"] = self.url
            if self.target != "_self":
                result["target"] = self.target

        if self.type == ActionType.EMIT_EVENT:
            if self.event:
                result["event"] = self.event
            if self.payload:
                result["payload"] = self.payload

        if self.type in [ActionType.OPEN_MODAL, ActionType.CLOSE_MODAL] and self.modalId:
            result["modalId"] = self.modalId

        if self.confirm:
            result["confirm"] = self.confirm.to_dict()

        if self.callbacks:
            callbacks_dict = self.callbacks.to_dict()
            if callbacks_dict:
                result["callbacks"] = callbacks_dict

        return result


# ==================== Convenience Constructors ====================

def api_call(
    endpoint: str,
    method: str = "POST",
    success_redirect: Optional[str] = None,
    success_message: str = "Operation successful",
    confirm: Optional[ConfirmConfig] = None
) -> Dict[str, Any]:
    """Create API call action"""
    callbacks = None
    if success_redirect or success_message:
        on_success = []
        if success_redirect:
            on_success.append({"type": "navigate", "url": success_redirect})
        callbacks = CallbackConfig(
            onSuccess=on_success if on_success else None,
            feedback=FeedbackConfig(successText=success_message)
        )

    action = ActionSchema(
        type=ActionType.API_CALL,
        api=ApiConfig(endpoint=endpoint, method=method),
        confirm=confirm,
        callbacks=callbacks
    )
    return action.to_dict()


def navigate(url: str, target: str = "_self") -> Dict[str, Any]:
    """Create navigation action"""
    return ActionSchema(
        type=ActionType.NAVIGATE,
        url=url,
        target=target
    ).to_dict()


def emit_event(event: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create event emission action"""
    return ActionSchema(
        type=ActionType.EMIT_EVENT,
        event=event,
        payload=payload
    ).to_dict()


def open_modal(modal_id: str) -> Dict[str, Any]:
    """Create open modal action"""
    return ActionSchema(
        type=ActionType.OPEN_MODAL,
        modalId=modal_id
    ).to_dict()


def close_modal(modal_id: str) -> Dict[str, Any]:
    """Create close modal action"""
    return ActionSchema(
        type=ActionType.CLOSE_MODAL,
        modalId=modal_id
    ).to_dict()


def reset() -> Dict[str, Any]:
    """Create form reset action"""
    return ActionSchema(type=ActionType.RESET).to_dict()


def delete_with_confirm(
    endpoint: str,
    redirect: Optional[str] = None,
    message: str = "Are you sure you want to delete? This action cannot be undone."
) -> Dict[str, Any]:
    """Create delete action with confirmation"""
    return api_call(
        endpoint=endpoint,
        method="DELETE",
        success_redirect=redirect,
        success_message="Deleted successfully",
        confirm=ConfirmConfig(
            title="Confirm Delete",
            message=message,
            type="danger"
        )
    )


if __name__ == "__main__":
    import json

    print("=" * 50)
    print("Action Schema v0.8.0 Examples")
    print("=" * 50)

    print("\n[1] API call:")
    print(json.dumps(api_call("/api/users", success_redirect="/users"), indent=2, ensure_ascii=False))

    print("\n[2] Delete with confirmation:")
    print(json.dumps(delete_with_confirm("/api/users/{id}", "/users"), indent=2, ensure_ascii=False))

    print("\n[3] Navigate:")
    print(json.dumps(navigate("/dashboard"), indent=2, ensure_ascii=False))

    print("\n[4] Emit event:")
    print(json.dumps(emit_event("user_updated", {"id": 123}), indent=2, ensure_ascii=False))

    print("\n[5] Open modal:")
    print(json.dumps(open_modal("edit_modal"), indent=2, ensure_ascii=False))

    print("\n[6] Reset form:")
    print(json.dumps(reset(), indent=2, ensure_ascii=False))
