"""Media player widget for GeekMagic displays."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..const import COLOR_CYAN, COLOR_GRAY, COLOR_WHITE
from .base import Widget, WidgetConfig
from .components import Color, Component

if TYPE_CHECKING:
    from ..render_context import RenderContext
    from .state import WidgetState


def _format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


@dataclass
class NowPlaying(Component):
    """Now playing display component."""

    title: str
    artist: str = ""
    album: str = ""
    position: float = 0
    duration: float = 0
    color: Color = COLOR_CYAN
    show_artist: bool = True
    show_album: bool = False
    show_progress: bool = True

    def measure(self, ctx: RenderContext, max_width: int, max_height: int) -> tuple[int, int]:
        return (max_width, max_height)

    def render(self, ctx: RenderContext, x: int, y: int, width: int, height: int) -> None:
        """Render now playing info."""
        center_x = x + width // 2
        font_label = ctx.get_font("small")
        font_title = ctx.get_font("regular")
        font_small = ctx.get_font("small")
        padding = int(width * 0.05)

        # Truncate text
        max_chars = (width - padding * 2) // 8
        title = self.title[: max_chars - 2] + ".." if len(self.title) > max_chars else self.title
        artist = (
            self.artist[: max_chars - 2] + ".." if len(self.artist) > max_chars else self.artist
        )

        current_y = y + int(height * 0.12)

        # Draw "NOW PLAYING"
        ctx.draw_text(
            "NOW PLAYING", (center_x, current_y), font=font_label, color=COLOR_GRAY, anchor="mm"
        )
        current_y += int(height * 0.20)

        # Draw title
        ctx.draw_text(title, (center_x, current_y), font=font_title, color=COLOR_WHITE, anchor="mm")
        current_y += int(height * 0.17)

        # Draw artist
        if self.show_artist and artist:
            ctx.draw_text(
                artist, (center_x, current_y), font=font_small, color=COLOR_GRAY, anchor="mm"
            )
            current_y += int(height * 0.15)

        # Draw album
        if self.show_album and self.album:
            album = (
                self.album[: max_chars - 2] + ".." if len(self.album) > max_chars else self.album
            )
            ctx.draw_text(
                album, (center_x, current_y), font=font_small, color=COLOR_GRAY, anchor="mm"
            )

        # Draw progress bar
        if self.show_progress and self.duration > 0:
            bar_height = max(4, int(height * 0.05))
            bar_y = y + height - int(height * 0.21)
            bar_rect = (x + padding, bar_y, x + width - padding, bar_y + bar_height)
            progress = min(100, (self.position / self.duration) * 100)
            ctx.draw_bar(bar_rect, progress, color=self.color)

            # Draw time
            pos_str = _format_time(self.position)
            dur_str = _format_time(self.duration)
            time_y = bar_y + int(height * 0.12)
            ctx.draw_text(
                pos_str, (x + padding, time_y), font=font_small, color=COLOR_GRAY, anchor="lm"
            )
            ctx.draw_text(
                dur_str,
                (x + width - padding, time_y),
                font=font_small,
                color=COLOR_GRAY,
                anchor="rm",
            )


@dataclass
class MediaIdle(Component):
    """Idle/paused state display."""

    def measure(self, ctx: RenderContext, max_width: int, max_height: int) -> tuple[int, int]:
        return (max_width, max_height)

    def render(self, ctx: RenderContext, x: int, y: int, width: int, height: int) -> None:
        """Render paused state."""
        center_x = x + width // 2
        center_y = y + height // 2
        font_label = ctx.get_font("small")

        # Draw pause icon
        bar_width = max(4, int(width * 0.04))
        bar_height = max(15, int(height * 0.25))
        gap = max(5, int(width * 0.05))

        left_bar = (
            center_x - gap - bar_width,
            center_y - bar_height // 2,
            center_x - gap,
            center_y + bar_height // 2,
        )
        right_bar = (
            center_x + gap,
            center_y - bar_height // 2,
            center_x + gap + bar_width,
            center_y + bar_height // 2,
        )

        ctx.draw_rect(left_bar, fill=COLOR_GRAY)
        ctx.draw_rect(right_bar, fill=COLOR_GRAY)

        ctx.draw_text(
            "PAUSED",
            (center_x, center_y + int(height * 0.29)),
            font=font_label,
            color=COLOR_GRAY,
            anchor="mm",
        )


class MediaWidget(Widget):
    """Widget that displays media player information."""

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the media widget."""
        super().__init__(config)
        self.show_artist = config.options.get("show_artist", True)
        self.show_album = config.options.get("show_album", False)
        self.show_progress = config.options.get("show_progress", True)

    def render(self, ctx: RenderContext, state: WidgetState) -> Component:
        """Render the media player widget.

        Args:
            ctx: RenderContext for drawing
            state: Widget state with entity data
        """
        entity = state.entity

        if entity is None or entity.state in ("off", "unavailable", "unknown", "idle"):
            return MediaIdle()

        return NowPlaying(
            title=entity.get("media_title", "Unknown"),
            artist=entity.get("media_artist", ""),
            album=entity.get("media_album_name", ""),
            position=entity.get("media_position", 0),
            duration=entity.get("media_duration", 0),
            color=self.config.color or COLOR_CYAN,
            show_artist=self.show_artist,
            show_album=self.show_album,
            show_progress=self.show_progress,
        )
