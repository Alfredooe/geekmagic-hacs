"""Tests for widget classes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unittest.mock import MagicMock

import pytest

from custom_components.geekmagic.const import COLOR_CYAN
from custom_components.geekmagic.render_context import RenderContext
from custom_components.geekmagic.renderer import Renderer
from custom_components.geekmagic.widgets.base import WidgetConfig
from custom_components.geekmagic.widgets.chart import ChartWidget
from custom_components.geekmagic.widgets.clock import ClockWidget
from custom_components.geekmagic.widgets.entity import EntityWidget
from custom_components.geekmagic.widgets.gauge import GaugeWidget
from custom_components.geekmagic.widgets.media import MediaWidget
from custom_components.geekmagic.widgets.progress import MultiProgressWidget, ProgressWidget
from custom_components.geekmagic.widgets.status import StatusListWidget, StatusWidget
from custom_components.geekmagic.widgets.text import TextWidget
from custom_components.geekmagic.widgets.weather import WeatherWidget


@pytest.fixture
def renderer():
    """Create a renderer instance."""
    return Renderer()


@pytest.fixture
def canvas(renderer):
    """Create a canvas for drawing."""
    return renderer.create_canvas()


@pytest.fixture
def rect():
    """Standard widget rectangle."""
    return (10, 10, 110, 110)


@pytest.fixture
def render_context(renderer, canvas, rect):
    """Create a RenderContext for widgets."""
    _, draw = canvas
    return RenderContext(draw, rect, renderer)


@pytest.fixture
def mock_entity_state():
    """Create a mock entity state."""
    state = MagicMock()
    state.state = "23.5"
    state.entity_id = "sensor.temperature"
    state.attributes = {
        "friendly_name": "Temperature",
        "unit_of_measurement": "°C",
    }
    return state


class TestWidgetConfig:
    """Tests for WidgetConfig."""

    def test_create_config(self):
        """Test creating widget config."""
        config = WidgetConfig(
            widget_type="clock",
            slot=0,
        )
        assert config.widget_type == "clock"
        assert config.slot == 0
        assert config.entity_id is None

    def test_create_config_with_options(self):
        """Test creating widget config with all options."""
        config = WidgetConfig(
            widget_type="entity",
            slot=1,
            entity_id="sensor.temp",
            label="Temperature",
            color=COLOR_CYAN,
            options={"show_name": True},
        )
        assert config.entity_id == "sensor.temp"
        assert config.label == "Temperature"
        assert config.color == COLOR_CYAN
        assert config.options["show_name"] is True


class TestClockWidget:
    """Tests for ClockWidget."""

    def test_init(self):
        """Test clock widget initialization."""
        config = WidgetConfig(widget_type="clock", slot=0)
        widget = ClockWidget(config)
        assert widget.show_date is True
        assert widget.show_seconds is False

    def test_init_with_options(self):
        """Test clock widget with custom options."""
        config = WidgetConfig(
            widget_type="clock",
            slot=0,
            options={"show_date": False, "show_seconds": True, "time_format": "12h"},
        )
        widget = ClockWidget(config)
        assert widget.show_date is False
        assert widget.show_seconds is True
        assert widget.time_format == "12h"

    def test_get_entities(self):
        """Test that clock has no entity dependencies."""
        config = WidgetConfig(widget_type="clock", slot=0)
        widget = ClockWidget(config)
        assert widget.get_entities() == []

    def test_render(self, renderer, canvas, rect):
        """Test clock rendering."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(widget_type="clock", slot=0)
        widget = ClockWidget(config)

        # Should not raise exception
        widget.render(ctx)

        # Verify image is valid
        assert img.size == (480, 480)

    def test_render_24h(self, renderer, canvas, rect):
        """Test clock with 24-hour format."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(
            widget_type="clock",
            slot=0,
            options={"time_format": "24h"},
        )
        widget = ClockWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)

    def test_render_12h(self, renderer, canvas, rect):
        """Test clock with 12-hour format."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(
            widget_type="clock",
            slot=0,
            options={"time_format": "12h"},
        )
        widget = ClockWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)


class TestEntityWidget:
    """Tests for EntityWidget."""

    def test_init(self):
        """Test entity widget initialization."""
        config = WidgetConfig(
            widget_type="entity",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = EntityWidget(config)
        assert widget.show_name is True
        assert widget.show_unit is True

    def test_get_entities(self):
        """Test entity dependencies."""
        config = WidgetConfig(
            widget_type="entity",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = EntityWidget(config)
        assert widget.get_entities() == ["sensor.temperature"]

    def test_render_without_hass(self, renderer, canvas, rect):
        """Test rendering without Home Assistant (placeholder)."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(
            widget_type="entity",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = EntityWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)

    def test_render_with_entity(self, renderer, canvas, rect, hass, mock_entity_state):
        """Test rendering with entity state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        # Set up the entity state in hass
        hass.states.async_set(
            "sensor.temperature",
            "23.5",
            {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
        )

        config = WidgetConfig(
            widget_type="entity",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = EntityWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)


class TestMediaWidget:
    """Tests for MediaWidget."""

    def test_init(self):
        """Test media widget initialization."""
        config = WidgetConfig(
            widget_type="media",
            slot=0,
            entity_id="media_player.living_room",
        )
        widget = MediaWidget(config)
        assert widget.show_artist is True
        assert widget.show_progress is True

    def test_render_idle(self, renderer, canvas, rect, hass):
        """Test rendering idle state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)

        # Set up media player state in hass
        hass.states.async_set("media_player.living_room", "idle", {})

        config = WidgetConfig(
            widget_type="media",
            slot=0,
            entity_id="media_player.living_room",
        )
        widget = MediaWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_playing(self, renderer, canvas, rect, hass):
        """Test rendering playing state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)

        # Set up media player state in hass
        hass.states.async_set(
            "media_player.living_room",
            "playing",
            {
                "media_title": "Test Song",
                "media_artist": "Test Artist",
                "media_position": 60,
                "media_duration": 180,
            },
        )

        config = WidgetConfig(
            widget_type="media",
            slot=0,
            entity_id="media_player.living_room",
        )
        widget = MediaWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_format_time(self):
        """Test time formatting."""
        config = WidgetConfig(widget_type="media", slot=0)
        widget = MediaWidget(config)

        assert widget._format_time(0) == "0:00"
        assert widget._format_time(65) == "1:05"
        assert widget._format_time(3661) == "1:01:01"


class TestChartWidget:
    """Tests for ChartWidget."""

    def test_init(self):
        """Test chart widget initialization."""
        config = WidgetConfig(
            widget_type="chart",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = ChartWidget(config)
        assert widget.hours == 24
        assert widget.show_value is True

    def test_set_history(self):
        """Test setting history data."""
        config = WidgetConfig(widget_type="chart", slot=0)
        widget = ChartWidget(config)

        data = [10, 15, 12, 18, 22]
        widget.set_history(data)
        assert widget._history_data == data

    def test_render_no_data(self, renderer, canvas, rect):
        """Test rendering without data."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(
            widget_type="chart",
            slot=0,
            label="Temperature",
        )
        widget = ChartWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)

    def test_render_with_data(self, renderer, canvas, rect, hass, mock_entity_state):
        """Test rendering with history data."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        # Set up the entity state in hass
        hass.states.async_set(
            "sensor.temperature",
            "23.5",
            {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
        )

        config = WidgetConfig(
            widget_type="chart",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = ChartWidget(config)
        widget.set_history([20.0, 21.5, 22.0, 21.0, 23.5, 24.0, 23.0])
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_is_binary_data_true(self):
        """Test binary data detection returns true for 0/1 data."""
        config = WidgetConfig(widget_type="chart", slot=0)
        widget = ChartWidget(config)
        widget.set_history([0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0])
        assert widget._is_binary_data() is True

    def test_is_binary_data_false(self):
        """Test binary data detection returns false for numeric data."""
        config = WidgetConfig(widget_type="chart", slot=0)
        widget = ChartWidget(config)
        widget.set_history([20.0, 21.5, 22.0, 21.0, 23.5])
        assert widget._is_binary_data() is False

    def test_is_binary_data_empty(self):
        """Test binary data detection returns false for empty data."""
        config = WidgetConfig(widget_type="chart", slot=0)
        widget = ChartWidget(config)
        assert widget._is_binary_data() is False

    def test_render_binary_data(self, renderer, canvas, rect, hass):
        """Test rendering with binary sensor data uses timeline bar."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set(
            "binary_sensor.door",
            "off",
            {"friendly_name": "Door"},
        )

        config = WidgetConfig(
            widget_type="chart",
            slot=0,
            entity_id="binary_sensor.door",
            label="Door",
        )
        widget = ChartWidget(config)
        # Binary data: 0=closed, 1=open
        widget.set_history([0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0])
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)


class TestTextWidget:
    """Tests for TextWidget."""

    def test_init(self):
        """Test text widget initialization."""
        config = WidgetConfig(
            widget_type="text",
            slot=0,
            options={"text": "Hello World"},
        )
        widget = TextWidget(config)
        assert widget.text == "Hello World"
        assert widget.size == "regular"
        assert widget.align == "center"

    def test_render_static_text(self, renderer, canvas, rect):
        """Test rendering static text."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        config = WidgetConfig(
            widget_type="text",
            slot=0,
            options={"text": "Hello", "size": "large"},
        )
        widget = TextWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)

    def test_render_entity_text(self, renderer, canvas, rect, hass, mock_entity_state):
        """Test rendering entity state as text."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        # Set up the entity state in hass
        hass.states.async_set(
            "sensor.temperature",
            "23.5",
            {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
        )

        config = WidgetConfig(
            widget_type="text",
            slot=0,
            entity_id="sensor.temperature",
        )
        widget = TextWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_different_alignments(self, renderer, rect):
        """Test different text alignments."""
        for align in ["left", "center", "right"]:
            img, draw = renderer.create_canvas()
            ctx = RenderContext(draw, rect, renderer)
            config = WidgetConfig(
                widget_type="text",
                slot=0,
                options={"text": "Test", "align": align},
            )
            widget = TextWidget(config)
            widget.render(ctx)
            assert img.size == (480, 480)

    def test_different_sizes(self, renderer, rect):
        """Test different text sizes."""
        for size in ["small", "regular", "large", "xlarge"]:
            img, draw = renderer.create_canvas()
            ctx = RenderContext(draw, rect, renderer)
            config = WidgetConfig(
                widget_type="text",
                slot=0,
                options={"text": "Test", "size": size},
            )
            widget = TextWidget(config)
            widget.render(ctx)
            assert img.size == (480, 480)


class TestGaugeWidget:
    """Tests for GaugeWidget."""

    def test_init(self):
        """Test gauge widget initialization."""
        config = WidgetConfig(
            widget_type="gauge",
            slot=0,
            entity_id="sensor.cpu",
        )
        widget = GaugeWidget(config)
        assert widget.style == "bar"
        assert widget.min_value == 0
        assert widget.max_value == 100
        assert widget.show_value is True

    def test_init_with_options(self):
        """Test gauge widget with custom options."""
        config = WidgetConfig(
            widget_type="gauge",
            slot=0,
            entity_id="sensor.cpu",
            options={"style": "ring", "min": 10, "max": 50, "unit": "%"},
        )
        widget = GaugeWidget(config)
        assert widget.style == "ring"
        assert widget.min_value == 10
        assert widget.max_value == 50
        assert widget.unit == "%"

    def test_render_bar_style(self, renderer, canvas, rect, hass):
        """Test rendering bar gauge."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("sensor.cpu", "75", {"friendly_name": "CPU"})

        config = WidgetConfig(
            widget_type="gauge",
            slot=0,
            entity_id="sensor.cpu",
            options={"style": "bar"},
        )
        widget = GaugeWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_ring_style(self, renderer, canvas, rect, hass):
        """Test rendering ring gauge."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("sensor.cpu", "50", {"friendly_name": "CPU"})

        config = WidgetConfig(
            widget_type="gauge",
            slot=0,
            entity_id="sensor.cpu",
            options={"style": "ring"},
        )
        widget = GaugeWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_arc_style(self, renderer, canvas, rect, hass):
        """Test rendering arc gauge."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("sensor.cpu", "25", {"friendly_name": "CPU"})

        config = WidgetConfig(
            widget_type="gauge",
            slot=0,
            entity_id="sensor.cpu",
            options={"style": "arc"},
        )
        widget = GaugeWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_without_entity(self, renderer, canvas, rect):
        """Test rendering without entity shows placeholder."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)

        config = WidgetConfig(widget_type="gauge", slot=0)
        widget = GaugeWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)


class TestProgressWidget:
    """Tests for ProgressWidget."""

    def test_init(self):
        """Test progress widget initialization."""
        config = WidgetConfig(
            widget_type="progress",
            slot=0,
            entity_id="sensor.steps",
        )
        widget = ProgressWidget(config)
        assert widget.target == 100
        assert widget.show_target is True

    def test_init_with_options(self):
        """Test progress widget with custom options."""
        config = WidgetConfig(
            widget_type="progress",
            slot=0,
            entity_id="sensor.steps",
            options={"target": 10000, "unit": "steps", "show_target": False},
        )
        widget = ProgressWidget(config)
        assert widget.target == 10000
        assert widget.unit == "steps"
        assert widget.show_target is False

    def test_render_with_entity(self, renderer, canvas, rect, hass):
        """Test rendering with entity state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set(
            "sensor.steps", "5000", {"friendly_name": "Steps", "unit_of_measurement": "steps"}
        )

        config = WidgetConfig(
            widget_type="progress",
            slot=0,
            entity_id="sensor.steps",
            options={"target": 10000},
        )
        widget = ProgressWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_without_entity(self, renderer, canvas, rect):
        """Test rendering without entity."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)

        config = WidgetConfig(widget_type="progress", slot=0)
        widget = ProgressWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)


class TestMultiProgressWidget:
    """Tests for MultiProgressWidget."""

    def test_init(self):
        """Test multi-progress widget initialization."""
        config = WidgetConfig(
            widget_type="multi_progress",
            slot=0,
            options={"items": [], "title": "Fitness"},
        )
        widget = MultiProgressWidget(config)
        assert widget.items == []
        assert widget.title == "Fitness"

    def test_get_entities(self):
        """Test entity dependencies."""
        config = WidgetConfig(
            widget_type="multi_progress",
            slot=0,
            options={
                "items": [
                    {"entity_id": "sensor.steps", "target": 10000},
                    {"entity_id": "sensor.calories", "target": 500},
                ]
            },
        )
        widget = MultiProgressWidget(config)
        assert "sensor.steps" in widget.get_entities()
        assert "sensor.calories" in widget.get_entities()

    def test_render_with_items(self, renderer, canvas, rect, hass):
        """Test rendering with multiple items."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("sensor.steps", "5000", {"friendly_name": "Steps"})
        hass.states.async_set("sensor.calories", "300", {"friendly_name": "Calories"})

        config = WidgetConfig(
            widget_type="multi_progress",
            slot=0,
            options={
                "title": "Fitness",
                "items": [
                    {"entity_id": "sensor.steps", "target": 10000, "label": "Steps"},
                    {"entity_id": "sensor.calories", "target": 500, "label": "Cal"},
                ],
            },
        )
        widget = MultiProgressWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)


class TestStatusWidget:
    """Tests for StatusWidget."""

    def test_init(self):
        """Test status widget initialization."""
        config = WidgetConfig(
            widget_type="status",
            slot=0,
            entity_id="binary_sensor.door",
        )
        widget = StatusWidget(config)
        assert widget.on_text == "ON"
        assert widget.off_text == "OFF"
        assert widget.show_status_text is True

    def test_init_with_options(self):
        """Test status widget with custom options."""
        config = WidgetConfig(
            widget_type="status",
            slot=0,
            entity_id="binary_sensor.door",
            options={"on_text": "Open", "off_text": "Closed"},
        )
        widget = StatusWidget(config)
        assert widget.on_text == "Open"
        assert widget.off_text == "Closed"

    def test_render_on_state(self, renderer, canvas, rect, hass):
        """Test rendering on state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("binary_sensor.door", "on", {"friendly_name": "Front Door"})

        config = WidgetConfig(
            widget_type="status",
            slot=0,
            entity_id="binary_sensor.door",
        )
        widget = StatusWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_off_state(self, renderer, canvas, rect, hass):
        """Test rendering off state."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("binary_sensor.door", "off", {"friendly_name": "Front Door"})

        config = WidgetConfig(
            widget_type="status",
            slot=0,
            entity_id="binary_sensor.door",
        )
        widget = StatusWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)


class TestStatusListWidget:
    """Tests for StatusListWidget."""

    def test_init(self):
        """Test status list widget initialization."""
        config = WidgetConfig(
            widget_type="status_list",
            slot=0,
            options={"entities": [], "title": "Doors"},
        )
        widget = StatusListWidget(config)
        assert widget.entities == []
        assert widget.title == "Doors"

    def test_get_entities(self):
        """Test entity dependencies."""
        config = WidgetConfig(
            widget_type="status_list",
            slot=0,
            options={"entities": ["binary_sensor.front_door", ["binary_sensor.back_door", "Back"]]},
        )
        widget = StatusListWidget(config)
        entities = widget.get_entities()
        assert "binary_sensor.front_door" in entities
        assert "binary_sensor.back_door" in entities

    def test_render_with_entities(self, renderer, canvas, rect, hass):
        """Test rendering with multiple entities."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set("binary_sensor.front_door", "on", {"friendly_name": "Front"})
        hass.states.async_set("binary_sensor.back_door", "off", {"friendly_name": "Back"})

        config = WidgetConfig(
            widget_type="status_list",
            slot=0,
            options={
                "title": "Doors",
                "entities": ["binary_sensor.front_door", "binary_sensor.back_door"],
            },
        )
        widget = StatusListWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)


class TestWeatherWidget:
    """Tests for WeatherWidget."""

    def test_init(self):
        """Test weather widget initialization."""
        config = WidgetConfig(
            widget_type="weather",
            slot=0,
            entity_id="weather.home",
        )
        widget = WeatherWidget(config)
        assert widget.show_forecast is True
        assert widget.forecast_days == 3
        assert widget.show_humidity is True

    def test_init_with_options(self):
        """Test weather widget with custom options."""
        config = WidgetConfig(
            widget_type="weather",
            slot=0,
            entity_id="weather.home",
            options={"show_forecast": False, "forecast_days": 5, "show_humidity": False},
        )
        widget = WeatherWidget(config)
        assert widget.show_forecast is False
        assert widget.forecast_days == 5
        assert widget.show_humidity is False

    def test_render_without_entity(self, renderer, canvas, rect):
        """Test rendering without entity shows placeholder."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)

        config = WidgetConfig(widget_type="weather", slot=0)
        widget = WeatherWidget(config)
        widget.render(ctx)
        assert img.size == (480, 480)

    def test_render_with_entity(self, renderer, canvas, rect, hass):
        """Test rendering with weather entity."""
        img, draw = canvas
        ctx = RenderContext(draw, rect, renderer)
        hass.states.async_set(
            "weather.home",
            "sunny",
            {
                "friendly_name": "Home",
                "temperature": 22,
                "humidity": 45,
                "forecast": [
                    {"datetime": "Mon", "condition": "sunny", "temperature": 24},
                    {"datetime": "Tue", "condition": "cloudy", "temperature": 20},
                ],
            },
        )

        config = WidgetConfig(
            widget_type="weather",
            slot=0,
            entity_id="weather.home",
        )
        widget = WeatherWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)

    def test_render_compact_mode(self, renderer, hass):
        """Test rendering in compact mode (small container)."""
        img, draw = renderer.create_canvas()
        # Small rect to trigger compact mode
        small_rect = (10, 10, 70, 70)
        ctx = RenderContext(draw, small_rect, renderer)
        hass.states.async_set(
            "weather.home",
            "rainy",
            {"temperature": 15, "humidity": 80},
        )

        config = WidgetConfig(
            widget_type="weather",
            slot=0,
            entity_id="weather.home",
        )
        widget = WeatherWidget(config)
        widget.render(ctx, hass=hass)
        assert img.size == (480, 480)
