import requests
import os
from typing import Dict, List, Optional
import json

class CostOfLivingAPI:
    """Handles cost of living data from RapidAPI sources"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.rapidapi_host = "cost-of-living-and-prices.p.rapidapi.com"
        self.base_url = f"https://{self.rapidapi_host}"
        
        self.headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host
        }
    
    def get_cost_of_living_data(self, city: str, country: str) -> Optional[Dict]:
        """Get cost of living data for a specific city"""
        if not self.rapidapi_key:
            return None
        
        try:
            # Try different endpoint variations
            endpoints = [
                f"/v1/cost-of-living/city/{city}/country/{country}",
                f"/cost-of-living/{city}",
                f"/cities/{city}-{country}"
            ]
            
            for endpoint in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_cost_data(data, city, country)
                    
                except requests.RequestException:
                    continue
            
            # Fallback to numbeo-style data
            return self._get_numbeo_style_data(city, country)
            
        except Exception as e:
            print(f"Cost of living API request failed for {city}, {country}: {str(e)}")
            return None
    
    def _parse_cost_data(self, data: Dict, city: str, country: str) -> Dict:
        """Parse cost of living data from API response"""
        try:
            # Handle different API response formats
            if 'cost_of_living_index' in data:
                return {
                    'cost_of_living_index': data.get('cost_of_living_index', 100),
                    'rent_index': data.get('rent_index', 100),
                    'cost_of_living_plus_rent_index': data.get('cost_of_living_plus_rent_index', 100),
                    'groceries_index': data.get('groceries_index', 100),
                    'restaurant_price_index': data.get('restaurant_price_index', 100),
                    'local_purchasing_power_index': data.get('local_purchasing_power_index', 100),
                    'source': 'rapidapi'
                }
            
            elif 'indices' in data:
                indices = data['indices']
                return {
                    'cost_of_living_index': indices.get('cost_of_living_index', 100),
                    'rent_index': indices.get('rent_index', 100),
                    'cost_of_living_plus_rent_index': indices.get('cost_of_living_plus_rent_index', 100),
                    'groceries_index': indices.get('groceries_index', 100),
                    'restaurant_price_index': indices.get('restaurant_price_index', 100),
                    'local_purchasing_power_index': indices.get('local_purchasing_power_index', 100),
                    'source': 'rapidapi'
                }
            
            # Default fallback with estimated values
            return self._generate_estimated_cost_data(city, country)
            
        except (KeyError, TypeError, ValueError) as e:
            print(f"Failed to parse cost data for {city}, {country}: {str(e)}")
            return self._generate_estimated_cost_data(city, country)
    
    def _get_numbeo_style_data(self, city: str, country: str) -> Optional[Dict]:
        """Get data using Numbeo-style API endpoints"""
        try:
            # Alternative API endpoint structures
            alt_headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "numbeo.p.rapidapi.com"
            }
            
            url = f"https://numbeo.p.rapidapi.com/get_city_prices_by_name"
            params = {
                'name': f"{city}, {country}"
            }
            
            response = requests.get(url, headers=alt_headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_numbeo_data(data, city, country)
            
            return None
            
        except Exception as e:
            print(f"Numbeo API fallback failed for {city}, {country}: {str(e)}")
            return None
    
    def _parse_numbeo_data(self, data: Dict, city: str, country: str) -> Dict:
        """Parse Numbeo API response data"""
        try:
            if 'cost_of_living_index' in data:
                return {
                    'cost_of_living_index': data.get('cost_of_living_index', 100),
                    'rent_index': data.get('rent_index', 100),
                    'cost_of_living_plus_rent_index': data.get('cost_of_living_plus_rent_index', 100),
                    'groceries_index': data.get('groceries_index', 100),
                    'restaurant_price_index': data.get('restaurant_price_index', 100),
                    'local_purchasing_power_index': data.get('local_purchasing_power_index', 100),
                    'source': 'numbeo'
                }
            
            return self._generate_estimated_cost_data(city, country)
            
        except Exception:
            return self._generate_estimated_cost_data(city, country)
    
    def _generate_estimated_cost_data(self, city: str, country: str) -> Dict:
        """Generate estimated cost data based on city/country"""
        # Basic cost estimation based on country and city tier
        cost_multipliers = {
            'Switzerland': 1.8, 'Norway': 1.7, 'Denmark': 1.6, 'Luxembourg': 1.6,
            'Iceland': 1.5, 'Singapore': 1.4, 'United States': 1.3, 'Australia': 1.25,
            'Germany': 1.1, 'United Kingdom': 1.15, 'France': 1.1, 'Canada': 1.2,
            'Japan': 1.2, 'South Korea': 1.0, 'Italy': 1.0, 'Spain': 0.9,
            'China': 0.6, 'India': 0.4, 'Mexico': 0.5, 'Brazil': 0.6,
            'Russia': 0.5, 'Poland': 0.7, 'Turkey': 0.6, 'Thailand': 0.5
        }
        
        base_index = 100
        country_multiplier = cost_multipliers.get(country, 1.0)
        
        # City tier adjustments
        major_cities = ['New York', 'London', 'Tokyo', 'Singapore', 'Hong Kong', 
                       'Paris', 'Sydney', 'Toronto', 'Vancouver', 'San Francisco',
                       'Los Angeles', 'Boston', 'Washington', 'Seattle']
        
        city_multiplier = 1.3 if city in major_cities else 1.0
        
        final_index = base_index * country_multiplier * city_multiplier
        
        return {
            'cost_of_living_index': round(final_index, 1),
            'rent_index': round(final_index * 1.2, 1),  # Rent typically higher
            'cost_of_living_plus_rent_index': round(final_index * 1.1, 1),
            'groceries_index': round(final_index * 0.9, 1),
            'restaurant_price_index': round(final_index * 1.1, 1),
            'local_purchasing_power_index': round(100 / country_multiplier, 1),
            'source': 'estimated'
        }
    
    def get_multiple_cities_cost_data(self, cities: List[Dict]) -> Dict[str, Dict]:
        """Get cost of living data for multiple cities"""
        results = {}
        
        for city_info in cities:
            city_key = f"{city_info['city_name']}, {city_info['country']}"
            
            cost_data = self.get_cost_of_living_data(
                city_info['city_name'],
                city_info['country']
            )
            
            if cost_data:
                results[city_key] = cost_data
            else:
                print(f"Failed to get cost data for {city_key}")
        
        return results
    
    def validate_api_key(self) -> bool:
        """Validate RapidAPI key"""
        return bool(self.rapidapi_key)
