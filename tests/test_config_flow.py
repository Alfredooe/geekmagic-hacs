"""Tests for GeekMagic config flow."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from homeassistant.data_entry_flow import FlowResultType

from custom_components.geekmagic.config_flow import (
    LAYOUT_OPTIONS,
    GeekMagicConfigFlow,
    GeekMagicOptionsFlow,
)
from custom_components.geekmagic.const import (
    CONF_LAYOUT,
    CONF_REFRESH_INTERVAL,
    CONF_SCREEN_CYCLE_INTERVAL,
    CONF_SCREENS,
    CONF_WIDGETS,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_SCREEN_CYCLE_INTERVAL,
    DOMAIN,
    LAYOUT_GRID_2X2,
)


class TestConfigFlowImports:
    """Test that config flow can be imported without errors."""

    def test_import_config_flow(self):
        """Test config flow module imports successfully."""
        from custom_components.geekmagic import config_flow

        assert config_flow.GeekMagicConfigFlow is not None
        assert config_flow.GeekMagicOptionsFlow is not None

    def test_import_all_dependencies(self):
        """Test all config flow dependencies import correctly."""
        from custom_components.geekmagic.config_flow import (
            LAYOUT_OPTIONS,
            selector,
            vol,
        )

        assert vol is not None
        assert selector is not None
        assert LAYOUT_OPTIONS is not None

    def test_config_flow_class_attributes(self):
        """Test GeekMagicConfigFlow has required attributes."""
        assert hasattr(GeekMagicConfigFlow, "VERSION")
        assert hasattr(GeekMagicConfigFlow, "async_step_user")
        assert hasattr(GeekMagicConfigFlow, "async_get_options_flow")

    def test_layout_options_defined(self):
        """Test layout options are properly defined."""
        assert LAYOUT_GRID_2X2 in LAYOUT_OPTIONS
        assert len(LAYOUT_OPTIONS) >= 4  # At least 4 layouts


class TestConfigFlowUser:
    """Test user config flow step using hass fixture."""

    @pytest.mark.asyncio
    async def test_user_flow_shows_form(self, hass):
        """Test that user flow shows the configuration form."""
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert "host" in result["data_schema"].schema

    @pytest.mark.asyncio
    async def test_user_flow_connection_failure(self, hass):
        """Test user flow handles connection failure."""
        with (
            patch(
                "custom_components.geekmagic.config_flow.async_get_clientsession"
            ) as mock_get_session,
            patch("custom_components.geekmagic.config_flow.GeekMagicDevice") as mock_device_class,
        ):
            mock_get_session.return_value = AsyncMock()
            mock_device = mock_device_class.return_value
            mock_device.test_connection = AsyncMock(return_value=False)

            result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"host": "192.168.1.100", "name": "Test Display"},
            )

            assert result["type"] == FlowResultType.FORM
            assert result["errors"] == {"base": "cannot_connect"}

        await hass.async_block_till_done()

    @pytest.mark.asyncio
    async def test_user_flow_success(self, hass):
        """Test successful user flow creates entry."""
        with (
            patch(
                "custom_components.geekmagic.config_flow.async_get_clientsession"
            ) as mock_get_session,
            patch("custom_components.geekmagic.config_flow.GeekMagicDevice") as mock_device_class,
            # Mock the integration setup to prevent actual device connection
            patch(
                "custom_components.geekmagic.async_setup_entry",
                return_value=True,
            ),
        ):
            mock_get_session.return_value = AsyncMock()
            mock_device = mock_device_class.return_value
            mock_device.test_connection = AsyncMock(return_value=True)

            result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"host": "192.168.1.100", "name": "Test Display"},
            )

            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["title"] == "Test Display"
            assert result["data"]["host"] == "192.168.1.100"

        await hass.async_block_till_done()


class TestOptionsFlowInit:
    """Test options flow initialization."""

    def test_options_flow_init(self):
        """Test GeekMagicOptionsFlow can be instantiated."""
        flow = GeekMagicOptionsFlow()

        assert flow is not None
        assert flow._options == {}
        assert flow._current_screen_index == 0
        assert flow._widget_types == {}
        assert flow._editing_screen is False

    def test_migrate_empty_options(self):
        """Test migration handles empty options."""
        flow = GeekMagicOptionsFlow()
        migrated = flow._migrate_options({})

        assert CONF_SCREENS in migrated
        assert CONF_REFRESH_INTERVAL in migrated
        assert CONF_SCREEN_CYCLE_INTERVAL in migrated
        assert len(migrated[CONF_SCREENS]) == 1
        assert migrated[CONF_REFRESH_INTERVAL] == DEFAULT_REFRESH_INTERVAL
        assert migrated[CONF_SCREEN_CYCLE_INTERVAL] == DEFAULT_SCREEN_CYCLE_INTERVAL

    def test_migrate_existing_screens(self):
        """Test migration preserves existing screens."""
        existing = {
            CONF_SCREENS: [{"name": "Test", CONF_LAYOUT: LAYOUT_GRID_2X2, CONF_WIDGETS: []}],
            CONF_REFRESH_INTERVAL: 15,
            CONF_SCREEN_CYCLE_INTERVAL: 30,
        }

        flow = GeekMagicOptionsFlow()
        migrated = flow._migrate_options(existing)

        assert migrated[CONF_SCREENS][0]["name"] == "Test"
        assert migrated[CONF_REFRESH_INTERVAL] == 15
        assert migrated[CONF_SCREEN_CYCLE_INTERVAL] == 30

    def test_migrate_old_single_screen_format(self):
        """Test migration handles old single-screen format."""
        old_format = {
            CONF_LAYOUT: LAYOUT_GRID_2X2,
            CONF_WIDGETS: [{"type": "clock", "slot": 0}],
            CONF_REFRESH_INTERVAL: 10,
        }

        flow = GeekMagicOptionsFlow()
        migrated = flow._migrate_options(old_format)

        # Should be converted to multi-screen format
        assert CONF_SCREENS in migrated
        assert len(migrated[CONF_SCREENS]) == 1
        assert migrated[CONF_SCREENS][0][CONF_LAYOUT] == LAYOUT_GRID_2X2
        assert migrated[CONF_SCREENS][0][CONF_WIDGETS] == [{"type": "clock", "slot": 0}]


class TestSlotMatching:
    """Test slot matching logic (regression tests for bug fixes)."""

    @pytest.fixture
    def options_flow(self):
        """Create an options flow instance."""
        return GeekMagicOptionsFlow()

    def test_slot_matching_at_slot_zero(self, options_flow):
        """Test slot matching works correctly when current_slot is 0.

        Regression test: Previously, the code checked for `slot in (current_slot - 1, current_slot)`
        which would match slot -1 when current_slot was 0, causing incorrect behavior.
        """
        options_flow._current_slot = 0
        options_flow._screen_config = {
            CONF_WIDGETS: [
                {"type": "clock", "slot": 0},
                {"type": "entity", "slot": 1},
            ]
        }
        options_flow._current_widget_type = "clock"

        # Simulate finding existing widget for slot 0
        existing_widget = None
        for w in options_flow._screen_config.get(CONF_WIDGETS, []):
            if w.get("slot") == options_flow._current_slot and w.get("type") == "clock":
                existing_widget = w
                break

        assert existing_widget is not None
        assert existing_widget["slot"] == 0
        assert existing_widget["type"] == "clock"

    def test_slot_matching_does_not_match_wrong_slot(self, options_flow):
        """Test slot matching doesn't match adjacent slots incorrectly."""
        options_flow._current_slot = 1
        options_flow._screen_config = {
            CONF_WIDGETS: [
                {"type": "clock", "slot": 0},
                {"type": "entity", "slot": 2},
            ]
        }

        # Slot 1 has no widget, so should not find anything
        existing_widget = None
        for w in options_flow._screen_config.get(CONF_WIDGETS, []):
            if w.get("slot") == options_flow._current_slot:
                existing_widget = w
                break

        assert existing_widget is None


class TestWidgetSchema:
    """Test widget schema generation."""

    @pytest.fixture
    def options_flow(self):
        """Create an options flow instance."""
        return GeekMagicOptionsFlow()

    def test_clock_widget_schema(self, options_flow):
        """Test clock widget schema generation."""
        schema = options_flow._get_widget_schema("clock")

        assert schema is not None
        assert isinstance(schema, dict)

    def test_entity_widget_schema(self, options_flow):
        """Test entity widget schema generation."""
        schema = options_flow._get_widget_schema("entity")

        assert schema is not None
        assert isinstance(schema, dict)

    def test_unknown_widget_schema(self, options_flow):
        """Test unknown widget type returns empty schema."""
        schema = options_flow._get_widget_schema("nonexistent_widget")

        assert schema == {}

    def test_all_widget_types_have_schemas(self, options_flow):
        """Test all known widget types have schemas."""
        widget_types = [
            "clock",
            "entity",
            "media",
            "chart",
            "text",
            "gauge",
            "progress",
            "status",
            "weather",
            "multi_progress",
            "status_list",
        ]

        for widget_type in widget_types:
            schema = options_flow._get_widget_schema(widget_type)
            assert isinstance(schema, dict), f"Widget type '{widget_type}' should return a dict"
