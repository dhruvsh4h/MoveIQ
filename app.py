import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import os
from database.connection import DatabaseManager
from data.etl_pipeline import ETLPipeline
from analysis.life_cost_calculator import LifeCostCalculator
from utils.constants import GLOBE_CONFIG
import asyncio
import json

# Page configuration
st.set_page_config(
    page_title="True Cost of Living - Interactive Globe",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'selected_origin' not in st.session_state:
    st.session_state.selected_origin = None
if 'selected_destination' not in st.session_state:
    st.session_state.selected_destination = None
if 'cities_data' not in st.session_state:
    st.session_state.cities_data = None
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cities_data():
    """Load and cache cities data from database"""
    try:
        import psycopg2
        
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            city_name,
            country,
            latitude,
            longitude,
            standardized_aqi,
            cost_of_living_index,
            life_expectancy,
            pm25_concentration
        FROM cities_analysis 
        WHERE standardized_aqi IS NOT NULL 
        AND cost_of_living_index IS NOT NULL
        ORDER BY city_name
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create DataFrame from fetched data
        df = pd.DataFrame(rows, columns=columns)
        
        # Ensure numeric columns are properly typed
        numeric_columns = ['standardized_aqi', 'cost_of_living_index', 'life_expectancy', 'pm25_concentration', 'latitude', 'longitude']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading cities data: {str(e)}")
        return pd.DataFrame()

def create_map_visualization(cities_df, origin_city=None, dest_city=None):
    """Create an elegant 2D map visualization with optional flight path"""
    if cities_df.empty:
        st.warning("No cities data available for visualization")
        return None
    
    try:
        # Clean and prepare data for visualization
        viz_df = cities_df.dropna(subset=['standardized_aqi', 'cost_of_living_index', 'life_expectancy']).copy()
        
        if viz_df.empty:
            st.warning("No cities with complete data for visualization")
            return None
        
        st.success(f"Displaying {len(viz_df)} cities on the map")
        
        # Prepare data for visualization
        viz_df['radius'] = viz_df['standardized_aqi'] * 300 + 2000
        viz_df['color'] = viz_df['standardized_aqi'].apply(get_aqi_color)
        
        # Debug: Show sample of prepared data
        st.write("Sample visualization data:")
        sample_cols = ['city_name', 'country', 'latitude', 'longitude', 'standardized_aqi', 'radius']
        st.write(viz_df[sample_cols].head(3))
        
        layers = []
        
        # Create the scatter plot layer for cities
        cities_layer = pdk.Layer(
            'ScatterplotLayer',
            data=viz_df,
            get_position=['longitude', 'latitude'],
            get_radius='radius',
            get_fill_color='color',
            get_line_color=[255, 255, 255, 80],
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
            radius_scale=1,
            radius_min_pixels=3,
            radius_max_pixels=60
        )
        layers.append(cities_layer)
        
        # Add flight path if both cities are selected
        if origin_city and dest_city:
            flight_data = create_flight_path_data(viz_df, origin_city, dest_city)
            if flight_data:
                arc_layer = pdk.Layer(
                    'ArcLayer',
                    data=flight_data,
                    get_source_position=['source_lon', 'source_lat'],
                    get_target_position=['target_lon', 'target_lat'],
                    get_source_color=[255, 140, 0, 200],
                    get_target_color=[255, 69, 0, 200],
                    auto_highlight=True,
                    width_scale=0.0001,
                    get_width=50,
                )
                layers.append(arc_layer)
        
        # Set the viewport for a global view
        view_state = pdk.ViewState(
            longitude=20,
            latitude=30,
            zoom=1.5,
            min_zoom=0,
            max_zoom=15,
            pitch=0,
            bearing=0
        )
        
        # Create deck with a clean, elegant map style
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v10'
        )
        
        return deck
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None

def create_flight_path_data(cities_df, origin_city, dest_city):
    """Create flight path data for arc visualization"""
    try:
        origin_data = cities_df[cities_df.apply(lambda x: f"{x['city_name']}, {x['country']}" == origin_city, axis=1)]
        dest_data = cities_df[cities_df.apply(lambda x: f"{x['city_name']}, {x['country']}" == dest_city, axis=1)]
        
        if origin_data.empty or dest_data.empty:
            return None
        
        origin_row = origin_data.iloc[0]
        dest_row = dest_data.iloc[0]
        
        return [{
            'source_lon': origin_row['longitude'],
            'source_lat': origin_row['latitude'],
            'target_lon': dest_row['longitude'],
            'target_lat': dest_row['latitude'],
            'origin_city': origin_city,
            'dest_city': dest_city
        }]
        
    except Exception as e:
        print(f"Error creating flight path data: {e}")
        return None

def get_aqi_color(aqi_value):
    """Convert AQI value to color for visualization"""
    if aqi_value <= 50:
        return [0, 255, 0, 160]  # Green - Good
    elif aqi_value <= 100:
        return [255, 255, 0, 160]  # Yellow - Moderate
    elif aqi_value <= 150:
        return [255, 165, 0, 160]  # Orange - Unhealthy for Sensitive
    elif aqi_value <= 200:
        return [255, 0, 0, 160]  # Red - Unhealthy
    elif aqi_value <= 300:
        return [128, 0, 128, 160]  # Purple - Very Unhealthy
    else:
        return [128, 0, 0, 160]  # Maroon - Hazardous

def handle_city_selection(selected_data):
    """Handle city selection from globe interaction"""
    if selected_data and len(selected_data) > 0:
        city_info = selected_data[0]
        city_name = city_info.get('city_name', '')
        country = city_info.get('country', '')
        full_city_name = f"{city_name}, {country}"
        
        if st.session_state.selected_origin is None:
            st.session_state.selected_origin = full_city_name
            st.success(f"Origin selected: {full_city_name}")
            st.rerun()
        elif st.session_state.selected_destination is None and full_city_name != st.session_state.selected_origin:
            st.session_state.selected_destination = full_city_name
            st.success(f"Destination selected: {full_city_name}")
            # Trigger comparison calculation
            calculate_life_cost_comparison()
            st.rerun()

def calculate_life_cost_comparison():
    """Calculate and store the life-cost comparison"""
    if st.session_state.selected_origin and st.session_state.selected_destination:
        try:
            calculator = LifeCostCalculator()
            result = calculator.calculate_comparison(
                st.session_state.selected_origin,
                st.session_state.selected_destination
            )
            st.session_state.comparison_result = result
        except Exception as e:
            st.error(f"Error calculating comparison: {str(e)}")

def display_comparison_card():
    """Display the comparison results in a card format"""
    if st.session_state.comparison_result:
        result = st.session_state.comparison_result
        
        st.markdown("### 🔍 Life-Cost Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📍 Origin City")
            st.info(f"**{result['origin_city']}**")
            st.metric("AQI", f"{result['origin_aqi']:.1f}")
            st.metric("Cost Index", f"{result['origin_cost']:.1f}")
            st.metric("Life Expectancy", f"{result['origin_life_exp']:.1f} years")
        
        with col2:
            st.markdown("#### 🎯 Destination City")
            st.info(f"**{result['destination_city']}**")
            st.metric("AQI", f"{result['destination_aqi']:.1f}")
            st.metric("Cost Index", f"{result['destination_cost']:.1f}")
            st.metric("Life Expectancy", f"{result['destination_life_exp']:.1f} years")
        
        st.markdown("---")
        
        # Display deltas
        col3, col4, col5 = st.columns(3)
        
        with col3:
            cost_delta = result['cost_delta']
            st.metric(
                "Cost of Living Change",
                f"{cost_delta:+.1f}%",
                delta=f"{cost_delta:+.1f}%"
            )
        
        with col4:
            aqi_delta = result['aqi_delta']
            st.metric(
                "Air Quality Change",
                f"{aqi_delta:+.1f} AQI",
                delta=f"{aqi_delta:+.1f}",
                delta_color="inverse"  # Lower AQI is better
            )
        
        with col5:
            life_exp_delta = result['life_expectancy_delta']
            st.metric(
                "Life Expectancy Change",
                f"{life_exp_delta:+.2f} years",
                delta=f"{life_exp_delta:+.2f} years"
            )
        
        # Summary interpretation
        st.markdown("#### 💡 Analysis Summary")
        if cost_delta > 0 and life_exp_delta > 0:
            st.success("💰➡️❤️ Higher cost, but better health outcomes - a worthwhile investment in your wellbeing!")
        elif cost_delta < 0 and life_exp_delta > 0:
            st.success("🎉 Best of both worlds - lower cost AND better health outcomes!")
        elif cost_delta > 0 and life_exp_delta < 0:
            st.warning("⚠️ Higher cost with worse health outcomes - consider if other factors justify this move.")
        else:
            st.info("📊 Lower cost but potentially worse health outcomes - weigh your priorities carefully.")

def main():
    """Main application function"""
    
    # Header
    st.title("🌍 The True Cost of Living")
    st.markdown("**Interactive Globe Analysis: Cost of Living vs Health Impact**")
    st.markdown("Click two cities to compare their life-cost trade-offs!")
    
    # Sidebar for controls and information
    with st.sidebar:
        st.markdown("### 🎮 How to Use")
        st.markdown("""
        1. **Click a city** on the globe to set your **Origin**
        2. **Click another city** to set your **Destination**
        3. **View the analysis** comparing cost vs health impact
        4. **Reset** to start a new comparison
        """)
        
        if st.button("🔄 Reset Selection"):
            st.session_state.selected_origin = None
            st.session_state.selected_destination = None
            st.session_state.comparison_result = None
            st.rerun()
        
        # Display current selections
        st.markdown("### 📍 Current Selection")
        if st.session_state.selected_origin:
            st.success(f"**Origin:** {st.session_state.selected_origin}")
        else:
            st.info("Origin: Not selected")
            
        if st.session_state.selected_destination:
            st.success(f"**Destination:** {st.session_state.selected_destination}")
        else:
            st.info("Destination: Not selected")
        
        # Data refresh
        st.markdown("### 🔄 Data Management")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            etl = ETLPipeline()
            with st.spinner("Updating data from APIs..."):
                etl.run_full_pipeline()
            st.success("Data refreshed!")
            st.rerun()
    
    # Load cities data
    with st.spinner("Loading cities data..."):
        cities_df = load_cities_data()
    
    if cities_df.empty:
        st.error("No cities data available. Please check your database connection and run the ETL pipeline.")
        return
    
    st.session_state.cities_data = cities_df
    
    # Add a button to clear cache and reload data
    if st.sidebar.button("Clear Cache & Reload Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Clean data for use throughout the app
    clean_df = cities_df.dropna(subset=['standardized_aqi', 'cost_of_living_index', 'life_expectancy'])
    
    # Create and display the map
    st.markdown("### 🗺️ Interactive World Map")
    st.markdown("*Circle size and color represent Air Quality Index (AQI) levels across cities worldwide*")
    
    deck = create_map_visualization(
        cities_df, 
        origin_city=st.session_state.selected_origin,
        dest_city=st.session_state.selected_destination
    )
    if deck:
        st.pydeck_chart(deck)
    else:
        st.error("Unable to create map visualization")
        
    # Add city selection interface below the globe
    st.markdown("### 🏙️ Select Cities for Comparison")
    col1, col2 = st.columns(2)
    
    # Create dropdown list of cities from clean data
    if not clean_df.empty:
        city_options = [f"{row['city_name']}, {row['country']}" for _, row in clean_df.iterrows()]
        st.info(f"Found {len(city_options)} cities available for comparison")
    else:
        city_options = []
        st.warning("No cities available for selection")
        
        with col1:
            st.markdown("**Origin City:**")
            origin_selection = st.selectbox(
                "Choose origin city",
                options=[""] + city_options,
                index=0,
                key="origin_selector"
            )
            if origin_selection and origin_selection != st.session_state.selected_origin:
                st.session_state.selected_origin = origin_selection
                st.rerun()
        
        with col2:
            st.markdown("**Destination City:**")
            # Filter out the origin city from destination options
            dest_options = [city for city in city_options if city != st.session_state.selected_origin]
            destination_selection = st.selectbox(
                "Choose destination city",
                options=[""] + dest_options,
                index=0,
                key="destination_selector"
            )
            if destination_selection and destination_selection != st.session_state.selected_destination:
                st.session_state.selected_destination = destination_selection
                # Trigger comparison calculation
                if st.session_state.selected_origin:
                    calculate_life_cost_comparison()
                st.rerun()
    
    # Display comparison results if available
    if st.session_state.comparison_result:
        display_comparison_card()
    
    # Display data summary
    st.markdown("### 📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cities", len(clean_df))
    
    with col2:
        if not clean_df.empty and 'standardized_aqi' in clean_df.columns:
            avg_aqi = clean_df['standardized_aqi'].mean()
            st.metric("Average AQI", f"{avg_aqi:.1f}")
        else:
            st.metric("Average AQI", "No data")
    
    with col3:
        if not clean_df.empty and 'cost_of_living_index' in clean_df.columns:
            avg_cost = clean_df['cost_of_living_index'].mean()
            st.metric("Average Cost Index", f"{avg_cost:.1f}")
        else:
            st.metric("Average Cost Index", "No data")
    
    with col4:
        if not clean_df.empty and 'life_expectancy' in clean_df.columns:
            avg_life_exp = clean_df['life_expectancy'].mean()
            st.metric("Average Life Expectancy", f"{avg_life_exp:.1f} years")
        else:
            st.metric("Average Life Expectancy", "No data")

if __name__ == "__main__":
    main()
