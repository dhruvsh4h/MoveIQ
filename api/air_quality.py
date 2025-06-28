import requests
import os
from typing import Dict, List, Optional
import json
from datetime import datetime

class AirQualityAPI:
    """Handles air quality data from OpenWeather and IQAir APIs"""
    
    def __init__(self):
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.iqair_api_key = os.getenv('IQAIR_API_KEY', '')
        self.openweather_base_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.iqair_base_url = "http://api.airvisual.com/v2"
    
    def get_air_quality_openweather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get air quality data from OpenWeather API"""
        if not self.openweather_api_key:
            return None
        
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key
            }
            
            response = requests.get(self.openweather_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'list' in data and len(data['list']) > 0:
                current_data = data['list'][0]
                components = current_data.get('components', {})
                
                return {
                    'pm25': components.get('pm2_5', 0),
                    'pm10': components.get('pm10', 0),
                    'no2': components.get('no2', 0),
                    'so2': components.get('so2', 0),
                    'co': components.get('co', 0),
                    'o3': components.get('o3', 0),
                    'aqi': current_data.get('main', {}).get('aqi', 0),
                    'timestamp': datetime.fromtimestamp(current_data.get('dt', 0)),
                    'source': 'openweather'
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"OpenWeather API request failed: {str(e)}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"OpenWeather API data parsing failed: {str(e)}")
            return None
    
    def get_air_quality_iqair(self, city: str, country: str) -> Optional[Dict]:
        """Get air quality data from IQAir API"""
        if not self.iqair_api_key:
            return None
        
        try:
            url = f"{self.iqair_base_url}/city"
            params = {
                'city': city,
                'country': country,
                'key': self.iqair_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                pollution_data = data['data'].get('current', {}).get('pollution', {})
                
                return {
                    'pm25': pollution_data.get('p2', 0),
                    'pm10': pollution_data.get('p1', 0),
                    'aqi_us': pollution_data.get('aqius', 0),
                    'aqi_cn': pollution_data.get('aqicn', 0),
                    'timestamp': datetime.fromisoformat(pollution_data.get('ts', '').replace('Z', '+00:00')),
                    'source': 'iqair'
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"IQAir API request failed: {str(e)}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"IQAir API data parsing failed: {str(e)}")
            return None
    
    def get_air_quality_for_city(self, city: str, country: str, lat: float, lon: float) -> Optional[Dict]:
        """Get air quality data using both APIs with fallback"""
        
        # Try OpenWeather first (more reliable for coordinates)
        openweather_data = self.get_air_quality_openweather(lat, lon)
        if openweather_data:
            return openweather_data
        
        # Fallback to IQAir
        iqair_data = self.get_air_quality_iqair(city, country)
        if iqair_data:
            return iqair_data
        
        return None
    
    def get_multiple_cities_air_quality(self, cities: List[Dict]) -> Dict[str, Dict]:
        """Get air quality data for multiple cities"""
        results = {}
        
        for city_info in cities:
            city_key = f"{city_info['city_name']}, {city_info['country']}"
            
            air_quality_data = self.get_air_quality_for_city(
                city_info['city_name'],
                city_info['country'],
                city_info['latitude'],
                city_info['longitude']
            )
            
            if air_quality_data:
                results[city_key] = air_quality_data
            else:
                print(f"Failed to get air quality data for {city_key}")
        
        return results
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate available API keys"""
        return {
            'openweather': bool(self.openweather_api_key),
            'iqair': bool(self.iqair_api_key)
        }
