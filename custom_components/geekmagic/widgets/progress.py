"""Progress widget for GeekMagic displays."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from ..const import COLOR_CYAN, COLOR_DARK_GRAY, COLOR_GRAY, COLOR_WHITE
from .base import Widget, WidgetConfig
from .components import Color, Component
from .helpers import format_number

if TYPE_CHECKING:
    from ..render_context import RenderContext
    from .state import EntityState, WidgetState


def _extract_numeric(entity: EntityState | None) -> float:
    """Extract numeric value from entity state."""
    if entity is None:
        return 0.0
    try:
        return float(entity.state)
    except (ValueError, TypeError):
        return 0.0


@dataclass
class ProgressDisplay(Component):
    """Progress bar display component."""

    value: float
    target: float = 100
    label: str = "Progress"
    unit: str = ""
    color: Color = COLOR_CYAN
    icon: str | None = None
    show_target: bool = True
    bar_height_style: str = "normal"

    BAR_HEIGHT_MULTIPLIERS: ClassVar[dict[str, float]] = {
        "thin": 0.10,
        "normal": 0.17,
        "thick": 0.25,
    }

    def measure(self, ctx: RenderContext, max_width: int, max_height: int) -> tuple[int, int]:
        return (max_width, max_height)

    def render(self, ctx: RenderContext, x: int, y: int, width: int, height: int) -> None:
        """Render progress display."""
        padding = int(width * 0.05)
        icon_size = max(10, int(height * 0.20))
        bar_height_mult = self.BAR_HEIGHT_MULTIPLIERS.get(self.bar_height_style, 0.17)
        bar_height = max(4, int(height * bar_height_mult))

        # Format numbers with abbreviations for large values
        display_value = format_number(self.value)
        target = self.target or 100
        display_target = format_number(target)
        percent = min(100, (self.value / target) * 100) if target > 0 else 0

        # Adaptive layout based on size
        is_compact = height < 100

        if is_compact:
            # Compact: icon + value on first line, bar + percent on second
            font_value = ctx.get_font("small")
            font_percent = ctx.get_font("tiny")

            # Row 1: Icon + Value
            row1_y = y + int(height * 0.30)
            text_x = x + padding
            if self.icon:
                ctx.draw_icon(
                    self.icon,
                    (x + padding, row1_y - icon_size // 2),
                    size=icon_size,
                    color=self.color,
                )
                text_x = x + padding + icon_size + 4

            value_text = f"{display_value}/{display_target}" if self.show_target else display_value
            if self.unit:
                value_text += f" {self.unit}"
            ctx.draw_text(
                value_text, (text_x, row1_y), font=font_value, color=COLOR_WHITE, anchor="lm"
            )

            # Row 2: Progress bar + percent
            bar_y = y + int(height * 0.60)
            percent_width = int(width * 0.22)
            bar_rect = (x + padding, bar_y, x + width - percent_width - padding, bar_y + bar_height)
            ctx.draw_bar(bar_rect, percent, self.color, COLOR_DARK_GRAY)
            ctx.draw_text(
                f"{percent:.0f}%",
                (x + width - padding, bar_y + bar_height // 2),
                font=font_percent,
                color=COLOR_WHITE,
                anchor="rm",
            )
        else:
            # Full layout: label + value on first line, bar + percent on second
            font_label = ctx.get_font("small")
            font_value = ctx.get_font("regular")
            font_percent = ctx.get_font("small")

            top_y = y + int(height * 0.25)

            # Icon
            text_x = x + padding
            if self.icon:
                ctx.draw_icon(
                    self.icon,
                    (x + padding, top_y - icon_size // 2),
                    size=icon_size,
                    color=self.color,
                )
                text_x = x + padding + icon_size + 4

            # Value / target text
            value_text = f"{display_value}/{display_target}" if self.show_target else display_value
            if self.unit:
                value_text += f" {self.unit}"
            value_width, _ = ctx.get_text_size(value_text, font_value)

            # Check if label fits
            label_text = self.label.upper()
            label_width, _ = ctx.get_text_size(label_text, font_label)
            available_for_label = (x + width - padding) - text_x - value_width - 8

            if available_for_label >= label_width:
                # Label fits - draw both
                ctx.draw_text(
                    label_text, (text_x, top_y), font=font_label, color=COLOR_GRAY, anchor="lm"
                )
                ctx.draw_text(
                    value_text,
                    (x + width - padding, top_y),
                    font=font_value,
                    color=COLOR_WHITE,
                    anchor="rm",
                )
            else:
                # Not enough space - draw value only, left-aligned after icon
                ctx.draw_text(
                    value_text, (text_x, top_y), font=font_value, color=COLOR_WHITE, anchor="lm"
                )

            # Progress bar
            bar_y = y + int(height * 0.60)
            percent_width = int(width * 0.22)
            bar_rect = (x + padding, bar_y, x + width - percent_width, bar_y + bar_height)
            ctx.draw_bar(bar_rect, percent, self.color, COLOR_DARK_GRAY)

            # Percentage
            ctx.draw_text(
                f"{percent:.0f}%",
                (x + width - padding, bar_y + bar_height // 2),
                font=font_percent,
                color=COLOR_WHITE,
                anchor="rm",
            )


class ProgressWidget(Widget):
    """Widget that displays progress with label."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the progress widget."""
        super().__init__(config)
        self.target = config.options.get("target", 100)
        self.unit = config.options.get("unit", "")
        self.show_target = config.options.get("show_target", True)
        self.icon = config.options.get("icon")
        self.bar_height_style = config.options.get("bar_height", "normal")

    def render(self, ctx: RenderContext, state: WidgetState) -> Component:
        """Render the progress widget."""
        entity = state.entity
        value = _extract_numeric(entity)

        unit = self.unit
        if not unit and entity:
            unit = entity.unit or ""

        label = self.config.label
        if not label and entity:
            label = entity.friendly_name
        label = label or "Progress"

        return ProgressDisplay(
            value=value,
            target=self.target,
            label=label,
            unit=unit,
            color=self.config.color or COLOR_CYAN,
            icon=self.icon,
            show_target=self.show_target,
            bar_height_style=self.bar_height_style,
        )


@dataclass
class MultiProgressDisplay(Component):
    """Multi-progress list display component."""

    items: list[dict] = field(default_factory=list)
    title: str | None = None

    def measure(self, ctx: RenderContext, max_width: int, max_height: int) -> tuple[int, int]:
        return (max_width, max_height)

    def render(self, ctx: RenderContext, x: int, y: int, width: int, height: int) -> None:
        """Render multi-progress list."""
        font_title = ctx.get_font("small")
        font_label = ctx.get_font("tiny")

        padding = int(width * 0.05)
        current_y = y + padding

        if self.title:
            ctx.draw_text(
                self.title.upper(),
                (x + padding, current_y),
                font=font_title,
                color=COLOR_GRAY,
                anchor="lm",
            )
            current_y += int(height * 0.14)

        available_height = y + height - current_y - padding
        row_count = len(self.items) or 1
        row_height = min(int(height * 0.35), available_height // row_count)
        bar_height = max(4, int(height * 0.06))
        icon_size = max(8, int(height * 0.09))

        for item in self.items:
            label = item.get("label", "Item")
            value = item.get("value", 0)
            target = item.get("target", 100)
            color = item.get("color", COLOR_CYAN)
            icon = item.get("icon")
            unit = item.get("unit", "")

            percent = min(100, (value / target) * 100) if target > 0 else 0

            label_x = x + padding
            if icon:
                ctx.draw_icon(icon, (x + padding, current_y + 2), size=icon_size, color=color)
                label_x = x + padding + icon_size + 4

            ctx.draw_text(
                label.upper(),
                (label_x, current_y + int(row_height * 0.2)),
                font=font_label,
                color=COLOR_GRAY,
                anchor="lm",
            )

            value_text = f"{value:.0f}/{target:.0f}"
            if unit:
                value_text += f" {unit}"
            ctx.draw_text(
                value_text,
                (x + width - padding, current_y + int(row_height * 0.2)),
                font=font_label,
                color=COLOR_WHITE,
                anchor="rm",
            )

            bar_y = current_y + int(row_height * 0.55)
            percent_width = int(width * 0.20)
            bar_rect = (x + padding, bar_y, x + width - percent_width, bar_y + bar_height)
            ctx.draw_bar(bar_rect, percent, color, COLOR_DARK_GRAY)

            ctx.draw_text(
                f"{percent:.0f}%",
                (x + width - padding, bar_y + bar_height // 2),
                font=font_label,
                color=COLOR_WHITE,
                anchor="rm",
            )

            current_y += row_height


class MultiProgressWidget(Widget):
    """Widget that displays multiple progress items."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the multi-progress widget."""
        super().__init__(config)
        self.items = config.options.get("items", [])
        self.title = config.options.get("title")

    def get_entities(self) -> list[str]:
        """Return list of entity IDs."""
        return [item.get("entity_id") for item in self.items if item.get("entity_id")]

    def render(self, ctx: RenderContext, state: WidgetState) -> Component:
        """Render the multi-progress widget."""
        display_items = []
        for item in self.items:
            entity_id = item.get("entity_id")
            entity = state.get_entity(entity_id) if entity_id else None
            value = _extract_numeric(entity)

            label = item.get("label", "")
            if entity and not label:
                label = entity.friendly_name
            label = label or entity_id or "Item"

            unit = item.get("unit", "")
            if entity and not unit:
                unit = entity.unit or ""

            display_items.append(
                {
                    "label": label,
                    "value": value,
                    "target": item.get("target", 100),
                    "color": item.get("color", COLOR_CYAN),
                    "icon": item.get("icon"),
                    "unit": unit,
                }
            )

        return MultiProgressDisplay(items=display_items, title=self.title)
