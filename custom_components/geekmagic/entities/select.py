"""Select entities for GeekMagic integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from .base import GeekMagicEntity

if TYPE_CHECKING:
    from ..coordinator import GeekMagicCoordinator

_LOGGER = logging.getLogger(__name__)

# Built-in device themes/modes
DEVICE_MODES = {
    "custom": "Custom Views",
    "clock": "Clock",
    "weather": "Weather",
    "system": "System Info",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GeekMagic select entities."""
    coordinator: GeekMagicCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        GeekMagicModeSelect(coordinator),
        GeekMagicCurrentViewSelect(coordinator),
    ]

    async_add_entities(entities)


class GeekMagicModeSelect(GeekMagicEntity, SelectEntity):
    """Select entity for device mode."""

    _attr_name = "Mode"
    _attr_icon = "mdi:monitor-dashboard"

    def __init__(self, coordinator: GeekMagicCoordinator) -> None:
        """Initialize mode select."""
        super().__init__(coordinator, "mode")

    @property
    def options(self) -> list[str]:
        """Return available modes."""
        return list(DEVICE_MODES.values())

    @property
    def current_option(self) -> str | None:
        """Return current mode."""
        if self.coordinator.device_state:
            theme = self.coordinator.device_state.theme
            # Theme 3 = custom image mode (our integration)
            if theme == 3:
                return DEVICE_MODES["custom"]
            if theme == 0:
                return DEVICE_MODES["clock"]
            if theme == 1:
                return DEVICE_MODES["weather"]
            if theme == 2:
                return DEVICE_MODES["system"]
        return DEVICE_MODES["custom"]

    async def async_select_option(self, option: str) -> None:
        """Select a mode."""
        theme_map = {
            DEVICE_MODES["custom"]: 3,
            DEVICE_MODES["clock"]: 0,
            DEVICE_MODES["weather"]: 1,
            DEVICE_MODES["system"]: 2,
        }
        theme = theme_map.get(option, 3)
        await self.coordinator.device.set_theme(theme)
        await self.coordinator.async_request_refresh()


class GeekMagicCurrentViewSelect(GeekMagicEntity, SelectEntity):
    """Select entity for current view (when in custom mode)."""

    _attr_name = "Current View"
    _attr_icon = "mdi:view-dashboard"

    def __init__(self, coordinator: GeekMagicCoordinator) -> None:
        """Initialize current view select."""
        super().__init__(coordinator, "current_view")

    @property
    def options(self) -> list[str]:
        """Return available views."""
        store = self.coordinator.get_store()
        if not store:
            return []

        assigned_views = self.coordinator.options.get("assigned_views", [])
        options = []
        for view_id in assigned_views:
            view = store.get_view(view_id)
            if view:
                options.append(view.get("name", view_id))
        return options if options else ["No views assigned"]

    @property
    def current_option(self) -> str | None:
        """Return current view name."""
        store = self.coordinator.get_store()
        if not store:
            return None

        assigned_views = self.coordinator.options.get("assigned_views", [])
        if not assigned_views:
            return "No views assigned"

        current_idx = self.coordinator.current_screen
        if 0 <= current_idx < len(assigned_views):
            view_id = assigned_views[current_idx]
            view = store.get_view(view_id)
            if view:
                return view.get("name", view_id)
        return None

    async def async_select_option(self, option: str) -> None:
        """Select a view."""
        if option == "No views assigned":
            return

        store = self.coordinator.get_store()
        if not store:
            return

        assigned_views = self.coordinator.options.get("assigned_views", [])
        for idx, view_id in enumerate(assigned_views):
            view = store.get_view(view_id)
            if view and view.get("name") == option:
                self.coordinator.set_current_screen(idx)
                await self.coordinator.async_refresh_display()
                break
