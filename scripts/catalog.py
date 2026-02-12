"""
UI Component Catalog v0.8.0 - Component Registry

Defines all supported UI component types and their schemas, implementing a whitelist validation mechanism.

v0.8.0 component list (12):
- Display: Markdown, Collapse
- Card: AppCard
- Form: Form (contains fields + actions)
- Media: VideoPlayer, AudioPlayer, ImageGallery
- Feedback: Alert, Progress
- Layout: Card, Modal
- Embed: WebView
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum


class ComponentCategory(Enum):
    """Component categories"""
    DISPLAY = "display"     # Display components
    CARD = "card"           # Card components (AppCard)
    FORM = "form"           # Form components
    MEDIA = "media"         # Media components
    FEEDBACK = "feedback"   # Feedback components
    LAYOUT = "layout"       # Layout components
    EMBED = "embed"         # Embed components


class FormFieldType(Enum):
    """Form field types (12)"""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEXTAREA = "textarea"
    SELECT = "select"
    DATE = "date"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SWITCH = "switch"
    SLIDER = "slider"
    FILE = "file"


@dataclass
class ComponentSchema:
    """Component schema definition"""
    type: str
    category: ComponentCategory
    required_props: List[str] = field(default_factory=list)
    optional_props: Dict[str, Any] = field(default_factory=dict)
    supports_children: bool = False
    supports_actions: bool = False
    description: str = ""


class ComponentCatalog:
    """
    Component Catalog v0.8.0 - Whitelist Registry

    v0.8.0 component architecture (12):
    ─────────────────────────────────────────
    Display  (2): Markdown, Collapse
    Card     (1): AppCard
    Form     (1): Form (contains fields + actions)
    Media    (3): VideoPlayer, AudioPlayer, ImageGallery
    Feedback (2): Alert, Progress
    Layout   (2): Card, Modal
    Embed    (1): WebView
    """

    _instance: Optional['ComponentCatalog'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._registry: Dict[str, ComponentSchema] = {}
        self._register_builtin_components()
        self._initialized = True

    def _register_builtin_components(self):
        """Register built-in components (v0.8.0 - 12 components)"""

        # ========== Display Components (2) ==========
        self.register(ComponentSchema(
            type="Markdown",
            category=ComponentCategory.DISPLAY,
            required_props=[],
            optional_props={
                "content": "",
                "allowHtml": False,
                "codeOptions": {"copyable": True, "showLineNumbers": True, "highlightLines": []},
                "imageOptions": {"clickAction": "lightbox", "maxWidth": "100%"}
            },
            description="Markdown rich text rendering, supports tables, code blocks, images"
        ))

        self.register(ComponentSchema(
            type="Collapse",
            category=ComponentCategory.DISPLAY,
            required_props=[],
            optional_props={
                "items": [],  # CollapseItem[]
                "accordion": False,
                "bordered": True,
                "gap": 0
            },
            description="Collapsible panels, supports expand/collapse content"
        ))

        # ========== Card Components (1) ==========
        self.register(ComponentSchema(
            type="AppCard",
            category=ComponentCategory.CARD,
            required_props=["id", "title"],
            optional_props={
                "id": "",
                "title": "",
                "url": "",
                "description": "",
                "avatar": "",
                "thumbnail": "",
                "author_name": "",
                "type": "",
                "view_count": 0,
                "like_count": 0
            },
            description="App/work display card"
        ))

        # ========== Form Components (1) ==========
        self.register(ComponentSchema(
            type="Form",
            category=ComponentCategory.FORM,
            required_props=[],
            optional_props={
                "title": "",
                "description": "",
                "layout": "vertical",  # vertical | horizontal | inline
                "labelWidth": 100,
                "columns": 1,
                "gap": 16,
                "fields": [],  # FormFieldDef[]
                "actions": [],  # FormAction[]
                "actionsAlign": "right",
                "submitAction": None,  # ActionSchema
                "validateOnChange": True,
                "validateOnBlur": True
            },
            supports_actions=True,
            description="Form container with inline fields + actions"
        ))

        # ========== Media Components (3) ==========
        self.register(ComponentSchema(
            type="VideoPlayer",
            category=ComponentCategory.MEDIA,
            required_props=[],
            optional_props={
                "src": "",
                "poster": "",
                "title": "",
                "controls": True,
                "autoplay": False,
                "muted": False,
                "loop": False,
                "width": "100%",
                "height": None
            },
            description="Video player"
        ))

        self.register(ComponentSchema(
            type="AudioPlayer",
            category=ComponentCategory.MEDIA,
            required_props=[],
            optional_props={
                "src": "",
                "title": "",
                "controls": True,
                "autoplay": False,
                "loop": False
            },
            description="Audio player"
        ))

        self.register(ComponentSchema(
            type="ImageGallery",
            category=ComponentCategory.MEDIA,
            required_props=[],
            optional_props={
                "images": [],  # [{src, alt, thumbnail, caption}]
                "layout": "grid",  # grid | carousel
                "columns": 3,
                "gap": 8,
                "enableLightbox": True
            },
            description="Image gallery"
        ))

        # ========== Feedback Components (2) ==========
        self.register(ComponentSchema(
            type="Alert",
            category=ComponentCategory.FEEDBACK,
            required_props=[],
            optional_props={
                "type": "info",  # info | success | warning | error
                "message": "",
                "description": "",
                "showIcon": True,
                "closable": False,
                "actions": []  # ActionButton[]
            },
            supports_actions=True,
            description="Alert notification"
        ))

        self.register(ComponentSchema(
            type="Progress",
            category=ComponentCategory.FEEDBACK,
            required_props=[],
            optional_props={
                "value": 0,
                "max": 100,
                "type": "linear",  # linear | circle
                "label": "",
                "showValue": True,
                "size": None,
                "status": "normal"  # normal | success | error
            },
            description="Progress bar"
        ))

        # ========== Layout Components (2) ==========
        self.register(ComponentSchema(
            type="Card",
            category=ComponentCategory.LAYOUT,
            required_props=[],
            optional_props={
                "title": "",
                "subtitle": "",
                "content": "",
                "image": None,  # string | ImageConfig
                "layout": "flex",  # flex | grid
                "direction": "column",  # row | column
                "gap": 16,
                "padding": 16,
                "align": "stretch",
                "justify": "start",
                "gridColumns": 3,
                "bordered": True,
                "hoverable": False,
                "shadow": "none",  # none | sm | md | lg
                "background": None,
                "borderRadius": 8,
                "actions": [],
                "actionsPosition": "bottom"  # bottom | right
            },
            supports_children=True,
            supports_actions=True,
            description="Unified layout container, supports flex/grid"
        ))

        self.register(ComponentSchema(
            type="Modal",
            category=ComponentCategory.LAYOUT,
            required_props=[],
            optional_props={
                "title": "",
                "mode": "modal",  # modal | drawer
                "placement": "right",  # drawer: left | right | top | bottom
                "width": 520,
                "height": None,
                "closable": True,
                "maskClosable": True,
                "footer": []  # ActionButton[]
            },
            supports_children=True,
            supports_actions=True,
            description="Modal dialog / Drawer"
        ))

        # ========== Embed Components (1) ==========
        self.register(ComponentSchema(
            type="WebView",
            category=ComponentCategory.EMBED,
            required_props=[],
            optional_props={
                "url": "",
                "html": "",
                "width": "100%",
                "height": 400,
                "sandbox": []
            },
            description="Web page embed (iframe)"
        ))

    def register(self, schema: ComponentSchema) -> None:
        self._registry[schema.type] = schema

    def get(self, component_type: str) -> Optional[ComponentSchema]:
        return self._registry.get(component_type)

    def is_valid_type(self, component_type: str) -> bool:
        return component_type in self._registry

    def get_all_types(self) -> Set[str]:
        return set(self._registry.keys())

    def get_types_by_category(self, category: ComponentCategory) -> List[str]:
        return [s.type for s in self._registry.values() if s.category == category]

    def get_default_props(self, component_type: str) -> Dict[str, Any]:
        schema = self.get(component_type)
        return schema.optional_props.copy() if schema else {}

    def get_required_props(self, component_type: str) -> List[str]:
        schema = self.get(component_type)
        return schema.required_props.copy() if schema else []

    def supports_children(self, component_type: str) -> bool:
        schema = self.get(component_type)
        return schema.supports_children if schema else False

    def supports_actions(self, component_type: str) -> bool:
        schema = self.get(component_type)
        return schema.supports_actions if schema else False

    def get_fallback_type(self, component_type: str) -> str:
        """Get fallback type for a component"""
        schema = self.get(component_type)
        if not schema:
            return "Card"
        fallback_map = {
            ComponentCategory.DISPLAY: "Markdown",
            ComponentCategory.CARD: "Card",
            ComponentCategory.FORM: "Form",
            ComponentCategory.MEDIA: "Card",
            ComponentCategory.FEEDBACK: "Card",
            ComponentCategory.LAYOUT: "Card",
            ComponentCategory.EMBED: "WebView"
        }
        return fallback_map.get(schema.category, "Card")

    def is_valid_field_type(self, field_type: str) -> bool:
        try:
            FormFieldType(field_type)
            return True
        except ValueError:
            return False

    def get_field_type_values(self) -> List[str]:
        return [ft.value for ft in FormFieldType]


# Global singleton
catalog = ComponentCatalog()


def get_catalog() -> ComponentCatalog:
    return catalog


if __name__ == "__main__":
    cat = get_catalog()
    print(f"v0.8.0 component count: {len(cat.get_all_types())}")
    print(f"\nComponent type list:")
    for category in ComponentCategory:
        types = cat.get_types_by_category(category)
        print(f"  {category.value}: {', '.join(types) if types else '(none)'}")
    print(f"\nValid field types: {cat.get_field_type_values()}")
