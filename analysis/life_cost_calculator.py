import numpy as np
from typing import Dict, Optional, Tuple
from database.connection import DatabaseManager
import pandas as pd

class LifeCostCalculator:
    """Calculates life-cost trade-offs using AQLI methodology"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # AQLI coefficients: PM2.5 impact on life expectancy
        # Based on research: 10 µg/m³ increase in PM2.5 ≈ 1 year reduction in life expectancy
        self.pm25_life_impact_coefficient = 0.1  # years per µg/m³
        
        # Health impact factors for different AQI levels
        self.aqi_health_multipliers = {
            'good': 1.0,           # 0-50 AQI
            'moderate': 1.2,       # 51-100 AQI
            'unhealthy_sensitive': 1.5,  # 101-150 AQI
            'unhealthy': 2.0,      # 151-200 AQI
            'very_unhealthy': 3.0, # 201-300 AQI
            'hazardous': 4.0       # 301+ AQI
        }
    
    def calculate_comparison(self, origin_city: str, destination_city: str) -> Dict:
        """
        Calculate comprehensive life-cost comparison between two cities
        """
        try:
            # Get city data from database
            origin_data = self._get_city_data(origin_city)
            destination_data = self._get_city_data(destination_city)
            
            if not origin_data or not destination_data:
                raise ValueError("City data not found for one or both cities")
            
            # Calculate deltas
            cost_delta = destination_data['cost_of_living_index'] - origin_data['cost_of_living_index']
            aqi_delta = destination_data['standardized_aqi'] - origin_data['standardized_aqi']
            base_life_exp_delta = destination_data['life_expectancy'] - origin_data['life_expectancy']
            
            # Calculate health-adjusted life expectancy impact
            health_adjusted_life_exp_delta = self._calculate_health_adjusted_life_expectancy_delta(
                origin_data, destination_data
            )
            
            # Calculate cost-adjusted metrics
            cost_per_life_year = self._calculate_cost_per_life_year(cost_delta, health_adjusted_life_exp_delta)
            
            # Generate recommendation score
            recommendation_score = self._calculate_recommendation_score(
                cost_delta, health_adjusted_life_exp_delta, aqi_delta
            )
            
            return {
                'origin_city': origin_city,
                'destination_city': destination_city,
                'origin_aqi': origin_data['standardized_aqi'],
                'destination_aqi': destination_data['standardized_aqi'],
                'origin_cost': origin_data['cost_of_living_index'],
                'destination_cost': destination_data['cost_of_living_index'],
                'origin_life_exp': origin_data['life_expectancy'],
                'destination_life_exp': destination_data['life_expectancy'],
                'cost_delta': cost_delta,
                'aqi_delta': aqi_delta,
                'life_expectancy_delta': base_life_exp_delta,
                'health_adjusted_life_exp_delta': health_adjusted_life_exp_delta,
                'cost_per_life_year': cost_per_life_year,
                'recommendation_score': recommendation_score,
                'analysis_details': self._generate_analysis_details(
                    cost_delta, aqi_delta, health_adjusted_life_exp_delta, recommendation_score
                )
            }
            
        except Exception as e:
            raise Exception(f"Failed to calculate life-cost comparison: {str(e)}")
    
    def _get_city_data(self, city_full_name: str) -> Optional[Dict]:
        """Get comprehensive city data from database"""
        try:
            # Parse city name and country
            if ', ' in city_full_name:
                city_name, country = city_full_name.split(', ', 1)
            else:
                city_name = city_full_name
                country = None
            
            query = """
            SELECT 
                city_name,
                country,
                standardized_aqi,
                cost_of_living_index,
                life_expectancy,
                pm25_concentration,
                latitude,
                longitude
            FROM cities_analysis 
            WHERE city_name ILIKE %s
            """
            params = [city_name]
            
            if country:
                query += " AND country ILIKE %s"
                params.append(country)
            
            query += " LIMIT 1"
            
            result = self.db_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'city_name': row['city_name'],
                    'country': row['country'],
                    'standardized_aqi': float(row['standardized_aqi'] or 0),
                    'cost_of_living_index': float(row['cost_of_living_index'] or 100),
                    'life_expectancy': float(row['life_expectancy'] or 75),
                    'pm25_concentration': float(row['pm25_concentration'] or 0),
                    'latitude': float(row['latitude'] or 0),
                    'longitude': float(row['longitude'] or 0)
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting city data for {city_full_name}: {str(e)}")
            return None
    
    def _calculate_health_adjusted_life_expectancy_delta(self, origin_data: Dict, destination_data: Dict) -> float:
        """
        Calculate health-adjusted life expectancy delta using AQLI methodology
        """
        try:
            # Base life expectancy difference
            base_delta = destination_data['life_expectancy'] - origin_data['life_expectancy']
            
            # Calculate PM2.5 impact using AQLI methodology
            origin_pm25 = origin_data.get('pm25_concentration', 0)
            dest_pm25 = destination_data.get('pm25_concentration', 0)
            
            if origin_pm25 > 0 and dest_pm25 > 0:
                # Direct PM2.5 impact calculation
                pm25_delta = dest_pm25 - origin_pm25
                pm25_life_impact = -pm25_delta * self.pm25_life_impact_coefficient
            else:
                # Fallback to AQI-based calculation
                pm25_life_impact = self._estimate_life_impact_from_aqi(
                    origin_data['standardized_aqi'], 
                    destination_data['standardized_aqi']
                )
            
            # Combine base life expectancy with air quality impact
            total_delta = base_delta + pm25_life_impact
            
            return round(total_delta, 3)
            
        except Exception as e:
            print(f"Error calculating health-adjusted life expectancy: {str(e)}")
            return destination_data['life_expectancy'] - origin_data['life_expectancy']
    
    def _estimate_life_impact_from_aqi(self, origin_aqi: float, dest_aqi: float) -> float:
        """Estimate life expectancy impact from AQI differences"""
        try:
            # Convert AQI to estimated PM2.5 concentration
            origin_pm25_est = self._aqi_to_pm25_estimate(origin_aqi)
            dest_pm25_est = self._aqi_to_pm25_estimate(dest_aqi)
            
            pm25_delta = dest_pm25_est - origin_pm25_est
            return -pm25_delta * self.pm25_life_impact_coefficient
            
        except Exception:
            return 0.0
    
    def _aqi_to_pm25_estimate(self, aqi: float) -> float:
        """Convert AQI to estimated PM2.5 concentration"""
        if aqi <= 50:
            return aqi * 0.24  # 0-12 µg/m³
        elif aqi <= 100:
            return 12 + (aqi - 50) * 0.468  # 12-35.4 µg/m³
        elif aqi <= 150:
            return 35.4 + (aqi - 100) * 0.398  # 35.4-55.4 µg/m³
        elif aqi <= 200:
            return 55.4 + (aqi - 150) * 1.898  # 55.4-150.4 µg/m³
        else:
            return 150.4 + (aqi - 200) * 1.0  # 150.4+ µg/m³
    
    def _calculate_cost_per_life_year(self, cost_delta: float, life_exp_delta: float) -> Optional[float]:
        """Calculate cost per life year gained/lost"""
        try:
            if abs(life_exp_delta) < 0.01:  # Avoid division by near-zero
                return None
            
            # Cost per percentage point difference, converted to cost per life year
            # Assuming 1% cost of living = approximately $500-1000 annual impact for average household
            annual_cost_impact = cost_delta * 10  # Rough estimate in hundreds of dollars
            
            if life_exp_delta > 0:
                # Cost per year of life gained
                return round(annual_cost_impact / life_exp_delta, 2)
            else:
                # Cost savings per year of life lost (negative value)
                return round(annual_cost_impact / life_exp_delta, 2)
                
        except Exception:
            return None
    
    def _calculate_recommendation_score(self, cost_delta: float, life_exp_delta: float, aqi_delta: float) -> float:
        """
        Calculate recommendation score (0-100)
        100 = Highly recommended move
        0 = Not recommended move
        """
        try:
            score = 50  # Start with neutral score
            
            # Life expectancy impact (40% weight)
            if life_exp_delta > 0:
                score += min(life_exp_delta * 10, 30)  # Up to +30 points
            else:
                score += max(life_exp_delta * 10, -30)  # Up to -30 points
            
            # Cost impact (30% weight)
            if cost_delta < 0:
                score += min(abs(cost_delta) * 0.3, 20)  # Lower cost = up to +20 points
            else:
                score -= min(cost_delta * 0.2, 25)  # Higher cost = up to -25 points
            
            # Air quality impact (30% weight)
            if aqi_delta < 0:
                score += min(abs(aqi_delta) * 0.15, 25)  # Better air = up to +25 points
            else:
                score -= min(aqi_delta * 0.15, 20)  # Worse air = up to -20 points
            
            # Ensure score is within bounds
            return max(0, min(100, round(score, 1)))
            
        except Exception:
            return 50.0  # Default neutral score
    
    def _generate_analysis_details(self, cost_delta: float, aqi_delta: float, 
                                   life_exp_delta: float, recommendation_score: float) -> Dict:
        """Generate detailed analysis and recommendations"""
        
        analysis = {
            'primary_factors': [],
            'trade_offs': [],
            'recommendations': [],
            'risk_factors': []
        }
        
        # Primary factors analysis
        if abs(life_exp_delta) > 1.0:
            if life_exp_delta > 0:
                analysis['primary_factors'].append(f"Significant health benefit: +{life_exp_delta:.2f} years life expectancy")
            else:
                analysis['primary_factors'].append(f"Health concern: {life_exp_delta:.2f} years life expectancy reduction")
        
        if abs(cost_delta) > 20:
            if cost_delta > 0:
                analysis['primary_factors'].append(f"High cost increase: +{cost_delta:.1f}% cost of living")
            else:
                analysis['primary_factors'].append(f"Significant savings: {cost_delta:.1f}% cost of living reduction")
        
        if abs(aqi_delta) > 25:
            if aqi_delta > 0:
                analysis['primary_factors'].append(f"Air quality concern: +{aqi_delta:.1f} AQI increase")
            else:
                analysis['primary_factors'].append(f"Better air quality: {aqi_delta:.1f} AQI improvement")
        
        # Trade-offs analysis
        if cost_delta > 0 and life_exp_delta > 0:
            analysis['trade_offs'].append("Higher living costs but better health outcomes")
        elif cost_delta < 0 and life_exp_delta < 0:
            analysis['trade_offs'].append("Lower costs but potential health risks")
        elif cost_delta > 0 and life_exp_delta < 0:
            analysis['trade_offs'].append("Higher costs AND worse health outcomes")
        elif cost_delta < 0 and life_exp_delta > 0:
            analysis['trade_offs'].append("Lower costs AND better health - ideal scenario")
        
        # Recommendations based on score
        if recommendation_score >= 75:
            analysis['recommendations'].append("Highly recommended move - strong benefits outweigh costs")
        elif recommendation_score >= 60:
            analysis['recommendations'].append("Generally positive move - benefits likely outweigh drawbacks")
        elif recommendation_score >= 40:
            analysis['recommendations'].append("Mixed outcomes - carefully consider personal priorities")
        elif recommendation_score >= 25:
            analysis['recommendations'].append("Consider alternatives - significant trade-offs involved")
        else:
            analysis['recommendations'].append("Not recommended - costs and risks outweigh benefits")
        
        # Risk factors
        if aqi_delta > 50:
            analysis['risk_factors'].append("Significant air quality deterioration")
        if cost_delta > 50:
            analysis['risk_factors'].append("Very high cost of living increase")
        if life_exp_delta < -1:
            analysis['risk_factors'].append("Substantial health impact concerns")
        
        return analysis
