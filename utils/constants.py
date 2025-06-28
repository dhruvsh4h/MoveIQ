"""
Constants and configuration settings for the True Cost of Living application
"""

# Globe visualization configuration
GLOBE_CONFIG = {
    'initial_view_state': {
        'longitude': 0,
        'latitude': 20,
        'zoom': 1,
        'min_zoom': 1,
        'max_zoom': 15,
        'pitch': 60,
        'bearing': 0
    },
    'layer_settings': {
        'elevation_scale': 50,
        'radius': 50000,
        'pickable': True,
        'auto_highlight': True
    }
}

# AQI color mapping for visualization
AQI_COLOR_MAP = {
    'good': [0, 255, 0, 160],           # Green (0-50)
    'moderate': [255, 255, 0, 160],     # Yellow (51-100)
    'unhealthy_sensitive': [255, 165, 0, 160],  # Orange (101-150)
    'unhealthy': [255, 0, 0, 160],      # Red (151-200)
    'very_unhealthy': [128, 0, 128, 160],  # Purple (201-300)
    'hazardous': [128, 0, 0, 160]       # Maroon (301+)
}

# AQI thresholds
AQI_THRESHOLDS = {
    'good': (0, 50),
    'moderate': (51, 100),
    'unhealthy_sensitive': (101, 150),
    'unhealthy': (151, 200),
    'very_unhealthy': (201, 300),
    'hazardous': (301, 500)
}

# Health impact messages
HEALTH_MESSAGES = {
    'good': 'Air quality is satisfactory for most people',
    'moderate': 'Acceptable for most, but sensitive people may experience minor issues',
    'unhealthy_sensitive': 'Sensitive people should reduce outdoor activities',
    'unhealthy': 'Everyone may experience health effects',
    'very_unhealthy': 'Health alert: everyone may experience serious health effects',
    'hazardous': 'Emergency conditions: entire population likely to be affected'
}

# API configuration
API_CONFIG = {
    'openweather': {
        'base_url': 'http://api.openweathermap.org/data/2.5/air_pollution',
        'timeout': 10,
        'rate_limit_delay': 0.5
    },
    'iqair': {
        'base_url': 'http://api.airvisual.com/v2',
        'timeout': 10,
        'rate_limit_delay': 0.5
    },
    'rapidapi': {
        'cost_of_living_host': 'cost-of-living-and-prices.p.rapidapi.com',
        'timeout': 10,
        'rate_limit_delay': 0.3
    },
    'world_bank': {
        'base_url': 'https://api.worldbank.org/v2',
        'timeout': 10,
        'rate_limit_delay': 0.2
    }
}

# Database configuration
DATABASE_CONFIG = {
    'connection_timeout': 30,
    'query_timeout': 60,
    'max_retries': 3,
    'retry_delay': 1
}

# Life expectancy impact coefficients (AQLI methodology)
HEALTH_IMPACT_COEFFICIENTS = {
    'pm25_life_impact': 0.1,  # years per µg/m³
    'aqi_health_multipliers': {
        'good': 1.0,
        'moderate': 1.2,
        'unhealthy_sensitive': 1.5,
        'unhealthy': 2.0,
        'very_unhealthy': 3.0,
        'hazardous': 4.0
    }
}

# Cost of living estimation multipliers by country
COUNTRY_COST_MULTIPLIERS = {
    'Switzerland': 1.8, 'Norway': 1.7, 'Denmark': 1.6, 'Luxembourg': 1.6,
    'Iceland': 1.5, 'Singapore': 1.4, 'United States': 1.3, 'Australia': 1.25,
    'Germany': 1.1, 'United Kingdom': 1.15, 'France': 1.1, 'Canada': 1.2,
    'Japan': 1.2, 'South Korea': 1.0, 'Italy': 1.0, 'Spain': 0.9,
    'China': 0.6, 'India': 0.4, 'Mexico': 0.5, 'Brazil': 0.6,
    'Russia': 0.5, 'Poland': 0.7, 'Turkey': 0.6, 'Thailand': 0.5
}

# Major cities tier classification
MAJOR_CITIES = [
    'New York', 'London', 'Tokyo', 'Singapore', 'Hong Kong',
    'Paris', 'Sydney', 'Toronto', 'Vancouver', 'San Francisco',
    'Los Angeles', 'Boston', 'Washington', 'Seattle'
]

# Life expectancy estimates by country
ESTIMATED_LIFE_EXPECTANCIES = {
    'United States': 78.9, 'Canada': 82.0, 'United Kingdom': 81.2,
    'Germany': 81.3, 'France': 82.7, 'Italy': 83.5, 'Spain': 83.6,
    'Japan': 84.6, 'South Korea': 83.0, 'Australia': 83.4,
    'New Zealand': 82.3, 'Sweden': 82.8, 'Norway': 82.0,
    'Denmark': 80.9, 'Finland': 81.7, 'Netherlands': 82.3,
    'Belgium': 82.0, 'Switzerland': 83.8, 'Austria': 81.6,
    'Singapore': 83.1, 'Hong Kong': 85.3, 'China': 76.9,
    'India': 69.7, 'Brazil': 75.9, 'Russia': 72.6,
    'Mexico': 75.1, 'Poland': 77.8, 'Turkey': 77.7,
    'Thailand': 77.0, 'South Africa': 64.1, 'Nigeria': 54.7,
    'Kenya': 66.7, 'Egypt': 72.0, 'Argentina': 76.7,
    'Chile': 80.2, 'Colombia': 77.3, 'Peru': 76.7
}

# Application settings
APP_SETTINGS = {
    'title': 'The True Cost of Living',
    'subtitle': 'Interactive Globe Analysis: Cost of Living vs Health Impact',
    'cache_ttl': 3600,  # 1 hour in seconds
    'max_cities_display': 100,
    'default_comparison_threshold': {
        'cost_delta': 20,
        'aqi_delta': 25,
        'life_exp_delta': 1.0
    }
}

# Streamlit page configuration
STREAMLIT_CONFIG = {
    'page_title': 'True Cost of Living - Interactive Globe',
    'page_icon': '🌍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Error messages
ERROR_MESSAGES = {
    'database_connection': 'Unable to connect to database. Please check your connection settings.',
    'api_key_missing': 'API key is missing. Please check your environment variables.',
    'city_not_found': 'City not found in database. Please try refreshing the data.',
    'calculation_failed': 'Unable to calculate comparison. Please try again.',
    'data_loading_failed': 'Failed to load cities data. Please refresh the page.'
}

# Success messages
SUCCESS_MESSAGES = {
    'data_refreshed': 'Data has been successfully refreshed from APIs!',
    'comparison_calculated': 'Life-cost comparison has been calculated successfully!',
    'city_selected': 'City has been selected. Choose another city to compare.',
    'database_initialized': 'Database has been successfully initialized.'
}
