import os
import http.client
import json
import urllib.parse
from typing import Dict, List, Optional

class CostOfLivingAPI:
    """Handles cost of living data from RapidAPI find-places-to-live service"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.rapidapi_host = "find-places-to-live.p.rapidapi.com"
        
    def get_cost_of_living_data(self, city: str, country: str) -> Optional[Dict]:
        """Get cost of living data for a specific city using RapidAPI"""
        if not self.rapidapi_key:
            return None
            
        try:
            conn = http.client.HTTPSConnection(self.rapidapi_host)
            
            # Format the place parameter - try different formats
            place_formats = [
                f"{city.lower().replace(' ', '-')}-{country.lower().replace(' ', '-')}",
                f"{city.lower()}-{country.lower()}",
                city.lower().replace(' ', '-')
            ]
            
            for place in place_formats:
                try:
                    headers = {
                        'x-rapidapi-key': self.rapidapi_key,
                        'x-rapidapi-host': self.rapidapi_host
                    }
                    
                    endpoint = f"/placesToLive?place={place}&type=City"
                    conn.request("GET", endpoint, headers=headers)
                    
                    res = conn.getresponse()
                    data = res.read()
                    
                    if res.status == 200:
                        response_data = json.loads(data.decode("utf-8"))
                        conn.close()
                        return self._parse_rapidapi_data(response_data, city, country)
                    
                except Exception as e:
                    print(f"Error trying place format '{place}': {e}")
                    continue
            
            conn.close()
            return None
                
        except Exception as e:
            print(f"Error fetching RapidAPI cost of living data: {e}")
            return None
    
    def _parse_rapidapi_data(self, data: Dict, city: str, country: str) -> Dict:
        """Parse RapidAPI cost of living response data"""
        try:
            parsed_data = {
                'city': city,
                'country': country,
                'source': 'rapidapi_places_to_live',
                'data_date': '2025-06-28'
            }
            
            # Extract report card data
            if 'report-card' in data:
                report_card = data['report-card']
                
                # Overall grades and scores
                if 'Overall Niche Grade' in report_card:
                    parsed_data['overall_grade'] = report_card['Overall Niche Grade'].get('value', 0)
                
                if 'Cost of Living' in report_card:
                    parsed_data['cost_of_living_grade'] = report_card['Cost of Living'].get('value', 0)
                
                if 'Housing' in report_card:
                    parsed_data['housing_grade'] = report_card['Housing'].get('value', 0)
                
                # Quality of life indicators
                parsed_data['public_schools_grade'] = report_card.get('Public Schools', {}).get('value', 0)
                parsed_data['crime_safety_grade'] = report_card.get('Crime & Safety', {}).get('value', 0)
                parsed_data['nightlife_grade'] = report_card.get('Nightlife', {}).get('value', 0)
                parsed_data['family_friendly_grade'] = report_card.get('Good for Families', {}).get('value', 0)
                parsed_data['diversity_grade'] = report_card.get('Diversity', {}).get('value', 0)
                parsed_data['jobs_grade'] = report_card.get('Jobs', {}).get('value', 0)
                parsed_data['weather_grade'] = report_card.get('Weather', {}).get('value', 0)
                parsed_data['health_fitness_grade'] = report_card.get('Health & Fitness', {}).get('value', 0)
                parsed_data['outdoor_activities_grade'] = report_card.get('Outdoor Activities', {}).get('value', 0)
                parsed_data['commute_grade'] = report_card.get('Commute', {}).get('value', 0)
            
            # Extract real estate data
            if 'real-estate' in data:
                real_estate = data['real-estate']
                parsed_data['median_home_value'] = real_estate.get('Median Home Value', {}).get('value', 0)
                parsed_data['median_home_value_national'] = real_estate.get('Median Home Value', {}).get('national', 0)
                parsed_data['median_rent'] = real_estate.get('Median Rent', {}).get('value', 0)
                parsed_data['median_rent_national'] = real_estate.get('Median Rent', {}).get('national', 0)
                parsed_data['area_feel'] = real_estate.get('Area Feel', {}).get('value', '')
            
            # Extract income data
            if 'working-in' in data:
                working_data = data['working-in']
                parsed_data['median_household_income'] = working_data.get('Median Household Income', {}).get('value', 0)
                parsed_data['median_household_income_national'] = working_data.get('Median Household Income', {}).get('national', 0)
            
            # Extract population data
            if 'about' in data:
                about_data = data['about']
                parsed_data['population'] = about_data.get('Population', {}).get('value', 0)
            
            # Calculate cost of living index (normalized to 100 as baseline)
            home_value = float(parsed_data.get('median_home_value', 0))
            home_national = float(parsed_data.get('median_home_value_national', 1))
            rent_value = float(parsed_data.get('median_rent', 0))
            rent_national = float(parsed_data.get('median_rent_national', 1))
            
            if home_value > 0 and home_national > 0:
                home_ratio = home_value / home_national
                rent_ratio = rent_value / max(rent_national, 1)
                parsed_data['cost_of_living_index'] = ((home_ratio + rent_ratio) / 2) * 100
            else:
                # Fallback to grade-based index
                grade = float(parsed_data.get('cost_of_living_grade', 3))
                parsed_data['cost_of_living_index'] = max(20.0, min(200.0, (5 - grade) * 40 + 60))
            
            # Extract review data
            if 'reviews' in data:
                reviews = data['reviews']
                parsed_data['review_score'] = reviews.get('stars', {}).get('value', 0)
                parsed_data['review_count'] = reviews.get('stars', {}).get('count', 0)
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing RapidAPI data: {e}")
            return {
                'city': city,
                'country': country,
                'cost_of_living_index': 100,  # Default neutral value
                'source': 'rapidapi_places_to_live_fallback'
            }
    
    def get_multiple_cities_cost_data(self, cities: List[Dict]) -> Dict[str, Dict]:
        """Get cost of living data for multiple cities"""
        results = {}
        
        for city_info in cities:
            city_name = city_info.get('city_name', '')
            country = city_info.get('country', '')
            
            if city_name and country:
                cost_data = self.get_cost_of_living_data(city_name, country)
                
                if cost_data:
                    results[f"{city_name}, {country}"] = cost_data
        
        return results
    
    def validate_api_key(self) -> bool:
        """Validate RapidAPI key"""
        return bool(self.rapidapi_key)