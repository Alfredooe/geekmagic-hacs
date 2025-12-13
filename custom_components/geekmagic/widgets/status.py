"""Status widget for GeekMagic displays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import COLOR_GRAY, COLOR_LIME, COLOR_RED, COLOR_WHITE, PLACEHOLDER_NAME
from .base import Widget, WidgetConfig
from .helpers import estimate_max_chars, is_entity_on, resolve_label, truncate_text

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..render_context import RenderContext


class StatusWidget(Widget):
    """Widget that displays a binary sensor status with colored indicator."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the status widget."""
        super().__init__(config)
        self.on_color = config.options.get("on_color", COLOR_LIME)
        self.off_color = config.options.get("off_color", COLOR_RED)
        self.on_text = config.options.get("on_text", "ON")
        self.off_text = config.options.get("off_text", "OFF")
        self.icon = config.options.get("icon")
        self.show_status_text = config.options.get("show_status_text", True)

    def render(
        self,
        ctx: RenderContext,
        hass: HomeAssistant | None = None,
    ) -> None:
        """Render the status widget.

        Args:
            ctx: RenderContext for drawing
            hass: Home Assistant instance
        """
        center_y = ctx.height // 2

        # Get scaled fonts
        font_name = ctx.get_font("small")
        font_status = ctx.get_font("small")

        # Calculate relative padding and sizes
        padding = int(ctx.width * 0.06)
        dot_radius = max(3, int(ctx.height * 0.12))
        # Icon at 20% of height, capped at 20px to prevent dominating small cells
        icon_size = max(10, min(20, int(ctx.height * 0.20)))

        # Get entity state
        state = self.get_entity_state(hass)

        # Determine if on or off using helper
        is_on = is_entity_on(state)

        # Get color and text
        color = self.on_color if is_on else self.off_color
        status_text = self.on_text if is_on else self.off_text

        # Get label using helpers
        name = resolve_label(self.config, state, PLACEHOLDER_NAME)
        if not name and state:
            name = state.entity_id
        name = name or PLACEHOLDER_NAME

        # Truncate name using consistent helper
        max_name_len = estimate_max_chars(ctx.width, char_width=7, padding=20)
        name = truncate_text(name, max_name_len)

        # Draw status indicator (dot)
        dot_x = padding + dot_radius
        dot_y = center_y

        ctx.draw_ellipse(
            rect=(dot_x - dot_radius, dot_y - dot_radius, dot_x + dot_radius, dot_y + dot_radius),
            fill=color,
        )

        # Draw icon if present
        text_x = dot_x + dot_radius + int(ctx.width * 0.06)
        if self.icon:
            ctx.draw_icon(
                self.icon,
                (text_x, center_y - icon_size // 2),
                size=icon_size,
                color=COLOR_GRAY,
            )
            text_x += icon_size + 4

        # Draw name
        ctx.draw_text(
            name,
            (text_x, center_y),
            font=font_name,
            color=COLOR_WHITE,
            anchor="lm",
        )

        # Draw status text
        if self.show_status_text:
            ctx.draw_text(
                status_text,
                (ctx.width - padding, center_y),
                font=font_status,
                color=color,
                anchor="rm",
            )


class StatusListWidget(Widget):
    """Widget that displays a list of binary sensors with status indicators."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the status list widget."""
        super().__init__(config)
        # List of (entity_id, label) tuples
        self.entities = config.options.get("entities", [])
        self.on_color = config.options.get("on_color", COLOR_LIME)
        self.off_color = config.options.get("off_color", COLOR_RED)
        self.on_text = config.options.get("on_text")
        self.off_text = config.options.get("off_text")
        self.title = config.options.get("title")

    def get_entities(self) -> list[str]:
        """Return list of entity IDs this widget depends on."""
        return [e[0] if isinstance(e, list | tuple) else e for e in self.entities]

    def render(
        self,
        ctx: RenderContext,
        hass: HomeAssistant | None = None,
    ) -> None:
        """Render the status list widget.

        Args:
            ctx: RenderContext for drawing
            hass: Home Assistant instance
        """
        # Get scaled fonts
        font_title = ctx.get_font("small")
        font_label = ctx.get_font("tiny")

        # Calculate relative padding
        padding = int(ctx.width * 0.05)
        current_y = padding

        # Draw title if present
        if self.title:
            ctx.draw_text(
                self.title.upper(),
                (padding, current_y),
                font=font_title,
                color=COLOR_GRAY,
                anchor="lm",
            )
            title_height = int(ctx.height * 0.15)
            current_y += title_height

        # Calculate row height relative to container
        available_height = ctx.height - current_y - padding
        row_count = len(self.entities) or 1
        row_height = min(int(ctx.height * 0.17), available_height // row_count)
        dot_radius = max(2, int(ctx.height * 0.025))

        # Calculate max label length once
        max_len = estimate_max_chars(ctx.width, char_width=7, padding=30)

        # Draw each entity
        for entry in self.entities:
            if isinstance(entry, list | tuple):
                entity_id, label = entry[0], entry[1]
            else:
                entity_id = entry
                label = None

            # Get state
            state = hass.states.get(entity_id) if hass else None

            # Use helper for state checking
            is_on = is_entity_on(state)
            if state is not None and not label:
                label = state.attributes.get("friendly_name", entity_id)
            label = label or entity_id

            # Get color
            color = self.on_color if is_on else self.off_color

            # Truncate label using helper
            label = truncate_text(label, max_len)

            # Draw dot
            dot_y = current_y + row_height // 2
            ctx.draw_ellipse(
                rect=(
                    padding,
                    dot_y - dot_radius,
                    padding + dot_radius * 2,
                    dot_y + dot_radius,
                ),
                fill=color,
            )

            # Draw label
            ctx.draw_text(
                label,
                (padding + dot_radius * 2 + 6, dot_y),
                font=font_label,
                color=COLOR_WHITE,
                anchor="lm",
            )

            # Draw status text
            if self.on_text or self.off_text:
                status_text = self.on_text if is_on else self.off_text
                if status_text:
                    ctx.draw_text(
                        status_text,
                        (ctx.width - padding, dot_y),
                        font=font_label,
                        color=color,
                        anchor="rm",
                    )

            current_y += row_height
