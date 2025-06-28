# True Cost of Living - Interactive Globe Application

## Overview

This is a Streamlit-based interactive data application that analyzes the relationship between cost of living, air quality, and public health outcomes across global cities. The application features a 3D interactive globe that allows users to compare cities by clicking to select an origin and destination, then provides comprehensive life-cost trade-off analysis.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Visualization**: PyDeck for 3D globe rendering with interactive city selection
- **Data Display**: Pandas DataFrames for tabular data presentation
- **Caching**: Streamlit's `@st.cache_data` decorator for performance optimization

### Backend Architecture
- **Data Pipeline**: ETL system using custom Python classes
- **APIs**: Multiple external data source integrations
- **Analysis Engine**: Custom calculators for AQI normalization and life-cost analysis
- **Database**: PostgreSQL with psycopg2 connection management

### Data Storage Solutions
- **Primary Database**: PostgreSQL (configured for cloud deployment)
- **Schema Management**: Dedicated schema creation and migration system
- **Connection Pooling**: Context manager-based connection handling
- **Data Models**: Separate tables for cities, air quality, cost of living, and life expectancy

## Key Components

### 1. ETL Pipeline (`data/etl_pipeline.py`)
- Automated data ingestion from multiple APIs
- Handles 25+ major cities worldwide
- Processes and normalizes data from different sources
- Manages data freshness and updates

### 2. API Integrations (`api/`)
- **Air Quality**: OpenWeather and IQAir APIs for pollution data
- **Cost of Living**: RapidAPI sources for economic data
- **Life Expectancy**: World Bank API for health statistics
- Fallback mechanisms and error handling for API failures

### 3. Analysis Engines (`analysis/`)
- **AQI Normalizer**: Standardizes air quality indices using EPA standards
- **Life Cost Calculator**: Implements AQLI methodology for health impact assessment
- Health-adjusted life expectancy calculations

### 4. Database Layer (`database/`)
- **Connection Manager**: Handles PostgreSQL connections with environment variable configuration
- **Schema Manager**: Creates and maintains database structure
- **Data Models**: Cities, air quality, cost of living, and life expectancy tables

### 5. Interactive Interface (`app.py`)
- 3D globe visualization with clickable city markers
- Session state management for user selections
- Real-time comparison calculations
- Responsive sidebar and main content areas

## Data Flow

1. **Data Ingestion**: ETL pipeline fetches data from external APIs
2. **Data Processing**: AQI normalization and data standardization
3. **Database Storage**: Processed data stored in PostgreSQL
4. **User Interaction**: Globe interface allows city selection
5. **Analysis Computation**: Life-cost calculations performed on demand
6. **Results Display**: Comparison results shown in interactive interface

## External Dependencies

### APIs
- OpenWeather API (air quality data)
- IQAir API (alternative air quality source)
- RapidAPI Hub (cost of living data)
- World Bank API (life expectancy statistics)

### Python Packages
- `streamlit`: Web application framework
- `pydeck`: 3D visualization library
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `psycopg2`: PostgreSQL database adapter
- `requests`: HTTP client for API calls

### Database
- PostgreSQL (cloud-hosted, environment configured)
- Support for both connection parameters and DATABASE_URL

## Deployment Strategy

### Environment Configuration
- Database connection via environment variables (PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGPORT)
- Alternative DATABASE_URL support for cloud deployments
- API keys stored as environment variables
- Streamlit configuration for wide layout and globe visualization

### Database Setup
- Automated schema creation on first run
- Index optimization for city lookups and coordinate searches
- Connection pooling and error handling
- Migration support for schema updates

### Performance Optimizations
- Data caching with TTL (1 hour for city data)
- Session state management for user interactions
- Efficient database queries with proper indexing
- API rate limiting and fallback mechanisms

## Changelog
- June 28, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.