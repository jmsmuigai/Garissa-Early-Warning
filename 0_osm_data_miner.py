#!/usr/bin/env python3
"""
OSM Data Miner for Garissa DRM
Fetches Mosques, Bullas (Informal Settlements), and Named POIs using Overpass API.
Author: Garissa GIS Directorate
"""
import requests
import json
import time
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def get_overpass_query(query_str):
    try:
        headers = {'User-Agent': 'GarissaDRM/1.0 (Python)'}
        response = requests.post(OVERPASS_URL, data={'data': query_str}, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching from Overpass: {e}")
        return None

def overpass_to_geojson(data, name_field="name"):
    features = []
    if not data or 'elements' not in data:
        return {"type": "FeatureCollection", "features": features}
        
    for element in data['elements']:
        tags = element.get('tags', {})
        geom = None
        
        if element['type'] == 'node':
            geom = {
                "type": "Point",
                "coordinates": [element['lon'], element['lat']]
            }
        elif element['type'] == 'way' and 'center' in element:
            geom = {
                "type": "Point",
                "coordinates": [element['center']['lon'], element['center']['lat']]
            }
        
        if geom:
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "id": element['id'],
                    "name": tags.get('name', 'Unknown'),
                    **tags
                }
            })
            
    return {"type": "FeatureCollection", "features": features}

def main():
    print("🌍 GARISSA DRM - OSM DATA MINER")
    print("=" * 50)
    
    # Bounding Box for Garissa Town and surrounding areas (approx: S: -0.55, W: 39.5, N: -0.35, E: 39.75)
    bbox = "-0.55,39.5,-0.35,39.75"
    
    print("⏳ Fetching Mosques in Garissa...")
    query_mosques = f"""
    [out:json][timeout:50];
    (
      node["amenity"="place_of_worship"]["religion"="muslim"]({bbox});
      way["amenity"="place_of_worship"]["religion"="muslim"]({bbox});
    );
    out center;
    """
    mosques_data = get_overpass_query(query_mosques)
    mosques_geojson = overpass_to_geojson(mosques_data)
    out_mosques = OUTPUT_DIR / "garissa_mosques.geojson"
    with open(out_mosques, 'w') as f:
        json.dump(mosques_geojson, f)
    print(f"✅ Saved {len(mosques_geojson['features'])} Mosques to {out_mosques.name}")
    
    time.sleep(2) # Respect Overpass rate limits
    
    print("⏳ Fetching Bullas (Informal Settlements/Neighborhoods)...")
    query_bullas = f"""
    [out:json][timeout:50];
    (
      node["place"~"neighbourhood|village|hamlet"]({bbox});
      node["name"~"Bulla",i]({bbox});
    );
    out center;
    """
    bullas_data = get_overpass_query(query_bullas)
    
    # Filter for names containing 'Bulla' or just keep all neighborhoods in Garissa township area
    # We will keep all to be safe, but specifically tag 'Bulla'
    bullas_geojson = overpass_to_geojson(bullas_data)
    out_bullas = OUTPUT_DIR / "garissa_bullas.geojson"
    with open(out_bullas, 'w') as f:
        json.dump(bullas_geojson, f)
    print(f"✅ Saved {len(bullas_geojson['features'])} Neighborhoods/Bullas to {out_bullas.name}")
    
    time.sleep(2)
    
    print("⏳ Fetching Named POIs (Markets, Hospitals, Police)...")
    query_pois = f"""
    [out:json][timeout:50];
    (
      node["amenity"~"hospital|clinic|police|marketplace|bus_station"]({bbox});
      way["amenity"~"hospital|clinic|police|marketplace|bus_station"]({bbox});
    );
    out center;
    """
    pois_data = get_overpass_query(query_pois)
    pois_geojson = overpass_to_geojson(pois_data)
    out_pois = OUTPUT_DIR / "garissa_pois.geojson"
    with open(out_pois, 'w') as f:
        json.dump(pois_geojson, f)
    print(f"✅ Saved {len(pois_geojson['features'])} POIs to {out_pois.name}")

    print("🎉 Data Mining Complete!")

if __name__ == "__main__":
    main()
