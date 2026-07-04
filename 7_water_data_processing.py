import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

# Paths
INPUT_DIR = Path("WATER DATA")
OUTPUT_DIR = Path("OUTPUT")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Process Boreholes
print("Processing Boreholes...")
try:
    df_boreholes = pd.read_csv(INPUT_DIR / "Merged 201022 WP-Final.csv", encoding='latin1')
    df_boreholes = df_boreholes.dropna(subset=['Latitude', 'Longitude'])
    df_boreholes['Latitude'] = pd.to_numeric(df_boreholes['Latitude'], errors='coerce')
    df_boreholes['Longitude'] = pd.to_numeric(df_boreholes['Longitude'], errors='coerce')
    df_boreholes = df_boreholes.dropna(subset=['Latitude', 'Longitude'])
    
    # Filter rogue data (Garissa rough bounds: Lat: -2.5 to 2.0, Lon: 38.0 to 42.0)
    df_boreholes = df_boreholes[
        (df_boreholes['Latitude'] >= -2.5) & (df_boreholes['Latitude'] <= 2.0) &
        (df_boreholes['Longitude'] >= 38.0) & (df_boreholes['Longitude'] <= 42.0)
    ]
    
    gdf_boreholes = gpd.GeoDataFrame(
        df_boreholes, 
        geometry=[Point(xy) for xy in zip(df_boreholes['Longitude'], df_boreholes['Latitude'])],
        crs="EPSG:4326"
    )
    # Save base boreholes
    gdf_boreholes.to_file(OUTPUT_DIR / "boreholes_updated.geojson", driver="GeoJSON")
    print(f"✅ Saved {len(gdf_boreholes)} valid boreholes.")
except Exception as e:
    print(f"Error processing boreholes: {e}")
    gdf_boreholes = gpd.GeoDataFrame()

# 2. Process Water Pans
print("Processing Water Pans...")
try:
    df_pans = pd.read_excel(INPUT_DIR / "Garissa_county_water_pans_updated_xlx.xlsx")
    df_pans = df_pans.rename(columns={'ycoord': 'Latitude', 'xcoord': 'Longitude'})
    df_pans = df_pans.dropna(subset=['Latitude', 'Longitude'])
    df_pans['Latitude'] = pd.to_numeric(df_pans['Latitude'], errors='coerce')
    df_pans['Longitude'] = pd.to_numeric(df_pans['Longitude'], errors='coerce')
    df_pans = df_pans.dropna(subset=['Latitude', 'Longitude'])
    
    # Filter rogue data
    df_pans = df_pans[
        (df_pans['Latitude'] >= -2.5) & (df_pans['Latitude'] <= 2.0) &
        (df_pans['Longitude'] >= 38.0) & (df_pans['Longitude'] <= 42.0)
    ]
    
    gdf_pans = gpd.GeoDataFrame(
        df_pans, 
        geometry=[Point(xy) for xy in zip(df_pans['Longitude'], df_pans['Latitude'])],
        crs="EPSG:4326"
    )
    # Save base water pans
    gdf_pans.to_file(OUTPUT_DIR / "water_pans_updated.geojson", driver="GeoJSON")
    print(f"✅ Saved {len(gdf_pans)} valid water pans.")
except Exception as e:
    print(f"Error processing water pans: {e}")

# 3. Calculate Distances for Schools and Health Facilities
print("Calculating distances to nearest boreholes...")

def calculate_nearest(target_gdf, resource_gdf, resource_name_col, out_col_dist, out_col_name):
    # Ensure geometries are valid and drop NaNs
    target_gdf = target_gdf[target_gdf.is_valid & ~target_gdf.is_empty].copy()
    resource_gdf = resource_gdf[resource_gdf.is_valid & ~resource_gdf.is_empty].copy()
    
    if target_gdf.empty or resource_gdf.empty:
        return target_gdf
        
    # Reproject to a metric CRS for accurate distance (e.g., EPSG:3857)
    target_metric = target_gdf.to_crs(epsg=3857)
    resource_metric = resource_gdf.to_crs(epsg=3857)
    
    nearest_dists = []
    nearest_names = []
    
    for idx, row in target_metric.iterrows():
        geom = row.geometry
        distances = resource_metric.geometry.distance(geom)
        min_dist_idx = distances.idxmin()
        min_dist_m = distances[min_dist_idx]
        nearest_dists.append(round(min_dist_m / 1000.0, 2)) # in km
        
        # Handle case where name is empty/NaN
        r_name = resource_gdf.loc[min_dist_idx, resource_name_col]
        if pd.isna(r_name):
            r_name = "Unnamed Borehole"
        nearest_names.append(str(r_name))
        
    target_gdf[out_col_dist] = nearest_dists
    target_gdf[out_col_name] = nearest_names
    return target_gdf

# Schools
try:
    if os.path.exists(OUTPUT_DIR / "schools_risk_assessed.geojson") and not gdf_boreholes.empty:
        gdf_schools = gpd.read_file(OUTPUT_DIR / "schools_risk_assessed.geojson")
        gdf_schools = calculate_nearest(
            gdf_schools, gdf_boreholes, 'Village', 
            'Dist_to_Borehole_km', 'Nearest_Borehole'
        )
        gdf_schools.to_file(OUTPUT_DIR / "schools_risk_assessed.geojson", driver="GeoJSON")
        print("✅ Updated schools with nearest borehole data.")
except Exception as e:
    print(f"Error updating schools: {e}")

# Health Clinics
try:
    if os.path.exists(OUTPUT_DIR / "health_facilities_risk_assessed.geojson") and not gdf_boreholes.empty:
        gdf_health = gpd.read_file(OUTPUT_DIR / "health_facilities_risk_assessed.geojson")
        gdf_health = calculate_nearest(
            gdf_health, gdf_boreholes, 'Village', 
            'Dist_to_Borehole_km', 'Nearest_Borehole'
        )
        gdf_health.to_file(OUTPUT_DIR / "health_facilities_risk_assessed.geojson", driver="GeoJSON")
        print("✅ Updated health facilities with nearest borehole data.")
except Exception as e:
    print(f"Error updating health facilities: {e}")

# IDP Camps
try:
    if os.path.exists(OUTPUT_DIR / "idp_camps_risk_assessed.geojson") and not gdf_boreholes.empty:
        gdf_camps = gpd.read_file(OUTPUT_DIR / "idp_camps_risk_assessed.geojson")
        
        # Count boreholes in camp boundaries
        camps_metric = gdf_camps.to_crs(epsg=3857)
        boreholes_metric = gdf_boreholes.to_crs(epsg=3857)
        
        # Approximate a 2km buffer around camps for borehole availability
        camp_buffers = camps_metric.geometry.buffer(2000)
        
        borehole_counts = []
        for buff in camp_buffers:
            count = boreholes_metric.geometry.within(buff).sum()
            borehole_counts.append(int(count))
            
        gdf_camps['Boreholes_Within_2km'] = borehole_counts
        
        gdf_camps = calculate_nearest(
            gdf_camps, gdf_boreholes, 'Village', 
            'Dist_to_Nearest_Borehole_km', 'Nearest_Borehole'
        )
        gdf_camps.to_file(OUTPUT_DIR / "idp_camps_risk_assessed.geojson", driver="GeoJSON")
        print("✅ Updated IDP camps with borehole counts and nearest data.")
except Exception as e:
    print(f"Error updating IDP camps: {e}")

print("🎉 Water data processing complete!")
