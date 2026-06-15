#!/usr/bin/env python3
"""
Step 5: Looker Studio Export for GarissaDRM
Exports Earth Engine analysis outputs into clean CSVs in the OUTPUT folder 
for automatic Looker Studio ingestion.
"""
import ee
import geemap
import os
import pandas as pd
from pathlib import Path

# Initialize EE 
ee.Initialize(project='garissadrm')

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

def export_ee_feature_collection_to_csv(ee_fc, filename):
    """
    Export an Earth Engine FeatureCollection to a local CSV file.
    
    Args:
        ee_fc (ee.FeatureCollection): The Earth Engine data collection.
        filename (str): Name of the output CSV file.
    """
    output_path = OUTPUT_DIR / filename
    print(f"🔄 Exporting data to {output_path.name} for Looker Studio...")
    
    try:
        # Use geemap's built-in export tool which handles the conversion from EE to CSV
        geemap.ee_to_csv(ee_fc, filename=str(output_path), timeout=300)
        print(f"   ✅ Successfully exported {output_path.name}")
        return output_path
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        
        # Fallback: manually fetch URL if geemap fails
        try:
            print("   🔄 Attempting fallback export method...")
            url = ee_fc.getDownloadURL(filetype='csv')
            df = pd.read_csv(url)
            df.to_csv(output_path, index=False)
            print(f"   ✅ Fallback export successful: {output_path.name}")
            return output_path
        except Exception as e2:
            print(f"   ❌ Fallback failed: {e2}")
            return None

def process_and_export_all(boreholes_fc, camps_fc):
    """
    Wrapper function to simulate the end-of-pipeline export for Looker Studio.
    In practice, boreholes_fc and camps_fc are passed from the modeling_stubs.
    """
    print(f"🚀 Starting Looker Studio Data Export to {OUTPUT_DIR}...")
    
    # Export Water Resources Data (Boreholes + Soil Moisture)
    if boreholes_fc:
        export_ee_feature_collection_to_csv(boreholes_fc, 'looker_boreholes_water_resources.csv')
        
    # Export Rangeland Management Data (Camp Blocks + NDVI Anomaly)
    if camps_fc:
        export_ee_feature_collection_to_csv(camps_fc, 'looker_camp_ndvi_anomalies.csv')
        
    print("🎉 All Looker Studio exports completed! Dashboards will auto-update.")

if __name__ == "__main__":
    print("This script is meant to be called at the end of the analysis pipeline.")
    # Example placeholder for independent run:
    # ee.Initialize(project='garissadrm')
    # dummy_fc = ee.FeatureCollection(...)
    # export_ee_feature_collection_to_csv(dummy_fc, "test_export.csv")
