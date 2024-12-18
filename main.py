from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import csv
import aiohttp
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory='templates')

cities = {}

def load_cities(filename):
    global cities
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
        	cities[row['capital']] = {
        		'country': row['country'],
        		'lat': float(row['latitude']),
        		'lon': float(row['longitude']),
                'weather': 'N/A'
        		}

load_cities('europe.csv')

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/update')
async def fetch_weather():
    global cities

    async def fetch_city_weather(name):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={cities[name]['lat']}&longitude={cities[name]['lon']}&current_weather=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                cities[name]['weather'] = data.get('current_weather', {}).get('temperature', 'N/A')

    tasks = [fetch_city_weather(city) for city in cities]
    await asyncio.gather(*tasks)
    print(cities)
    return cities