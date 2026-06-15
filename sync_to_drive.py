#!/usr/bin/env python3
"""
sync_to_drive.py
Workaround sync script to transfer updated notebook, HTML outputs, scripts,
and map gallery PNGs back to the Google Drive workspace safely.
Bypasses FileProvider locks by unlinking destination files before copying.
"""
import os
import shutil
from pathlib import Path

LOCAL_DIR = Path("/Users/james/garissa_local_workdir")
DRIVE_DIR = Path("/Users/james/Library/CloudStorage/GoogleDrive-jmsmuigai@gmail.com/My Drive/GARISSADRM")

# Files to sync directly from root
ROOT_FILES = [
    "garissa_elnino_flood_risk.ipynb",
    "garissa_flood_risk_story.html",
    "2_flood_risk_analysis.py",
    "3_qgis_workspace_builder.py",
    "5_generate_dashboard.py",
    "6_generate_maps.py",
    "run_full_pipeline.sh",
    "index.html",
    "fast_sync.py",
    "sync_to_drive.py"
]

def safe_copy(src: Path, dst: Path):
    """Safely copies a file by deleting the destination first to bypass sync locks."""
    try:
        if dst.exists():
            # Standard cp or write causes FileProvider locks on Google Drive.
            # Unlinking first removes the sync lock on the existing file name.
            dst.unlink()
        
        # Ensure parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"   ✅ Synced: {src.name} -> {dst.relative_to(DRIVE_DIR)}")
    except Exception as e:
        print(f"   ❌ Error syncing {src.name} to {dst}: {e}")

def sync_directory(src_dir: Path, dst_dir: Path):
    """Recursively syncs a directory using the unlink-before-copy workaround."""
    if not src_dir.exists():
        return
        
    for root, dirs, files in os.walk(src_dir):
        rel_path = Path(root).relative_to(src_dir)
        target_dir = dst_dir / rel_path
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            src_file = Path(root) / file
            dst_file = target_dir / file
            
            # Skip temp or cache files
            if file.startswith(".") or file.endswith(".pyc") or "__pycache__" in root:
                continue
                
            safe_copy(src_file, dst_file)

def main():
    print("🔄 Starting bidrectional sync back to Google Drive...")
    
    if not DRIVE_DIR.exists():
        print(f"❌ Google Drive workspace directory not found at {DRIVE_DIR}")
        return
        
    # 1. Sync specified root files
    print("\n📦 Syncing root scripts and deliverables...")
    for filename in ROOT_FILES:
        src = LOCAL_DIR / filename
        dst = DRIVE_DIR / filename
        if src.exists():
            safe_copy(src, dst)
            
    # 2. Sync OUTPUT/ directory (contains maps, geojsons, resource tables)
    print("\n🗺️  Syncing OUTPUT directory (maps, data, reports)...")
    sync_directory(LOCAL_DIR / "OUTPUT", DRIVE_DIR / "OUTPUT")
    
    print("\n🎉 Sync back to Google Drive completed successfully!")

if __name__ == "__main__":
    main()
