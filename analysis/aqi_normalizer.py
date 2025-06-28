import numpy as np
from typing import Dict, Optional
import math

class AQINormalizer:
    """Normalizes air quality data to standardized AQI using EPA standards"""
    
    def __init__(self):
        # EPA AQI breakpoints for PM2.5 (µg/m³)
        self.pm25_breakpoints = [
            (0.0, 12.0, 0, 50),      # Good
            (12.1, 35.4, 51, 100),   # Moderate
            (35.5, 55.4, 101, 150),  # Unhealthy for Sensitive Groups
            (55.5, 150.4, 151, 200), # Unhealthy
            (150.5, 250.4, 201, 300), # Very Unhealthy
            (250.5, 350.4, 301, 400), # Hazardous
            (350.5, 500.4, 401, 500)  # Hazardous
        ]
        
        # EPA AQI breakpoints for PM10 (µg/m³)
        self.pm10_breakpoints = [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500)
        ]
        
        # EPA AQI breakpoints for NO2 (ppb)
        self.no2_breakpoints = [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 1649, 301, 400),
            (1650, 2049, 401, 500)
        ]
        
        # EPA AQI breakpoints for SO2 (ppb)
        self.so2_breakpoints = [
            (0, 35, 0, 50),
            (36, 75, 51, 100),
            (76, 185, 101, 150),
            (186, 304, 151, 200),
            (305, 604, 201, 300),
            (605, 804, 301, 400),
            (805, 1004, 401, 500)
        ]
        
        # EPA AQI breakpoints for CO (ppm)
        self.co_breakpoints = [
            (0.0, 4.4, 0, 50),
            (4.5, 9.4, 51, 100),
            (9.5, 12.4, 101, 150),
            (12.5, 15.4, 151, 200),
            (15.5, 30.4, 201, 300),
            (30.5, 40.4, 301, 400),
            (40.5, 50.4, 401, 500)
        ]
        
        # EPA AQI breakpoints for O3 (ppm) - 8-hour average
        self.o3_breakpoints = [
            (0.000, 0.054, 0, 50),
            (0.055, 0.070, 51, 100),
            (0.071, 0.085, 101, 150),
            (0.086, 0.105, 151, 200),
            (0.106, 0.200, 201, 300)
        ]
    
    def calculate_standardized_aqi(self, pollutant_data: Dict) -> Optional[float]:
        """
        Calculate standardized AQI from raw pollutant concentrations
        Uses EPA methodology as the universal standard
        """
        try:
            individual_aqis = []
            
            # Calculate AQI for each available pollutant
            if 'pm25' in pollutant_data and pollutant_data['pm25'] is not None:
                pm25_aqi = self._calculate_pollutant_aqi(
                    pollutant_data['pm25'], self.pm25_breakpoints
                )
                if pm25_aqi is not None:
                    individual_aqis.append(pm25_aqi)
            
            if 'pm10' in pollutant_data and pollutant_data['pm10'] is not None:
                pm10_aqi = self._calculate_pollutant_aqi(
                    pollutant_data['pm10'], self.pm10_breakpoints
                )
                if pm10_aqi is not None:
                    individual_aqis.append(pm10_aqi)
            
            if 'no2' in pollutant_data and pollutant_data['no2'] is not None:
                # Convert µg/m³ to ppb for NO2 (approximate conversion)
                no2_ppb = pollutant_data['no2'] * 0.532
                no2_aqi = self._calculate_pollutant_aqi(no2_ppb, self.no2_breakpoints)
                if no2_aqi is not None:
                    individual_aqis.append(no2_aqi)
            
            if 'so2' in pollutant_data and pollutant_data['so2'] is not None:
                # Convert µg/m³ to ppb for SO2 (approximate conversion)
                so2_ppb = pollutant_data['so2'] * 0.382
                so2_aqi = self._calculate_pollutant_aqi(so2_ppb, self.so2_breakpoints)
                if so2_aqi is not None:
                    individual_aqis.append(so2_aqi)
            
            if 'co' in pollutant_data and pollutant_data['co'] is not None:
                # Convert µg/m³ to ppm for CO (approximate conversion)
                co_ppm = pollutant_data['co'] * 0.000873
                co_aqi = self._calculate_pollutant_aqi(co_ppm, self.co_breakpoints)
                if co_aqi is not None:
                    individual_aqis.append(co_aqi)
            
            if 'o3' in pollutant_data and pollutant_data['o3'] is not None:
                # Convert µg/m³ to ppm for O3 (approximate conversion)
                o3_ppm = pollutant_data['o3'] * 0.000512
                o3_aqi = self._calculate_pollutant_aqi(o3_ppm, self.o3_breakpoints)
                if o3_aqi is not None:
                    individual_aqis.append(o3_aqi)
            
            if not individual_aqis:
                return None
            
            # Return the maximum AQI (worst pollutant determines overall AQI)
            return max(individual_aqis)
            
        except Exception as e:
            print(f"Error calculating standardized AQI: {str(e)}")
            return None
    
    def _calculate_pollutant_aqi(self, concentration: float, breakpoints: list) -> Optional[float]:
        """Calculate AQI for a specific pollutant using EPA formula"""
        try:
            if concentration < 0:
                return None
            
            # Find the appropriate breakpoint range
            for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
                if bp_low <= concentration <= bp_high:
                    # EPA AQI calculation formula
                    aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                    return round(aqi, 1)
            
            # If concentration exceeds all breakpoints, use the highest range
            if concentration > breakpoints[-1][1]:
                bp_low, bp_high, aqi_low, aqi_high = breakpoints[-1]
                # Extrapolate beyond the highest breakpoint
                aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                return min(round(aqi, 1), 500)  # Cap at 500
            
            return None
            
        except Exception as e:
            print(f"Error calculating pollutant AQI: {str(e)}")
            return None
    
    def normalize_existing_aqi(self, aqi_value: int, source_standard: str) -> Optional[float]:
        """
        Convert existing AQI from different standards to EPA standard
        """
        try:
            if source_standard.lower() == 'epa' or source_standard.lower() == 'us':
                return float(aqi_value)
            elif source_standard.lower() == 'china' or source_standard.lower() == 'cn':
                return self._convert_china_aqi_to_epa(aqi_value)
            elif source_standard.lower() == 'india':
                return self._convert_india_aqi_to_epa(aqi_value)
            elif source_standard.lower() == 'eu' or source_standard.lower() == 'european':
                return self._convert_eu_aqi_to_epa(aqi_value)
            else:
                # Assume it's already EPA-like if unknown
                return float(aqi_value)
                
        except Exception as e:
            print(f"Error normalizing AQI: {str(e)}")
            return None
    
    def _convert_china_aqi_to_epa(self, china_aqi: int) -> float:
        """Convert Chinese AQI to EPA AQI (approximate conversion)"""
        # Rough conversion based on different PM2.5 standards
        if china_aqi <= 50:
            return china_aqi * 1.0  # Similar for good air
        elif china_aqi <= 100:
            return 50 + (china_aqi - 50) * 1.4  # China is more lenient
        elif china_aqi <= 200:
            return 100 + (china_aqi - 100) * 1.0
        else:
            return min(200 + (china_aqi - 200) * 0.8, 500)
    
    def _convert_india_aqi_to_epa(self, india_aqi: int) -> float:
        """Convert Indian AQI to EPA AQI (approximate conversion)"""
        # Indian AQI is generally similar to EPA but with some differences
        if india_aqi <= 50:
            return india_aqi * 1.0
        elif india_aqi <= 100:
            return india_aqi * 1.0
        elif india_aqi <= 200:
            return 100 + (india_aqi - 100) * 0.9
        else:
            return min(180 + (india_aqi - 200) * 0.7, 500)
    
    def _convert_eu_aqi_to_epa(self, eu_aqi: int) -> float:
        """Convert European AQI to EPA AQI (approximate conversion)"""
        # European standards are often stricter
        if eu_aqi <= 50:
            return eu_aqi * 1.2
        elif eu_aqi <= 100:
            return 50 + (eu_aqi - 50) * 1.5
        else:
            return min(125 + (eu_aqi - 100) * 1.0, 500)
    
    def get_aqi_category(self, aqi_value: float) -> Dict[str, str]:
        """Get AQI category and health message"""
        if aqi_value <= 50:
            return {
                'category': 'Good',
                'color': 'green',
                'health_message': 'Air quality is satisfactory for most people'
            }
        elif aqi_value <= 100:
            return {
                'category': 'Moderate',
                'color': 'yellow',
                'health_message': 'Acceptable for most, but sensitive people may experience minor issues'
            }
        elif aqi_value <= 150:
            return {
                'category': 'Unhealthy for Sensitive Groups',
                'color': 'orange',
                'health_message': 'Sensitive people should reduce outdoor activities'
            }
        elif aqi_value <= 200:
            return {
                'category': 'Unhealthy',
                'color': 'red',
                'health_message': 'Everyone may experience health effects'
            }
        elif aqi_value <= 300:
            return {
                'category': 'Very Unhealthy',
                'color': 'purple',
                'health_message': 'Health alert: everyone may experience serious health effects'
            }
        else:
            return {
                'category': 'Hazardous',
                'color': 'maroon',
                'health_message': 'Emergency conditions: entire population likely to be affected'
            }
    
    def calculate_health_impact_score(self, aqi_value: float) -> float:
        """Calculate a health impact score based on AQI (0-100 scale)"""
        try:
            if aqi_value <= 50:
                return 10  # Minimal impact
            elif aqi_value <= 100:
                return 10 + (aqi_value - 50) * 0.6  # 10-40
            elif aqi_value <= 150:
                return 40 + (aqi_value - 100) * 0.8  # 40-80
            elif aqi_value <= 200:
                return 80 + (aqi_value - 150) * 0.4  # 80-100
            else:
                return min(100, 100 + (aqi_value - 200) * 0.1)  # Cap at 100+
        except:
            return 50  # Default moderate impact
