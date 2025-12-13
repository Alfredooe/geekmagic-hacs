# GeekMagic Display for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for GeekMagic displays (SmallTV Pro and similar ESP8266-based devices).

## Dashboard Samples

<p align="center">
  <img src="samples/01_system_monitor.png" alt="System Monitor" width="120">
  <img src="samples/02_smart_home.png" alt="Smart Home" width="120">
  <img src="samples/03_weather.png" alt="Weather" width="120">
  <img src="samples/04_server_stats.png" alt="Server Stats" width="120">
</p>

<p align="center">
  <img src="samples/05_media_player.png" alt="Media Player" width="120">
  <img src="samples/06_energy_monitor.png" alt="Energy Monitor" width="120">
  <img src="samples/07_fitness.png" alt="Fitness Tracker" width="120">
  <img src="samples/08_clock_dashboard.png" alt="Clock Dashboard" width="120">
</p>

<p align="center">
  <img src="samples/09_network_monitor.png" alt="Network Monitor" width="120">
  <img src="samples/10_thermostat.png" alt="Thermostat" width="120">
  <img src="samples/11_batteries.png" alt="Batteries" width="120">
  <img src="samples/12_security.png" alt="Security" width="120">
</p>

## Features

- **12 widget types**: Clock, entity, media, chart, text, gauge, progress, weather, status, camera, and more
- **7 layout options**: Grid (2x2, 2x3, 3x3), hero, split (vertical/horizontal), three-column
- **Pure Python rendering**: Uses Pillow for image generation (no browser required)
- **Configurable refresh**: Updates every 5-300 seconds
- **Easy setup**: Add device by IP address through the UI

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Custom repositories"
3. Add this repository URL
4. Install "GeekMagic Display"
5. Restart Home Assistant

### Manual

1. Copy `custom_components/geekmagic` to your Home Assistant's `custom_components` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "GeekMagic"
4. Enter your device's IP address

### Initial Setup

After adding the integration, your device will display a welcome screen with live data until you configure a dashboard:

<p align="center">
  <img src="samples/00_welcome_screen.png" alt="Welcome Screen" width="180">
</p>

The welcome screen shows:
- **Current time and date** - Updates every refresh interval
- **Home Assistant version** - Your HA instance version
- **Entity count** - Total entities in your system
- **Configure hint** - Reminder to set up your dashboard

Go to the integration options to add screens and widgets. Changes are applied immediately to the device.

---

## Widgets

### Available Widget Types

| Widget | Type | Description |
|--------|------|-------------|
| Camera | `camera` | Camera snapshot display |
| Clock | `clock` | Current time and date |
| Entity | `entity` | Any Home Assistant entity value |
| Media | `media` | Now playing from media player |
| Chart | `chart` | Sparkline chart from entity history |
| Text | `text` | Static or dynamic text |
| Gauge | `gauge` | Progress bar, ring, or arc gauge |
| Progress | `progress` | Goal tracking with progress bar |
| Multi-Progress | `multi_progress` | Multiple progress items |
| Weather | `weather` | Weather with forecast |
| Status | `status` | Binary sensor indicator |
| Status List | `status_list` | Multiple status indicators |

### Widget Examples

#### Camera

Displays a camera entity snapshot.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_label` | bool | `false` | Show camera name label |
| `fit` | string | `"contain"` | `"contain"` (preserve aspect) or `"cover"` (fill) |

#### Clock
<img src="samples/widgets/widget_clock.png" alt="Clock Widget" width="120">

Displays current time and date.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_date` | bool | `true` | Show date below time |
| `show_seconds` | bool | `false` | Include seconds |
| `time_format` | string | `"24h"` | `"24h"` or `"12h"` |

#### Entity
<img src="samples/widgets/widget_entity.png" alt="Entity Widget" width="100">
<img src="samples/widgets/widget_entity_icon.png" alt="Entity Widget with Icon" width="100">

Displays any Home Assistant entity state.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_name` | bool | `true` | Show entity name |
| `show_unit` | bool | `true` | Show unit of measurement |
| `icon` | string | - | Icon name (e.g., `"drop"`, `"bolt"`) |
| `show_panel` | bool | `false` | Draw panel background |

#### Media Player
<img src="samples/widgets/widget_media.png" alt="Media Widget" width="200">

Displays now-playing information from a media player.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_artist` | bool | `true` | Show artist name |
| `show_album` | bool | `false` | Show album name |
| `show_progress` | bool | `true` | Show progress bar |

#### Chart
<img src="samples/widgets/widget_chart.png" alt="Chart Widget" width="120">

Displays sparkline chart from entity history.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `hours` | int | `24` | Hours of history |
| `show_value` | bool | `true` | Show current value |
| `show_range` | bool | `true` | Show min/max range |

#### Text
<img src="samples/widgets/widget_text.png" alt="Text Widget" width="120">

Displays static or dynamic text.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `text` | string | - | Static text to display |
| `size` | string | `"regular"` | `"small"`, `"regular"`, `"large"`, `"xlarge"` |
| `align` | string | `"center"` | `"left"`, `"center"`, `"right"` |

#### Gauge
<img src="samples/widgets/widget_gauge_bar.png" alt="Gauge Bar" width="160">
<img src="samples/widgets/widget_gauge_ring.png" alt="Gauge Ring" width="100">
<img src="samples/widgets/widget_gauge_arc.png" alt="Gauge Arc" width="120">

Displays value as bar, ring, or arc gauge.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `style` | string | `"bar"` | `"bar"`, `"ring"`, or `"arc"` |
| `min` | float | `0` | Minimum value |
| `max` | float | `100` | Maximum value |
| `icon` | string | - | Icon name |
| `unit` | string | - | Unit of measurement |
| `attribute` | string | - | Read from entity attribute |

#### Progress
<img src="samples/widgets/widget_progress.png" alt="Progress Widget" width="180">

Displays progress toward a goal.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `target` | float | `100` | Goal value |
| `unit` | string | - | Unit of measurement |
| `show_target` | bool | `true` | Show "current/target" |
| `icon` | string | - | Icon name |

#### Multi-Progress
<img src="samples/widgets/widget_multi_progress.png" alt="Multi-Progress Widget" width="180">

Displays multiple progress items (fitness tracking style).

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | string | - | Widget title |
| `items` | list | - | List of progress configs |

Each item in `items`:
```yaml
- entity_id: sensor.calories
  label: "Move"
  target: 800
  color: [255, 0, 0]
  icon: "flame"
  unit: "cal"
```

#### Weather
<img src="samples/widgets/widget_weather.png" alt="Weather Widget" width="180">

Displays weather with forecast.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_forecast` | bool | `true` | Show forecast days |
| `forecast_days` | int | `3` | Number of forecast days |
| `show_humidity` | bool | `true` | Show humidity |
| `show_wind` | bool | `false` | Show wind speed |

#### Status
<img src="samples/widgets/widget_status.png" alt="Status Widget" width="140">

Displays binary sensor with colored indicator.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `on_color` | tuple | lime | Color when on |
| `off_color` | tuple | red | Color when off |
| `on_text` | string | `"ON"` | Text when on |
| `off_text` | string | `"OFF"` | Text when off |
| `icon` | string | - | Icon name |

#### Status List
<img src="samples/widgets/widget_status_list.png" alt="Status List Widget" width="160">

Displays list of binary sensors.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | string | - | List title |
| `entities` | list | - | List of entity IDs or (id, label) tuples |
| `on_color` | tuple | lime | Color when on |
| `off_color` | tuple | red | Color when off |

---

## Layouts

### Available Layout Types

| Layout | Type | Slots | Description |
|--------|------|-------|-------------|
| Grid 2x2 | `grid_2x2` | 4 | 2x2 grid of equal widgets |
| Grid 2x3 | `grid_2x3` | 6 | 2 rows, 3 columns |
| Grid 3x3 | `grid_3x3` | 9 | 3x3 grid (compact) |
| Hero | `hero` | 4 | Large hero + 3 footer widgets |
| Split Vertical | `split` | 2 | Left/right panels |
| Split Horizontal | `split` | 2 | Top/bottom panels |
| Three Column | `three_column` | 3 | 3 vertical columns |

### Layout Examples

#### Grid 2x2
<img src="samples/layouts/layout_grid_2x2.png" alt="Grid 2x2" width="180">

4 equal slots in a 2x2 arrangement. Each slot is ~112x112px.

```
+-------+-------+
|   0   |   1   |
+-------+-------+
|   2   |   3   |
+-------+-------+
```

**Best for**: 4 medium widgets (gauges, entities)

#### Grid 2x3
<img src="samples/layouts/layout_grid_2x3.png" alt="Grid 2x3" width="180">

6 slots in 2 rows, 3 columns. Each slot is ~75x112px.

```
+-----+-----+-----+
|  0  |  1  |  2  |
+-----+-----+-----+
|  3  |  4  |  5  |
+-----+-----+-----+
```

**Best for**: 6 entity values, compact dashboard

#### Grid 3x3
<img src="samples/layouts/layout_grid_3x3.png" alt="Grid 3x3" width="180">

9 slots in 3x3 arrangement. Each slot is ~74x74px.

```
+----+----+----+
| 0  | 1  | 2  |
+----+----+----+
| 3  | 4  | 5  |
+----+----+----+
| 6  | 7  | 8  |
+----+----+----+
```

**Best for**: Many small indicators, temperature overview

#### Hero Layout
<img src="samples/layouts/layout_hero.png" alt="Hero Layout" width="180">

Large hero slot (70% height) + 3 footer widgets.

```
+-------------------+
|                   |
|    HERO (0)       |
|                   |
+-----+------+------+
|  1  |   2  |   3  |
+-----+------+------+
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `footer_slots` | int | `3` | Number of footer widgets |
| `hero_ratio` | float | `0.7` | Hero height ratio (0.5-0.8) |

**Best for**: Weather + stats, clock + info, media player

#### Split Vertical
<img src="samples/layouts/layout_split_vertical.png" alt="Split Vertical" width="180">

Two side-by-side panels (left/right).

```
+----------+----------+
|          |          |
|    0     |    1     |
|          |          |
+----------+----------+
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `horizontal` | bool | `false` | Set to `false` for vertical split |
| `ratio` | float | `0.5` | Left panel ratio (0.2-0.8) |

**Best for**: Clock + chart, media + status

#### Split Horizontal
<img src="samples/layouts/layout_split_horizontal.png" alt="Split Horizontal" width="180">

Two stacked panels (top/bottom).

```
+---------------------+
|         0           |
+---------------------+
|         1           |
+---------------------+
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `horizontal` | bool | `true` | Set to `true` for horizontal split |
| `ratio` | float | `0.5` | Top panel ratio (0.2-0.8) |

**Best for**: Clock + status list, weather + entities

#### Three Column
<img src="samples/layouts/layout_three_column.png" alt="Three Column" width="180">

Three vertical columns with customizable widths.

```
+------+------+------+
|      |      |      |
|  0   |  1   |  2   |
|      |      |      |
+------+------+------+
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ratios` | tuple | `(0.33, 0.34, 0.33)` | Column width ratios |

**Best for**: 3 gauges, 3 status lists, comparison view

---

## Services

| Service | Description |
|---------|-------------|
| `geekmagic.refresh` | Force immediate display update |
| `geekmagic.brightness` | Set display brightness (0-100) |

## Device Compatibility

Tested with:
- GeekMagic SmallTV Pro (240x240, ESP8266)

Should work with any GeekMagic device that supports the `/doUpload` HTTP API.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and type check
uv run ruff check .
uv run ty check

# Run all checks (pre-commit)
uv run pre-commit run --all-files

# Generate sample images
uv run python scripts/generate_samples.py
uv run python scripts/generate_widget_samples.py
uv run python scripts/generate_layout_samples.py
```

## License

MIT
