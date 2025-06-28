import requests
import os
from typing import Dict, List, Optional
import json
from datetime import datetime

class LifeExpectancyAPI:
    """Handles life expectancy data from World Bank API"""
    
    def __init__(self):
        self.world_bank_base_url = "https://api.worldbank.org/v2"
        self.who_api_key = os.getenv('WHO_API_KEY', '')  # Optional WHO API key
    
    def get_life_expectancy_world_bank(self, country_code: str, year: int = None) -> Optional[Dict]:
        """Get life expectancy data from World Bank API"""
        try:
            if year is None:
                year = datetime.now().year - 1  # Get most recent available year
            
            # World Bank API endpoint for life expectancy at birth
            indicator = "SP.DYN.LE00.IN"  # Life expectancy at birth, total (years)
            url = f"{self.world_bank_base_url}/country/{country_code}/indicator/{indicator}"
            
            params = {
                'format': 'json',
                'date': f"{year-5}:{year}",  # Get last 5 years of data
                'per_page': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1 and isinstance(data[1], list) and len(data[1]) > 0:
                # Get the most recent year with data
                for record in data[1]:
                    if record.get('value') is not None:
                        return {
                            'country': record.get('country', {}).get('value', ''),
                            'country_code': record.get('countryiso3code', ''),
                            'life_expectancy': float(record.get('value', 0)),
                            'year': int(record.get('date', year)),
                            'source': 'world_bank'
                        }
            
            return None
            
        except requests.RequestException as e:
            print(f"World Bank API request failed for {country_code}: {str(e)}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError, TypeError) as e:
            print(f"World Bank API data parsing failed for {country_code}: {str(e)}")
            return None
    
    def get_life_expectancy_by_country_name(self, country_name: str) -> Optional[Dict]:
        """Get life expectancy by country name (converts to ISO code first)"""
        country_code = self._get_country_code(country_name)
        if country_code:
            return self.get_life_expectancy_world_bank(country_code)
        return None
    
    def _get_country_code(self, country_name: str) -> Optional[str]:
        """Convert country name to ISO3 code using World Bank API"""
        try:
            url = f"{self.world_bank_base_url}/country"
            params = {
                'format': 'json',
                'per_page': 300
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1 and isinstance(data[1], list):
                for country in data[1]:
                    if (country.get('name', '').lower() == country_name.lower() or
                        country_name.lower() in country.get('name', '').lower()):
                        return country.get('id', '')
            
            # Fallback to common country code mappings
            return self._get_country_code_fallback(country_name)
            
        except Exception as e:
            print(f"Country code lookup failed for {country_name}: {str(e)}")
            return self._get_country_code_fallback(country_name)
    
    def _get_country_code_fallback(self, country_name: str) -> Optional[str]:
        """Fallback country code mapping"""
        country_codes = {
            'united states': 'USA', 'usa': 'USA', 'america': 'USA',
            'united kingdom': 'GBR', 'uk': 'GBR', 'britain': 'GBR',
            'canada': 'CAN', 'germany': 'DEU', 'france': 'FRA',
            'italy': 'ITA', 'spain': 'ESP', 'japan': 'JPN',
            'china': 'CHN', 'india': 'IND', 'brazil': 'BRA',
            'russia': 'RUS', 'australia': 'AUS', 'mexico': 'MEX',
            'south korea': 'KOR', 'netherlands': 'NLD', 'belgium': 'BEL',
            'switzerland': 'CHE', 'austria': 'AUT', 'sweden': 'SWE',
            'norway': 'NOR', 'denmark': 'DNK', 'finland': 'FIN',
            'poland': 'POL', 'turkey': 'TUR', 'thailand': 'THA',
            'singapore': 'SGP', 'hong kong': 'HKG', 'new zealand': 'NZL'
        }
        
        return country_codes.get(country_name.lower())
    
    def get_multiple_countries_life_expectancy(self, countries: List[str]) -> Dict[str, Dict]:
        """Get life expectancy data for multiple countries"""
        results = {}
        
        for country in countries:
            life_exp_data = self.get_life_expectancy_by_country_name(country)
            if life_exp_data:
                results[country] = life_exp_data
            else:
                print(f"Failed to get life expectancy data for {country}")
        
        return results
    
    def get_estimated_life_expectancy(self, country: str) -> Dict:
        """Generate estimated life expectancy based on country development level"""
        # Estimated life expectancies for countries (rough estimates)
        life_expectancies = {
            'united states': 78.9, 'canada': 82.0, 'united kingdom': 81.2,
            'germany': 81.3, 'france': 82.7, 'italy': 83.5, 'spain': 83.6,
            'japan': 84.6, 'south korea': 83.0, 'australia': 83.4,
            'new zealand': 82.3, 'sweden': 82.8, 'norway': 82.0,
            'denmark': 80.9, 'finland': 81.7, 'netherlands': 82.3,
            'belgium': 82.0, 'switzerland': 83.8, 'austria': 81.6,
            'singapore': 83.1, 'hong kong': 85.3, 'china': 76.9,
            'india': 69.7, 'brazil': 75.9, 'russia': 72.6,
            'mexico': 75.1, 'poland': 77.8, 'turkey': 77.7,
            'thailand': 77.0, 'south africa': 64.1, 'nigeria': 54.7,
            'kenya': 66.7, 'egypt': 72.0, 'argentina': 76.7,
            'chile': 80.2, 'colombia': 77.3, 'peru': 76.7
        }
        
        estimated_age = life_expectancies.get(country.lower(), 72.0)  # Global average fallback
        
        return {
            'country': country,
            'life_expectancy': estimated_age,
            'year': datetime.now().year,
            'source': 'estimated'
        }
    
    def validate_api_connection(self) -> bool:
        """Test connection to World Bank API"""
        try:
            url = f"{self.world_bank_base_url}/country/USA/indicator/SP.DYN.LE00.IN"
            params = {'format': 'json', 'date': '2020:2023', 'per_page': 5}
            response = requests.get(url, params=params, timeout=5)
            return response.status_code == 200
        except:
            return False
