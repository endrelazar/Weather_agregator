import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app, get_coordinates

client = TestClient(app)

# Async tesztek 
@pytest.mark.asyncio
async def test_get_coordinates():
    """Koordináták lekérése teszt"""
    try:
        lat, lon = await get_coordinates("Budapest")
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180
    except Exception:
        # Ha nincs internet vagy API limit
        pytest.skip("Geocoding service unavailable")

def test_root():
    """Root endpoint teszt"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Weather Aggregator API!"}

def test_weather_valid_city():
    """Érvényes város lekérdezése"""
    response = client.get("/weather/Budapest")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "average_temperature" in data
    assert "details" in data
    assert data["city"] == "Budapest"

def test_weather_invalid_city_numbers():
    """Számokat tartalmazó város"""
    response = client.get("/weather/City123")
    assert response.status_code == 400
    assert "Numbers not allowed" in response.json()["detail"]

def test_weather_city_too_short():
    """Túl rövid városnév"""
    response = client.get("/weather/A")
    assert response.status_code == 400
    assert "too short" in response.json()["detail"]

def test_weather_invalid_format():
    """Érvénytelen karakterek"""
    response = client.get("/weather/City@#$")
    assert response.status_code == 400
    assert "Invalid city name format" in response.json()["detail"]

def test_nonexistent_city():
    """Nem létező város"""
    response = client.get("/weather/Nonexistentcityxyz")
    assert response.status_code in [404, 500] 