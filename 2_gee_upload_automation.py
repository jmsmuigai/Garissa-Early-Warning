#!/usr/bin/env python3
"""
Step 3: GEE Asset Upload Automation for GarissaDRM
Iterates through the 'GEE_UPLOAD_READY' folder and uploads every spatial file
as an Earth Engine FeatureCollection using the earthengine-api/geemap.
"""
import os
import ee
import geemap
from pathlib import Path
import subprocess

# Define your target Google Cloud project and Earth Engine bucket
PROJECT_ID = "garissadrm"
ASSET_BUCKET = f"projects/{PROJECT_ID}/assets"
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "GEE_UPLOAD_READY"

def upload_to_gee():
    print("🚀 Initializing Earth Engine...")
    try:
        # Initialize the Earth Engine module.
        # This requires the user to have authenticated via `earthengine authenticate`
        ee.Initialize(project=PROJECT_ID)
    except Exception as e:
        print(f"❌ Error initializing Earth Engine: {e}")
        print(f"   Have you run `earthengine authenticate --auth_mode=notebook --project={PROJECT_ID}`?")
        return

    print(f"📂 Scanning for GeoJSONs to upload in {UPLOAD_DIR.name}...")
    
    if not UPLOAD_DIR.exists():
        print(f"❌ Upload directory {UPLOAD_DIR} does not exist. Did you run the ingestion script?")
        return
        
    geojson_files = list(UPLOAD_DIR.glob('*.geojson'))
    
    if not geojson_files:
        print("⚠️ No GeoJSON files found to upload.")
        return
        
    print(f"   Found {len(geojson_files)} files to upload.")
    
    for file_path in geojson_files:
        asset_id = f"{ASSET_BUCKET}/{file_path.stem}"
        print(f"\n🔄 Uploading {file_path.name} to {asset_id}...")
        
        try:
            # We use the earthengine command line tool for reliable uploads
            # Command: earthengine upload table --asset_id=projects/garissadrm/assets/filename filename.geojson
            cmd = [
                "earthengine", "upload", "table", 
                f"--asset_id={asset_id}", 
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Upload task successfully submitted for {file_path.name}.")
                print(f"      (Check task status with 'earthengine task list')")
            else:
                print(f"   ❌ Upload failed for {file_path.name}: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Exception during upload of {file_path.name}: {e}")

if __name__ == "__main__":
    upload_to_gee()
