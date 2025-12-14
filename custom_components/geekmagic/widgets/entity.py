"""Entity widget for GeekMagic displays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import (
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_PANEL,
    COLOR_WHITE,
    PLACEHOLDER_NAME,
    PLACEHOLDER_VALUE,
)
from .base import Widget, WidgetConfig
from .component_helpers import CenteredValue, IconValue
from .components import Component, Panel
from .helpers import (
    estimate_max_chars,
    format_value_with_unit,
    get_entity_icon,
    get_unit,
    resolve_label,
    truncate_text,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..render_context import RenderContext


class EntityWidget(Widget):
    """Widget that displays a Home Assistant entity state."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the entity widget."""
        super().__init__(config)
        self.show_name = config.options.get("show_name", True)
        self.show_unit = config.options.get("show_unit", True)
        self.show_icon = config.options.get("show_icon", True)
        self.icon = config.options.get("icon")  # Explicit icon override
        self.show_panel = config.options.get("show_panel", False)

    def render(
        self,
        ctx: RenderContext,
        hass: HomeAssistant | None = None,
    ) -> Component:
        """Render the entity widget.

        Args:
            ctx: RenderContext for drawing
            hass: Home Assistant instance

        Returns:
            Component tree for rendering
        """
        # Get entity state
        state = self.get_entity_state(hass)

        if state is None:
            value = PLACEHOLDER_VALUE
            unit = ""
            name = self.config.label or self.config.entity_id or PLACEHOLDER_NAME
        else:
            value = state.state
            unit = get_unit(state) if self.show_unit else ""
            name = resolve_label(self.config, state, state.entity_id)

        # Truncate value and name - use generous estimates to avoid over-truncation
        # Values can be longer text (e.g., "Team Meeting"), labels use smaller font
        max_value_chars = estimate_max_chars(ctx.width, char_width=6, padding=6)
        max_name_chars = estimate_max_chars(ctx.width, char_width=5, padding=4)
        value = truncate_text(value, max_value_chars)
        name = truncate_text(name, max_name_chars)

        color = self.config.color or COLOR_CYAN
        value_text = format_value_with_unit(value, unit)
        label = name if self.show_name else None

        # Determine icon to use (priority: explicit config > entity icon > none)
        icon = self.icon
        if not icon and self.show_icon:
            # Try to get icon from HA entity (e.g., "mdi:thermometer")
            icon = get_entity_icon(state)

        # Build component based on whether we have an icon
        if icon:
            content = IconValue(
                icon=icon,
                value=value_text,
                label=label or "",
                color=color,
                value_color=COLOR_WHITE,
                label_color=COLOR_GRAY,
            )
        else:
            content = CenteredValue(
                value=value_text,
                label=label,
                value_color=color,
                label_color=COLOR_GRAY,
            )

        # Wrap in panel if enabled
        if self.show_panel:
            return Panel(child=content, color=COLOR_PANEL)

        return content
