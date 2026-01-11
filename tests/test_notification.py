"""Tests for GeekMagic notification service."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from custom_components.geekmagic.const import (
    CONF_LAYOUT,
    CONF_REFRESH_INTERVAL,
    CONF_SCREENS,
    CONF_WIDGETS,
    LAYOUT_GRID_2X2,
)
from custom_components.geekmagic.coordinator import GeekMagicCoordinator
from custom_components.geekmagic.layouts.hero import HeroLayout

@pytest.fixture
def coordinator_device():
    """Create mock GeekMagic device."""
    device = MagicMock()
    device.upload_and_display = AsyncMock()
    device.set_brightness = AsyncMock()
    device.get_brightness = AsyncMock(return_value=50)
    device.get_state = AsyncMock(return_value=None)
    device.get_space = AsyncMock(return_value=None)
    return device

@pytest.fixture
def options():
    """Create default options."""
    return {
        CONF_REFRESH_INTERVAL: 60,
        CONF_SCREENS: [
            {
                "name": "Screen 1",
                CONF_LAYOUT: LAYOUT_GRID_2X2,
                CONF_WIDGETS: [{"type": "clock", "slot": 0}],
            }
        ],
    }

class TestNotification:
    """Test notification functionality."""

    @pytest.mark.asyncio
    async def test_trigger_notification(self, hass, coordinator_device, options):
        """Test triggering a notification sets state."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, options)
        coordinator.async_request_refresh = AsyncMock()

        data = {
            "message": "Hello World",
            "title": "Alert",
            "duration": 5,
            "icon": "mdi:test"
        }

        with patch("time.time", return_value=1000):
            await coordinator.trigger_notification(data)

            assert coordinator._notification_data == data
            assert coordinator._notification_expiry == 1005
            assert coordinator.async_request_refresh.called

    @pytest.mark.asyncio
    async def test_notification_layout_creation(self, hass, coordinator_device, options):
        """Test notification layout is created correctly."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, options)
        
        data = {
            "message": "Test Message",
            "title": "Test Title",
            "icon": "mdi:check",
            "image": "camera.test"
        }
        
        layout = coordinator._create_notification_layout(data)
        
        assert isinstance(layout, HeroLayout)
        # Slot 0 should be CameraWidget because image starts with camera.
        assert layout.get_widget(0).config.widget_type == "camera"
        # Slot 1 should be Title
        assert layout.get_widget(1).config.options["text"] == "Test Title"
        # Slot 2 should be Message
        assert layout.get_widget(2).config.options["text"] == "Test Message"

    @pytest.mark.asyncio
    async def test_render_notification_active(self, hass, coordinator_device, options):
        """Test render loop uses notification layout when active."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, options)
        
        # Setup active notification
        coordinator._notification_data = {"message": "Active"}
        coordinator._notification_expiry = 2000
        
        # Mock renderer methods to avoid actual PIL calls
        coordinator.renderer.create_canvas = MagicMock(return_value=(MagicMock(), MagicMock()))
        coordinator.renderer.to_jpeg = MagicMock(return_value=b"jpeg")
        coordinator.renderer.to_png = MagicMock(return_value=b"png")
        
        # Build widget states mock
        coordinator._build_widget_states = MagicMock(return_value={})

        with patch("time.time", return_value=1000):
            # Spy on _create_notification_layout
            with patch.object(coordinator, "_create_notification_layout", wraps=coordinator._create_notification_layout) as mock_create:
                coordinator._render_display()
                mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_render_notification_expired(self, hass, coordinator_device, options):
        """Test render loop ignores notification when expired."""
        coordinator = GeekMagicCoordinator(hass, coordinator_device, options)
        
        # Setup expired notification
        coordinator._notification_data = {"message": "Expired"}
        coordinator._notification_expiry = 900
        
        # Mock renderer methods
        coordinator.renderer.create_canvas = MagicMock(return_value=(MagicMock(), MagicMock()))
        coordinator.renderer.to_jpeg = MagicMock(return_value=b"jpeg")
        coordinator.renderer.to_png = MagicMock(return_value=b"png")
        coordinator._build_widget_states = MagicMock(return_value={})
        
        with patch("time.time", return_value=1000):
             with patch.object(coordinator, "_create_notification_layout", wraps=coordinator._create_notification_layout) as mock_create:
                coordinator._render_display()
                mock_create.assert_not_called()
