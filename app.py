import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
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
        db_manager = DatabaseManager()
        with db_manager.get_connection() as conn:
            query = """
            SELECT 
                city_name,
                country,
                latitude,
                longitude,
                CAST(standardized_aqi AS FLOAT) as standardized_aqi,
                CAST(cost_of_living_index AS FLOAT) as cost_of_living_index,
                CAST(life_expectancy AS FLOAT) as life_expectancy,
                CAST(pm25_concentration AS FLOAT) as pm25_concentration,
                last_updated
            FROM cities_analysis 
            WHERE standardized_aqi IS NOT NULL 
            AND cost_of_living_index IS NOT NULL
            ORDER BY city_name
            """
            df = pd.read_sql(query, conn)
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['standardized_aqi', 'cost_of_living_index', 'life_expectancy', 'pm25_concentration', 'latitude', 'longitude']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
    except Exception as e:
        st.error(f"Error loading cities data: {str(e)}")
        return pd.DataFrame()

def create_globe_visualization(cities_df):
    """Create the 3D globe visualization with pydeck"""
    if cities_df.empty:
        return None
    
    # Prepare data for visualization
    cities_df['elevation'] = cities_df['standardized_aqi'] * 1000  # Scale for visibility
    cities_df['color'] = cities_df['standardized_aqi'].apply(get_aqi_color)
    
    # Create the pydeck layer
    layer = pdk.Layer(
        'ColumnLayer',
        data=cities_df,
        get_position=['longitude', 'latitude'],
        get_elevation='elevation',
        elevation_scale=50,
        get_fill_color='color',
        radius=50000,
        pickable=True,
        auto_highlight=True,
    )
    
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=0,
        latitude=20,
        zoom=1,
        min_zoom=1,
        max_zoom=15,
        pitch=60,
        bearing=0
    )
    
    # Render
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '''
            <b>{city_name}, {country}</b><br/>
            AQI: {standardized_aqi}<br/>
            Cost Index: {cost_of_living_index}<br/>
            Life Expectancy: {life_expectancy} years
            ''',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white'
            }
        }
    )
    
    return deck

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
    
    # Create and display the globe
    st.markdown("### 🌐 Interactive 3D Globe")
    st.markdown("*3D bars represent Air Quality Index (AQI) - height and color indicate air quality levels*")
    
    deck = create_globe_visualization(cities_df)
    if deck:
        selected_data = st.pydeck_chart(deck, on_select="rerun")
        
        # Handle selection if data is returned
        if selected_data and selected_data['selection']['indices']:
            selected_indices = selected_data['selection']['indices']
            if selected_indices:
                selected_city_data = cities_df.iloc[selected_indices]
                handle_city_selection(selected_city_data.to_dict('records'))
    
    # Display comparison results if available
    if st.session_state.comparison_result:
        display_comparison_card()
    
    # Display data summary
    st.markdown("### 📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cities", len(cities_df))
    
    with col2:
        avg_aqi = cities_df['standardized_aqi'].mean()
        st.metric("Average AQI", f"{avg_aqi:.1f}")
    
    with col3:
        avg_cost = cities_df['cost_of_living_index'].mean()
        st.metric("Average Cost Index", f"{avg_cost:.1f}")
    
    with col4:
        avg_life_exp = cities_df['life_expectancy'].mean()
        st.metric("Average Life Expectancy", f"{avg_life_exp:.1f} years")

if __name__ == "__main__":
    main()
