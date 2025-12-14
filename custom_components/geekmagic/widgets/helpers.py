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
    """Get the icon for an HA entity.

    Checks multiple sources:
    1. Explicit icon attribute (user customization or integration)
    2. Device class default icon
    3. Domain default icon

    Args:
        state: Entity state object

    Returns:
        Icon string in MDI format (e.g., "mdi:thermometer") or None if not found
    """
    if state is None:
        return None

    # Check explicit icon attribute first
    icon = state.attributes.get("icon")
    if icon:
        return icon

    # Get domain from entity_id
    entity_id = state.entity_id
    domain = entity_id.split(".")[0] if "." in entity_id else None

    # Check device class for domain-specific icons
    device_class = state.attributes.get("device_class")
    if device_class:
        device_class_icon = _get_device_class_icon(domain, device_class)
        if device_class_icon:
            return device_class_icon

    # Fall back to domain default
    if domain:
        return _get_domain_icon(domain)

    return None


def _get_device_class_icon(domain: str | None, device_class: str) -> str | None:
    """Get icon for a device class."""
    # Common device class icons
    device_class_icons = {
        # Sensors
        "temperature": "mdi:thermometer",
        "humidity": "mdi:water-percent",
        "pressure": "mdi:gauge",
        "battery": "mdi:battery",
        "power": "mdi:flash",
        "energy": "mdi:lightning-bolt",
        "voltage": "mdi:sine-wave",
        "current": "mdi:current-ac",
        "frequency": "mdi:sine-wave",
        "illuminance": "mdi:brightness-5",
        "signal_strength": "mdi:wifi",
        "carbon_dioxide": "mdi:molecule-co2",
        "carbon_monoxide": "mdi:molecule-co",
        "pm25": "mdi:blur",
        "pm10": "mdi:blur",
        "volatile_organic_compounds": "mdi:air-filter",
        "nitrogen_dioxide": "mdi:molecule",
        "ozone": "mdi:molecule",
        "sulphur_dioxide": "mdi:molecule",
        "timestamp": "mdi:clock",
        "duration": "mdi:timer",
        "moisture": "mdi:water",
        "gas": "mdi:gas-cylinder",
        "speed": "mdi:speedometer",
        "wind_speed": "mdi:weather-windy",
        "weight": "mdi:weight",
        "distance": "mdi:ruler",
        "monetary": "mdi:currency-usd",
        "data_rate": "mdi:download",
        "data_size": "mdi:database",
        # Binary sensors
        "motion": "mdi:motion-sensor",
        "door": "mdi:door",
        "window": "mdi:window-closed",
        "opening": "mdi:door-open",
        "presence": "mdi:home-account",
        "occupancy": "mdi:home-account",
        "smoke": "mdi:smoke-detector",
        "lock": "mdi:lock",
        "plug": "mdi:power-plug",
        "connectivity": "mdi:connection",
        "problem": "mdi:alert-circle",
        "safety": "mdi:shield-check",
        "sound": "mdi:microphone",
        "vibration": "mdi:vibrate",
        "running": "mdi:play-circle",
        "update": "mdi:package-up",
    }
    return (
        f"mdi:{device_class_icons.get(device_class, '').replace('mdi:', '')}"
        if device_class in device_class_icons
        else None
    )


def _get_domain_icon(domain: str) -> str | None:
    """Get default icon for a domain."""
    domain_icons = {
        "sensor": "mdi:eye",
        "binary_sensor": "mdi:checkbox-blank-circle",
        "switch": "mdi:toggle-switch",
        "light": "mdi:lightbulb",
        "fan": "mdi:fan",
        "climate": "mdi:thermostat",
        "lock": "mdi:lock",
        "cover": "mdi:window-shutter",
        "camera": "mdi:camera",
        "media_player": "mdi:cast",
        "vacuum": "mdi:robot-vacuum",
        "weather": "mdi:weather-partly-cloudy",
        "person": "mdi:account",
        "device_tracker": "mdi:crosshairs-gps",
        "automation": "mdi:robot",
        "script": "mdi:script-text",
        "scene": "mdi:palette",
        "input_boolean": "mdi:toggle-switch",
        "input_number": "mdi:ray-vertex",
        "input_select": "mdi:format-list-bulleted",
        "input_text": "mdi:form-textbox",
        "input_datetime": "mdi:calendar-clock",
        "input_button": "mdi:gesture-tap-button",
        "counter": "mdi:counter",
        "timer": "mdi:timer",
        "calendar": "mdi:calendar",
        "alarm_control_panel": "mdi:shield-home",
        "number": "mdi:ray-vertex",
        "select": "mdi:format-list-bulleted",
        "button": "mdi:gesture-tap-button",
        "text": "mdi:form-textbox",
        "update": "mdi:package-up",
        "water_heater": "mdi:water-boiler",
        "humidifier": "mdi:air-humidifier",
        "remote": "mdi:remote",
        "siren": "mdi:bullhorn",
        "lawn_mower": "mdi:robot-mower",
        "valve": "mdi:valve",
    }
    return domain_icons.get(domain)


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
