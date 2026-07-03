import requests
import json
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"

def overpass_to_geojson(data):
    features = []
    if not data or 'elements' not in data:
        return {"type": "FeatureCollection", "features": features}
    for element in data['elements']:
        tags = element.get('tags', {})
        geom = None
        if element['type'] == 'node':
            geom = {"type": "Point", "coordinates": [element['lon'], element['lat']]}
        elif element['type'] == 'way' and 'center' in element:
            geom = {"type": "Point", "coordinates": [element['center']['lon'], element['center']['lat']]}
        if geom:
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {"id": element['id'], "name": tags.get('name', 'Unknown Mosque'), **tags}
            })
    return {"type": "FeatureCollection", "features": features}

bbox = "-0.55,39.5,-0.35,39.75"
query = f"""
[out:json][timeout:90];
(
  node["amenity"="place_of_worship"]({bbox});
  way["amenity"="place_of_worship"]({bbox});
);
out center;
"""
print("Fetching places of worship...")
headers = {'User-Agent': 'GarissaDRM/1.0'}
response = requests.post("http://overpass-api.de/api/interpreter", data={'data': query}, headers=headers)
data = response.json()
# Filter manually for mosques just in case
if 'elements' in data:
    data['elements'] = [e for e in data['elements'] if e.get('tags', {}).get('religion') == 'muslim' or 'mosque' in e.get('tags', {}).get('name', '').lower() or e.get('tags', {}).get('building') == 'mosque']
    
geojson = overpass_to_geojson(data)
with open(OUTPUT_DIR / "garissa_mosques.geojson", "w") as f:
    json.dump(geojson, f)
print(f"Saved {len(geojson['features'])} Mosques.")
