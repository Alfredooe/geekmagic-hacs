"""Screen templates for GeekMagic integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import (
    CONF_LAYOUT,
    CONF_SCREENS,
    CONF_WIDGETS,
    LAYOUT_GRID_2X2,
    LAYOUT_GRID_2X3,
    LAYOUT_HERO,
    LAYOUT_SPLIT,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


# Template definitions
# Each template defines a layout and pre-configured widgets
# Labels are NOT set - widgets infer labels from entity friendly_name
SCREEN_TEMPLATES: dict[str, dict[str, Any]] = {
    "system_monitor": {
        "name": "System Monitor",
        "description": "CPU, memory, disk, and network monitoring",
        "layout": LAYOUT_GRID_2X2,
        "widgets": [
            {
                "slot": 0,
                "type": "gauge",
                "options": {"style": "ring", "min": 0, "max": 100, "unit": "%"},
                "hint": "CPU usage sensor (e.g., sensor.processor_use)",
            },
            {
                "slot": 1,
                "type": "gauge",
                "options": {"style": "ring", "min": 0, "max": 100, "unit": "%"},
                "hint": "Memory usage sensor (e.g., sensor.memory_use_percent)",
            },
            {
                "slot": 2,
                "type": "gauge",
                "options": {"style": "ring", "min": 0, "max": 100, "unit": "%"},
                "hint": "Disk usage sensor (e.g., sensor.disk_use_percent)",
            },
            {
                "slot": 3,
                "type": "chart",
                "options": {"hours": 24, "show_value": True, "show_range": False},
                "hint": "Network sensor (e.g., sensor.speedtest_download)",
            },
        ],
    },
    "smart_home": {
        "name": "Smart Home",
        "description": "Temperature, humidity, lights, motion, door, presence",
        "layout": LAYOUT_GRID_2X3,
        "widgets": [
            {
                "slot": 0,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True, "icon": "thermometer"},
                "hint": "Temperature sensor",
            },
            {
                "slot": 1,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True, "icon": "drop"},
                "hint": "Humidity sensor",
            },
            {
                "slot": 2,
                "type": "entity",
                "options": {"show_name": True, "icon": "bulb"},
                "hint": "Light entity or group",
            },
            {
                "slot": 3,
                "type": "status",
                "options": {"icon": "motion", "on_text": "Motion", "off_text": "Clear"},
                "hint": "Motion sensor",
            },
            {
                "slot": 4,
                "type": "status",
                "options": {"icon": "door", "on_text": "Open", "off_text": "Closed"},
                "hint": "Door sensor",
            },
            {
                "slot": 5,
                "type": "status",
                "options": {"icon": "home", "on_text": "Home", "off_text": "Away"},
                "hint": "Presence sensor or person entity",
            },
        ],
    },
    "weather": {
        "name": "Weather Dashboard",
        "description": "Weather with forecast and indoor conditions",
        "layout": LAYOUT_HERO,
        "widgets": [
            {
                "slot": 0,
                "type": "weather",
                "options": {"show_forecast": True, "forecast_days": 3, "show_humidity": True},
                "hint": "Weather entity (e.g., weather.home)",
            },
            {
                "slot": 1,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True, "icon": "thermometer"},
                "hint": "Indoor temperature sensor",
            },
            {
                "slot": 2,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True, "icon": "drop"},
                "hint": "Indoor humidity sensor",
            },
            {
                "slot": 3,
                "type": "entity",
                "options": {"show_name": True, "icon": "sun"},
                "hint": "UV index or outdoor condition",
            },
        ],
    },
    "media_player": {
        "name": "Media Player",
        "description": "Now playing with album art and controls",
        "layout": LAYOUT_HERO,
        "widgets": [
            {
                "slot": 0,
                "type": "media",
                "options": {"show_artist": True, "show_album": False, "show_progress": True},
                "hint": "Media player entity",
            },
            {
                "slot": 1,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True},
                "hint": "Volume level (media_player attribute)",
            },
            {
                "slot": 2,
                "type": "text",
                "options": {"text": "Now Playing", "size": "small", "align": "center"},
            },
            {
                "slot": 3,
                "type": "entity",
                "options": {"show_name": True},
                "hint": "Media source (media_player attribute)",
            },
        ],
    },
    "clock": {
        "name": "Clock Dashboard",
        "description": "Large clock with date and status info",
        "layout": LAYOUT_HERO,
        "widgets": [
            {
                "slot": 0,
                "type": "clock",
                "options": {"show_date": True, "show_seconds": False, "time_format": "24h"},
            },
            {
                "slot": 1,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True, "icon": "thermometer"},
                "hint": "Temperature sensor",
            },
            {
                "slot": 2,
                "type": "entity",
                "options": {"show_name": True},
                "hint": "Weather condition or outdoor temp",
            },
            {
                "slot": 3,
                "type": "status",
                "options": {"icon": "home", "on_text": "Home", "off_text": "Away"},
                "hint": "Presence indicator",
            },
        ],
    },
    "energy": {
        "name": "Energy Monitor",
        "description": "Power consumption and energy tracking",
        "layout": LAYOUT_GRID_2X2,
        "widgets": [
            {
                "slot": 0,
                "type": "gauge",
                "options": {"style": "arc", "min": 0, "max": 5000, "unit": "W"},
                "hint": "Current power usage sensor",
            },
            {
                "slot": 1,
                "type": "chart",
                "options": {"hours": 24, "show_value": True, "show_range": True},
                "hint": "Energy consumption sensor",
            },
            {
                "slot": 2,
                "type": "entity",
                "options": {"show_name": True, "show_unit": True},
                "hint": "Energy cost sensor or utility meter",
            },
            {
                "slot": 3,
                "type": "status",
                "options": {"icon": "bolt", "on_text": "Import", "off_text": "Export"},
                "hint": "Grid import/export status",
            },
        ],
    },
    "security": {
        "name": "Security",
        "description": "Camera, doors, windows, and alarm status",
        "layout": LAYOUT_GRID_2X3,
        "widgets": [
            {
                "slot": 0,
                "type": "camera",
                "options": {"show_label": True, "fit": "cover"},
                "hint": "Security camera entity",
            },
            {
                "slot": 1,
                "type": "status",
                "options": {"icon": "door", "on_text": "Open", "off_text": "Closed"},
                "hint": "Front door sensor",
            },
            {
                "slot": 2,
                "type": "status",
                "options": {"icon": "door", "on_text": "Open", "off_text": "Closed"},
                "hint": "Back door sensor",
            },
            {
                "slot": 3,
                "type": "status",
                "options": {"icon": "motion", "on_text": "Detected", "off_text": "Clear"},
                "hint": "Motion sensor",
            },
            {
                "slot": 4,
                "type": "status",
                "options": {"icon": "alarm", "on_text": "Armed", "off_text": "Disarmed"},
                "hint": "Alarm panel state",
            },
            {
                "slot": 5,
                "type": "status",
                "options": {"icon": "lock", "on_text": "Locked", "off_text": "Unlocked"},
                "hint": "Smart lock state",
            },
        ],
    },
    "thermostat": {
        "name": "Thermostat",
        "description": "Climate control with temperature and humidity",
        "layout": LAYOUT_SPLIT,
        "widgets": [
            {
                "slot": 0,
                "type": "gauge",
                "options": {"style": "arc", "min": 10, "max": 35, "unit": "°"},
                "hint": "Current temperature from climate entity",
            },
            {
                "slot": 1,
                "type": "gauge",
                "options": {"style": "arc", "min": 0, "max": 100, "unit": "%"},
                "hint": "Current humidity sensor",
            },
        ],
    },
}


def get_template(template_key: str) -> dict[str, Any] | None:
    """Get a template by key.

    Args:
        template_key: Template identifier

    Returns:
        Template configuration or None if not found
    """
    return SCREEN_TEMPLATES.get(template_key)


def get_template_names() -> dict[str, str]:
    """Get mapping of template keys to display names.

    Returns:
        Dictionary of {key: name}
    """
    return {key: template["name"] for key, template in SCREEN_TEMPLATES.items()}


async def apply_template(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    screen_index: int,
    template_key: str,
) -> bool:
    """Apply a template to a screen.

    Args:
        hass: Home Assistant instance
        config_entry: Config entry to update
        screen_index: Screen index to apply template to
        template_key: Template to apply

    Returns:
        True if successful
    """
    template = get_template(template_key)
    if template is None:
        return False

    new_options = dict(config_entry.options)
    screens = list(new_options.get(CONF_SCREENS, []))

    # Ensure screen exists
    while len(screens) <= screen_index:
        screens.append(
            {
                "name": f"Screen {len(screens) + 1}",
                CONF_LAYOUT: LAYOUT_GRID_2X2,
                CONF_WIDGETS: [],
            }
        )

    # Update screen with template
    screens[screen_index] = dict(screens[screen_index])
    screens[screen_index]["name"] = template.get("name", screens[screen_index].get("name"))
    screens[screen_index][CONF_LAYOUT] = template["layout"]

    # Create widgets from template (without labels - they'll be inferred from entities)
    widgets = []
    for widget_template in template.get("widgets", []):
        widget = {
            "type": widget_template["type"],
            "slot": widget_template["slot"],
        }
        # Don't copy label - let widget infer from entity friendly_name
        if "options" in widget_template:
            widget["options"] = dict(widget_template["options"])
        widgets.append(widget)

    screens[screen_index][CONF_WIDGETS] = widgets
    new_options[CONF_SCREENS] = screens

    hass.config_entries.async_update_entry(
        config_entry,
        options=new_options,
    )

    return True
