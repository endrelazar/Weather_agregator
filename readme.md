# Weather Aggregator API

A FastAPI-based weather aggregation service that fetches weather data from multiple APIs and provides averaged temperature information.

## Features

- 🌡️ **Multi-source weather data**: Aggregates data from OpenWeatherMap, WeatherAPI, Open-Meteo, and Weatherstack
- 📊 **Temperature averaging**: Calculates average temperature from multiple sources
- 🔍 **Input validation**: Validates city names and handles errors gracefully
- 🌐 **Web interface**: Clean, responsive frontend for easy interaction
- 🧪 **Comprehensive testing**: Unit tests for all major functionality
- 🐳 **Docker ready**: Containerized for easy deployment

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **HTTP Client**: httpx (async)
- **Geocoding**: geopy (Nominatim)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Testing**: pytest
- **Containerization**: Docker

## API Endpoints

### GET `/`
Returns welcome message.

### GET `/weather/{city}`
Fetches weather data for the specified city.

**Parameters:**
- `city` (string): City name (2-50 characters, letters only)

**Response:**
```json
{
  "city": "Budapest",
  "average_temperature": 15.2,
  "details": [
    {
      "source": "OpenWeatherMap",
      "temperature": 15.0
    },
    {
      "source": "WeatherAPI", 
      "temperature": 15.5
    }
  ]
}
```

**Error responses:**
- `400`: Invalid city name format
- `404`: City not found
- `500`: Service temporarily unavailable

## Setup

### Prerequisites
- Python 3.9+
- API keys for weather services (optional, Open-Meteo works without key)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd weather-aggregator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys** (optional)
Create a `keys.env` file:
```env
OPENWEATHERMAP_API_KEY=your_openweather_key
WEATHER_API_KEY=your_weatherapi_key
WEATHERSTACK_API_KEY=your_weatherstack_key
```

5. **Run the application**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
Web interface: `http://localhost:8000/static/index.html`

## Docker Deployment

1. **Build the image**
```bash
docker build -t weather-aggregator .
```

2. **Run the container**
```bash
docker run -p 8000:8000 weather-aggregator
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=main
```

## API Sources

- **OpenWeatherMap**: Comprehensive weather data
- **WeatherAPI**: Accurate current conditions
- **Open-Meteo**: Free, no API key required
- **Weatherstack**: Global weather information

## Input Validation

City names must meet the following criteria:
- 2-50 characters long
- Letters only (including accented characters)
- No numbers or special characters
- Spaces and hyphens allowed

## Error Handling

The application gracefully handles:
- Invalid city names
- API rate limits
- Network timeouts
- Partial API failures
- Non-existent cities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For questions or support, please open an issue on GitHub.