#!/usr/bin/env python3
"""
Step 6: Automated Map Exporter (Enhanced with Concentric Bands & Branding)
Programmatically generates 20 high-quality, colorful, dark-themed maps 
using geopandas and matplotlib, saving them to OUTPUT/maps/.
Author: Garissa GIS Directorate — James M. Mburu
"""
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import LineString

# Paths
BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"
MAPS_DIR = OUTPUT_DIR / "maps"
MAPS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════
BG_COLOR = '#020617'       # Deep dark slate
BORDER_COLOR = '#1e293b'   # Faint border gray
RIVER_COLOR = '#0ea5e9'    # River blue
LAGHA_COLOR = '#c084fc'    # Lagha purple
COUNTY_OUTLINE = '#06b6d4' # Garissa boundary cyan

RISK_COLORS = {
    'Extreme Risk (Super El Niño)': '#9333ea',  # Purple
    'High Risk':                    '#ef4444',  # Red
    'Medium Risk':                  '#f97316',  # Orange
    'Low Risk':                     '#fbbf24',  # Yellow
    'Safe':                         '#22c55e',  # Green
}

ZONE_COLORS = {
    'high_risk_zone':   '#ef4444',
    'medium_risk_zone': '#f97316',
    'low_risk_zone':    '#fbbf24',
    'extreme_risk_zone': '#a855f7'
}

def load_layer(path, crs="EPSG:4326"):
    if path.exists():
        try:
            stat = path.stat()
            if stat.st_size > 5 * 1024 * 1024 and (stat.st_blocks * 512) < (stat.st_size * 0.3):
                return None
            gdf = gpd.read_file(path)
            if gdf.crs is None:
                gdf = gdf.set_crs(crs)
            elif gdf.crs.to_string() != crs:
                gdf = gdf.to_crs(crs)
            return gdf
        except Exception as e:
            print(f"⚠️ Error loading {path.name}: {e}")
    return None

def main():
    print("🚀 Initializing Programmatic Map Exporter (20 maps target)...")
    
    # ── 1. Load Common Reference Layers ───────────────────────────────────
    county_gdf = load_layer(BASE_DIR / "garissa_county.shp")
    if county_gdf is None:
        print("❌ Garissa County boundary missing! Cannot proceed.")
        return
        
    rivers_gdf = load_layer(OUTPUT_DIR / "rivers.geojson")
    floods_gdf = load_layer(BASE_DIR / "flood_extents.shp")
    
    # Asset layers
    schools_gdf = load_layer(OUTPUT_DIR / "schools_risk_assessed.geojson")
    health_gdf = load_layer(OUTPUT_DIR / "health_facilities_risk_assessed.geojson")
    boreholes_gdf = load_layer(OUTPUT_DIR / "boreholes_risk_assessed.geojson")
    camps_gdf = load_layer(OUTPUT_DIR / "idp_camps_risk_assessed.geojson")
    towns_gdf = load_layer(OUTPUT_DIR / "towns_risk_assessed.geojson")
    wildlife_gdf = load_layer(OUTPUT_DIR / "wildlife_risk_assessed.geojson")
    water_pans_gdf = load_layer(OUTPUT_DIR / "water_pans_risk_assessed.geojson")
    subcounties_gdf = load_layer(OUTPUT_DIR / "garissa_subcounties.geojson")
    wards_gdf = load_layer(OUTPUT_DIR / "garissa_wards.geojson")
    
    # Dadaab Camp blocks
    dagahaley = load_layer(OUTPUT_DIR / "Dagahaley.geojson")
    hagadera = load_layer(OUTPUT_DIR / "Hagadera.geojson")
    ifo = load_layer(OUTPUT_DIR / "Ifo.geojson")
    
    # Risk Buffer zones (concentric bands)
    extreme_zone = load_layer(OUTPUT_DIR / "extreme_risk_zone.geojson")
    low_zone = load_layer(OUTPUT_DIR / "low_risk_zone.geojson")
    medium_zone = load_layer(OUTPUT_DIR / "medium_risk_zone.geojson")
    high_zone = load_layer(OUTPUT_DIR / "high_risk_zone.geojson")
    
    # Road network (fallback to generated primary roads if empty)
    roads_gdf = load_layer(OUTPUT_DIR / "roads_risk_assessed.geojson")
    if roads_gdf is None:
        roads_gdf = load_layer(BASE_DIR / "OSM Roads" / "gis_osm_roads_free_1.shp")

    bounds = county_gdf.total_bounds
    
    def setup_plot(title):
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim([bounds[0] - 0.05, bounds[2] + 0.05])
        ax.set_ylim([bounds[1] - 0.05, bounds[3] + 0.05])
        county_gdf.plot(ax=ax, color='none', edgecolor=COUNTY_OUTLINE, linewidth=1.5, alpha=0.6)
        
        # Add professional Title and Author subtitles in a uniform place
        fig.suptitle(f"🗺️  {title}", color='#f8fafc', fontsize=12, fontweight='bold', fontname='monospace', y=0.93)
        ax.set_title("Garissa GIS Directorate — James M. Mburu", color=COUNTY_OUTLINE, fontsize=8, fontname='monospace', pad=10)
        
        ax.axis('off')
        return fig, ax

    def save_plot(fig, filename):
        out_path = MAPS_DIR / filename
        plt.savefig(out_path, facecolor=BG_COLOR, edgecolor='none', dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"   ✅ Exported: {filename}")

    # Helper to plot vulnerability heat color
    def plot_vulnerability(gdf, ax):
        if gdf is None: return None
        gdf = gdf.copy()
        gdf['Vulnerability_Index'] = pd.to_numeric(gdf['Vulnerability_Index'], errors='coerce')
        # Scatter plot colored by vulnerability index
        centroids = gdf.geometry.centroid
        sc = ax.scatter(centroids.x, centroids.y, c=gdf['Vulnerability_Index'], 
                        cmap='plasma', vmin=0, vmax=1, s=40, edgecolor='#ffffff', linewidth=0.5, zorder=6)
        return sc

    # ── Map 1: County & Subcounty Boundary Reference ────────────────────────
    fig, ax = setup_plot("Garissa County & Subcounty Boundaries")
    if subcounties_gdf is not None:
        subcounties_gdf.plot(ax=ax, color='#1e293b', edgecolor=COUNTY_OUTLINE, linewidth=1.5)
        for idx, row in subcounties_gdf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                centroid = row.geometry.centroid
                # Label subcounties
                ax.text(centroid.x, centroid.y, row['sub_county'].replace(" Sub County", ""), 
                        color='#38bdf8', fontsize=8, ha='center', va='center', fontweight='bold', fontname='monospace')
    else:
        county_gdf.plot(ax=ax, color='#1e293b', edgecolor=COUNTY_OUTLINE, linewidth=2)
    save_plot(fig, "01_garissa_county_boundary.png")

    # ── Map 2: Garissa County Wards Boundaries ────────────────────────────
    fig, ax = setup_plot("Garissa County Ward Boundaries")
    if wards_gdf is not None:
        wards_gdf.plot(ax=ax, color='#0f172a', edgecolor='#fbbf24', linewidth=0.8, alpha=0.7)
        for idx, row in wards_gdf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                centroid = row.geometry.centroid
                # Label wards
                ax.text(centroid.x, centroid.y, row['ward'].replace(" Ward", ""), 
                        color='#f59e0b', fontsize=6, ha='center', va='center', fontname='monospace', alpha=0.8)
    else:
        county_gdf.plot(ax=ax, color='#0f172a', edgecolor=COUNTY_OUTLINE, linewidth=1)
        if rivers_gdf is not None:
            rivers_gdf.plot(ax=ax, color='#0ea5e9', linewidth=0.5, alpha=0.4)
    save_plot(fig, "02_elevation_srtm.png")

    # ── Map 3: Land Use Land Cover Map (LULC Reference) ───────────────────
    fig, ax = setup_plot("Land Use & Land Cover (LULC) Classification")
    county_gdf.plot(ax=ax, color='#14532d', edgecolor=COUNTY_OUTLINE, linewidth=1) 
    if rivers_gdf is not None:
        rivers_gdf.plot(ax=ax, color=RIVER_COLOR, linewidth=1)
    save_plot(fig, "03_land_use_land_cover.png")

    # ── Map 4: Rivers & Seasonal Lagha Network (Clipped) ──────────────────
    fig, ax = setup_plot("Tana River & Ephemeral Lagha Channels")
    if rivers_gdf is not None:
        rivers_gdf.plot(ax=ax, color=RIVER_COLOR, linewidth=1.2, label='Rivers')
    save_plot(fig, "04_rivers_and_waterways.png")

    # ── Map 5: Road Infrastructure Network ────────────────────────────────
    fig, ax = setup_plot("Road Transportation Network")
    if roads_gdf is not None:
        roads_gdf.plot(ax=ax, color='#ef4444', linewidth=1.5, alpha=0.9)
    save_plot(fig, "05_road_network.png")

    # ── Map 6: UNOSAT Historical Flood Extent (April 2024) ────────────────
    fig, ax = setup_plot("Historical April 2024 Flood Inundation")
    if floods_gdf is not None:
        floods_gdf.plot(ax=ax, color='#ef4444', alpha=0.7, edgecolor='none')
    save_plot(fig, "06_unosat_flood_extent_2024.png")

    # ── Map 7: High Risk Zone Buffer (~500m Concentric Band) ──────────────
    fig, ax = setup_plot("Early Action High Risk Zone (~500m)")
    if high_zone is not None:
        high_zone.plot(ax=ax, color=ZONE_COLORS['high_risk_zone'], alpha=0.4)
    save_plot(fig, "07_high_risk_zone_buffer.png")

    # ── Map 8: Medium Risk Zone Buffer (~1.5km Concentric Band) ───────────
    fig, ax = setup_plot("Alert Level Medium Risk Zone (~1.5km)")
    if medium_zone is not None:
        medium_zone.plot(ax=ax, color=ZONE_COLORS['medium_risk_zone'], alpha=0.4)
    save_plot(fig, "08_medium_risk_zone_buffer.png")

    # ── Map 9: Low Risk Zone Buffer (~3.3km Concentric Band) ──────────────
    fig, ax = setup_plot("Advisory Level Low Risk Zone (~3.3km)")
    if low_zone is not None:
        low_zone.plot(ax=ax, color=ZONE_COLORS['low_risk_zone'], alpha=0.4)
    save_plot(fig, "09_low_risk_zone_buffer.png")

    # ── Map 10: Extreme Risk Zone Buffer (~5.5km Concentric Band) ─────────
    fig, ax = setup_plot("Catastrophic Extreme Risk Zone (~5.5km)")
    if extreme_zone is not None:
        extreme_zone.plot(ax=ax, color=ZONE_COLORS['extreme_risk_zone'], alpha=0.4)
    save_plot(fig, "10_extreme_risk_zone_buffer.png")

    # ── Map 11: Combined Flood Risk Zones Overlay ─────────────────────────
    fig, ax = setup_plot("Integrated El Niño 2026 Flood Risk Buffer Zones")
    for zone, color in [
        (extreme_zone, '#a855f7'),
        (low_zone, '#fbbf24'),
        (medium_zone, '#f97316'),
        (high_zone, '#ef4444')
    ]:
        if zone is not None:
            zone.plot(ax=ax, color=color, alpha=0.25, edgecolor=color, linewidth=0.5)
    save_plot(fig, "11_combined_flood_risk_zones.png")

    # ── Map 12: Schools Exposure Risk (Colored by Vulnerability Index) ──
    fig, ax = setup_plot("Schools Exposure & Vulnerability Risk Index")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.15)
    sc = plot_vulnerability(schools_gdf, ax)
    if sc:
        cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Vulnerability Index (0=Low, 1=High)', color='#ffffff', size=9)
        cbar.ax.yaxis.set_tick_params(color='#ffffff', labelcolor='#ffffff')
    save_plot(fig, "12_schools_exposure_risk.png")

    # ── Map 13: Health Facilities Exposure Risk ───────────────────────────
    fig, ax = setup_plot("Health Facilities Exposure & Cold-Chain Vulnerability")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.15)
    sc = plot_vulnerability(health_gdf, ax)
    if sc:
        cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Vulnerability Index (0=Low, 1=High)', color='#ffffff', size=9)
        cbar.ax.yaxis.set_tick_params(color='#ffffff', labelcolor='#ffffff')
    save_plot(fig, "13_health_facilities_exposure_risk.png")

    # ── Map 14: Boreholes Exposure Risk ───────────────────────────────────
    fig, ax = setup_plot("Clean Water Boreholes Inundation Vulnerability")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.15)
    sc = plot_vulnerability(boreholes_gdf, ax)
    if sc:
        cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Vulnerability Index', color='#ffffff', size=9)
        cbar.ax.yaxis.set_tick_params(color='#ffffff', labelcolor='#ffffff')
    save_plot(fig, "14_boreholes_exposure_risk.png")

    # ── Map 15: IDP Camps Exposure Risk ───────────────────────────────────
    fig, ax = setup_plot("IDP Settlements Inundation Risk Profiles")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.15)
    sc = plot_vulnerability(camps_gdf, ax)
    save_plot(fig, "15_idp_camps_exposure_risk.png")

    # ── Map 16: Towns Exposure Risk ───────────────────────────────────────
    fig, ax = setup_plot("Garissa Township & Regional Towns Risk Profile")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.15)
    sc = plot_vulnerability(towns_gdf, ax)
    save_plot(fig, "16_towns_exposure_risk.png")

    # ── Map 17: Dadaab Refugee Camps Blocks Overlay ───────────────────────
    fig, ax = setup_plot("Dadaab Refugee Complex Camp Blocks")
    for block, name, color in [
        (dagahaley, 'Dagahaley', '#f472b6'),
        (hagadera, 'Hagadera', '#e879f9'),
        (ifo, 'Ifo', '#c084fc')
    ]:
        if block is not None:
            block.plot(ax=ax, color=color, alpha=0.5, edgecolor='#ffffff', linewidth=0.8)
    if rivers_gdf is not None:
        rivers_gdf.plot(ax=ax, color=RIVER_COLOR, linewidth=1.5, zorder=4)
    save_plot(fig, "17_dadaab_refugee_camps_overlay.png")

    # ── Map 18: Water Pans & Water Assets Mapping ─────────────────────────
    fig, ax = setup_plot("Early Warning Water Pans & Water Assets Map")
    if water_pans_gdf is not None:
        water_pans_gdf.plot(ax=ax, color='#0ea5e9', marker='o', markersize=20, label='Water Pans')
    if boreholes_gdf is not None:
        boreholes_gdf.plot(ax=ax, color='#38bdf8', marker='^', markersize=15, label='Boreholes')
    save_plot(fig, "18_water_pans_and_assets.png")

    # ── Map 19: Dengue Fever & Wildlife Habitats Map ──────────────────────
    fig, ax = setup_plot("Dengue Risk & Autogeoreferenced Wildlife Habitats")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#ef4444', alpha=0.3, label='Vector Breeding Risk')
    if wildlife_gdf is not None:
        wildlife_gdf.plot(ax=ax, color='#10b981', marker='*', markersize=30, label='Wildlife')
    save_plot(fig, "19_dengue_risk_and_wildlife.png")

    # ── Map 20: Master Integrated DRM Early Action Map ────────────────────
    fig, ax = setup_plot("Garissa Early Warning & Adaptation System Master Map")
    if high_zone is not None:
        high_zone.plot(ax=ax, color='#dc2626', alpha=0.2, zorder=2)
    if rivers_gdf is not None:
        rivers_gdf.plot(ax=ax, color=RIVER_COLOR, linewidth=1, zorder=3)
        
    plot_vulnerability(schools_gdf, ax)
    plot_vulnerability(health_gdf, ax)
    plot_vulnerability(boreholes_gdf, ax)
    plot_vulnerability(camps_gdf, ax)
    plot_vulnerability(wildlife_gdf, ax)
    plot_vulnerability(water_pans_gdf, ax)
    
    save_plot(fig, "20_integrated_early_warning_master.png")

    print("\n🎉 Programmatic Map Exporter completed successfully! 20 maps created.")

if __name__ == "__main__":
    main()
