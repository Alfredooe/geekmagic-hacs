"""Tests for GeekMagic coordinator multi-screen support."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.geekmagic.const import (
    CONF_LAYOUT,
    CONF_REFRESH_INTERVAL,
    CONF_SCREEN_CYCLE_INTERVAL,
    CONF_SCREENS,
    CONF_WIDGETS,
    LAYOUT_GRID_2X2,
    LAYOUT_SPLIT,
)
from custom_components.geekmagic.coordinator import GeekMagicCoordinator


@pytest.fixture
def coordinator_device():
    """Create mock GeekMagic device for coordinator tests."""
    device = MagicMock()
    device.upload_and_display = AsyncMock()
    device.set_brightness = AsyncMock()
    return device


@pytest.fixture
def old_format_options():
    """Create old single-screen format options."""
    return {
        CONF_REFRESH_INTERVAL: 15,
        CONF_LAYOUT: LAYOUT_GRID_2X2,
        CONF_WIDGETS: [{"type": "clock", "slot": 0}],
    }


@pytest.fixture
def new_format_options():
    """Create new multi-screen format options."""
    return {
        CONF_REFRESH_INTERVAL: 10,
        CONF_SCREEN_CYCLE_INTERVAL: 30,
        CONF_SCREENS: [
            {
                "name": "Dashboard",
                CONF_LAYOUT: LAYOUT_GRID_2X2,
                CONF_WIDGETS: [{"type": "clock", "slot": 0}],
            },
            {
                "name": "Media",
                CONF_LAYOUT: LAYOUT_SPLIT,
                CONF_WIDGETS: [{"type": "clock", "slot": 0}],
            },
        ],
    }


class TestCoordinatorMigration:
    """Test options migration."""

    def test_migrate_old_format(self, hass, coordinator_device, old_format_options):
        """Test migrating old single-screen format."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, old_format_options)

        assert CONF_SCREENS in coordinator.options
        assert len(coordinator.options[CONF_SCREENS]) == 1
        assert coordinator.options[CONF_SCREENS][0][CONF_LAYOUT] == LAYOUT_GRID_2X2
        assert coordinator.options[CONF_REFRESH_INTERVAL] == 15

    def test_already_migrated(self, hass, coordinator_device, new_format_options):
        """Test that already-migrated options are unchanged."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)

        assert coordinator.options[CONF_SCREEN_CYCLE_INTERVAL] == 30
        assert len(coordinator.options[CONF_SCREENS]) == 2


class TestCoordinatorMultiScreen:
    """Test multi-screen functionality."""

    def test_screen_count(self, hass, coordinator_device, new_format_options):
        """Test screen count property."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        assert coordinator.screen_count == 2

    def test_current_screen_initial(self, hass, coordinator_device, new_format_options):
        """Test initial current screen is 0."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        assert coordinator.current_screen == 0

    def test_current_screen_name(self, hass, coordinator_device, new_format_options):
        """Test current screen name property."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        assert coordinator.current_screen_name == "Dashboard"

    @pytest.mark.asyncio
    async def test_set_screen(self, hass, coordinator_device, new_format_options):
        """Test setting screen by index."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        coordinator.async_request_refresh = AsyncMock()  # type: ignore[method-assign]

        await coordinator.async_set_screen(1)
        assert coordinator.current_screen == 1
        assert coordinator.current_screen_name == "Media"

    @pytest.mark.asyncio
    async def test_set_screen_invalid_index(self, hass, coordinator_device, new_format_options):
        """Test setting invalid screen index is ignored."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        coordinator.async_request_refresh = AsyncMock()  # type: ignore[method-assign]

        await coordinator.async_set_screen(10)  # Invalid index
        assert coordinator.current_screen == 0  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_next_screen(self, hass, coordinator_device, new_format_options):
        """Test cycling to next screen."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        coordinator.async_request_refresh = AsyncMock()  # type: ignore[method-assign]

        assert coordinator.current_screen == 0
        await coordinator.async_next_screen()
        assert coordinator.current_screen == 1
        await coordinator.async_next_screen()
        assert coordinator.current_screen == 0  # Wraps around

    @pytest.mark.asyncio
    async def test_previous_screen(self, hass, coordinator_device, new_format_options):
        """Test cycling to previous screen."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, new_format_options)
        coordinator.async_request_refresh = AsyncMock()  # type: ignore[method-assign]

        assert coordinator.current_screen == 0
        await coordinator.async_previous_screen()
        assert coordinator.current_screen == 1  # Wraps around


class TestCoordinatorUpdateOptions:
    """Test options update functionality."""

    def test_update_options_rebuilds_screens(self, hass, coordinator_device, old_format_options):
        """Test that updating options rebuilds screens."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, old_format_options)
        assert coordinator.screen_count == 1

        # Update to multi-screen
        new_options = {
            CONF_REFRESH_INTERVAL: 10,
            CONF_SCREEN_CYCLE_INTERVAL: 0,
            CONF_SCREENS: [
                {"name": "Screen 1", CONF_LAYOUT: LAYOUT_GRID_2X2, CONF_WIDGETS: []},
                {"name": "Screen 2", CONF_LAYOUT: LAYOUT_SPLIT, CONF_WIDGETS: []},
                {"name": "Screen 3", CONF_LAYOUT: LAYOUT_GRID_2X2, CONF_WIDGETS: []},
            ],
        }
        coordinator.update_options(new_options)

        assert coordinator.screen_count == 3


class TestCoordinatorWidgetRegistration:
    """Test that all widget types are registered."""

    def test_all_widgets_registered(self):
        """Test that all 12 widget types are registered."""
        from custom_components.geekmagic.coordinator import WIDGET_CLASSES

        expected_widgets = [
            "camera",
            "clock",
            "entity",
            "media",
            "chart",
            "text",
            "gauge",
            "progress",
            "multi_progress",
            "status",
            "status_list",
            "weather",
        ]

        for widget_type in expected_widgets:
            assert widget_type in WIDGET_CLASSES, f"Widget {widget_type} not registered"

        assert len(WIDGET_CLASSES) == 12
