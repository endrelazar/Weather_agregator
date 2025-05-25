from fastapi import FastAPI, HTTPException
import httpx
import asyncio
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
from fastapi.staticfiles import StaticFiles
import re
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="weatheragr.log",
    filemode="a"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

load_dotenv('keys.env')

app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to the Weather Aggregator API!"}

API_KEYS = {
    "openweathermap": os.getenv("OPENWEATHERMAP_API_KEY"),
    "weatherapi": os.getenv("WEATHER_API_KEY"),
    "weatherstack": os.getenv("WEATHERSTACK_API_KEY")
}

def validate_city_name(city: str):
    if re.search(r'\d', city):
        logging.error(f"Invalid city name: '{city}' contains numbers.")
        raise HTTPException(status_code=400, detail=f" Numbers not allowed in city name: '{city}'")
    
    if not re.match(r'^[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ\s\-\.]+$', city):
        logging.error(f"Invalid city name format: '{city}'")
        raise HTTPException(status_code=400, detail=f" Invalid city name format: '{city}'")
    
    if len(city.strip()) <= 2 or len(city.strip()) > 50:
        logging.error(f"City name too short or too long: '{city}'")
        raise HTTPException(status_code=400, detail=f" City name too short or too long: '{city}'")



async def get_coordinates(city: str):
    validate_city_name(city) 
    geolocator = Nominatim(user_agent="weather-aggregator")
    location = geolocator.geocode(city)
    if not location:
        logging.error(f"City not found: '{city}'")
        raise HTTPException(status_code=404, detail=f" City '{city}' not found")
    return location.latitude, location.longitude


async def fetch_openweathermap(city: str):
    validate_city_name(city)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEYS['openweathermap']}&units=metric"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            logging.error(f"Error fetching data from OpenWeatherMap for city '{city}': {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from OpenWeatherMap")
        data = response.json()
        temperature = data["main"]["temp"]
        return {"source": "OpenWeatherMap", "temperature": temperature}
    
async def fetch_weatherapi(city: str):
    validate_city_name(city)
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEYS['weatherapi']}&q={city}&aqi=no"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            logging.error(f"Error fetching data from WeatherAPI for city '{city}': {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from WeatherAPI")
        data = response.json()
        temperature = data["current"]["temp_c"]
        return {"source": "WeatherAPI", "temperature": temperature}
    
async def fetch_openmeteo(city: str):
    validate_city_name(city)
    try:
        latitude, longitude = await get_coordinates(city)
    except HTTPException as e:
        logging.error(f"Error getting coordinates for city '{city}': {e.detail}")
        raise e
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}&current_weather=true"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            logging.error(f"Error fetching data from Open-Meteo for city '{city}': {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Open-Meteo")
        data = response.json()
        temperature = data["current_weather"]["temperature"]
        return {"source": "Open-Meteo", "temperature": temperature}
    
async def fetch_weatherstack(city: str):
    validate_city_name(city)
    url = f"http://api.weatherstack.com/current?access_key={os.getenv('WEATHERSTACK_API_KEY')}&query={city}&units=m"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            logging.error(f"Error fetching data from Weatherstack for city '{city}': {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Weatherstack")
        data = response.json()
        if "current" not in data:
            logging.error(f"Invalid response from Weatherstack for city '{city}': {data}")
            raise HTTPException(status_code=500, detail="Invalid response from Weatherstack")
        temperature = data["current"]["temperature"]
        return {"source": "Weatherstack", "temperature": temperature}

@app.get("/weather/{city}")
async def get_weather(city: str):
    weather_tasks = [
        fetch_openweathermap(city),
        fetch_weatherapi(city), 
        fetch_openmeteo(city),
        fetch_weatherstack(city)
    ]
    
    results = await asyncio.gather(*weather_tasks, return_exceptions=True)
    
    valid_results = []
    city_not_found_errors = 0
    
    for result in results:
        if isinstance(result, dict): 
            valid_results.append(result)
        elif isinstance(result, Exception):
            logging.error(f"Error fetching weather data for city '{city}': {result}")
            error_message = str(result)
            if any(phrase in error_message for phrase in ["Numbers not allowed", "Invalid city name format", "too short", "too long"]):
                clean_message = error_message.split(": ", 1)[-1] if ": " in error_message else error_message
                logging.error(f"Validation error for city '{city}': {clean_message}")
                raise HTTPException(status_code=400, detail=clean_message)
            else:
                city_not_found_errors += 1

    if not valid_results:
        if city_not_found_errors >= len(weather_tasks) // 2: 
            logging.error(f"City '{city}' not found in any weather service")
            raise HTTPException(status_code=404, detail=f" City '{city}' not found")
        else:
            logging.error(f"Weather data temporarily unavailable for city '{city}'")
            raise HTTPException(status_code=500, detail=" Weather data temporarily unavailable")
    
    avg_temp = sum([result["temperature"] for result in valid_results]) / len(valid_results)
    return {"city": city, "average_temperature": avg_temp, "details": valid_results}