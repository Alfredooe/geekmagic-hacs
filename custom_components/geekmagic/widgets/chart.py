"""Chart widget for GeekMagic displays."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from ..const import COLOR_CYAN, COLOR_GRAY
from .base import Widget, WidgetConfig

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..render_context import RenderContext


class ChartWidget(Widget):
    """Widget that displays a sparkline chart or timeline bar from entity history.

    Automatically detects binary data (all 0.0/1.0 values) and displays
    as a timeline bar instead of a sparkline chart.
    """

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the chart widget."""
        super().__init__(config)
        self.hours = config.options.get("hours", 24)
        self.show_value = config.options.get("show_value", True)
        self.show_range = config.options.get("show_range", True)

        # History data cache (populated externally)
        self._history_data: list[float] = []

    def set_history(self, data: list[float]) -> None:
        """Set the history data for the chart.

        Args:
            data: List of numeric values
        """
        self._history_data = data

    def _is_binary_data(self) -> bool:
        """Check if history data is binary (all values are 0.0 or 1.0).

        Returns:
            True if data appears to be from a binary sensor
        """
        if not self._history_data:
            return False
        return all(v in {0.0, 1.0} for v in self._history_data)

    def render(
        self,
        ctx: RenderContext,
        hass: HomeAssistant | None = None,
    ) -> None:
        """Render the chart widget.

        Args:
            ctx: RenderContext for drawing
            hass: Home Assistant instance
        """
        # Get scaled fonts
        font_label = ctx.get_font("small")
        font_value = ctx.get_font("regular")

        # Calculate relative padding
        padding = int(ctx.width * 0.08)

        # Get current value from entity
        state = self.get_entity_state(hass)
        current_value = None
        unit = ""
        name = self.config.label or "Chart"

        if state is not None:
            with contextlib.suppress(ValueError, TypeError):
                current_value = float(state.state)
            unit = state.attributes.get("unit_of_measurement", "")
            name = self.config.label or state.attributes.get("friendly_name", "Chart")

        # Calculate chart area relative to container
        header_height = int(ctx.height * 0.15) if self.config.label else int(ctx.height * 0.08)
        footer_height = int(ctx.height * 0.12) if self.show_range else int(ctx.height * 0.04)
        chart_top = header_height
        chart_bottom = ctx.height - footer_height
        chart_rect = (padding, chart_top, ctx.width - padding, chart_bottom)

        # Draw header with label and value
        # Use horizontal layout (label left, value right) to prevent overlap
        header_y = int(ctx.height * 0.08)

        if self.config.label:
            # For small containers (<100px), truncate label
            max_label_len = max(3, ctx.width // 12)
            display_name = name.upper()
            if len(display_name) > max_label_len:
                display_name = display_name[: max_label_len - 2] + ".."

            ctx.draw_text(
                display_name,
                (padding, header_y),
                font=font_label,
                color=COLOR_GRAY,
                anchor="lm",  # Left-align to prevent overlap with value
            )

        # Draw current value (always right-aligned)
        if self.show_value and current_value is not None:
            value_str = f"{current_value:.1f}{unit}"
            ctx.draw_text(
                value_str,
                (ctx.width - padding, header_y),
                font=font_value,
                color=self.config.color or COLOR_CYAN,
                anchor="rm",
            )

        # Draw chart
        if self._history_data and len(self._history_data) >= 2:
            color = self.config.color or COLOR_CYAN
            is_binary = self._is_binary_data()

            if is_binary:
                # Binary data: use timeline bar visualization
                ctx.draw_timeline_bar(chart_rect, self._history_data, on_color=color)
                # No range footer for binary (would just be 0/1)
            else:
                # Numeric data: use sparkline chart
                ctx.draw_sparkline(chart_rect, self._history_data, color=color, fill=True)

                # Draw min/max range for numeric data
                if self.show_range:
                    min_val = min(self._history_data)
                    max_val = max(self._history_data)
                    range_y = chart_bottom + int(ctx.height * 0.08)

                    ctx.draw_text(
                        f"{min_val:.1f}",
                        (padding, range_y),
                        font=font_label,
                        color=COLOR_GRAY,
                        anchor="lm",
                    )
                    ctx.draw_text(
                        f"{max_val:.1f}",
                        (ctx.width - padding, range_y),
                        font=font_label,
                        color=COLOR_GRAY,
                        anchor="rm",
                    )
        else:
            # No data - show placeholder
            center_x = ctx.width // 2
            center_y = (chart_top + chart_bottom) // 2
            ctx.draw_text(
                "No data",
                (center_x, center_y),
                font=font_label,
                color=COLOR_GRAY,
                anchor="mm",
            )
