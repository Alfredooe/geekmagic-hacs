"""Camera platform for GeekMagic display preview."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import GeekMagicCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GeekMagic camera from a config entry."""
    coordinator: GeekMagicCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([GeekMagicPreviewCamera(coordinator, entry)])


class GeekMagicPreviewCamera(Camera):
    """Camera entity showing the GeekMagic display preview."""

    _attr_has_entity_name = True
    _attr_name = "Display Preview"

    def __init__(
        self,
        coordinator: GeekMagicCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self._entry = entry

        # Entity attributes
        self._attr_unique_id = f"{entry.data[CONF_HOST]}_preview"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data[CONF_HOST])},
            "name": entry.data.get(CONF_NAME, "GeekMagic Display"),
            "manufacturer": "GeekMagic",
            "model": "SmallTV Pro",
        }

    @property
    def frame_interval(self) -> float:
        """Return the polling interval for the camera."""
        # Match the coordinator's refresh interval
        if self.coordinator.update_interval:
            return self.coordinator.update_interval.total_seconds()
        return 10.0

    def camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the current camera image."""
        return self.coordinator.last_image

    @property
    def available(self) -> bool:
        """Return True if the camera is available."""
        return self.coordinator.last_update_success
