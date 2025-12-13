"""Entity widget for GeekMagic displays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import COLOR_CYAN, COLOR_GRAY, COLOR_PANEL, COLOR_WHITE
from .base import Widget, WidgetConfig

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from PIL import ImageDraw

    from ..renderer import Renderer


class EntityWidget(Widget):
    """Widget that displays a Home Assistant entity state."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the entity widget."""
        super().__init__(config)
        self.show_name = config.options.get("show_name", True)
        self.show_unit = config.options.get("show_unit", True)
        self.icon = config.options.get("icon")
        self.show_panel = config.options.get("show_panel", False)

    def render(
        self,
        renderer: Renderer,
        draw: ImageDraw.ImageDraw,
        rect: tuple[int, int, int, int],
        hass: HomeAssistant | None = None,
    ) -> None:
        """Render the entity widget.

        Args:
            renderer: Renderer instance
            draw: ImageDraw instance
            rect: (x1, y1, x2, y2) bounding box
            hass: Home Assistant instance
        """
        x1, y1, x2, y2 = rect
        width = x2 - x1

        # Draw panel background if enabled
        if self.show_panel:
            renderer.draw_panel(draw, rect, COLOR_PANEL, radius=4)

        # Get entity state
        state = self.get_entity_state(hass)

        if state is None:
            # No entity or no hass - show placeholder
            value = "--"
            unit = ""
            name = self.config.label or self.config.entity_id or "Unknown"
        else:
            value = state.state
            unit = state.attributes.get("unit_of_measurement", "") if self.show_unit else ""
            name = self.config.label or state.attributes.get("friendly_name", state.entity_id)

        # Truncate value if too long
        max_value_len = (width - 20) // 10
        if len(value) > max_value_len:
            value = value[: max_value_len - 2] + ".."

        # Truncate name if too long
        max_name_len = (width - 10) // 7
        if len(name) > max_name_len:
            name = name[: max_name_len - 2] + ".."

        color = self.config.color or COLOR_CYAN

        # Layout depends on whether we have an icon
        if self.icon:
            self._render_with_icon(renderer, draw, rect, value, unit, name, color)
        else:
            self._render_centered(renderer, draw, rect, value, unit, name, color)

    def _render_centered(
        self,
        renderer: Renderer,
        draw: ImageDraw.ImageDraw,
        rect: tuple[int, int, int, int],
        value: str,
        unit: str,
        name: str,
        color: tuple[int, int, int],
    ) -> None:
        """Render with value centered and name below."""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        center_x = x1 + width // 2
        center_y = y1 + height // 2

        # Calculate positions
        value_y = center_y if not self.show_name else center_y - 8
        name_y = y2 - 12

        # Draw value
        value_text = f"{value}{unit}" if unit else value
        renderer.draw_text(
            draw,
            value_text,
            (center_x, value_y),
            font=renderer.font_large,
            color=color,
            anchor="mm",
        )

        # Draw name
        if self.show_name:
            renderer.draw_text(
                draw,
                name.upper(),
                (center_x, name_y),
                font=renderer.font_tiny,
                color=COLOR_GRAY,
                anchor="mm",
            )

    def _render_with_icon(
        self,
        renderer: Renderer,
        draw: ImageDraw.ImageDraw,
        rect: tuple[int, int, int, int],
        value: str,
        unit: str,
        name: str,
        color: tuple[int, int, int],
    ) -> None:
        """Render with icon on top, value below, name at bottom."""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        center_x = x1 + width // 2
        padding = 6

        # Layout: icon at top, value in middle, name at bottom
        icon_size = min(24, height // 3)

        # Draw icon (self.icon is guaranteed to be set when this method is called)
        assert self.icon is not None
        renderer.draw_icon(
            draw,
            self.icon,
            (center_x - icon_size // 2, y1 + padding),
            size=icon_size,
            color=color,
        )

        # Draw value
        value_text = f"{value}{unit}" if unit else value
        value_y = y1 + height // 2 + 5
        renderer.draw_text(
            draw,
            value_text,
            (center_x, value_y),
            font=renderer.font_medium_bold
            if hasattr(renderer, "font_medium_bold")
            else renderer.font_regular,
            color=COLOR_WHITE,
            anchor="mm",
        )

        # Draw name
        if self.show_name:
            renderer.draw_text(
                draw,
                name.upper(),
                (center_x, y2 - 10),
                font=renderer.font_tiny,
                color=COLOR_GRAY,
                anchor="mm",
            )
