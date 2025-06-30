The True Cost of Living - Interactive Globe 🌍💸
A data application to explore the trade-off between living costs, air quality, and public health outcomes across global cities.

✨ Core Features
Interactive 3D Globe: High-performance visualization with pydeck, showcasing cities with bar heights and colors representing standardized Air Quality Index (AQI).

Click-to-Compare Analysis: Intuitively select "Origin" and "Destination" cities on the globe to trigger a real-time, in-depth "Life-Cost" analysis.

Scientific Methodology: Analysis based on the robust Air Quality Life Index (AQLI) methodology from the University of Chicago, providing a quantifiable understanding of health impacts due to air quality changes.

Detailed Comparison Insights: Comprehensive results including Cost of Living Change, Air Quality Change, and Health-Adjusted Life Expectancy Change between your selected cities.

Automated Data Pipeline: A robust ETL (Extract, Transform, Load) system that continuously ingests and processes up-to-date data from various external APIs.

🛠️ Tech Stack
Frontend: Streamlit (web interface), PyDeck (3D visualizations)

Backend: Python

Database: PostgreSQL (psycopg2 for connectivity)

Data Sources: Integrations with Air Quality APIs (OpenWeather, IQAir), Cost of Living APIs (RapidAPI), and Life Expectancy APIs (World Bank).

Data Processing: Pandas, NumPy

🚀 Quickstart
Follow these steps to get the application running on your local machine.

Clone the Repository:

git clone https://github.com/dhruvsh4h/MoveIQ.git
cd MoveIQ

Set Up a Virtual Environment:

python -m venv venv
# Activate venv:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

Install Dependencies:

pip install numpy pandas psycopg2-binary pydeck requests streamlit

Configure Environment Variables:
Create a file named .env in the root directory of the project. Add your database connection string and RapidAPI key:

DATABASE_URL="postgres://user:password@host:port/database"
# Example: DATABASE_URL="postgresql://user:password@containers-us-west-80.railway.app:5640/railway"

RAPIDAPI_KEY="your_rapidapi_key_here"

Initialize the Database:
Run the demo data setup script to create tables and populate with sample data:

python CostCalculator/setup_demo_data.py

(If you have a live API key and wish to pull real data, you can run python CostCalculator/data/etl_pipeline.py instead.)

Run the Streamlit App:

streamlit run CostCalculator/app.py

Access the application in your web browser, usually at http://localhost:8501.

☁️ Deployment
This application is designed for cloud deployment on platforms like Render for the Streamlit web service, utilizing a free-tier PostgreSQL database service such as Neon. Ensure all necessary environment variables (e.g., DATABASE_URL and RAPIDAPI_KEY) are configured in your deployment environment settings on these platforms.

