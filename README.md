# Google Maps Coordinate Extractor

A Python tool to extract precise latitude and longitude coordinates from Google Maps URLs or search queries. Works for any type of location - restaurants, hotels, landmarks, retail stores, and more.

## Features

- 🎯 **Pin-Precise Extraction** - Gets exact coordinates from Google Maps pins
- 🔄 **Multiple Strategies** - Direct URL extraction + search fallback
- 📊 **Progress Tracking** - Real-time progress bar with ETA
- 💾 **Multiple Formats** - Export to JSON or CSV
- 🔁 **Retry Mechanism** - Automatic retries with exponential backoff
- ✅ **Data Validation** - Validates coordinate ranges and quality
- 📝 **Comprehensive Logging** - Configurable log levels and file output
- 🌍 **Location Context** - Optional context for better search results
- ⚡ **Performance Metrics** - Track processing time and rate

## Installation

### Prerequisites

- Python 3.7+
- Google Chrome browser

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/gmaps-coordinate-extractor.git
cd gmaps-coordinate-extractor

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. **Prepare your data** - Copy `places_template.json` and add your locations:

```json
{
  "place_001": {
    "key": "place_001",
    "name": "Central Park",
    "gmaps": "https://maps.app.goo.gl/xyz",
    "latlong": {
      "lat": "",
      "long": ""
    }
  }
}
```

2. **Run the extractor**:

```bash
python3 fetch_coordinates.py your_places.json
```

3. **View results** - Coordinates are automatically added to your JSON file!

## Usage Examples

### Basic Extraction

```bash
# Extract missing coordinates
python3 fetch_coordinates.py places.json

# Force update all entries
python3 fetch_coordinates.py places.json --force
```

### With Location Context

```bash
# Add location context for better search results
python3 fetch_coordinates.py restaurants.json --context "New York"
python3 fetch_coordinates.py hotels.json --context "Paris"
```

### Export to CSV

```bash
# Generate CSV for spreadsheets/GIS tools
python3 fetch_coordinates.py places.json --output-format csv
```

### Advanced Options

```bash
# Full configuration
python3 fetch_coordinates.py places.json \
  --output-format csv \
  --context "London" \
  --max-retries 5 \
  --retry-delay 10 \
  --log-level DEBUG \
  --log-file extraction.log
```

## Command-Line Options

| Option            | Type     | Default | Description                      |
| ----------------- | -------- | ------- | -------------------------------- |
| `input_file`      | Required | -       | Path to JSON file                |
| `--force`         | Flag     | False   | Update all entries               |
| `--output-format` | Choice   | json    | json or csv                      |
| `--context`       | String   | None    | Location context (e.g., "Tokyo") |
| `--max-retries`   | Integer  | 3       | Retry attempts                   |
| `--retry-delay`   | Integer  | 5       | Initial delay (seconds)          |
| `--log-level`     | Choice   | INFO    | DEBUG/INFO/WARNING/ERROR         |
| `--log-file`      | String   | None    | Log file path                    |

## Output Format

### JSON Output

```json
{
  "place_001": {
    "key": "place_001",
    "name": "Central Park",
    "gmaps": "https://maps.app.goo.gl/xyz",
    "latlong": {
      "lat": "40.785091",
      "long": "-73.968285"
    }
  }
}
```

### CSV Output

```csv
key,name,gmaps_url,latitude,longitude
place_001,Central Park,https://maps.app.goo.gl/xyz,40.785091,-73.968285
```

## Use Cases

- 🍽️ **Restaurants** - Build location databases for food delivery apps
- 🏨 **Hotels** - Create travel booking platforms
- 🏪 **Retail** - Map store locations for chain businesses
- 🏛️ **Tourism** - Develop city guide applications
- 🏢 **Real Estate** - Geocode property listings
- 📍 **Any Location-Based Project**

## Performance

- **Average Speed**: ~9 locations/minute
- **Accuracy**: Pin-precise coordinates from Google Maps
- **Reliability**: Automatic retry with exponential backoff
- **Validation**: Built-in coordinate range and quality checks

## Troubleshooting

### CAPTCHA Detection

If you encounter CAPTCHAs, the tool will automatically:

- Detect and log the issue
- Retry with exponential backoff
- Fall back to search-based extraction

**Solutions**:

- Reduce processing speed with `--retry-delay 10`
- Process in smaller batches
- Use a VPN or different network

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### ChromeDriver Issues

The tool uses `webdriver-manager` to automatically download and manage ChromeDriver. If issues occur:

- Ensure Google Chrome is installed
- Check internet connectivity
- Clear cache: `rm -rf ~/.wdm`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - feel free to use this tool for any purpose!

## Acknowledgments

- Uses Selenium WebDriver for browser automation
- Built with Python's robust ecosystem
- Inspired by the need for accessible geocoding tools

---

**Made with ❤️ for the open-source community**
