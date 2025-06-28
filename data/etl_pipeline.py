import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time

from database.connection import DatabaseManager
from database.schema import DatabaseSchema
from api.air_quality import AirQualityAPI
from api.cost_of_living import CostOfLivingAPI
from api.life_expectancy import LifeExpectancyAPI
from analysis.aqi_normalizer import AQINormalizer

class ETLPipeline:
    """Automated ETL pipeline for ingesting and processing data from all APIs"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db_schema = DatabaseSchema()
        self.air_quality_api = AirQualityAPI()
        self.cost_api = CostOfLivingAPI()
        self.life_exp_api = LifeExpectancyAPI()
        self.aqi_normalizer = AQINormalizer()
        
        # Major cities for initial data collection
        self.major_cities = [
            {'city_name': 'New York', 'country': 'United States', 'latitude': 40.7128, 'longitude': -74.0060},
            {'city_name': 'Los Angeles', 'country': 'United States', 'latitude': 34.0522, 'longitude': -118.2437},
            {'city_name': 'London', 'country': 'United Kingdom', 'latitude': 51.5074, 'longitude': -0.1278},
            {'city_name': 'Paris', 'country': 'France', 'latitude': 48.8566, 'longitude': 2.3522},
            {'city_name': 'Tokyo', 'country': 'Japan', 'latitude': 35.6762, 'longitude': 139.6503},
            {'city_name': 'Singapore', 'country': 'Singapore', 'latitude': 1.3521, 'longitude': 103.8198},
            {'city_name': 'Sydney', 'country': 'Australia', 'latitude': -33.8688, 'longitude': 151.2093},
            {'city_name': 'Toronto', 'country': 'Canada', 'latitude': 43.6532, 'longitude': -79.3832},
            {'city_name': 'Vancouver', 'country': 'Canada', 'latitude': 49.2827, 'longitude': -123.1207},
            {'city_name': 'Berlin', 'country': 'Germany', 'latitude': 52.5200, 'longitude': 13.4050},
            {'city_name': 'Amsterdam', 'country': 'Netherlands', 'latitude': 52.3676, 'longitude': 4.9041},
            {'city_name': 'Stockholm', 'country': 'Sweden', 'latitude': 59.3293, 'longitude': 18.0686},
            {'city_name': 'Copenhagen', 'country': 'Denmark', 'latitude': 55.6761, 'longitude': 12.5683},
            {'city_name': 'Zurich', 'country': 'Switzerland', 'latitude': 47.3769, 'longitude': 8.5417},
            {'city_name': 'Vienna', 'country': 'Austria', 'latitude': 48.2082, 'longitude': 16.3738},
            {'city_name': 'Madrid', 'country': 'Spain', 'latitude': 40.4168, 'longitude': -3.7038},
            {'city_name': 'Rome', 'country': 'Italy', 'latitude': 41.9028, 'longitude': 12.4964},
            {'city_name': 'Seoul', 'country': 'South Korea', 'latitude': 37.5665, 'longitude': 126.9780},
            {'city_name': 'Hong Kong', 'country': 'Hong Kong', 'latitude': 22.3193, 'longitude': 114.1694},
            {'city_name': 'Shanghai', 'country': 'China', 'latitude': 31.2304, 'longitude': 121.4737},
            {'city_name': 'Beijing', 'country': 'China', 'latitude': 39.9042, 'longitude': 116.4074},
            {'city_name': 'Mumbai', 'country': 'India', 'latitude': 19.0760, 'longitude': 72.8777},
            {'city_name': 'Delhi', 'country': 'India', 'latitude': 28.7041, 'longitude': 77.1025},
            {'city_name': 'São Paulo', 'country': 'Brazil', 'latitude': -23.5505, 'longitude': -46.6333},
            {'city_name': 'Mexico City', 'country': 'Mexico', 'latitude': 19.4326, 'longitude': -99.1332},
            {'city_name': 'Dubai', 'country': 'United Arab Emirates', 'latitude': 25.2048, 'longitude': 55.2708},
            {'city_name': 'Tel Aviv', 'country': 'Israel', 'latitude': 32.0853, 'longitude': 34.7818},
            {'city_name': 'Bangkok', 'country': 'Thailand', 'latitude': 13.7563, 'longitude': 100.5018},
            {'city_name': 'Kuala Lumpur', 'country': 'Malaysia', 'latitude': 3.1390, 'longitude': 101.6869},
            {'city_name': 'Jakarta', 'country': 'Indonesia', 'latitude': -6.2088, 'longitude': 106.8456},
            {'city_name': 'Manila', 'country': 'Philippines', 'latitude': 14.5995, 'longitude': 120.9842},
            {'city_name': 'Kelowna', 'country': 'Canada', 'latitude': 49.8880, 'longitude': -119.4960},
            {'city_name': 'Calgary', 'country': 'Canada', 'latitude': 51.0447, 'longitude': -114.0719},
            {'city_name': 'Montreal', 'country': 'Canada', 'latitude': 45.5017, 'longitude': -73.5673},
            {'city_name': 'Ottawa', 'country': 'Canada', 'latitude': 45.4215, 'longitude': -75.6972}
        ]
    
    def run_full_pipeline(self):
        """Run the complete ETL pipeline"""
        try:
            print("Starting ETL Pipeline...")
            
            # Initialize database schema
            if not self.db_schema.initialize_database():
                raise Exception("Failed to initialize database schema")
            
            # Step 1: Insert cities data
            self._insert_cities_data()
            
            # Step 2: Collect and process air quality data
            self._collect_air_quality_data()
            
            # Step 3: Collect cost of living data
            self._collect_cost_of_living_data()
            
            # Step 4: Collect life expectancy data
            self._collect_life_expectancy_data()
            
            print("ETL Pipeline completed successfully!")
            return True
            
        except Exception as e:
            print(f"ETL Pipeline failed: {str(e)}")
            return False
    
    def _insert_cities_data(self):
        """Insert city data into the database"""
        print("Inserting cities data...")
        
        try:
            insert_query = """
            INSERT INTO cities (city_name, country, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (city_name, country) DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = CURRENT_TIMESTAMP
            """
            
            city_data = [
                (city['city_name'], city['country'], city['latitude'], city['longitude'])
                for city in self.major_cities
            ]
            
            success = self.db_manager.execute_many(insert_query, city_data)
            if success:
                print(f"Successfully inserted {len(self.major_cities)} cities")
            else:
                raise Exception("Failed to insert cities data")
                
        except Exception as e:
            raise Exception(f"Cities data insertion failed: {str(e)}")
    
    def _collect_air_quality_data(self):
        """Collect and process air quality data"""
        print("Collecting air quality data...")
        
        try:
            air_quality_data = self.air_quality_api.get_multiple_cities_air_quality(self.major_cities)
            
            for city_info in self.major_cities:
                city_key = f"{city_info['city_name']}, {city_info['country']}"
                
                # Get city ID from database
                city_id = self._get_city_id(city_info['city_name'], city_info['country'])
                if not city_id:
                    print(f"City ID not found for {city_key}")
                    continue
                
                if city_key in air_quality_data:
                    aq_data = air_quality_data[city_key]
                    
                    # Calculate standardized AQI
                    standardized_aqi = self.aqi_normalizer.calculate_standardized_aqi(aq_data)
                    
                    # Insert air quality data
                    self._insert_air_quality_data(city_id, aq_data, standardized_aqi)
                else:
                    print(f"No air quality data available for {city_key}")
                
                # Rate limiting
                time.sleep(0.5)
            
            print("Air quality data collection completed")
            
        except Exception as e:
            raise Exception(f"Air quality data collection failed: {str(e)}")
    
    def _collect_cost_of_living_data(self):
        """Collect cost of living data"""
        print("Collecting cost of living data...")
        
        try:
            cost_data = self.cost_api.get_multiple_cities_cost_data(self.major_cities)
            
            for city_info in self.major_cities:
                city_key = f"{city_info['city_name']}, {city_info['country']}"
                
                # Get city ID from database
                city_id = self._get_city_id(city_info['city_name'], city_info['country'])
                if not city_id:
                    continue
                
                if city_key in cost_data:
                    cost_info = cost_data[city_key]
                    self._insert_cost_of_living_data(city_id, cost_info)
                else:
                    print(f"No cost data available for {city_key}")
                
                # Rate limiting
                time.sleep(0.3)
            
            print("Cost of living data collection completed")
            
        except Exception as e:
            raise Exception(f"Cost of living data collection failed: {str(e)}")
    
    def _collect_life_expectancy_data(self):
        """Collect life expectancy data"""
        print("Collecting life expectancy data...")
        
        try:
            # Get unique countries
            countries = list(set([city['country'] for city in self.major_cities]))
            
            life_exp_data = self.life_exp_api.get_multiple_countries_life_expectancy(countries)
            
            for country in countries:
                if country in life_exp_data:
                    life_data = life_exp_data[country]
                    self._insert_life_expectancy_data(life_data)
                else:
                    # Use estimated data if API fails
                    estimated_data = self.life_exp_api.get_estimated_life_expectancy(country)
                    self._insert_life_expectancy_data(estimated_data)
                
                # Rate limiting
                time.sleep(0.2)
            
            print("Life expectancy data collection completed")
            
        except Exception as e:
            raise Exception(f"Life expectancy data collection failed: {str(e)}")
    
    def _get_city_id(self, city_name: str, country: str) -> int:
        """Get city ID from database"""
        try:
            query = "SELECT id FROM cities WHERE city_name = %s AND country = %s"
            result = self.db_manager.execute_query(query, [city_name, country])
            
            if result and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception:
            return None
    
    def _insert_air_quality_data(self, city_id: int, aq_data: Dict, standardized_aqi: float):
        """Insert air quality data into database"""
        try:
            query = """
            INSERT INTO air_quality (
                city_id, pm25_concentration, pm10_concentration, no2_concentration,
                so2_concentration, co_concentration, o3_concentration,
                raw_aqi, standardized_aqi, data_source, measurement_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (city_id) DO UPDATE SET
                pm25_concentration = EXCLUDED.pm25_concentration,
                pm10_concentration = EXCLUDED.pm10_concentration,
                no2_concentration = EXCLUDED.no2_concentration,
                so2_concentration = EXCLUDED.so2_concentration,
                co_concentration = EXCLUDED.co_concentration,
                o3_concentration = EXCLUDED.o3_concentration,
                raw_aqi = EXCLUDED.raw_aqi,
                standardized_aqi = EXCLUDED.standardized_aqi,
                data_source = EXCLUDED.data_source,
                measurement_date = EXCLUDED.measurement_date,
                updated_at = CURRENT_TIMESTAMP
            """
            
            # First, check if record exists and delete it to avoid unique constraint issues
            delete_query = "DELETE FROM air_quality WHERE city_id = %s"
            self.db_manager.execute_query(delete_query, [city_id])
            
            params = [
                city_id,
                aq_data.get('pm25', 0),
                aq_data.get('pm10', 0),
                aq_data.get('no2', 0),
                aq_data.get('so2', 0),
                aq_data.get('co', 0),
                aq_data.get('o3', 0),
                aq_data.get('aqi', 0),
                standardized_aqi,
                aq_data.get('source', 'unknown'),
                aq_data.get('timestamp', datetime.now())
            ]
            
            self.db_manager.execute_query(query, params)
            
        except Exception as e:
            print(f"Failed to insert air quality data for city_id {city_id}: {str(e)}")
    
    def _insert_cost_of_living_data(self, city_id: int, cost_data: Dict):
        """Insert cost of living data into database"""
        try:
            query = """
            INSERT INTO cost_of_living (
                city_id, cost_of_living_index, rent_index, cost_of_living_plus_rent_index,
                groceries_index, restaurant_price_index, local_purchasing_power_index,
                data_source, data_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (city_id) DO UPDATE SET
                cost_of_living_index = EXCLUDED.cost_of_living_index,
                rent_index = EXCLUDED.rent_index,
                cost_of_living_plus_rent_index = EXCLUDED.cost_of_living_plus_rent_index,
                groceries_index = EXCLUDED.groceries_index,
                restaurant_price_index = EXCLUDED.restaurant_price_index,
                local_purchasing_power_index = EXCLUDED.local_purchasing_power_index,
                data_source = EXCLUDED.data_source,
                data_date = EXCLUDED.data_date,
                updated_at = CURRENT_TIMESTAMP
            """
            
            # Delete existing record first
            delete_query = "DELETE FROM cost_of_living WHERE city_id = %s"
            self.db_manager.execute_query(delete_query, [city_id])
            
            params = [
                city_id,
                cost_data.get('cost_of_living_index', 100),
                cost_data.get('rent_index', 100),
                cost_data.get('cost_of_living_plus_rent_index', 100),
                cost_data.get('groceries_index', 100),
                cost_data.get('restaurant_price_index', 100),
                cost_data.get('local_purchasing_power_index', 100),
                cost_data.get('source', 'unknown'),
                datetime.now().date()
            ]
            
            self.db_manager.execute_query(query, params)
            
        except Exception as e:
            print(f"Failed to insert cost data for city_id {city_id}: {str(e)}")
    
    def _insert_life_expectancy_data(self, life_data: Dict):
        """Insert life expectancy data into database"""
        try:
            query = """
            INSERT INTO life_expectancy (country, life_expectancy, year, data_source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (country, year) DO UPDATE SET
                life_expectancy = EXCLUDED.life_expectancy,
                data_source = EXCLUDED.data_source,
                updated_at = CURRENT_TIMESTAMP
            """
            
            params = [
                life_data.get('country', ''),
                life_data.get('life_expectancy', 75),
                life_data.get('year', datetime.now().year),
                life_data.get('source', 'unknown')
            ]
            
            self.db_manager.execute_query(query, params)
            
        except Exception as e:
            print(f"Failed to insert life expectancy data: {str(e)}")
    
    def update_data_for_city(self, city_name: str, country: str):
        """Update data for a specific city"""
        try:
            city_info = {
                'city_name': city_name,
                'country': country,
                'latitude': 0,  # Will need to be provided or looked up
                'longitude': 0
            }
            
            # Get city ID
            city_id = self._get_city_id(city_name, country)
            if not city_id:
                print(f"City not found: {city_name}, {country}")
                return False
            
            # Update air quality data
            aq_data = self.air_quality_api.get_air_quality_for_city(
                city_name, country, city_info['latitude'], city_info['longitude']
            )
            if aq_data:
                standardized_aqi = self.aqi_normalizer.calculate_standardized_aqi(aq_data)
                self._insert_air_quality_data(city_id, aq_data, standardized_aqi)
            
            # Update cost data
            cost_data = self.cost_api.get_cost_of_living_data(city_name, country)
            if cost_data:
                self._insert_cost_of_living_data(city_id, cost_data)
            
            # Update life expectancy data
            life_data = self.life_exp_api.get_life_expectancy_by_country_name(country)
            if life_data:
                self._insert_life_expectancy_data(life_data)
            
            return True
            
        except Exception as e:
            print(f"Failed to update data for {city_name}, {country}: {str(e)}")
            return False
