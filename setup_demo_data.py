#!/usr/bin/env python3
"""
Demo data setup script for the True Cost of Living application.
This creates realistic estimated data when APIs are not available.
"""

import random
from datetime import datetime
from database.connection import DatabaseManager
from database.schema import DatabaseSchema

def setup_demo_data():
    """Setup demo data for the application"""
    print("Setting up demo data...")
    
    # Initialize database
    schema = DatabaseSchema()
    db_manager = DatabaseManager()
    
    # Demo cities data
    demo_cities = [
        {'city_name': 'New York', 'country': 'United States', 'latitude': 40.7128, 'longitude': -74.0060, 'aqi': 85, 'cost': 130, 'life_exp': 78.9},
        {'city_name': 'Vancouver', 'country': 'Canada', 'latitude': 49.2827, 'longitude': -123.1207, 'aqi': 42, 'cost': 115, 'life_exp': 82.0},
        {'city_name': 'London', 'country': 'United Kingdom', 'latitude': 51.5074, 'longitude': -0.1278, 'aqi': 68, 'cost': 120, 'life_exp': 81.2},
        {'city_name': 'Tokyo', 'country': 'Japan', 'latitude': 35.6762, 'longitude': 139.6503, 'aqi': 75, 'cost': 125, 'life_exp': 84.6},
        {'city_name': 'Singapore', 'country': 'Singapore', 'latitude': 1.3521, 'longitude': 103.8198, 'aqi': 58, 'cost': 140, 'life_exp': 83.1},
        {'city_name': 'Sydney', 'country': 'Australia', 'latitude': -33.8688, 'longitude': 151.2093, 'aqi': 45, 'cost': 125, 'life_exp': 83.4},
        {'city_name': 'Toronto', 'country': 'Canada', 'latitude': 43.6532, 'longitude': -79.3832, 'aqi': 55, 'cost': 110, 'life_exp': 82.0},
        {'city_name': 'Paris', 'country': 'France', 'latitude': 48.8566, 'longitude': 2.3522, 'aqi': 72, 'cost': 118, 'life_exp': 82.7},
        {'city_name': 'Berlin', 'country': 'Germany', 'latitude': 52.5200, 'longitude': 13.4050, 'aqi': 65, 'cost': 108, 'life_exp': 81.3},
        {'city_name': 'Zurich', 'country': 'Switzerland', 'latitude': 47.3769, 'longitude': 8.5417, 'aqi': 35, 'cost': 180, 'life_exp': 83.8},
        {'city_name': 'Stockholm', 'country': 'Sweden', 'latitude': 59.3293, 'longitude': 18.0686, 'aqi': 40, 'cost': 112, 'life_exp': 82.8},
        {'city_name': 'Copenhagen', 'country': 'Denmark', 'latitude': 55.6761, 'longitude': 12.5683, 'aqi': 48, 'cost': 115, 'life_exp': 80.9},
        {'city_name': 'Amsterdam', 'country': 'Netherlands', 'latitude': 52.3676, 'longitude': 4.9041, 'aqi': 52, 'cost': 113, 'life_exp': 82.3},
        {'city_name': 'Seoul', 'country': 'South Korea', 'latitude': 37.5665, 'longitude': 126.9780, 'aqi': 95, 'cost': 95, 'life_exp': 83.0},
        {'city_name': 'Hong Kong', 'country': 'Hong Kong', 'latitude': 22.3193, 'longitude': 114.1694, 'aqi': 88, 'cost': 135, 'life_exp': 85.3},
        {'city_name': 'Beijing', 'country': 'China', 'latitude': 39.9042, 'longitude': 116.4074, 'aqi': 155, 'cost': 75, 'life_exp': 76.9},
        {'city_name': 'Shanghai', 'country': 'China', 'latitude': 31.2304, 'longitude': 121.4737, 'aqi': 135, 'cost': 85, 'life_exp': 76.9},
        {'city_name': 'Delhi', 'country': 'India', 'latitude': 28.7041, 'longitude': 77.1025, 'aqi': 185, 'cost': 45, 'life_exp': 69.7},
        {'city_name': 'Mumbai', 'country': 'India', 'latitude': 19.0760, 'longitude': 72.8777, 'aqi': 165, 'cost': 55, 'life_exp': 69.7},
        {'city_name': 'Kelowna', 'country': 'Canada', 'latitude': 49.8880, 'longitude': -119.4960, 'aqi': 28, 'cost': 95, 'life_exp': 82.0},
        {'city_name': 'Bangkok', 'country': 'Thailand', 'latitude': 13.7563, 'longitude': 100.5018, 'aqi': 125, 'cost': 60, 'life_exp': 77.0},
        {'city_name': 'Mexico City', 'country': 'Mexico', 'latitude': 19.4326, 'longitude': -99.1332, 'aqi': 145, 'cost': 65, 'life_exp': 75.1},
        {'city_name': 'São Paulo', 'country': 'Brazil', 'latitude': -23.5505, 'longitude': -46.6333, 'aqi': 115, 'cost': 70, 'life_exp': 75.9},
        {'city_name': 'Los Angeles', 'country': 'United States', 'latitude': 34.0522, 'longitude': -118.2437, 'aqi': 95, 'cost': 135, 'life_exp': 78.9},
        {'city_name': 'Dubai', 'country': 'United Arab Emirates', 'latitude': 25.2048, 'longitude': 55.2708, 'aqi': 78, 'cost': 105, 'life_exp': 78.0}
    ]
    
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Insert cities
                for city in demo_cities:
                    cursor.execute("""
                        INSERT INTO cities (city_name, country, latitude, longitude)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (city_name, country) DO UPDATE SET
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            updated_at = CURRENT_TIMESTAMP
                    """, (city['city_name'], city['country'], city['latitude'], city['longitude']))
                
                # Get city IDs and insert related data
                for city in demo_cities:
                    cursor.execute("""
                        SELECT id FROM cities WHERE city_name = %s AND country = %s
                    """, (city['city_name'], city['country']))
                    
                    result = cursor.fetchone()
                    if result:
                        city_id = result[0]
                        
                        # Convert AQI to PM2.5 estimate
                        aqi = city['aqi']
                        if aqi <= 50:
                            pm25 = aqi * 0.24
                        elif aqi <= 100:
                            pm25 = 12 + (aqi - 50) * 0.468
                        elif aqi <= 150:
                            pm25 = 35.4 + (aqi - 100) * 0.398
                        else:
                            pm25 = 55.4 + (aqi - 150) * 1.898
                        
                        # Insert air quality data
                        cursor.execute("""
                            DELETE FROM air_quality WHERE city_id = %s
                        """, (city_id,))
                        
                        cursor.execute("""
                            INSERT INTO air_quality (
                                city_id, pm25_concentration, pm10_concentration, 
                                standardized_aqi, data_source, measurement_date
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (city_id, pm25, pm25 * 1.5, aqi, 'demo', datetime.now()))
                        
                        # Insert cost of living data
                        cursor.execute("""
                            DELETE FROM cost_of_living WHERE city_id = %s
                        """, (city_id,))
                        
                        cursor.execute("""
                            INSERT INTO cost_of_living (
                                city_id, cost_of_living_index, rent_index, 
                                cost_of_living_plus_rent_index, data_source, data_date
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (city_id, city['cost'], city['cost'] * 1.2, city['cost'] * 1.1, 'demo', datetime.now().date()))
                
                # Insert life expectancy data by country
                countries_done = set()
                for city in demo_cities:
                    if city['country'] not in countries_done:
                        cursor.execute("""
                            INSERT INTO life_expectancy (country, life_expectancy, year, data_source)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (country, year) DO UPDATE SET
                                life_expectancy = EXCLUDED.life_expectancy,
                                data_source = EXCLUDED.data_source,
                                updated_at = CURRENT_TIMESTAMP
                        """, (city['country'], city['life_exp'], datetime.now().year, 'demo'))
                        countries_done.add(city['country'])
        
        print(f"Successfully set up demo data for {len(demo_cities)} cities")
        return True
        
    except Exception as e:
        print(f"Failed to setup demo data: {str(e)}")
        return False

if __name__ == "__main__":
    setup_demo_data()