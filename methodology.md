# Village Economic Growth Intelligence

## Overview
This project identifies the top 100 economically growing villages in a given district (currently configured for Goalpara, Assam) between 2020 and 2025. Because traditional economic data is rarely granular enough for the village level, this pipeline relies on satellite imagery and geospatial proxies to measure ground-level economic activity.

## Definition of "Economic Growth"
In this framework, **Economic Growth** is defined as the concurrent expansion of physical infrastructure and electricity consumption, supported by a stable or growing human capital base. 
A village is only classified as "growing" if it exhibits positive change in *both* built-up area and nightlight emissions.

## Data Sources & Justification
All data is open-source and extracted via Google Earth Engine (GEE).
1. **NOAA VIIRS Nighttime Day/Night Band Composites (VCMCFG):** 
   * **Justification:** Nightlights are a globally recognized proxy for economic activity, capturing household wealth, electrification, and commercial operations. We used median annual composites to filter out temporal noise.
2. **Google Dynamic World (V1):**
   * **Justification:** A 10m resolution land-cover dataset. Instead of categorical labels, we used continuous probability bands for `built`, `crops`, and `trees` to track the physical transition of land into concrete infrastructure (capital investment) and the clearing of vegetation.
3. **WorldPop Global Project Population Data (100m):**
   * **Justification:** Estimates demographic shifts. While population alone doesn't guarantee wealth, it acts as a supporting metric for labor force expansion.

## Pipeline Methodology (Extraction -> Cleaning -> Processing -> Scoring)
1. **Extraction:** Data is extracted asynchronously via GEE batch tasks to handle large geometries without timeout errors.
2. **Cleaning (Spatial & Outlier):** 
   * *Resolution Constraint:* VIIRS has a native resolution of ~463m (~21 hectares). Villages smaller than 50 hectares are removed to prevent "mixed pixel" light contamination from neighboring areas.
   * *Anomaly Removal:* Interquartile Range (IQR) filtering is applied to remove extreme anomalies (e.g., solar glare or classification errors) that could skew the index.
3. **Processing (Scaling):** Because the variables have vastly different scales and distributions with long right tails, a `RobustScaler` (using median and IQR) is applied to normalize the features into a comparable format without being skewed by outliers.
4. **Scoring:** A Normalized Weighted Sum is applied:
   * **45% Built-up Change:** Heavy weight for direct infrastructure investment.
   * **45% Nightlight Change:** Heavy weight for energy consumption/commercial activity.
   * **10% Population Change:** Minor weight as a supporting demographic indicator.
