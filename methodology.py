"""
METHODOLOGY: True Cost of Living Analysis

This document explains the scientific methodology used to calculate the relationship 
between cost of living, air quality, and public health outcomes.

Core Methodology: AQLI-Inspired Life-Cost Analysis
Our analysis is based on the Air Quality Life Index (AQLI) methodology developed by 
the Energy Policy Institute at the University of Chicago, adapted for cost-of-living 
comparisons.

1. Air Quality Standardization (EPA-Based)
All air quality measurements are normalized to EPA standards using:
- PM2.5 concentration estimates derived from local AQI values
- Standardized AQI calculation using EPA breakpoints
- Health impact scaling based on WHO and EPA guidelines

Formula: AQI = ((I_hi - I_lo) / (C_hi - C_lo)) * (C - C_lo) + I_lo

2. Health-Adjusted Life Expectancy Calculation
Core Formula: ΔLE = β * (PM2.5_origin - PM2.5_destination) * RF
Where β = 0.098 years per μg/m³ (based on Pope et al. 2009, updated by AQLI)

3. Cost-Effectiveness Analysis
Cost per Life Year = (Annual_Cost_Delta * Life_Remaining) / Life_Expectancy_Delta

Value Assessment:
- Excellent: < $10,000 per life year
- Good: $10,000 - $50,000 per life year  
- Fair: $50,000 - $100,000 per life year
- Poor: > $100,000 per life year

References:
1. Pope, C.A. et al. (2009). Fine-particulate air pollution and life expectancy. NEJM.
2. Greenstone, M. & Fan, C.Q. (2018). Air Quality Life Index. University of Chicago.
3. WHO (2021). Ambient Air Quality Guidelines.
4. EPA (2012). Integrated Science Assessment for Particulate Matter.
"""

def get_methodology_text():
    """Return the methodology text for display in the app"""
    return """
## 🔬 Scientific Methodology

Our analysis uses the **Air Quality Life Index (AQLI)** methodology from the University of Chicago's Energy Policy Institute, adapted for cost-of-living comparisons.

### Key Calculations:
1. **Air Quality Standardization**: All AQI values normalized to EPA standards
2. **Health Impact**: Life expectancy change = 0.098 years per μg/m³ PM2.5 difference
3. **Cost-Effectiveness**: Dollar cost per life year gained/lost
4. **Risk Adjustment**: Diminishing returns in highly polluted areas

### Value Thresholds:
- **Excellent**: < $10,000 per life year
- **Good**: $10,000 - $50,000 per life year
- **Fair**: $50,000 - $100,000 per life year
- **Poor**: > $100,000 per life year

### Data Sources:
- **Air Quality**: RapidAPI Weather Service
- **Cost of Living**: RapidAPI Find Places to Live
- **Life Expectancy**: World Bank API

### Limitations:
- City-level life expectancy estimated from country averages
- PM2.5 concentrations estimated from AQI values
- Health impacts assume long-term residence (5+ years)
- Cost data may not reflect individual circumstances

**Based on**: Pope et al. (2009) NEJM, Greenstone & Fan (2018) AQLI, WHO Guidelines
"""