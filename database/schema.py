import psycopg2
from database.connection import DatabaseManager
import streamlit as st

class DatabaseSchema:
    """Manages database schema creation and updates"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_tables(self):
        """Create all necessary tables"""
        tables = [
            self._create_cities_table(),
            self._create_air_quality_table(),
            self._create_cost_of_living_table(),
            self._create_life_expectancy_table(),
            self._create_cities_analysis_view()
        ]
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    for table_sql in tables:
                        cursor.execute(table_sql)
            return True
        except Exception as e:
            st.error(f"Failed to create database tables: {str(e)}")
            return False
    
    def _create_cities_table(self):
        """SQL for cities table"""
        return """
        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL,
            country VARCHAR(100) NOT NULL,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            population BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city_name, country)
        );
        
        CREATE INDEX IF NOT EXISTS idx_cities_name_country ON cities(city_name, country);
        CREATE INDEX IF NOT EXISTS idx_cities_coordinates ON cities(latitude, longitude);
        """
    
    def _create_air_quality_table(self):
        """SQL for air quality data table"""
        return """
        CREATE TABLE IF NOT EXISTS air_quality (
            id SERIAL PRIMARY KEY,
            city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
            pm25_concentration DECIMAL(10, 4),
            pm10_concentration DECIMAL(10, 4),
            no2_concentration DECIMAL(10, 4),
            so2_concentration DECIMAL(10, 4),
            co_concentration DECIMAL(10, 4),
            o3_concentration DECIMAL(10, 4),
            raw_aqi INTEGER,
            standardized_aqi DECIMAL(10, 4),
            data_source VARCHAR(50),
            measurement_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_air_quality_city_date ON air_quality(city_id, measurement_date);
        CREATE INDEX IF NOT EXISTS idx_air_quality_standardized_aqi ON air_quality(standardized_aqi);
        """
    
    def _create_cost_of_living_table(self):
        """SQL for cost of living data table"""
        return """
        CREATE TABLE IF NOT EXISTS cost_of_living (
            id SERIAL PRIMARY KEY,
            city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
            cost_of_living_index DECIMAL(10, 4),
            rent_index DECIMAL(10, 4),
            cost_of_living_plus_rent_index DECIMAL(10, 4),
            groceries_index DECIMAL(10, 4),
            restaurant_price_index DECIMAL(10, 4),
            local_purchasing_power_index DECIMAL(10, 4),
            data_source VARCHAR(50),
            data_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_cost_of_living_city ON cost_of_living(city_id);
        CREATE INDEX IF NOT EXISTS idx_cost_of_living_index ON cost_of_living(cost_of_living_index);
        """
    
    def _create_life_expectancy_table(self):
        """SQL for life expectancy data table"""
        return """
        CREATE TABLE IF NOT EXISTS life_expectancy (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100) NOT NULL,
            life_expectancy DECIMAL(5, 2),
            year INTEGER,
            data_source VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(country, year)
        );
        
        CREATE INDEX IF NOT EXISTS idx_life_expectancy_country_year ON life_expectancy(country, year);
        """
    
    def _create_cities_analysis_view(self):
        """SQL for comprehensive cities analysis view"""
        return """
        CREATE OR REPLACE VIEW cities_analysis AS
        SELECT 
            c.id,
            c.city_name,
            c.country,
            c.latitude,
            c.longitude,
            c.population,
            aq.pm25_concentration,
            aq.standardized_aqi,
            col.cost_of_living_index,
            col.rent_index,
            col.cost_of_living_plus_rent_index,
            le.life_expectancy,
            aq.measurement_date as air_quality_date,
            col.data_date as cost_data_date,
            GREATEST(aq.updated_at, col.updated_at, le.updated_at) as last_updated
        FROM cities c
        LEFT JOIN (
            SELECT DISTINCT ON (city_id) 
                city_id, pm25_concentration, standardized_aqi, measurement_date, updated_at
            FROM air_quality 
            ORDER BY city_id, measurement_date DESC
        ) aq ON c.id = aq.city_id
        LEFT JOIN (
            SELECT DISTINCT ON (city_id) 
                city_id, cost_of_living_index, rent_index, cost_of_living_plus_rent_index, data_date, updated_at
            FROM cost_of_living 
            ORDER BY city_id, data_date DESC
        ) col ON c.id = col.city_id
        LEFT JOIN (
            SELECT DISTINCT ON (country) 
                country, life_expectancy, updated_at
            FROM life_expectancy 
            ORDER BY country, year DESC
        ) le ON c.country = le.country;
        """
    
    def drop_all_tables(self):
        """Drop all tables (for development/testing)"""
        drop_commands = [
            "DROP VIEW IF EXISTS cities_analysis CASCADE;",
            "DROP TABLE IF EXISTS air_quality CASCADE;",
            "DROP TABLE IF EXISTS cost_of_living CASCADE;",
            "DROP TABLE IF EXISTS life_expectancy CASCADE;",
            "DROP TABLE IF EXISTS cities CASCADE;"
        ]
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    for command in drop_commands:
                        cursor.execute(command)
            return True
        except Exception as e:
            st.error(f"Failed to drop tables: {str(e)}")
            return False
    
    def initialize_database(self):
        """Initialize database with schema"""
        if self.db_manager.test_connection():
            return self.create_tables()
        return False
