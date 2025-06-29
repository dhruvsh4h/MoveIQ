import os
import http.client
import json
import urllib.parse
from typing import Dict, List, Optional
from datetime import datetime

class AirQualityAPI:
    """Handles air quality data from RapidAPI weather service"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.rapidapi_host = "weather-api167.p.rapidapi.com"
        
    def get_air_quality_rapidapi(self, city: str, country_code: str) -> Optional[Dict]:
        """Get air quality data from RapidAPI weather service"""
        if not self.rapidapi_key:
            return None
            
        try:
            conn = http.client.HTTPSConnection(self.rapidapi_host)
            
            # Format the place parameter
            place = f"{city},{country_code}"
            place_encoded = urllib.parse.quote(place)
            
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.rapidapi_host,
                'Accept': "application/json"
            }
            
            endpoint = f"/api/weather/air_pollution?place={place_encoded}&type=current"
            conn.request("GET", endpoint, headers=headers)
            
            res = conn.getresponse()
            data = res.read()
            conn.close()
            
            if res.status == 200:
                response_data = json.loads(data.decode("utf-8"))
                
                # Parse the RapidAPI response format
                if 'list' in response_data and len(response_data['list']) > 0:
                    air_data = response_data['list'][0]
                    components = air_data.get('components', {})
                    main = air_data.get('main', {})
                    
                    # Convert to standardized format
                    return {
                        'pm25': components.get('pm2_5', 0),
                        'pm10': components.get('pm10', 0),
                        'no2': components.get('no2', 0),
                        'so2': components.get('so2', 0),
                        'co': components.get('co', 0),
                        'o3': components.get('o3', 0),
                        'nh3': components.get('nh3', 0),
                        'aqi': main.get('air_quality_index', 0),
                        'air_quality_text': main.get('air_quality', 'Unknown'),
                        'timestamp': datetime.fromtimestamp(air_data.get('dt', 0)) if air_data.get('dt') else datetime.now(),
                        'source': 'rapidapi_weather',
                        'coordinates': response_data.get('coord', {})
                    }
                
                return None
            else:
                print(f"Error fetching air quality data: HTTP {res.status}")
                return None
                
        except Exception as e:
            print(f"Error fetching RapidAPI air quality data: {e}")
            return None
    
    def get_air_quality_for_city(self, city: str, country: str, lat: float, lon: float) -> Optional[Dict]:
        """Get air quality data for a city using RapidAPI"""
        # Convert country name to code if needed
        country_code = self._get_country_code(country)
        return self.get_air_quality_rapidapi(city, country_code)
    
    def get_multiple_cities_air_quality(self, cities: List[Dict]) -> Dict[str, Dict]:
        """Get air quality data for multiple cities"""
        results = {}
        
        for city_info in cities:
            city_name = city_info.get('city_name', '')
            country = city_info.get('country', '')
            
            if city_name and country:
                air_data = self.get_air_quality_for_city(
                    city_name, 
                    country, 
                    city_info.get('latitude', 0), 
                    city_info.get('longitude', 0)
                )
                
                if air_data:
                    results[f"{city_name}, {country}"] = air_data
        
        return results
    
    def _get_country_code(self, country_name: str) -> str:
        """Convert country name to 2-letter country code"""
        country_codes = {
            'United States': 'US',
            'United Kingdom': 'GB',
            'Germany': 'DE',
            'France': 'FR',
            'Japan': 'JP',
            'China': 'CN',
            'India': 'IN',
            'Canada': 'CA',
            'Australia': 'AU',
            'Brazil': 'BR',
            'Russia': 'RU',
            'South Korea': 'KR',
            'Italy': 'IT',
            'Spain': 'ES',
            'Netherlands': 'NL',
            'Switzerland': 'CH',
            'Sweden': 'SE',
            'Norway': 'NO',
            'Denmark': 'DK',
            'Finland': 'FI',
            'Belgium': 'BE',
            'Austria': 'AT',
            'Poland': 'PL',
            'Czech Republic': 'CZ',
            'Hungary': 'HU',
            'Portugal': 'PT',
            'Greece': 'GR',
            'Ireland': 'IE',
            'Luxembourg': 'LU',
            'Singapore': 'SG',
            'Hong Kong': 'HK',
            'New Zealand': 'NZ',
            'South Africa': 'ZA',
            'Mexico': 'MX',
            'Argentina': 'AR',
            'Chile': 'CL',
            'Colombia': 'CO',
            'Peru': 'PE',
            'Venezuela': 'VE',
            'Thailand': 'TH',
            'Malaysia': 'MY',
            'Philippines': 'PH',
            'Indonesia': 'ID',
            'Vietnam': 'VN',
            'Turkey': 'TR',
            'Israel': 'IL',
            'Saudi Arabia': 'SA',
            'United Arab Emirates': 'AE',
            'Egypt': 'EG',
            'Morocco': 'MA',
            'Nigeria': 'NG',
            'Kenya': 'KE',
            'Ethiopia': 'ET'
        }
        
        return country_codes.get(country_name, country_name[:2].upper())
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate available API keys"""
        return {
            'rapidapi': bool(self.rapidapi_key)
        }