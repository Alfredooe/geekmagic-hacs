"""Shared utilities for widgets."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import State

    from .base import WidgetConfig

# States considered "on" for binary sensors and similar entities
ON_STATES = frozenset({"on", "true", "home", "locked", "1"})


def truncate_text(text: str, max_chars: int, suffix: str = "..") -> str:
    """Truncate text with ellipsis if it exceeds max_chars.

    Args:
        text: Text to truncate
        max_chars: Maximum number of characters
        suffix: String to append when truncating (default: "..")

    Returns:
        Original text if short enough, otherwise truncated with suffix
    """
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def extract_numeric(
    state: State | None,
    attribute: str | None = None,
    default: float = 0.0,
) -> float:
    """Extract numeric value from entity state or attribute.

    Args:
        state: Home Assistant entity state object
        attribute: Optional attribute name to read from (reads state.state if None)
        default: Default value if extraction fails

    Returns:
        Extracted float value or default
    """
    if state is None:
        return default

    raw_value = state.attributes.get(attribute) if attribute else state.state
    if raw_value is None:
        return default
    with contextlib.suppress(ValueError, TypeError):
        return float(raw_value)
    return default


def resolve_label(
    config: WidgetConfig,
    state: State | None,
    fallback: str = "",
) -> str:
    """Get label from config or entity friendly_name.

    Priority:
    1. config.label (explicit label)
    2. state.attributes["friendly_name"]
    3. fallback value

    Args:
        config: Widget configuration
        state: Entity state object (may be None)
        fallback: Fallback text if no label found

    Returns:
        Resolved label string
    """
    if config.label:
        return config.label
    if state:
        return state.attributes.get("friendly_name", fallback)
    return fallback


def calculate_percent(
    value: float,
    min_val: float,
    max_val: float,
) -> float:
    """Calculate percentage in range [0, 100].

    Args:
        value: Current value
        min_val: Minimum value (0%)
        max_val: Maximum value (100%)

    Returns:
        Percentage clamped to [0, 100]
    """
    value_range = max_val - min_val
    if value_range <= 0:
        return 0.0
    return max(0.0, min(100.0, ((value - min_val) / value_range) * 100))


def is_entity_on(state: State | None) -> bool:
    """Check if entity is in 'on' state.

    Considers these states as "on":
    - "on", "true", "1" for switches/lights
    - "home" for presence
    - "locked" for locks (security = good)

    Args:
        state: Entity state object

    Returns:
        True if entity is considered "on", False otherwise
    """
    if state is None:
        return False
    return state.state.lower() in ON_STATES


def get_unit(state: State | None, default: str = "") -> str:
    """Get unit of measurement from entity state.

    Args:
        state: Entity state object
        default: Default unit if not found

    Returns:
        Unit of measurement string
    """
    if state is None:
        return default
    return state.attributes.get("unit_of_measurement", default)


def get_entity_icon(state: State | None) -> str | None:
    """Get the icon configured for an HA entity.

    Home Assistant entities can have icons set via:
    - User customization in the UI
    - Integration defaults based on device class
    - Domain defaults

    The icon is in MDI format, e.g., "mdi:thermometer".

    Args:
        state: Entity state object

    Returns:
        Icon string in MDI format (e.g., "mdi:thermometer") or None if not set
    """
    if state is None:
        return None
    return state.attributes.get("icon")


def estimate_max_chars(
    available_width: int,
    char_width: int = 8,
    padding: int = 10,
) -> int:
    """Estimate maximum characters that fit in available width.

    Args:
        available_width: Available width in pixels
        char_width: Estimated average character width
        padding: Horizontal padding to account for

    Returns:
        Maximum number of characters
    """
    usable_width = available_width - 2 * padding
    return max(1, usable_width // char_width)


def format_value_with_unit(
    value: str,
    unit: str,
    separator: str = "",
) -> str:
    """Format value with optional unit.

    Args:
        value: Value string
        unit: Unit string (can be empty)
        separator: Separator between value and unit

    Returns:
        Formatted string like "23.5°C" or "23.5"
    """
    if unit:
        return f"{value}{separator}{unit}"
    return value


def extract_state_value(
    state: State | None,
    attribute: str | None = None,
    default_value: str = "--",
    default_unit: str = "",
) -> tuple[float, str, str]:
    """Extract value, display string, and unit from entity state.

    Convenience function that combines extract_numeric and get_unit.

    Args:
        state: Entity state object
        attribute: Optional attribute to read value from
        default_value: Default display string if extraction fails
        default_unit: Default unit if not found

    Returns:
        Tuple of (numeric_value, display_string, unit)
    """
    if state is None:
        return 0.0, default_value, default_unit

    raw_value = state.attributes.get(attribute) if attribute else state.state
    unit = state.attributes.get("unit_of_measurement", default_unit)

    if raw_value is None:
        return 0.0, default_value, unit

    with contextlib.suppress(ValueError, TypeError):
        numeric = float(raw_value)
        return numeric, f"{numeric:.0f}", unit

    return 0.0, default_value, unit
