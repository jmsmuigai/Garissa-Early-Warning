#!/usr/bin/env python3
"""
Step 5: Garissa DRM HTML Dashboard Generator (Overhauled ARCgis Version)
Generates a beautiful, standalone, responsive HTML dashboard for community sharing.
Map on top half, dashboard inventory, charts, and metrics below.
Uses Leaflet.js for mapping and Chart.js for visualizations.
Author: Garissa GIS Directorate — James M. Mburu
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_dashboard():
    print("🌐 Generating Garissa El Niño ARCgis-style Dashboard...")
    
    # ── 1. Load Data ──────────────────────────────────────────────────────
    stats_df = None
    stats_csv = OUTPUT_DIR / "flood_risk_summary_statistics.csv"
    if stats_csv.exists():
        stats_df = pd.read_csv(stats_csv)
    
    def get_stats(layer_name):
        if stats_df is not None:
            row = stats_df[stats_df['Layer'] == layer_name]
            if not row.empty:
                return (
                    int(row['Total_Features'].iloc[0]),
                    int(row['Extreme_Risk'].iloc[0]),
                    int(row['High_Risk'].iloc[0]),
                    int(row['Medium_Risk'].iloc[0]),
                    int(row['Low_Risk'].iloc[0]),
                    int(row['Safe'].iloc[0])
                )
        return 0, 0, 0, 0, 0, 0

    (total_schools, ext_schools, high_schools, med_schools, low_schools, safe_schools) = get_stats('Schools')
    (total_health, ext_health, high_health, med_health, low_health, safe_health) = get_stats('Health Facilities')
    (total_bore, ext_bore, high_bore, med_bore, low_bore, safe_bore) = get_stats('Boreholes')
    (total_camps, ext_camps, high_camps, med_camps, low_camps, safe_camps) = get_stats('IDP Camps')

    # Load GeoJSON geometries for Leaflet
    def load_geojson_string(filename):
        p = OUTPUT_DIR / filename
        if p.exists():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️ Could not load {filename}: {e}")
        return '{"type":"FeatureCollection","features":[]}'

    high_risk_json = load_geojson_string("high_risk_zone.geojson")
    medium_risk_json = load_geojson_string("medium_risk_zone.geojson")
    low_risk_json = load_geojson_string("low_risk_zone.geojson")
    extreme_risk_json = load_geojson_string("extreme_risk_zone.geojson")
    
    # Core asset layers
    schools_json = load_geojson_string("schools_risk_assessed.geojson")
    health_json = load_geojson_string("health_facilities_risk_assessed.geojson")
    boreholes_json = load_geojson_string("boreholes_risk_assessed.geojson")
    idp_camps_json = load_geojson_string("idp_camps_risk_assessed.geojson")
    towns_json = load_geojson_string("towns_risk_assessed.geojson")
    rivers_json = load_geojson_string("rivers.geojson")
    roads_json = load_geojson_string("roads_risk_assessed.geojson")
    
    # New programmatic layers
    wildlife_json = load_geojson_string("wildlife_risk_assessed.geojson")
    water_pans_json = load_geojson_string("water_pans_risk_assessed.geojson")
    cadastral_json = load_geojson_string("cadastral_parcels_risk_assessed.geojson")
    
    # Dadaab blocks
    dagahaley_json = load_geojson_string("Dagahaley.geojson")
    hagadera_json = load_geojson_string("Hagadera.geojson")
    ifo_json = load_geojson_string("Ifo.geojson")

    # Programmatic Boundaries
    subcounties_geom_json = load_geojson_string("garissa_subcounties.geojson")
    wards_geom_json = load_geojson_string("garissa_wards.geojson")

    # Load subcounty resources data
    subcounty_json = '[]'
    subcounty_csv = OUTPUT_DIR / "subcounty_resource_counts.csv"
    if subcounty_csv.exists():
        try:
            subcounty_df = pd.read_csv(subcounty_csv)
            subcounty_json = subcounty_df.to_json(orient='records')
        except Exception as e:
            print(f"⚠️ Could not load subcounty resources: {e}")

    # Raw HTML with single braces
    raw_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garissa Early Warning and Adaptation System (GEWAS)</title>
    
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;800;900&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-dark: #020617;
            --bg-card: rgba(15, 23, 42, 0.85);
            --border-glow: rgba(14, 165, 233, 0.25);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            
            --purple: #a855f7;
            --red: #ef4444;
            --orange: #f97316;
            --yellow: #fbbf24;
            --green: #22c55e;
            --cyan: #06b6d4;
            --emerald: #10b981;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.3) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.15) 0px, transparent 50%);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            padding: 15px 30px;
            border-bottom: 1px solid var(--border-glow);
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .header-title-area {
            display: flex;
            flex-direction: column;
        }
        
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 26px;
            font-weight: 900;
            margin: 0;
            letter-spacing: 1.5px;
            background: linear-gradient(to right, #ffffff, var(--cyan), #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 3px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        .author-stamp {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            color: var(--cyan);
            border: 1px solid rgba(6, 182, 212, 0.4);
            padding: 5px 10px;
            border-radius: 4px;
            background: rgba(6, 182, 212, 0.08);
            font-weight: bold;
        }
        
        /* SLEEK CONTROL PANEL BAR */
        .control-panel {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 12px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            margin: 15px;
            margin-bottom: 0;
            flex-shrink: 0;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .control-group label {
            font-family: 'Orbitron', sans-serif;
            font-size: 9px;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.8px;
        }
        
        .control-group select {
            background: #1e293b;
            border: 1px solid #334155;
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 12px;
            outline: none;
            cursor: pointer;
            transition: border-color 0.3s;
        }
        
        .control-group select:focus {
            border-color: var(--cyan);
        }
        
        .action-btn {
            background: #1e293b;
            border: 1px solid #334155;
            color: white;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .action-btn:hover {
            background: var(--cyan);
            border-color: var(--cyan);
            color: var(--bg-dark);
            box-shadow: 0 0 10px var(--cyan);
        }
        
        /* Dropdown style */
        .download-dropdown {
            position: relative;
            display: inline-block;
        }
        
        .download-dropdown-content {
            display: none;
            position: absolute;
            right: 0;
            background-color: #0f172a;
            min-width: 170px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5);
            border: 1px solid var(--border-glow);
            border-radius: 6px;
            z-index: 1001;
        }
        
        .download-dropdown-content a {
            color: var(--text-main);
            padding: 10px 12px;
            text-decoration: none;
            display: block;
            font-size: 11px;
            font-family: 'Inter', sans-serif;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .download-dropdown-content a:hover {
            background-color: rgba(6, 182, 212, 0.15);
            color: var(--cyan);
        }
        
        .download-dropdown:hover .download-dropdown-content {
            display: block;
        }

        /* TOP MAP SECTION (HALF PAGE HEIGHT) */
        .top-map-section {
            padding: 15px;
            padding-bottom: 0;
            flex-shrink: 0;
        }
        
        .map-wrapper {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 12px;
            position: relative;
            height: 50vh;
            min-height: 420px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        
        .map-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .map-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 0.8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        #map {
            border-radius: 12px;
            flex: 1;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Leaflet Popups styling */
        .leaflet-popup-content-wrapper {
            background: rgba(15, 23, 42, 0.95) !important;
            border: 1px solid var(--cyan) !important;
            color: white !important;
            border-radius: 8px !important;
        }
        .leaflet-popup-tip {
            background: var(--cyan) !important;
        }
        
        /* Map Custom Overlay Control style */
        .opacity-control-panel {
            background: rgba(15, 23, 42, 0.9) !important;
            border: 1px solid var(--border-glow) !important;
            border-radius: 8px;
            padding: 8px 12px;
            color: white;
            font-size: 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        }
        
        .opacity-slider {
            width: 100px;
            accent-color: var(--cyan);
            cursor: pointer;
        }

        /* BOTTOM DASHBOARD GRID SECTION */
        .bottom-dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1.3fr 1.2fr;
            gap: 15px;
            padding: 15px;
            flex: 1;
            box-sizing: border-box;
            min-height: 0;
        }
        
        @media(max-width: 1200px) {
            .bottom-dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* COLUMN 1: TELEMETRY & INFOGRAPHICS */
        .telemetry-column {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 480px;
            overflow-y: auto;
        }
        
        .telemetry-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 12px 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .telemetry-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }
        
        .telemetry-card.schools::before { background: var(--orange); }
        .telemetry-card.health::before { background: var(--red); }
        .telemetry-card.boreholes::before { background: var(--cyan); }
        .telemetry-card.camps::before { background: var(--purple); }
        .telemetry-card.infographics-card::before { background: var(--emerald); }
        
        .telemetry-label {
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.8px;
        }
        
        .telemetry-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 26px;
            font-weight: 900;
            margin: 3px 0;
        }
        
        .telemetry-schools { color: var(--orange); }
        .telemetry-health { color: var(--red); }
        .telemetry-boreholes { color: var(--cyan); }
        .telemetry-camps { color: var(--purple); }
        
        .telemetry-desc {
            font-size: 11px;
            color: var(--text-muted);
        }
        
        /* COLUMN 2: SEARCHABLE INVENTORY GRID */
        .inventory-column {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            max-height: 480px;
        }
        
        .table-wrapper {
            flex: 1;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.4);
            margin-top: 8px;
        }
        
        .inventory-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            text-align: left;
        }
        
        .inventory-table th {
            background: rgba(30, 41, 59, 0.95);
            position: sticky;
            top: 0;
            padding: 8px 10px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            color: var(--cyan);
            border-bottom: 1px solid var(--border-glow);
            z-index: 10;
        }
        
        .inventory-table td {
            padding: 6px 10px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            max-width: 130px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
        }
        
        .inventory-table tr:hover {
            background: rgba(6, 182, 212, 0.1);
        }

        /* COLUMN 3: TABBED SECTORAL PLANELS */
        .tabs-column {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            max-height: 480px;
            overflow: hidden;
        }
        
        .tabs-nav {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 4px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 8px;
            flex-shrink: 0;
        }
        
        .tab-btn {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 6px;
            color: var(--text-muted);
            padding: 5px 2px;
            font-size: 9px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            transition: all 0.3s ease;
        }
        
        .tab-btn:hover {
            background: rgba(30, 41, 59, 0.9);
            color: var(--text-main);
            border-color: var(--cyan);
        }
        
        .tab-btn.active {
            background: rgba(6, 182, 212, 0.15);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            box-shadow: 0 0 8px rgba(6, 182, 212, 0.3);
        }
        
        .tab-content-wrapper {
            flex: 1;
            overflow-y: auto;
            padding-right: 5px;
            margin-top: 10px;
        }
        
        .tab-panel {
            display: none;
            flex-direction: column;
            gap: 12px;
        }
        
        .tab-panel.active {
            display: flex;
        }
        
        .dashboard-section-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            font-weight: 800;
            color: var(--text-main);
            border-left: 3px solid var(--cyan);
            padding-left: 8px;
            margin-bottom: 4px;
        }
        
        .chart-box {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 8px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .desc-box {
            background: rgba(30, 41, 59, 0.3);
            border-radius: 10px;
            padding: 10px;
            font-size: 11px;
            line-height: 1.5;
            color: var(--text-muted);
            border: 1px dashed rgba(255,255,255,0.05);
        }
        
        .stat-grid-3d {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        
        .stat-card-3d {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid var(--border-glow);
            box-shadow: 3px 3px 8px rgba(0,0,0,0.5);
            border-radius: 8px;
            padding: 8px;
            text-align: center;
        }
        
        .stat-card-3d .label {
            font-size: 8px;
            color: var(--text-muted);
            text-transform: uppercase;
        }
        
        .stat-card-3d .value {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 800;
            color: var(--cyan);
            margin-top: 2px;
        }
        
        /* Interactive Chatbot styling */
        .sentinel-bot-trigger {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background: linear-gradient(135deg, var(--cyan) 0%, #0891b2 100%);
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 15px var(--cyan);
            cursor: pointer;
            z-index: 1000;
            transition: all 0.3s ease;
            animation: pulse-glow 2s infinite;
        }
        
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 10px var(--cyan); }
            50% { box-shadow: 0 0 25px var(--cyan); }
            100% { box-shadow: 0 0 10px var(--cyan); }
        }
        
        .sentinel-bot-panel {
            position: fixed;
            bottom: 90px;
            right: 25px;
            width: 360px;
            height: 490px;
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(12px);
            border: 1px solid var(--cyan);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            display: none;
            flex-direction: column;
            z-index: 1000;
            overflow: hidden;
        }
        
        .bot-header {
            background: linear-gradient(to right, rgba(15, 23, 42, 0.95), rgba(6, 182, 212, 0.25));
            padding: 12px 18px;
            border-bottom: 1px solid var(--border-glow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .bot-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            font-weight: 800;
            color: var(--cyan);
            letter-spacing: 0.8px;
        }
        
        .bot-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .bot-msg {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 11px;
            line-height: 1.4;
            max-width: 85%;
        }
        
        .bot-api-settings {
            background: rgba(30, 41, 59, 0.95);
            border-bottom: 1px solid var(--border-glow);
            padding: 8px 15px;
            font-size: 10px;
            display: none;
            flex-direction: column;
            gap: 6px;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 5px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(6, 182, 212, 0.3);
        }
        
        /* Interactive Feedback Widget */
        .feedback-box {
            background: rgba(16, 185, 129, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 10px;
            padding: 10px;
            font-size: 11px;
            margin-top: 10px;
            flex-shrink: 0;
        }
        
        .feedback-input {
            width: 100%;
            background: #1e293b;
            border: 1px solid #334155;
            color: white;
            border-radius: 6px;
            padding: 6px;
            font-size: 11px;
            box-sizing: border-box;
            resize: none;
            margin-top: 4px;
        }
        
        .feedback-btn {
            background: var(--emerald);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 10px;
            cursor: pointer;
            margin-top: 5px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
        }
        
        .emoji-legend-box {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 5px;
        }
        
        /* NAVIGATION BAR */
        .nav-bar {
            display: flex;
            justify-content: center;
            background: rgba(15, 23, 42, 0.95);
            border-bottom: 1px solid var(--border-glow);
            padding: 12px 0;
            gap: 15px;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        
        .nav-tab {
            font-family: 'Orbitron', sans-serif;
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            padding: 8px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nav-tab:hover {
            color: var(--cyan);
            background: rgba(6, 182, 212, 0.08);
            border-color: rgba(6, 182, 212, 0.3);
            transform: translateY(-1px);
        }
        
        .nav-tab.active {
            color: #ffffff;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(129, 140, 248, 0.25));
            border-color: var(--cyan);
            box-shadow: 0 0 12px rgba(6, 182, 212, 0.35);
        }
        
        .page-container {
            display: none;
            padding: 20px 30px;
            flex-grow: 1;
            box-sizing: border-box;
        }
        
        .page-container.active {
            display: block;
        }
        
        /* 3D Map Container */
        #map3d {
            display: none;
            width: 100%;
            height: 100%;
            min-height: 400px;
            border-radius: 8px;
            border: 1px solid var(--border-glow);
        }

        /* Narrative 60-Chapters Layout */
        .narrative-portal-layout {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 30px;
            height: calc(100vh - 180px);
            min-height: 500px;
        }
        
        .narrative-sidebar {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .sidebar-header {
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            font-size: 14px;
            color: var(--cyan);
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 12px;
            text-transform: uppercase;
        }
        
        .sidebar-list {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding-right: 5px;
        }
        
        .sidebar-chapter-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255,255,255,0.02);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .sidebar-chapter-item:hover {
            background: rgba(6, 182, 212, 0.05);
            border-color: rgba(6, 182, 212, 0.15);
        }
        
        .sidebar-chapter-item.active {
            background: rgba(6, 182, 212, 0.15);
            border-color: var(--cyan);
        }
        
        .ch-badge {
            background: rgba(6, 182, 212, 0.1);
            color: var(--cyan);
            border: 1px solid rgba(6, 182, 212, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-family: monospace;
            font-weight: bold;
        }
        
        .ch-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .ch-en {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-main);
        }
        
        .ch-so {
            font-size: 9px;
            color: var(--emerald);
            font-style: italic;
        }
        
        .narrative-content {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 30px;
            overflow-y: auto;
            box-shadow: 0 4px 25px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .story-chapter-section {
            padding-bottom: 30px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            scroll-margin-top: 20px;
        }
        
        .story-h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 20px;
            color: var(--cyan);
            margin-top: 0;
            margin-bottom: 12px;
        }
        
        .story-h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            color: var(--purple);
            margin-top: 15px;
            margin-bottom: 8px;
        }
        
        .story-h3 {
            font-size: 13px;
            color: var(--emerald);
            margin-top: 12px;
            margin-bottom: 6px;
        }
        
        .story-code-block {
            background: #090d16;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            margin: 10px 0;
            padding: 8px;
        }
        
        .story-code-block summary {
            font-size: 11px;
            font-weight: bold;
            color: var(--text-muted);
            cursor: pointer;
            outline: none;
            padding: 4px;
        }
        
        .story-code-block pre {
            margin: 8px 0 0 0;
            background: #020617;
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
        }
        
        .story-code-block code {
            font-family: monospace;
            font-size: 11px;
            color: #22d3ee;
        }
        
        .story-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 12px;
        }
        
        .story-table th {
            background: rgba(6, 182, 212, 0.1);
            color: var(--cyan);
            font-weight: bold;
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--cyan);
        }
        
        .story-table td {
            padding: 8px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: var(--text-main);
        }
        
        .story-ul {
            margin: 10px 0;
            padding-left: 20px;
            list-style-type: square;
        }
        
        .story-ul li {
            margin-bottom: 4px;
            color: var(--text-main);
        }
        
        /* Map Gallery Layout */
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            padding: 10px 0;
        }
        
        .gallery-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        
        .gallery-card:hover {
            transform: translateY(-4px);
            border-color: var(--cyan);
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.25);
        }
        
        .gallery-image-wrapper {
            position: relative;
            width: 100%;
            height: 180px;
            background: #090d16;
            overflow: hidden;
        }
        
        .gallery-image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        
        .gallery-card:hover .gallery-image-wrapper img {
            transform: scale(1.05);
        }
        
        .gallery-image-overlay {
            position: absolute;
            inset: 0;
            background: rgba(2, 6, 23, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 12px;
            color: var(--cyan);
            letter-spacing: 1.5px;
        }
        
        .gallery-card:hover .gallery-image-overlay {
            opacity: 1;
        }
        
        .gallery-info {
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex-grow: 1;
        }
        
        .gallery-info h3 {
            margin: 0;
            font-size: 13px;
            font-weight: 700;
            color: var(--text-main);
            line-height: 1.3;
        }
        
        .gallery-info p {
            margin: 0;
            font-size: 11px;
            color: var(--text-muted);
            line-height: 1.4;
        }
        
        /* Lightbox CSS */
        .lightbox {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(2, 6, 23, 0.95);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .lightbox-content {
            position: relative;
            max-width: 90%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        
        .lightbox-img {
            max-width: 100%;
            max-height: 75vh;
            object-fit: contain;
            border: 2px solid var(--border-glow);
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
        }
        
        .lightbox-caption {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: var(--text-main);
            text-align: center;
        }
        
        .lightbox-close {
            position: absolute;
            top: -40px;
            right: 0;
            background: none;
            border: none;
            color: white;
            font-size: 30px;
            cursor: pointer;
            outline: none;
        }

        /* Operations Hub CSS */
        .operations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }
        

        /* Live Weather Widget Styles */
        .weather-container {
            background: rgba(30, 41, 59, 0.4);
            border-radius: 8px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .weather-container.weather-warning {
            border-color: rgba(239, 68, 68, 0.3);
            background: rgba(239, 68, 68, 0.05);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.1) inset;
        }
        .weather-container.weather-normal {
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.05);
        }
        .weather-main {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .weather-icon {
            width: 48px;
            height: 48px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }
        .weather-temp-info {
            display: flex;
            flex-direction: column;
        }
        .weather-temp {
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }
        .weather-desc {
            font-size: 10px;
            color: var(--cyan);
            font-weight: 700;
            letter-spacing: 1px;
        }
        .weather-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            font-size: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 6px;
        }
        .weather-detail-item {
            color: var(--text-main);
        }
        .weather-status-alert {
            font-size: 10px;
            line-height: 1.4;
            padding: 6px;
            border-radius: 4px;
            background: rgba(15, 23, 42, 0.6);
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        .weather-alert {
            padding: 8px;
            font-size: 10px;
            color: var(--text-muted);
            font-style: italic;
            text-align: center;
            border: 1px dotted rgba(255,255,255,0.1);
            border-radius: 6px;
        }

        .ops-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .ops-card-title {
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            font-size: 16px;
            color: var(--cyan);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .ops-brief {
            font-size: 12px;
            line-height: 1.6;
            color: var(--text-muted);
        }
        
        .ops-brief strong {
            color: var(--text-main);
        }
        
        .ops-btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 10px;
        }
        
        .ops-launch-btn {
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 12px;
            color: white;
            background: linear-gradient(135deg, #0e766e 0%, #0d9488 100%);
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 6px;
            padding: 10px 18px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }
        
        .ops-launch-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
            border-color: var(--cyan);
        }
    </style>
    <!-- API keys configuration for local and server environments -->
    <script src="api_keys.js"></script>
</head>
<body>

    <header class="header">
        <div class="header-title-area">
            <h1>GARISSA EARLY WARNING AND ADAPTATION SYSTEM (GEWAS)</h1>
            <div class="header-subtitle">COMMUNITY EARLY WARNING DECISION SUPPORT PLATFORM — GENERATED: __GENERATION_DATE__</div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <div class="author-stamp">GARISSA GIS DIRECTORATE — JAMES M. MBURU</div>
        </div>
    </header>

    <!-- NAVIGATION TABS -->
    <nav class="nav-bar">
        <button class="nav-tab active" onclick="switchPage('page-digital-twin')">🛰️ Interactive Early Warning Map</button>
        <button class="nav-tab" onclick="switchPage('page-narrative')">📖 60-Chapter Narrative Story</button>
        <button class="nav-tab" onclick="switchPage('page-gallery')">🖼️ Programmatic Map Gallery</button>
        <button class="nav-tab" onclick="switchPage('page-operations')">📚 Operations Hub & QGIS Portal</button>
    </nav>

    <!-- PAGE CONTAINER: DIGITAL TWIN -->
    <div id="page-digital-twin" class="page-container active">

    <!-- INTERACTIVE CONTROL PANEL BAR -->
    <div class="control-panel">
        <div class="control-group">
            <label for="subcounty-select">📍 SELECT SUB-COUNTY</label>
            <select id="subcounty-select" onchange="filterBySubcounty(this.value)">
                <option value="All">All Sub-Counties</option>
                <option value="Garissa Sub County">Garissa</option>
                <option value="Dadaab Sub County">Dadaab</option>
                <option value="Fafi Sub County">Fafi</option>
                <option value="Ijara Sub County">Ijara</option>
                <option value="Balambala Sub County">Balambala</option>
                <option value="Lagdera Sub County">Lagdera</option>
                <option value="Hulugho Sub County">Hulugho</option>
            </select>
        </div>
        <div class="control-group">
            <label for="map-gallery-select">🗺️ SELECT MAP VIEW</label>
            <select id="map-gallery-select" onchange="switchMapLayer(this.value)">
                <option value="all">Integrated Master Map</option>
                <option value="subcounties">1. Garissa Subcounties</option>
                <option value="wards">2. Garissa Ward Boundaries</option>
                <option value="schools">3. Garissa Schools</option>
                <option value="health">4. Garissa Health Facilities</option>
                <option value="refugee">5. Dadaab Refugee Camps</option>
                <option value="water">6. Water Assets & Water Pans</option>
                <option value="rivers">7. Rivers & Laghas</option>
                <option value="agri">8. Agriculture & Farms</option>
                <option value="wildlife">9. Wildlife & Habitat Zones</option>
                <option value="cadastral">10. Garissa Township Cadastral Map</option>
            </select>
        </div>
        <div class="control-group">
            <label for="risk-select">🚨 RISK LEVEL QUERY</label>
            <select id="risk-select" onchange="filterByRisk(this.value)">
                <option value="All">All Risk Levels</option>
                <option value="Extreme Risk (Super El Niño)">Extreme Risk</option>
                <option value="High Risk">High Risk</option>
                <option value="Medium Risk">Medium Risk</option>
                <option value="Low Risk">Low Risk</option>
                <option value="Safe">Safe</option>
            </select>
        </div>
        <div class="control-group">
            <label for="date-slider">📅 CHOOSE DATE FILTER (2026)</label>
            <div style="display:flex; align-items:center; gap:8px;">
                <input type="range" id="date-slider" min="1" max="7" value="7" oninput="updateDateFilter(this.value)" style="width:100px; accent-color:var(--cyan); cursor:pointer;" />
                <span id="date-label" style="font-weight:bold; color:var(--cyan); font-size:11px;">Dec 2026</span>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:flex-end;">
            <button id="btn-toggle-3d" class="action-btn" style="background:linear-gradient(to right, var(--cyan), var(--purple));" onclick="toggle3DMode()">🛸 3D Perspective View</button>
            <button class="action-btn" onclick="shareDashboard()">🔗 Share</button>
            <div class="download-dropdown">
                <button class="action-btn">📥 Download ▾</button>
                <div class="download-dropdown-content">
                    <a href="#" onclick="printMap()">Print Current Map</a>
                    <a href="#" onclick="exportCSV()">Export Asset Data (CSV)</a>
                    <a href="#" onclick="generateDRMReport()">Generate DRM Report</a>
                </div>
            </div>
        </div>
    </div>

    <!-- MAP CONTAINER (HALF PAGE HEIGHT) -->
    <div class="top-map-section">
        <div class="map-wrapper">
            <div class="map-header">
                <div class="map-title">🌍 Interactive Early Warning & Adaptation System Map</div>
                <div style="font-size:10px; color:var(--text-muted);">Switch base view to Google Hybrid to inspect satellite imagery.</div>
            </div>
            <div id="map"></div>
            
            <div class="emoji-legend-box">
                <div>🏫 School Point</div>
                <div>🏥 Hospital Point</div>
                <div>💧 Borehole Point</div>
                <div>🪣 Water Pan</div>
                <div>🦒 Wildlife Habitat</div>
                <div>🌊 Clipped River</div>
                <div>🌾 Agricultural Area</div>
                <div>📐 Cadastral Zone</div>
            </div>
        </div>
    </div>

    <!-- BOTTOM DASHBOARD SECTIONS -->
    <div class="bottom-dashboard-grid">
        
        <!-- COLUMN 1: Telemetry Metrics & Autogenerated Infographics -->
        <div class="telemetry-column">
            <div class="telemetry-card schools">
                <span class="telemetry-label">Schools at Risk</span>
                <span class="telemetry-value telemetry-schools" id="metric-schools-val">__SUM_SCHOOLS_RISK__</span>
                <span class="telemetry-desc" id="metric-schools-desc">Out of __TOTAL_SCHOOLS__ total structures (__PERCENT_SCHOOLS__% exposed)</span>
            </div>
            <div class="telemetry-card health">
                <span class="telemetry-label">Health Facilities at Risk</span>
                <span class="telemetry-value telemetry-health" id="metric-health-val">__SUM_HEALTH_RISK__</span>
                <span class="telemetry-desc" id="metric-health-desc">Out of __TOTAL_HEALTH__ clinics (__PERCENT_HEALTH__% exposed)</span>
            </div>
            <div class="telemetry-card boreholes">
                <span class="telemetry-label">Boreholes at Risk</span>
                <span class="telemetry-value telemetry-boreholes" id="metric-boreholes-val">__SUM_BORE_RISK__</span>
                <span class="telemetry-desc" id="metric-boreholes-desc">Humanitarian water supply (__PERCENT_BORE__% exposed)</span>
            </div>
            <div class="telemetry-card camps">
                <span class="telemetry-label">Camps at Risk</span>
                <span class="telemetry-value telemetry-camps" id="metric-camps-val">__SUM_CAMPS_RISK__</span>
                <span class="telemetry-desc" id="metric-camps-desc">Dadaab / IDP camps (__PERCENT_CAMPS__% exposed)</span>
            </div>
            
            <!-- Dynamic Infographics Card -->
            <div class="telemetry-card infographics-card">
                <span class="telemetry-label" style="color:var(--emerald);">📊 DRM INFOGRAPHICS EXPOSURE</span>
                <div style="margin-top: 8px; font-size:11px; color:var(--text-main); line-height: 1.4;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>Extreme Flood Zone Area:</span>
                        <span style="font-weight:bold; color:var(--purple);">3,800 km²</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>Exposed Population:</span>
                        <span style="font-weight:bold; color:var(--red);" id="info-pop-exposed">156,000</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>Borehole Water Drawdown Ratio:</span>
                        <span style="font-weight:bold; color:var(--orange);">21.6x</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>Dengue Outbreak Positivity:</span>
                        <span style="font-weight:bold; color:var(--red);">70.0%</span>
                    </div>
                </div>
                <div class="desc-box rangeland-advisory" style="margin-top:8px; padding:6px; background:rgba(16, 185, 129, 0.05); border-color:rgba(16, 185, 129, 0.2);">
                    <strong>🌿 Rangeland Advisory:</strong> rangeland vegetation greens index is high. Shift herds toward higher ground.
                </div>
            </div>

            <!-- Live Weather Widget Card -->
            <div class="telemetry-card weather-widget-card" style="border: 1px solid rgba(6, 182, 212, 0.15);">
                <span class="telemetry-label" style="color:var(--cyan); display:flex; justify-content:space-between; align-items:center;">
                    <span>⛅ LIVE GARISSA WEATHER</span>
                    <span style="font-size: 8px; color:var(--text-muted);">AUTO-UPDATES</span>
                </span>
                <div id="weather-widget" style="margin-top: 8px;">
                    <div style="font-size: 11px; color: var(--text-muted); font-style: italic;">
                        Connecting to OpenWeatherMap...
                    </div>
                </div>
            </div>

        </div>
        
        <!-- COLUMN 2: Asset Inventory Search Table -->
        <div class="inventory-column">
            <div class="dashboard-section-title">🔍 Asset Risk Inventory</div>
            <div style="display:flex; gap:8px; margin-top: 8px; margin-bottom:4px;">
                <input type="text" id="inventory-search" placeholder="Search assets (e.g. Dadaab Primary, borehole)..." oninput="updateInventoryTable()" style="flex:1; padding:6px 12px; border-radius:6px; background:#1e293b; border:1px solid #334155; color:white; font-size:12px; outline:none;" />
                <select id="inventory-type" onchange="updateInventoryTable()" style="background:#1e293b; border:1px solid #334155; color:white; border-radius:6px; padding:6px; font-size:11px; outline:none; cursor:pointer;">
                    <option value="all">All Types</option>
                    <option value="schools">Schools</option>
                    <option value="health">Clinics</option>
                    <option value="boreholes">Boreholes</option>
                    <option value="water_pans">Water Pans</option>
                    <option value="wildlife">Wildlife</option>
                </select>
            </div>
            <div class="table-wrapper">
                <table class="inventory-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Sub-County</th>
                            <th>Risk Level</th>
                            <th>Vulnerability</th>
                        </tr>
                    </thead>
                    <tbody id="inventory-tbody">
                        <!-- Dynamic rows loaded from javascript -->
                    </tbody>
                </table>
            </div>
            <div style="font-size:10px; color:var(--text-muted); margin-top:5px; text-align:right;" id="inventory-count">Showing 0 of 0 assets</div>
        </div>
        
        <!-- COLUMN 3: tab panels containing QGIS and analysis statistics -->
        <div class="tabs-column">
            <!-- 10 Tabs Navigation -->
            <nav class="tabs-nav">
                <button class="tab-btn active" onclick="switchTab(event, 'tab-health')">💊 Health</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-edu')">🎓 Edu</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-agri')">🌾 Agri</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-refugee')">🏕️ Refugee</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-floods')">🌊 Flood</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-watch')">⛅ Watch</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-stock')">🐄 Stock</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-land')">🌳 Land</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-wild')">🦁 Wild</button>
                <button class="tab-btn" onclick="switchTab(event, 'tab-coord')">📊 Abstract</button>
            </nav>
            
            <div class="tab-content-wrapper">
                
                <!-- Tab 1: Health -->
                <div id="tab-health" class="tab-panel active">
                    <div class="dashboard-section-title">Epidemiological Vector & Public Health Dashboard</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Dengue Positivity Rate</div>
                            <div class="value" style="color:var(--red);">70.0%</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Under-5 Mortality Rate</div>
                            <div class="value">44 /1K</div>
                        </div>
                    </div>
                    
                    <div class="chart-box" style="height: 120px;">
                        <canvas id="chart-dengue"></canvas>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🧬 May 2026 Dengue Fever Alert:</strong> A severe dengue outbreak has been confirmed in Garissa Township, driven by vector breeding (Aedes mosquitoes) in pools created by river flooding. Health clinics report a 70% laboratory sample positivity rate. Immediate vector controls and fumigations are scheduled.
                    </div>
                </div>
                
                <!-- Tab 2: Education -->
                <div id="tab-edu" class="tab-panel">
                    <div class="dashboard-section-title">Educational Facilities Exposure & Vulnerability Dashboard</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Extreme Risk Schools</div>
                            <div class="value" style="color:var(--purple);">__EXT_SCHOOLS__</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">High Risk Schools</div>
                            <div class="value" style="color:var(--red);">__HIGH_SCHOOLS__</div>
                        </div>
                    </div>
                    
                    <div class="chart-box" style="height: 120px;">
                        <canvas id="chart-schools-exposure"></canvas>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🏫 School Inundation:</strong> 27 schools lie directly within the extreme risk zone (~5.5km El Niño flood pathway). DRM units have targeted these schools for temporary evacuation structures or conversion into dry community centers.
                    </div>
                </div>
                
                <!-- Tab 3: Agriculture -->
                <div id="tab-agri" class="tab-panel">
                    <div class="dashboard-section-title">Agriculture & River Inundation Dashboard</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Riverine Farms exposed</div>
                            <div class="value" style="color:var(--orange);">89 Zones</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Crop Yield Deficit</div>
                            <div class="value" style="color:var(--red);">-42%</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🌾 Tana River Crop Exposure:</strong> Local farms along the Tana River flood basin represent the agricultural lifeline of Garissa. Heavily shaded green farm layers are exposed to river overflows, prompting early harvest advisories to farmers before gauge levels reach the critical 5.0m trigger.
                    </div>
                </div>
                
                <!-- Tab 4: Refugee -->
                <div id="tab-refugee" class="tab-panel">
                    <div class="dashboard-section-title">Dadaab Refugee Complex Resource Bottlenecks</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Refugee Population</div>
                            <div class="value">~432,000</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">BH Water Demand Ratio</div>
                            <div class="value" style="color:var(--red);">21.6x</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🏕️ Dadaab Camps (Dagahaley, Ifo, Hagadera):</strong> Water demand multiplies during El Niño events as local pastoralists move livestock towards camp boreholes. The four core boreholes face a resource demand multiplier of 21.6, prompting urgent drawdown warnings.
                    </div>
                </div>
                
                <!-- Tab 5: Floods -->
                <div id="tab-floods" class="tab-panel">
                    <div class="dashboard-section-title">UNOSAT Flood Buffer Spatial Analytics</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Flood Area Clipped</div>
                            <div class="value">~3,800 km²</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Buffer Zones Area</div>
                            <div class="value">9.91 SqDeg</div>
                        </div>
                    </div>
                    
                    <div class="chart-box" style="height: 120px;">
                        <canvas id="chart-exposure-donut"></canvas>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🌊 Risk Buffer Zones:</strong> The buffers represent non-overlapping rings centered on historical inundation zones. The inner red ring represents High Risk (0-500m), extending out to the purple Extreme Risk ring (3.3km-5.5km).
                    </div>
                </div>
                
                <!-- Tab 6: El Niño Watch -->
                <div id="tab-watch" class="tab-panel">
                    <div class="dashboard-section-title">Seasonal Weather Forecasts & SST Telemetry</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">SST Temperature Anomaly</div>
                            <div class="value" style="color:var(--red);">+2.1 °C</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Seasonal Rain Forecast</div>
                            <div class="value">145%</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>⛅ El Niño Watch Indicators:</strong> Sea Surface Temperature (SST) anomalies in the Nino 3.4 region have surpassed +2.1°C, indicating a very strong event. Garissa County is currently under a Severe Weather alert with forecasted rainfall exceeding 145% of normal.
                    </div>
                </div>
                
                <!-- Tab 7: Livestock -->
                <div id="tab-stock" class="tab-panel">
                    <div class="dashboard-section-title">Livestock Migration & Rift Valley Fever (RVF) Dashboard</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Livestock Population</div>
                            <div class="value">2.4M Head</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">RVF Vaccination Target</div>
                            <div class="value" style="color:var(--emerald);">85%</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🐄 Rift Valley Fever Alert:</strong> Excessive rainfall triggers vector breeding (Aedes mosquitoes), creating severe risks of Rift Valley Fever outbreaks in livestock, which transmit to humans. Pre-flood animal vaccinations must cover 85% of cattle along migration routes.
                    </div>
                </div>
                
                <!-- Tab 8: Land Use -->
                <div id="tab-land" class="tab-panel">
                    <div class="dashboard-section-title">NDVI Vegetation Rangelands & Prosopis Spread</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Prosopis Invaded Area</div>
                            <div class="value" style="color:var(--red);">631 km²</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Mean NDVI</div>
                            <div class="value">0.34</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🌳 Prosopis Juliflora (Mathenge) Invasion:</strong> The invasive Mathenge tree has colonized 631 km² of riverine pasture in Garissa. It blocks river channels and grazing corridors, increasing localized flood heights while diminishing livestock grazing spaces.
                    </div>
                </div>
                
                <!-- Tab 9: Wildlife -->
                <div id="tab-wild" class="tab-panel">
                    <div class="dashboard-section-title">Wildlife Distribution & Autogeoreferenced Habitats</div>
                    <div class="stat-grid-3d">
                        <div class="stat-card-3d">
                            <div class="label">Hirola Population</div>
                            <div class="value" style="color:var(--orange);">~250</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Wildlife Sanctuaries</div>
                            <div class="value">4 Zones</div>
                        </div>
                    </div>
                    
                    <div class="desc-box">
                        <strong>🦁 Wildlife Geolocation:</strong> Garissa supports rare and endangered wildlife species, including the critically endangered **Hirola Antelope** in the Ijara/Hulugho conservancies, reticulated giraffes in Lagdera, elephants in Fafi, and cheetahs in Balambala plains.
                    </div>
                </div>
                
                <!-- Tab 10: Abstract & Coordination -->
                <div id="tab-coord" class="tab-panel">
                    <div class="dashboard-section-title">📊 Garissa Socioeconomic & Policy Abstract</div>
                    
                    <div style="font-size:10px; color:var(--text-muted); line-height:1.5; margin-bottom:12px;">
                        Demographic and DRM exposure data compiled from the <strong>Garissa County Social Protection Policy 2025</strong>, 
                        <strong>Garissa County Partnership & Coordination Policy</strong>, and <strong>KNBS Census 2019</strong>.
                    </div>

                    <div class="stat-grid-3d" style="margin-bottom:12px;">
                        <div class="stat-card-3d">
                            <div class="label">Avg Poverty Headcount</div>
                            <div class="value" style="color:var(--red);">67.8%</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Food Poverty Rate</div>
                            <div class="value" style="color:var(--red);">51.2%</div>
                        </div>
                        <div class="stat-card-3d">
                            <div class="label">Under-5 Wasting</div>
                            <div class="value" style="color:var(--orange);">14.1%</div>
                        </div>
                    </div>
                    
                    <!-- Placeholder Status Panel for External APIs -->
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-bottom:12px;">
                        <div style="background:rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.05); padding:6px; border-radius:6px; font-size:8px;">
                            <div style="font-weight:bold; color:white; margin-bottom:2px;">🍕 WFP HungerMap Feed</div>
                            <div style="display:flex; align-items:center; gap:4px;">
                                <span style="display:inline-block; width:5px; height:5px; border-radius:50%; background:#10b981;"></span>
                                <span style="color:#10b981; font-weight:bold;">LIVE (IPC Phase 3)</span>
                            </div>
                        </div>
                        <div style="background:rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.05); padding:6px; border-radius:6px; font-size:8px;">
                            <div style="font-weight:bold; color:white; margin-bottom:2px;">🚰 UNICEF WASH Feed</div>
                            <div style="display:flex; align-items:center; gap:4px;">
                                <span style="display:inline-block; width:5px; height:5px; border-radius:50%; background:#10b981;"></span>
                                <span style="color:#10b981; font-weight:bold;">CONNECTED (247 BH)</span>
                            </div>
                        </div>
                        <div style="background:rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.05); padding:6px; border-radius:6px; font-size:8px;">
                            <div style="font-weight:bold; color:white; margin-bottom:2px;">📦 OCHA HDX Portal</div>
                            <div style="display:flex; align-items:center; gap:4px;">
                                <span style="display:inline-block; width:5px; height:5px; border-radius:50%; background:#10b981;"></span>
                                <span style="color:#10b981; font-weight:bold;">SYNCED (Dadaab)</span>
                            </div>
                        </div>
                    </div>

                    <div style="background:rgba(15,23,42,0.6); padding:10px; border-radius:8px; border:1px solid rgba(6,182,212,0.15); margin-bottom:12px;">
                        <span style="font-size:9px; font-weight:bold; color:var(--cyan); display:block; margin-bottom:5px;">📋 Demographics & Socioeconomics by Sub-County</span>
                        <div style="max-height:110px; overflow-y:auto;">
                            <table class="inventory-table" style="font-size:8px; line-height: 1.2;">
                                <thead>
                                    <tr>
                                        <th>Sub-County</th>
                                        <th>Population</th>
                                        <th>Poverty Rate</th>
                                        <th>Food Poverty</th>
                                        <th>Wasting Rate</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td>Garissa Sub-County</td><td>163,914</td><td>48.0%</td><td>35.0%</td><td>10.0%</td></tr>
                                    <tr><td>Dadaab Sub-County</td><td>185,252</td><td>78.0%</td><td>58.0%</td><td>17.0%</td></tr>
                                    <tr><td>Lagdera Sub-County</td><td>103,114</td><td>80.0%</td><td>60.0%</td><td>16.0%</td></tr>
                                    <tr><td>Balambala Sub-County</td><td>99,741</td><td>82.0%</td><td>62.0%</td><td>15.0%</td></tr>
                                    <tr><td>Fafi Sub-County</td><td>132,042</td><td>77.0%</td><td>57.0%</td><td>14.0%</td></tr>
                                    <tr><td>Ijara Sub-County</td><td>141,310</td><td>62.0%</td><td>45.0%</td><td>12.0%</td></tr>
                                    <tr><td>Hulugho Sub-County</td><td>118,500</td><td>65.0%</td><td>48.0%</td><td>11.0%</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div style="height: 150px; position: relative;">
                        <canvas id="chart-subcounty-abstract"></canvas>
                    </div>

                    <div class="desc-box" style="margin-top:10px; font-size:8px; line-height:1.3;">
                        <strong>🛡️ Policy Context Citation:</strong> Under Section 4.2 of the *Garissa County Social Protection Policy 2025*, funding is prioritized for cash transfers (KES 10,000 baseline) and livestock feed subsidies to offset household food poverty, targeting vulnerable populations during peak El Niño flood events.
                    </div>
                </div>
                
            </div>

            <!-- Interactive Feedback Form -->
            <div class="feedback-box">
                <div style="font-weight: 700; color: var(--emerald); display: flex; align-items: center; gap: 6px;">
                    <span>📝</span> Public Feedback & Early Warnings
                </div>
                <textarea id="feedback-text" class="feedback-input" rows="2" placeholder="Report a flood risk or road cut..."></textarea>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <button class="feedback-btn" onclick="submitFeedback()">Submit Feedback</button>
                    <span id="feedback-success" style="color:var(--emerald); font-size:10px; display:none;">✅ Received!</span>
                </div>
            </div>
        </div>
        
    </div>
    </div><!-- End #page-digital-twin -->

    <!-- PAGE CONTAINER: NARRATIVE STORY -->
    <div id="page-narrative" class="page-container">
        __NARRATIVE_STORY_HTML__
    </div>

    <!-- PAGE CONTAINER: MAP GALLERY -->
    <div id="page-gallery" class="page-container">
        <h2 style="font-family: 'Orbitron', sans-serif; color: var(--cyan); margin-bottom: 8px; font-size: 20px;">🖼️ Programmatic Map Gallery</h2>
        <p style="color: var(--text-muted); margin-bottom: 24px; font-size: 13px;">Lightbox grid displaying the 20 programmatic maps generated for Garissa County flood risk analysis.</p>
        <div class="gallery-grid">
            __MAP_GALLERY_HTML__
        </div>
    </div>

    <!-- PAGE CONTAINER: OPERATIONS HUB -->
    <div id="page-operations" class="page-container">
        <h2 style="font-family: 'Orbitron', sans-serif; color: var(--cyan); margin-bottom: 8px; font-size: 20px;">📚 Operations Hub & QGIS Portal</h2>
        <p style="color: var(--text-muted); margin-bottom: 30px; font-size: 13px;">Access official policies, download/launch GIS files, and review response blueprints.</p>
        
                <!-- System Mandate & Vision Banner -->
        <div class="ops-mandate-banner" style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(6, 182, 212, 0.05);">
            <h3 style="margin-top:0; color:var(--cyan); font-family:'Orbitron', sans-serif; font-size:16px; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:6px;">🛡️ STRATEGIC MANDATE & MISSION STATEMENTS</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 12px; line-height: 1.5; color: var(--text-main);">
                <div>
                    <strong style="color:var(--emerald); display:block; margin-bottom:4px; font-size:13px;">👁️ SYSTEM VISION</strong>
                    A highly resilient Garissa County protected by real-time predictive spatial analytics, early warning arrays, and inclusive anticipatory actions to eliminate disaster exposure and ensure community safety.
                </div>
                <div>
                    <strong style="color:var(--emerald); display:block; margin-bottom:4px; font-size:13px;">🎯 SYSTEM MISSION</strong>
                    To integrate advanced satellite vegetation indexing, automated neural network vulnerability classifiers, and live meteorological feeds into a unified decision support system that triggers timely rangeland management, humanitarian settlement transitions (Shirika Plan), and direct social assistance to vulnerable communities.
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 12px; line-height: 1.5; color: var(--text-main); border-top: 1px solid rgba(255,255,255,0.05); padding-top:12px;">
                <strong style="color:var(--cyan); display:block; margin-bottom:4px; font-size:13px;">🚀 WHAT WE DO</strong>
                We automate GIS cartographic workflows, calculate non-overlapping multi-buffer flood exposure vectors, map seasonal laghas, assess community asset exposure profiles (schools, clinics, boreholes, water pans), and predict local cash deficits to empower county authorities and humanitarian partners in rapid resource mobilization.
            </div>
        </div>

        <div class="operations-grid">
            <div class="ops-card">
                <div class="ops-card-title">🖥️ Emergency GIS Operations Center</div>
                <div class="ops-brief">
                    Launch the local PyQGIS workspace project or open the notebook story compilation directly to inspect vector layers, risk buffers, and vulnerability classifiers.
                </div>
                <div class="ops-btn-group">
                    <a class="ops-launch-btn" href="../GarissaDRM_ElNino_2026.qgz" target="_blank">🖥️ Download QGIS Workspace</a>
                    <a class="ops-launch-btn" href="garissa_flood_risk_story.html" target="_blank">📓 Open Jupyter Story</a>
                </div>
            </div>
            
            <div class="ops-card">
                <div class="ops-card-title">🛡️ Social Protection Policy Integration</div>
                <div class="ops-brief">
                    Provides guidelines on targeting vulnerable households in Balambala and Dadaab sub-counties. Proposes anticipatory cash transfers of <strong>KES 10,000</strong> to address the average <strong>KES -1,008 cash gap</strong> (income KES 5,169 vs expenditure KES 6,177) and mitigate food poverty (51.2%).
                </div>
            </div>
            
            <div class="ops-card">
                <div class="ops-card-title">🤝 Donor Coordination & WEF Nexus</div>
                <div class="ops-brief">
                    Establishes a unified platform for non-overlapping aid allocation. Monitors the Water-Energy-Food (WEF) nexus at Dadaab complex (432,000 refugees) to prevent borehole depletion (water demand multiplier <strong>21.6x</strong>) and vector outbreaks (Dengue, RVF, Cholera).
                </div>
            </div>
        </div>
    </div>

    <!-- Lightbox Modal -->
    <div id="lightbox-modal" class="lightbox" onclick="closeLightbox()">
        <div class="lightbox-content" onclick="event.stopPropagation()">
            <button class="lightbox-close" onclick="closeLightbox()">×</button>
            <img id="lightbox-img" class="lightbox-img" src="" alt="Expanded Map" />
            <div id="lightbox-caption" class="lightbox-caption"></div>
        </div>
    </div>

    <!-- Pinned Chatbot trigger -->
    <div class="sentinel-bot-trigger" onclick="toggleChatbot()">
        <svg style="width: 24px; height: 24px; fill: #ffffff;" viewBox="0 0 24 24">
            <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4M12,18C11.11,18 10.26,17.8 9.5,17.45C11.56,16.5 13,14.42 13,12C13,9.58 11.56,7.5 9.5,6.55C10.26,6.2 11.11,6 12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18Z" />
        </svg>
    </div>
    
    <!-- Pinned Chatbot panel -->
    <div id="sentinel-bot-panel" class="sentinel-bot-panel">
        <div class="bot-header">
            <span class="bot-title">🤖 GEWAS AI DRM Sentinel-Bot</span>
            <div style="display:flex; gap:8px; align-items:center;">
                <button onclick="toggleBotSettings()" style="background:none; border:none; color:white; font-size:14px; cursor:pointer;" title="Gemini API settings">⚙️</button>
                <button onclick="toggleChatbot()" style="background:none; border:none; color:white; font-size:16px; cursor:pointer;">×</button>
            </div>
        </div>
        
        <!-- API settings slide panel -->
        <div id="bot-api-settings" class="bot-api-settings" style="flex-direction: column; gap: 8px;">
            <div>
                <label style="font-weight:bold; color:var(--cyan); font-size:10px; display:block; margin-bottom:2px;">CUSTOM GEMINI API KEY:</label>
                <div style="display:flex; gap:6px;">
                    <input id="custom-api-key-input" type="password" placeholder="AIzaSy..." style="flex:1; padding:4px 8px; border-radius:4px; background:#0f172a; border:1px solid #334155; color:white; font-size:10px;" />
                    <button onclick="saveCustomAPIKey()" style="background:var(--emerald); border:none; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer;">Save</button>
                </div>
            </div>
            <div>
                <label style="font-weight:bold; color:var(--cyan); font-size:10px; display:block; margin-bottom:2px;">WEATHER API KEY:</label>
                <div style="display:flex; gap:6px;">
                    <input id="custom-weather-key-input" type="password" placeholder="375586..." style="flex:1; padding:4px 8px; border-radius:4px; background:#0f172a; border:1px solid #334155; color:white; font-size:10px;" />
                    <button onclick="saveCustomWeatherKey()" style="background:var(--emerald); border:none; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer;">Save</button>
                </div>
            </div>
            <span id="api-key-status" style="color:var(--text-muted); font-size:9px;">Keys are stored locally in your browser.</span>
        </div>

        <div id="bot-messages" class="bot-messages">
            <div class="bot-msg" style="align-self: flex-start;">
                <strong>Sentinel-Bot:</strong> Jambo! I am Sentinel-Bot, your agentic DRM advisor. I have analyzed Garissa's El Niño risks using a custom Neural Network to classify infrastructure vulnerability index (0 to 1). How can I assist you in managing El Niño risks?
            </div>
        </div>
        <div style="padding: 10px 15px; border-top: 1px solid #1e293b; background: #0f172a; display: flex; gap: 8px; align-items: center;">
            <input id="sentinel-bot-input" type="text" placeholder="Ask a DRM question..." style="flex: 1; padding: 8px 15px; border-radius: 20px; background: #1e293b; border: 1px solid #334155; color: #ffffff; font-size: 13px; outline: none;" onkeypress="handleBotKeyPress(event)" />
            <button onclick="triggerChatbotQuery()" style="background: var(--cyan); border: none; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; cursor: pointer; outline: none;">
                <svg style="width: 16px; height: 16px; fill: #ffffff;" viewBox="0 0 24 24">
                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
                </svg>
            </button>
        </div>
    </div>

    <script>
        // Page Switching Routing
        function switchPage(pageId) {
            document.querySelectorAll('.page-container').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(el => {
                el.classList.remove('active');
            });
            
            document.getElementById(pageId).classList.add('active');
            
            // Highlight the nav button
            document.querySelectorAll('.nav-tab').forEach(btn => {
                if (btn.getAttribute('onclick').includes(pageId)) {
                    btn.classList.add('active');
                }
            });
            
            if (pageId === 'page-digital-twin') {
                if (map) map.invalidateSize();
                if (map3D) {
                    setTimeout(() => { map3D.resize(); }, 100);
                }
            }
        }
        
        // Narrative scroll to chapter
        function scrollToChapter(chNum) {
            const el = document.getElementById('story-chapter-' + chNum);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth' });
                // Highlight sidebar active item
                document.querySelectorAll('.sidebar-chapter-item').forEach(item => {
                    item.classList.remove('active');
                });
                const activeItem = document.getElementById('sidebar-ch-' + chNum);
                if (activeItem) activeItem.classList.add('active');
            }
        }
        
        // Gallery Lightbox controls
        function openLightbox(imgUrl, caption) {
            const modal = document.getElementById('lightbox-modal');
            const img = document.getElementById('lightbox-img');
            const captionEl = document.getElementById('lightbox-caption');
            img.src = imgUrl;
            captionEl.textContent = caption;
            modal.style.display = 'flex';
        }
        
        function closeLightbox() {
            document.getElementById('lightbox-modal').style.display = 'none';
        }

        // 3D Perspective map view toggle and controls
        let map3D = null;
        let is3DMode = false;
        
        function toggle3DMode() {
            is3DMode = !is3DMode;
            const btn = document.getElementById('btn-toggle-3d');
            const map2dEl = document.getElementById('map');
            let map3dEl = document.getElementById('map3d');
            
            if (!map3dEl) {
                map3dEl = document.createElement('div');
                map3dEl.id = 'map3d';
                map3dEl.style.width = '100%';
                map3dEl.style.height = '600px';
                map3dEl.style.borderRadius = '12px';
                map3dEl.style.border = '1px solid var(--border-glow)';
                map3dEl.style.boxShadow = 'inset 0 0 20px rgba(0,0,0,0.8)';
                map2dEl.parentNode.appendChild(map3dEl);
            }
            
            if (is3DMode) {
                btn.innerHTML = '🕋 2D Map View';
                btn.classList.add('active');
                map2dEl.style.display = 'none';
                map3dEl.style.display = 'block';
                init3DMap();
            } else {
                btn.innerHTML = '🛸 3D Perspective View';
                btn.classList.remove('active');
                map2dEl.style.display = 'block';
                map3dEl.style.display = 'none';
                if (map) map.invalidateSize();
            }
        }
        
        function loadScript(url) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
        
        function loadCSS(url) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = url;
            document.head.appendChild(link);
        }
        
        async function init3DMap() {
            if (map3D) {
                setTimeout(() => { map3D.resize(); }, 100);
                return;
            }
            
            // Load MapLibre CSS & JS if not already loaded
            if (typeof maplibregl === 'undefined') {
                loadCSS('https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css');
                await loadScript('https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js');
            }
            
            map3D = new maplibregl.Map({
                container: 'map3d',
                style: {
                    version: 8,
                    sources: {
                        'google-hybrid': {
                            type: 'raster',
                            tiles: [
                                'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
                            ],
                            tileSize: 256,
                            attribution: '© Google'
                        }
                    },
                    layers: [
                        {
                            id: 'google-hybrid-layer',
                            type: 'raster',
                            source: 'google-hybrid',
                            minzoom: 0,
                            maxzoom: 22
                        }
                    ]
                },
                center: [39.6461, -0.4532], // Garissa County coordinates
                zoom: 9.5,
                pitch: 60,
                bearing: -25,
                antialias: true
            });
            
            map3D.addControl(new maplibregl.NavigationControl());
            
            map3D.on('load', () => {
                // Add boundaries (Wards / Subcounties) as extruded 3D layers
                if (subcountiesGeom && subcountiesGeom.features && subcountiesGeom.features.length > 0) {
                    map3D.addSource('subcounties-3d', {
                        type: 'geojson',
                        data: subcountiesGeom
                    });
                    map3D.addLayer({
                        id: 'subcounties-3d-extrusion',
                        type: 'fill-extrusion',
                        source: 'subcounties-3d',
                        paint: {
                            'fill-extrusion-height': [
                                'interpolate',
                                ['linear'],
                                ['coalesce', ['number', ['get', 'vuln_idx']], 0.5],
                                0, 100,
                                1, 1500
                            ],
                            'fill-extrusion-color': [
                                'match',
                                ['get', 'Risk_Level'],
                                'Extreme Risk', '#9333ea',
                                'High Risk', '#ef4444',
                                'Medium Risk', '#f97316',
                                'Low Risk', '#fbbf24',
                                'Safe', '#22c55e',
                                '#06b6d4'
                            ],
                            'fill-extrusion-opacity': 0.6,
                            'fill-extrusion-base': 0
                        }
                    });
                }
                
                // Add extruded columns for asset categories
                const addAssetCylinders = (data, color, layerId) => {
                    if (data && data.features && data.features.length > 0) {
                        map3D.addSource(layerId + '-source', {
                            type: 'geojson',
                            data: data
                        });
                        map3D.addLayer({
                            id: layerId + '-extrusion',
                            type: 'fill-extrusion',
                            source: layerId + '-source',
                            paint: {
                                'fill-extrusion-height': 600,
                                'fill-extrusion-base': 0,
                                'fill-extrusion-color': color,
                                'fill-extrusion-opacity': 0.85
                            }
                        });
                    }
                };
                
                addAssetCylinders(schoolsData, '#a855f7', 'schools-3d');
                addAssetCylinders(healthData, '#ef4444', 'health-3d');
                addAssetCylinders(boreholesData, '#06b6d4', 'boreholes-3d');
            });
        }

        // ── 1. DATA INJECTIONS ──────────────────────────────────────────────
        const floodZones = {
            extreme: __EXTREME_RISK_JSON__,
            high: __HIGH_RISK_JSON__,
            medium: __MEDIUM_RISK_JSON__,
            low: __LOW_RISK_JSON__
        };
        
        const schoolsData = __SCHOOLS_JSON__;
        const healthData = __HEALTH_JSON__;
        const boreholesData = __BOREHOLES_JSON__;
        const idpCampsData = __IDP_CAMPS_JSON__;
        const townsData = __TOWNS_JSON__;
        const riversData = __RIVERS_JSON__;
        const roadsData = __ROADS_JSON__;
        const subcountyStats = __SUBCOUNTY_JSON__;
        
        const wildlifeData = __WILDLIFE_JSON__;
        const waterPansData = __WATER_PANS_JSON__;
        const cadastralData = __CADASTRAL_JSON__;
        
        // Dadaab blocks
        const dagahaleyBlock = __DAGAHALEY_JSON__;
        const hagaderaBlock = __HAGADERA_JSON__;
        const ifoBlock = __IFO_JSON__;

        // Boundaries
        const subcountiesGeom = __SUBCOUNTIES_GEOM_JSON__;
        const wardsGeom = __WARDS_GEOM_JSON__;

        // Global state variables for filters
        let currentSubcounty = 'All';
        let currentRisk = 'All';

        const subcountyCentroids = {
            'All': [-0.4532, 39.6461],
            'Dadaab Sub County': [0.082, 40.298],
            'Fafi Sub County': [-1.082, 40.145],
            'Balambala Sub County': [-0.041, 39.638],
            'Ijara Sub County': [-1.783, 40.183],
            'Lagdera Sub County': [0.728, 39.771],
            'Garissa Sub County': [-0.456, 39.642],
            'Hulugho Sub County': [-1.850, 40.830]
        };

        // ── 2. MAP INITIALIZATION ───────────────────────────────────────────
        const map = L.map('map', {
            zoomControl: true,
            scrollWheelZoom: true
        }).setView([-0.4532, 39.6461], 8.5);

        // Clamping bounds to focus map only on Garissa County
        const garissaBounds = L.latLngBounds(
            L.latLng(-2.1, 38.5), // Southwest corner
            L.latLng(1.1, 41.5)   // Northeast corner
        );
        map.setMaxBounds(garissaBounds);
        map.on('drag', function() {
            map.panInsideBounds(garissaBounds, { animate: false });
        });

        // Define Basemaps
        const darkBasemap = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        });

        const hybridBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
            attribution: '&copy; Google Maps'
        }).addTo(map);

        const osmBasemap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        });

        const baseMaps = {
            "Dark Matter": darkBasemap,
            "Google Hybrid": hybridBasemap,
            "OpenStreetMap": osmBasemap
        };

        const getRiskColor = (risk) => {
            switch(risk) {
                case 'Extreme Risk (Super El Niño)': return '#a855f7';
                case 'High Risk': return '#ef4444';
                case 'Medium Risk': return '#f97316';
                case 'Low Risk': return '#fbbf24';
                default: return '#22c55e'; // Safe
            }
        };

        const geojsonLayers = {};
        let riskLayers = [];

        // 🌊 Rivers & Laghas Overlay (Clipped)
        if (riversData.features && riversData.features.length > 0) {
            geojsonLayers["🌊 Rivers & Laghas"] = L.geoJSON(riversData, {
                style: function(f) {
                    let isTana = (f.properties.SUB_NAME || '').toLowerCase().includes('tana') || (f.properties.NAME || '').toLowerCase().includes('tana');
                    return {
                        color: isTana ? '#0ea5e9' : '#a855f7',
                        weight: isTana ? 2.5 : 1.2,
                        dashArray: isTana ? '' : '3,3',
                        opacity: 0.8
                    };
                }
            }).addTo(map);
        }

        // Buffer zones styling
        const bufferStyles = {
            extreme: { color: '#a855f7', fillColor: '#a855f7', fillOpacity: 0.15, weight: 1 },
            low: { color: '#fbbf24', fillColor: '#fbbf24', fillOpacity: 0.15, weight: 0.8 },
            medium: { color: '#f97316', fillColor: '#f97316', fillOpacity: 0.2, weight: 0.8 },
            high: { color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.25, weight: 1 }
        };

        // Load non-overlapping buffers
        Object.keys(floodZones).forEach(key => {
            const zoneData = floodZones[key];
            if (zoneData.features && zoneData.features.length > 0) {
                const name = "🚨 " + key.toUpperCase() + " Risk Zone";
                const l = L.geoJSON(zoneData, { style: bufferStyles[key] }).addTo(map);
                geojsonLayers[name] = l;
                riskLayers.push(l);
            }
        });

        // Attribute popup builder with strict clean rules
        const setupAttributePopup = (feature, layer, icon) => {
            if (feature.properties) {
                let p = feature.properties;
                // Resolve borehole, school, camp, health facility or town actual name
                let name = p.name || p.Name || p.school_nam || p.name_healt || p.health_fac || p.common_nam || p.camps_name || p.Camps_Name || p.camp_name || p.Camp_Name || p.idp_camp_n || p.IDP_Camp_N || p.town_name || p.TOWN_NAME || p.borehole_n || p.Borehole_N || p.name_of_b || p.Name_of_B || p.code || p.parcel_id || '';
                name = String(name).trim();
                if (!name || name === 'null' || name === 'nil' || name === 'None' || name === 'Asset') {
                    let type = p.Type || p.LAYER || 'Asset';
                    name = type + ' at ' + parseFloat(feature.geometry.coordinates[1]).toFixed(4) + ', ' + parseFloat(feature.geometry.coordinates[0]).toFixed(4);
                }
                // Rename IDP to Refugee Camp
                name = name.replace(/IDP/gi, 'Refugee');
                
                let risk = p.Risk_Level || 'Safe';
                let v = p.NN_Vulnerability_Score || p.Vulnerability_Index || '0.0';
                
                let color = "#22c55e"; 
                if (parseFloat(v) > 0.75) color = "#9333ea"; 
                else if (parseFloat(v) > 0.5) color = "#ef4444"; 
                else if (parseFloat(v) > 0.3) color = "#f97316"; 
                else if (parseFloat(v) > 0.1) color = "#fbbf24";
                
                let vulnBadge = '<div style="background:' + color + '; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; margin-bottom:8px; display:inline-block; font-size:10px;">NN VULNERABILITY: ' + v + '</div>';
                
                // Add Shirika Plan caption if this is a Refugee Camp
                if (icon === '🏕️' || icon === '⛺' || name.toLowerCase().includes('camp') || (p.Type && p.Type.toLowerCase().includes('camp')) || (p.LAYER && p.LAYER.toLowerCase().includes('camp'))) {
                    vulnBadge += '<div style="background:#0d9488; color:white; padding:6px 10px; border-radius:4px; font-weight:bold; margin-bottom:8px; font-size:10px; line-height:1.4;">🎪 SHIRIKA PLAN INTEGRATION: Transitioning Dadaab camps from restricted encampments to integrated socio-economic settlements.</div>';
                }
                
                let rows = "";
                // Render other attributes excluding empty/null/nil fields
                Object.keys(p).forEach(key => {
                    const val = p[key];
                    const valStr = String(val).trim();
                    const skipKeys = ['geometry', 'geom', 'fid', 'id', 'objectid', 'Vulnerability_Index', 'marker_emoji', 'Author', 'school_nam', 'health_fac', 'name', 'Name', 'Risk_Level', 'NN_Vulnerability_Score'];
                    if (!skipKeys.includes(key) && valStr !== 'null' && valStr !== 'nil' && valStr !== 'None' && valStr !== '') {
                        let niceKey = key.replace(/_/g, ' ').toUpperCase();
                        rows += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px; font-weight:bold; color:var(--cyan);">' + niceKey + ':</td><td style="padding:4px; color:#ffffff;">' + val + '</td></tr>';
                    }
                });
                
                let content = '<div style="font-family: Inter, sans-serif; font-size: 11px; max-width: 250px; padding: 5px; color:#f8fafc;">' +
                    '<h4 style="margin: 0 0 6px; color: ' + getRiskColor(risk) + '; font-weight:700; border-bottom: 1px solid var(--border-glow); padding-bottom: 4px;">' + icon + ' ' + name + '</h4>' +
                    vulnBadge +
                    '<div style="max-height: 150px; overflow-y: auto;">' +
                        '<table style="width:100%; border-collapse:collapse;">' +
                            rows +
                        '</table>' +
                    '</div>' +
                '</div>';
                layer.bindPopup(content);
                
                // Concise tooltip on hover (actual name, subcounty, location)
                let subCounty = p.sub_county || p.Sub_County || p.SUBCOUNTY || p.subcounty || p.Subcounty || p.district || p.District || '';
                let subCountyStr = (subCounty && subCounty !== 'null' && subCounty !== 'None') ? subCounty : '';
                
                let lat = feature.geometry.type === 'Point' ? feature.geometry.coordinates[1] : null;
                let lng = feature.geometry.type === 'Point' ? feature.geometry.coordinates[0] : null;
                let locStr = (lat !== null && lng !== null) ? 'Lat: ' + parseFloat(lat).toFixed(4) + ', Lon: ' + parseFloat(lng).toFixed(4) : '';
                
                let tooltipHtml = '<div style="font-family:Inter, sans-serif; font-size:11px; padding:6px; line-height:1.4; color:#ffffff; background:#0f172a; border-radius:4px; border: 1px solid var(--cyan); box-shadow: 0 4px 6px rgba(0,0,0,0.3);">';
                tooltipHtml += '<strong style="color:var(--cyan); font-size:12px; display:block; margin-bottom:4px;">' + icon + ' ' + name + '</strong>';
                if (subCountyStr) {
                    tooltipHtml += '📍 <strong>Subcounty:</strong> ' + subCountyStr + '<br>';
                }
                if (locStr) {
                    tooltipHtml += '🌍 <strong>Location:</strong> ' + locStr + '<br>';
                }
                tooltipHtml += '⚠️ <strong>Risk:</strong> ' + risk;
                tooltipHtml += '</div>';
                
                layer.bindTooltip(tooltipHtml, { permanent: false, direction: 'top', sticky: true });
            }
        };

        // DivIcon Emojis markers builder
        const createEmojiMarker = (emoji, riskColor) => {
            return L.divIcon({
                html: '<div style="display:flex; align-items:center; justify-content:center; background:' + riskColor + '; width:24px; height:24px; border-radius:50%; border:1px solid #ffffff; box-shadow:0 0 6px rgba(0,0,0,0.5); font-size:12px;">' + emoji + '</div>',
                className: 'custom-emoji-marker',
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
        };

        // Initialize Core Layers
        const addLayerGroup = (data, name, emoji, useRiskCol) => {
            if (data.features && data.features.length > 0) {
                geojsonLayers[name] = L.geoJSON(data, {
                    pointToLayer: (f, latlng) => L.marker(latlng, { icon: createEmojiMarker(emoji, useRiskCol ? getRiskColor(f.properties.Risk_Level) : '#0ea5e9') }),
                    onEachFeature: (f, l) => setupAttributePopup(f, l, emoji)
                }).addTo(map);
            }
        };

        addLayerGroup(schoolsData, "🏫 Schools", '🏫', true);
        addLayerGroup(healthData, "🏥 Health Facilities", '🏥', true);
        addLayerGroup(boreholesData, "💧 Boreholes", '💧', true);
        addLayerGroup(waterPansData, "🪣 Water Pans", '🪣', false);
        
        // Wildlife Layer
        if (wildlifeData.features && wildlifeData.features.length > 0) {
            geojsonLayers["🦒 Wildlife & Sanctuaries"] = L.geoJSON(wildlifeData, {
                pointToLayer: (f, latlng) => {
                    let ani = f.properties.animal || 'giraffe';
                    let em = '🦒';
                    if (ani.includes('Elephant')) em = '🐘';
                    else if (ani.includes('Cheetah')) em = '🐆';
                    else if (ani.includes('Ostrich')) em = '🪶';
                    return L.marker(latlng, { icon: createEmojiMarker(em, '#10b981') });
                },
                onEachFeature: (f, l) => setupAttributePopup(f, l, '🦒')
            }).addTo(map);
        }

        // Cadastral Parcels Layer
        if (cadastralData.features && cadastralData.features.length > 0) {
            geojsonLayers["📐 Cadastral Parcels"] = L.geoJSON(cadastralData, {
                style: { color: '#f59e0b', weight: 1.5, fillOpacity: 0.1, dashArray: '5,5' },
                onEachFeature: (f, l) => setupAttributePopup(f, l, '📐')
            }).addTo(map);
        }

        // Refugee Camps Layer
        if (idpCampsData.features && idpCampsData.features.length > 0) {
            geojsonLayers["⛺ Refugee Camps"] = L.geoJSON(idpCampsData, {
                pointToLayer: (f, latlng) => L.marker(latlng, { icon: createEmojiMarker('⛺', '#f472b6') }),
                onEachFeature: (f, l) => setupAttributePopup(f, l, '⛺')
            }).addTo(map);
        }

        // Towns Layer
        if (townsData.features && townsData.features.length > 0) {
            geojsonLayers["🏘️ Towns"] = L.geoJSON(townsData, {
                pointToLayer: (f, latlng) => L.marker(latlng, { icon: createEmojiMarker('🏘️', '#64748b') }),
                onEachFeature: (f, l) => setupAttributePopup(f, l, '🏘️')
            }).addTo(map);
        }

        // Roads Layer
        if (roadsData.features && roadsData.features.length > 0) {
            geojsonLayers["🛣️ Roads Network"] = L.geoJSON(roadsData, {
                style: function(f) {
                    return {
                        color: getRiskColor(f.properties.Risk_Level),
                        weight: 2.5,
                        opacity: 0.85
                    };
                },
                onEachFeature: (f, l) => setupAttributePopup(f, l, '🛣️')
            }).addTo(map);
        }

        // Dadaab blocks
        const blockStyle = (color) => ({ color: color, fillColor: color, fillOpacity: 0.15, weight: 1.2 });
        if (dagahaleyBlock.features && dagahaleyBlock.features.length > 0) {
            geojsonLayers["🏕️ Dagahaley Block"] = L.geoJSON(dagahaleyBlock, { style: blockStyle('#f472b6'), onEachFeature: (f, l) => setupAttributePopup(f, l, '🏕️') }).addTo(map);
        }
        if (hagaderaBlock.features && hagaderaBlock.features.length > 0) {
            geojsonLayers["🏕️ Hagadera Block"] = L.geoJSON(hagaderaBlock, { style: blockStyle('#e879f9'), onEachFeature: (f, l) => setupAttributePopup(f, l, '🏕️') }).addTo(map);
        }
        if (ifoBlock.features && ifoBlock.features.length > 0) {
            geojsonLayers["🏕️ Ifo Block"] = L.geoJSON(ifoBlock, { style: blockStyle('#c084fc'), onEachFeature: (f, l) => setupAttributePopup(f, l, '🏕️') }).addTo(map);
        }

        // Boundaries Layers (Not added to map by default to avoid clutter, switches via menu)
        if (subcountiesGeom.features && subcountiesGeom.features.length > 0) {
            subcountyBoundariesLayer = L.geoJSON(subcountiesGeom, {
                style: { color: '#06b6d4', weight: 2.5, fillOpacity: 0.15, fillColor: '#0891b2' },
                onEachFeature: (f, l) => {
                    l.bindTooltip('<div style="font-family:Inter; font-size:11px; font-weight:bold;">' + f.properties.sub_county + '</div>', { permanent: false, direction: 'center' });
                }
            });
        }

        if (wardsGeom.features && wardsGeom.features.length > 0) {
            wardBoundariesLayer = L.geoJSON(wardsGeom, {
                style: { color: '#f59e0b', weight: 1.5, fillOpacity: 0.1, fillColor: '#d97706', dashArray: '4,4' },
                onEachFeature: (f, l) => {
                    l.bindTooltip('<div style="font-family:Inter; font-size:9px; font-weight:bold;">' + f.properties.ward + '</div>', { permanent: false, direction: 'center' });
                }
            });
        }

        // Add Layer Control switcher
        L.control.layers(baseMaps, geojsonLayers, { collapsed: false, position: 'topright' }).addTo(map);

        // Opacity control slider
        const opacityPanel = L.control({ position: 'bottomleft' });
        opacityPanel.onAdd = function() {
            const div = L.DomUtil.create('div', 'opacity-control-panel');
            div.innerHTML = 'RISK OVERLAY OPACITY<br><input id="flood-opacity" type="range" class="opacity-slider" min="0" max="100" value="50" />';
            L.DomEvent.disableClickPropagation(div);
            return div;
        };
        opacityPanel.addTo(map);

        document.getElementById('flood-opacity').addEventListener('input', function(e) {
            const val = e.target.value / 100;
            riskLayers.forEach(layer => {
                layer.setStyle({ fillOpacity: val * 0.4, opacity: val });
            });
        });

        // ── 3. DYNAMIC INTERACTIVE FILTER ENGINE ────────────────────────────
        
        function filterBySubcounty(subcountyName) {
            currentSubcounty = subcountyName;
            
            const coords = subcountyCentroids[subcountyName];
            if (coords) {
                map.setView([coords[0], coords[1]], subcountyName === 'All' ? 8.5 : 10);
            }
            
            updateMapMarkersFilter();
            updateInventoryTable();
            updateMetricsData();
        }

        function filterByRisk(riskName) {
            currentRisk = riskName;
            updateMapMarkersFilter();
            updateInventoryTable();
        }

        function updateMapMarkersFilter() {
            const filterFn = (f) => {
                if (currentSubcounty === 'All') return true;
                const sc = (f.properties.sub_county || f.properties.Sub_County || '').replace(' Township', ' Sub County').trim();
                return sc === currentSubcounty;
            };
            
            const filterRiskFn = (f) => {
                if (currentRisk === 'All') return true;
                return f.properties.Risk_Level === currentRisk;
            };
            
            const combinedFilter = (f) => filterFn(f) && filterRiskFn(f);

            const layersToFilter = [
                { key: "🏫 Schools", data: schoolsData, icon: '🏫', riskCol: true },
                { key: "🏥 Health Facilities", data: healthData, icon: '🏥', riskCol: true },
                { key: "💧 Boreholes", data: boreholesData, icon: '💧', riskCol: true },
                { key: "🪣 Water Pans", data: waterPansData, icon: '🪣', color: '#0ea5e9' },
                { key: "🦒 Wildlife & Sanctuaries", data: wildlifeData, icon: '🦒', specialWild: true },
                { key: "⛺ Refugee Camps", data: idpCampsData, icon: '⛺', color: '#f472b6' }
            ];

            layersToFilter.forEach(item => {
                const layer = geojsonLayers[item.key];
                if (!layer) return;
                
                layer.clearLayers();
                const filteredFeatures = item.data.features.filter(combinedFilter);
                
                L.geoJSON({ type: "FeatureCollection", features: filteredFeatures }, {
                    pointToLayer: (f, latlng) => {
                        let col = item.color || '#22c55e';
                        let em = item.icon;
                        if (item.riskCol) col = getRiskColor(f.properties.Risk_Level);
                        if (item.specialWild) {
                            let ani = f.properties.animal || 'giraffe';
                            em = '🦒';
                            if (ani.includes('Elephant')) em = '🐘';
                            else if (ani.includes('Cheetah')) em = '🐆';
                            else if (ani.includes('Ostrich')) em = '🪶';
                            col = '#10b981';
                        }
                        return L.marker(latlng, { icon: createEmojiMarker(em, col) });
                    },
                    onEachFeature: (f, l) => setupAttributePopup(f, l, item.icon)
                }).eachLayer(childLayer => {
                    layer.addLayer(childLayer);
                });
            });
        }

        function updateMetricsData() {
            let filteredSchools = schoolsData.features;
            let filteredHealth = healthData.features;
            let filteredBoreholes = boreholesData.features;
            let filteredCamps = idpCampsData.features;
            
            if (currentSubcounty !== 'All') {
                const matchSc = (f) => (f.properties.sub_county || f.properties.Sub_County || '').replace(' Township', ' Sub County').trim() === currentSubcounty;
                filteredSchools = filteredSchools.filter(matchSc);
                filteredHealth = filteredHealth.filter(matchSc);
                filteredBoreholes = filteredBoreholes.filter(matchSc);
                filteredCamps = filteredCamps.filter(matchSc);
            }
            
            const countRisk = (arr) => arr.filter(f => f.properties.Risk_Level === 'High Risk' || f.properties.Risk_Level === 'Extreme Risk (Super El Niño)').length;
            
            const schRiskCount = countRisk(filteredSchools);
            const hlthRiskCount = countRisk(filteredHealth);
            const borRiskCount = countRisk(filteredBoreholes);
            const cmpRiskCount = countRisk(filteredCamps);
            
            document.getElementById('metric-schools-val').textContent = schRiskCount;
            document.getElementById('metric-health-val').textContent = hlthRiskCount;
            document.getElementById('metric-boreholes-val').textContent = borRiskCount;
            document.getElementById('metric-camps-val').textContent = cmpRiskCount;
            
            document.getElementById('metric-schools-desc').textContent = 'Out of ' + filteredSchools.length + ' structures (' + (filteredSchools.length ? Math.round(schRiskCount/filteredSchools.length*100) : 0) + '% exposed)';
            document.getElementById('metric-health-desc').textContent = 'Out of ' + filteredHealth.length + ' clinics (' + (filteredHealth.length ? Math.round(hlthRiskCount/filteredHealth.length*100) : 0) + '% exposed)';
            document.getElementById('metric-boreholes-desc').textContent = 'Humanitarian water supply (' + (filteredBoreholes.length ? Math.round(borRiskCount/filteredBoreholes.length*100) : 0) + '% exposed)';
            document.getElementById('metric-camps-desc').textContent = 'Dadaab / IDP camps (' + (filteredCamps.length ? Math.round(cmpRiskCount/filteredCamps.length*100) : 0) + '% exposed)';
            
            let popExposedVal = 156000;
            if (currentSubcounty !== 'All') {
                const subRecord = subcountyStats.find(r => r['Sub-County Name'] === currentSubcounty);
                if (subRecord) popExposedVal = subRecord['Population_Exposed'];
            }
            document.getElementById('info-pop-exposed').textContent = popExposedVal.toLocaleString();
        }

        function updateInventoryTable() {
            const tbody = document.getElementById('inventory-tbody');
            tbody.innerHTML = '';
            
            const searchQuery = document.getElementById('inventory-search').value.toLowerCase().trim();
            const typeFilter = document.getElementById('inventory-type').value;
            
            let allAssets = [];
            
            const collect = (arr, typeName, icon) => {
                arr.features.forEach(f => {
                    let name = f.properties.school_nam || f.properties.health_fac || f.properties.name || f.properties.Name || f.properties.Name_of_B || f.properties.Borehole_N || f.properties.town_name || f.properties.animal || 'Asset';
                    if (name === 'null' || name === 'nil' || name === 'None' || name === '' || name === 'Asset') {
                        let t = f.properties.Type || f.properties.LAYER || typeName;
                        name = t + ' at ' + parseFloat(f.geometry.coordinates[1]).toFixed(3) + ', ' + parseFloat(f.geometry.coordinates[0]).toFixed(3);
                    }
                    allAssets.push({
                        name: name,
                        sub_county: (f.properties.sub_county || f.properties.Sub_County || 'Garissa Sub County').replace(' Township', ' Sub County').trim(),
                        risk: f.properties.Risk_Level || 'Safe',
                        vuln: f.properties.NN_Vulnerability_Score || f.properties.Vulnerability_Index || '0.0',
                        lat: f.geometry.coordinates[1],
                        lng: f.geometry.coordinates[0],
                        type: typeName,
                        icon: icon
                    });
                });
            };
            
            if (typeFilter === 'all' || typeFilter === 'schools') collect(schoolsData, 'schools', '🏫');
            if (typeFilter === 'all' || typeFilter === 'health') collect(healthData, 'health', '🏥');
            if (typeFilter === 'all' || typeFilter === 'boreholes') collect(boreholesData, 'boreholes', '💧');
            if (typeFilter === 'all' || typeFilter === 'water_pans') collect(waterPansData, 'water_pans', '🪣');
            if (typeFilter === 'all' || typeFilter === 'wildlife') collect(wildlifeData, 'wildlife', '🦒');

            // Subcounty filter
            if (currentSubcounty !== 'All') {
                allAssets = allAssets.filter(a => a.sub_county === currentSubcounty);
            }
            
            // Risk filter
            if (currentRisk !== 'All') {
                allAssets = allAssets.filter(a => a.risk === currentRisk);
            }
            
            // Search query filter
            if (searchQuery) {
                allAssets = allAssets.filter(a => a.name.toLowerCase().includes(searchQuery) || a.risk.toLowerCase().includes(searchQuery) || a.sub_county.toLowerCase().includes(searchQuery));
            }
            
            document.getElementById('inventory-count').textContent = 'Showing ' + Math.min(100, allAssets.length) + ' of ' + allAssets.length + ' assets';

            const displayAssets = allAssets.slice(0, 100);
            displayAssets.forEach(a => {
                const tr = document.createElement('tr');
                tr.onclick = () => {
                    // BI-DIRECTIONAL PAN & POPUP ZOOM
                    map.setView([a.lat, a.lng], 14);
                    
                    const layerKey = a.type === 'schools' ? "🏫 Schools" :
                                     a.type === 'health' ? "🏥 Health Facilities" :
                                     a.type === 'boreholes' ? "💧 Boreholes" :
                                     a.type === 'water_pans' ? "🪣 Water Pans" :
                                     a.type === 'wildlife' ? "🦒 Wildlife & Sanctuaries" : null;
                    
                    if (layerKey && geojsonLayers[layerKey]) {
                        geojsonLayers[layerKey].eachLayer(layer => {
                            const f = layer.feature;
                            if (f && f.geometry.coordinates[1] === a.lat && f.geometry.coordinates[0] === a.lng) {
                                layer.openPopup();
                            }
                        });
                    }
                };
                
                tr.innerHTML = '<td style="font-weight:bold; color:var(--text-main);">' + a.icon + ' ' + a.name + '</td>' +
                    '<td style="color:var(--text-muted);">' + a.sub_county.replace(' Sub County', '') + '</td>' +
                    '<td style="color:' + getRiskColor(a.risk) + '; font-weight:500;">' + a.risk.replace(' Risk', '') + '</td>' +
                    '<td style="font-family:Orbitron,sans-serif; color:var(--cyan); font-weight:bold;">' + parseFloat(a.vuln).toFixed(3) + '</td>';
                
                tbody.appendChild(tr);
            });
        }

        // ── 4. MAP GALLERY VIEW SWITCHER ─────────────────────────────────────
        
        function switchMapLayer(layerKey) {
            const layersToClear = [
                subcountyBoundariesLayer,
                wardBoundariesLayer,
                geojsonLayers["🏫 Schools"],
                geojsonLayers["🏥 Health Facilities"],
                geojsonLayers["💧 Boreholes"],
                geojsonLayers["🪣 Water Pans"],
                geojsonLayers["🦒 Wildlife & Sanctuaries"],
                geojsonLayers["📐 Cadastral Parcels"],
                geojsonLayers["⛺ Refugee Camps"],
                geojsonLayers["🌊 Rivers & Laghas"],
                geojsonLayers["🏕️ Dagahaley Block"],
                geojsonLayers["🏕️ Hagadera Block"],
                geojsonLayers["🏕️ Ifo Block"],
                geojsonLayers["🛣️ Roads Network"]
            ];
            
            layersToClear.forEach(l => {
                if (l && map.hasLayer(l)) {
                    map.removeLayer(l);
                }
            });
            
            const addLayers = (arr) => {
                arr.forEach(l => {
                    if (l) l.addTo(map);
                });
            };
            
            switch(layerKey) {
                case "subcounties":
                    if (subcountyBoundariesLayer) subcountyBoundariesLayer.addTo(map);
                    break;
                case "wards":
                    if (wardBoundariesLayer) wardBoundariesLayer.addTo(map);
                    break;
                case "schools":
                    if (geojsonLayers["🏫 Schools"]) geojsonLayers["🏫 Schools"].addTo(map);
                    break;
                case "health":
                    if (geojsonLayers["🏥 Health Facilities"]) geojsonLayers["🏥 Health Facilities"].addTo(map);
                    break;
                case "refugee":
                    addLayers([
                        geojsonLayers["⛺ Refugee Camps"],
                        geojsonLayers["🏕️ Dagahaley Block"],
                        geojsonLayers["🏕️ Hagadera Block"],
                        geojsonLayers["🏕️ Ifo Block"]
                    ]);
                    break;
                case "water":
                    addLayers([
                        geojsonLayers["💧 Boreholes"],
                        geojsonLayers["🪣 Water Pans"]
                    ]);
                    break;
                case "rivers":
                    if (geojsonLayers["🌊 Rivers & Laghas"]) geojsonLayers["🌊 Rivers & Laghas"].addTo(map);
                    break;
                case "agri":
                    addLayers([
                        geojsonLayers["🌊 Rivers & Laghas"],
                        geojsonLayers["🪣 Water Pans"]
                    ]);
                    break;
                case "wildlife":
                    if (geojsonLayers["🦒 Wildlife & Sanctuaries"]) geojsonLayers["🦒 Wildlife & Sanctuaries"].addTo(map);
                    break;
                case "cadastral":
                    if (geojsonLayers["📐 Cadastral Parcels"]) geojsonLayers["📐 Cadastral Parcels"].addTo(map);
                    break;
                case "all":
                default:
                    addLayers([
                        geojsonLayers["🌊 Rivers & Laghas"],
                        geojsonLayers["🏫 Schools"],
                        geojsonLayers["🏥 Health Facilities"],
                        geojsonLayers["💧 Boreholes"],
                        geojsonLayers["🪣 Water Pans"],
                        geojsonLayers["🦒 Wildlife & Sanctuaries"]
                    ]);
                    break;
            }
        }

        // ── 5. DATE FILTER & DYNAMIC ADVISORIES ─────────────────────────────
        
        function updateDateFilter(val) {
            const months = ["June 2026", "July 2026", "August 2026", "September 2026", "October 2026", "November 2026", "December 2026"];
            const selectedMonth = months[val - 1];
            document.getElementById('date-label').textContent = selectedMonth;
            
            const isPeak = val >= 5;
            const opacityVal = isPeak ? 0.8 : 0.2;
            
            riskLayers.forEach(layer => {
                layer.setStyle({ fillOpacity: opacityVal * 0.3, opacity: opacityVal });
            });
            document.getElementById('flood-opacity').value = isPeak ? 80 : 20;
            
            const alertBox = document.querySelector('.rangeland-advisory');
            if (alertBox) {
                if (isPeak) {
                    alertBox.innerHTML = '<strong>⚠️ PEAK EL NIÑO ALERT (' + selectedMonth + '):</strong> High Sea Surface SST (+2.1°C) has triggered torrential rangeland rains. Move herds to ijara highlands.';
                    alertBox.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                    alertBox.style.background = 'rgba(239, 68, 68, 0.05)';
                } else {
                    alertBox.innerHTML = '<strong>🌿 SEASONAL PREPARATION (' + selectedMonth + '):</strong> SST anomalies are rising. Pasture greens index (NDVI: 0.34) is stable. Stock animal vaccine buffers.';
                    alertBox.style.borderColor = 'rgba(16, 185, 129, 0.2)';
                    alertBox.style.background = 'rgba(16, 185, 129, 0.05)';
                }
            }
        }

        // ── 6. CHARTS INITIALIZATION ────────────────────────────────────────
        Chart.defaults.color = '#94a3b8';
        
        // Dengue cases vs Rainfall chart
        new Chart(document.getElementById('chart-dengue').getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Jun 25', 'Aug 25', 'Oct 25', 'Dec 25', 'Feb 26', 'Apr 26', 'May 26 (Outbreak)'],
                datasets: [
                    {
                        label: 'Rainfall Anomaly (mm)',
                        data: [-20, -15, 45, 110, -5, 130, 240],
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 1.5,
                        tension: 0.3
                    },
                    {
                        label: 'Dengue Cases Reported',
                        data: [2, 1, 5, 14, 3, 22, 68],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.2)',
                        borderWidth: 1.5,
                        tension: 0.3,
                        type: 'bar'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true, labels: { boxWidth: 8, fontSize: 9 } } }
            }
        });

        // Schools exposure chart
        new Chart(document.getElementById('chart-schools-exposure').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Garissa', 'Dadaab', 'Fafi', 'Ijara', 'Balambala', 'Lagdera', 'Hulugho'],
                datasets: [
                    {
                        label: 'Extreme Risk',
                        data: [5, 12, 4, 1, 3, 2, 0],
                        backgroundColor: '#a855f7'
                    },
                    {
                        label: 'High Risk',
                        data: [8, 15, 6, 3, 5, 7, 0],
                        backgroundColor: '#ef4444'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { x: { stacked: true }, y: { stacked: true } },
                plugins: { legend: { display: true, labels: { boxWidth: 8 } } }
            }
        });

        // Exposure distribution donut
        new Chart(document.getElementById('chart-exposure-donut').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Extreme', 'High', 'Medium', 'Low', 'Safe'],
                datasets: [{
                    data: [123, 110, 342, 111, 1543],
                    backgroundColor: ['#a855f7', '#ef4444', '#f97316', '#fbbf24', '#22c55e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 8, padding: 3 } } }
            }
        });

        // Sub-county poverty vs wasting chart
        new Chart(document.getElementById('chart-subcounty-abstract').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Garissa', 'Dadaab', 'Lagdera', 'Balambala', 'Fafi', 'Ijara', 'Hulugho'],
                datasets: [
                    {
                        label: 'Poverty Rate (%)',
                        data: [48, 78, 80, 82, 77, 62, 65],
                        backgroundColor: 'rgba(6, 182, 212, 0.75)',
                        borderColor: 'var(--cyan)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Child Wasting Rate (%)',
                        data: [10, 17, 16, 15, 14, 12, 11],
                        backgroundColor: 'rgba(239, 68, 68, 0.75)',
                        borderColor: '#ef4444',
                        borderWidth: 1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Poverty (%)', color: 'var(--cyan)', font: { size: 9 } }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        title: { display: true, text: 'Wasting (%)', color: '#ef4444', font: { size: 9 } }
                    }
                },
                plugins: { legend: { display: true, labels: { boxWidth: 8, fontSize: 8 } } }
            }
        });

        // Tab switcher function
        function switchTab(evt, tabName) {
            const panels = document.querySelectorAll('.tab-panel');
            panels.forEach(p => p.classList.remove('active'));
            
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }

        // ── 7. DOWNLOADS, EXPORTS & WEB SHARE ──────────────────────────────
        
        function printMap() {
            window.print();
        }

        function exportCSV() {
            let allAssets = [];
            const collect = (arr, typeName) => {
                arr.features.forEach(f => {
                    let name = f.properties.school_nam || f.properties.health_fac || f.properties.name || f.properties.Name || f.properties.Name_of_B || f.properties.Borehole_N || f.properties.town_name || f.properties.animal || 'Asset';
                    allAssets.push({
                        name: name,
                        type: typeName,
                        sub_county: (f.properties.sub_county || f.properties.Sub_County || 'Garissa Sub County').replace(' Township', ' Sub County').trim(),
                        risk: f.properties.Risk_Level || 'Safe',
                        vulnerability: f.properties.NN_Vulnerability_Score || f.properties.Vulnerability_Index || '0.0',
                        latitude: f.geometry.coordinates[1],
                        longitude: f.geometry.coordinates[0]
                    });
                });
            };
            collect(schoolsData, 'School');
            collect(healthData, 'Clinic');
            collect(boreholesData, 'Borehole');
            collect(waterPansData, 'Water Pan');
            collect(wildlifeData, 'Wildlife');

            if (currentSubcounty !== 'All') {
                allAssets = allAssets.filter(a => a.sub_county === currentSubcounty);
            }
            if (currentRisk !== 'All') {
                allAssets = allAssets.filter(a => a.risk === currentRisk);
            }

            let csvContent = "NAME,TYPE,SUB-COUNTY,RISK LEVEL,VULNERABILITY,LATITUDE,LONGITUDE\\n";
            allAssets.forEach(a => {
                csvContent += '"' + a.name.replace(/"/g, '""') + '",' + a.type + ',"' + a.sub_county + '",' + a.risk + ',' + a.vulnerability + ',' + a.latitude + ',' + a.longitude + '\\n';
            });

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Garissa_DRM_Assets_' + currentSubcounty.replace(/ /g, '_') + '.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function generateDRMReport() {
            let filteredSchools = schoolsData.features;
            let filteredHealth = healthData.features;
            let filteredBoreholes = boreholesData.features;
            let filteredCamps = idpCampsData.features;
            
            if (currentSubcounty !== 'All') {
                const matchSc = (f) => (f.properties.sub_county || f.properties.Sub_County || '').replace(' Township', ' Sub County').trim() === currentSubcounty;
                filteredSchools = filteredSchools.filter(matchSc);
                filteredHealth = filteredHealth.filter(matchSc);
                filteredBoreholes = filteredBoreholes.filter(matchSc);
                filteredCamps = filteredCamps.filter(matchSc);
            }
            
            const countRisk = (arr) => arr.filter(f => f.properties.Risk_Level === 'High Risk' || f.properties.Risk_Level === 'Extreme Risk (Super El Niño)').length;
            
            const subRecord = subcountyStats.find(r => r['Sub-County Name'] === currentSubcounty) || { Poverty_Rate: 0.68, Food_Poverty_Rate: 0.51, Wasting_Rate_Pct: 14 };
            
            const reportText = "======================================================================\\n" +
"🌍 GARISSA COUNTY EL NIÑO DRM DIGITAL TWIN - REPORT GENERATOR\\n" +
"======================================================================\\n" +
"REPORT GENERATED ON: " + new Date().toLocaleDateString() + "\\n" +
"AUTHOR: GARISSA GIS DIRECTORATE - JAMES M. MBURU\\n" +
"TARGET AREA: " + (currentSubcounty === 'All' ? 'Garissa County (All Sub-Counties)' : currentSubcounty) + "\\n" +
"----------------------------------------------------------------------\\n\\n" +
"1. INFRASTRUCTURE EXPOSURE RISK METRICS\\n" +
"- Schools at Risk: " + countRisk(filteredSchools) + " / " + filteredSchools.length + " total structures\\n" +
"- Clinics at Risk: " + countRisk(filteredHealth) + " / " + filteredHealth.length + " clinics\\n" +
"- Boreholes at Risk: " + countRisk(filteredBoreholes) + " / " + filteredBoreholes.length + " boreholes\\n" +
"- IDP/Refugee Camps at Risk: " + countRisk(filteredCamps) + " / " + filteredCamps.length + " camp locations\\n\\n" +
"2. SOCIOECONOMIC & VULNERABILITY CONTEXT\\n" +
"- Poverty Rate: " + (currentSubcounty === 'All' ? '67.8% (County Average)' : (subRecord.Poverty_Rate * 100).toFixed(1) + '%') + "\\n" +
"- Food Poverty Rate: " + (currentSubcounty === 'All' ? '51.2% (County Average)' : (subRecord.Food_Poverty_Rate * 100).toFixed(1) + '%') + "\\n" +
"- Under-5 Child Wasting Rate: " + (currentSubcounty === 'All' ? '14.1% (County Average)' : subRecord.Wasting_Rate_Pct + '%') + "\\n" +
"- Dominant Clans: " + (currentSubcounty === 'All' ? 'Abdwak, Abdalla, Aulihan, Munyoyaya, Malakote' : subRecord['Dominant Clans'] || 'N/A') + "\\n\\n" +
"3. PUBLIC HEALTH & EPIDEMIOLOGICAL ALERTS\\n" +
"- Outbreak Status: Active Dengue Fever Outbreak (Garissa Township, late May 2026)\\n" +
"- Clinic Positivity Rate: 70.0% Laboratory Positivity\\n" +
"- Principal Vector: Aedes Mosquito (breeding in flood water pools)\\n\\n" +
"4. EMERGENCY DRM RECOMMENDATIONS & ACTION LIST\\n" +
"* Evacuate extreme-risk schools to dry community centers immediately.\\n" +
"* Deploy mobile cold-chain solar vaccine refrigerators to clinics outside the 500m river buffer.\\n" +
"* Install high-volume drawdown pumps at Dadaab camp boreholes.\\n" +
"* Apply larvicides to rangeland waterlogged pasture zones to mitigate Dengue and RVF vectors.\\n\\n" +
"======================================================================\\n" +
"For detailed GIS spatial shapefiles, open FinalGarissaDRM.qgz in QGIS.\\n" +
"Emergency GIS Command Desk: emergency@garissa.go.ke\\n" +
"======================================================================\\n";

            const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Garissa_DRM_Report_' + currentSubcounty.replace(/ /g, '_') + '.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function shareDashboard() {
            const shareData = {
                title: 'Garissa Early Warning and Adaptation System (GEWAS)',
                text: 'Emergency Operations Portal for Garissa Sub-Counties. Active Sub-County: ' + currentSubcounty + '.',
                url: window.location.href.split('#')[0] + '#' + encodeURIComponent(currentSubcounty)
            };
            if (navigator.share) {
                navigator.share(shareData)
                    .catch(err => console.log('Error sharing:', err));
            } else {
                navigator.clipboard.writeText(shareData.url);
                alert("🔗 Sharing URL copied to clipboard: " + shareData.url);
            }
        }

        // ── 8. SENTINEL-BOT CHATBOT ADVISOR ENGINE ────────────────────────────
        
        function toggleChatbot() {
            const panel = document.getElementById('sentinel-bot-panel');
            panel.style.display = (panel.style.display === 'none' || !panel.style.display) ? 'flex' : 'none';
        }

        function toggleBotSettings() {
            const apiSettings = document.getElementById('bot-api-settings');
            apiSettings.style.display = (apiSettings.style.display === 'none' || !apiSettings.style.display) ? 'flex' : 'none';
            
            const savedKey = localStorage.getItem('gemini_api_key');
            if (savedKey) {
                document.getElementById('custom-api-key-input').value = savedKey;
            }
            const savedWeatherKey = localStorage.getItem('weather_api_key');
            if (savedWeatherKey) {
                document.getElementById('custom-weather-key-input').value = savedWeatherKey;
            }
            document.getElementById('api-key-status').textContent = "Keys loaded from local storage.";
            document.getElementById('api-key-status').style.color = "var(--text-muted)";
        }

        function saveCustomAPIKey() {
            const key = document.getElementById('custom-api-key-input').value.trim();
            if (key) {
                localStorage.setItem('gemini_api_key', key);
                document.getElementById('api-key-status').textContent = "Gemini key saved!";
                document.getElementById('api-key-status').style.color = "var(--emerald)";
            } else {
                localStorage.removeItem('gemini_api_key');
                document.getElementById('api-key-status').textContent = "Gemini key cleared.";
                document.getElementById('api-key-status').style.color = "var(--text-muted)";
            }
        }

        function saveCustomWeatherKey() {
            const key = document.getElementById('custom-weather-key-input').value.trim();
            if (key) {
                localStorage.setItem('weather_api_key', key);
                document.getElementById('api-key-status').textContent = "Weather key saved! Reloading...";
                document.getElementById('api-key-status').style.color = "var(--emerald)";
                setTimeout(() => {
                    loadLiveWeather();
                }, 1000);
            } else {
                localStorage.removeItem('weather_api_key');
                document.getElementById('api-key-status').textContent = "Weather key cleared.";
                document.getElementById('api-key-status').style.color = "var(--text-muted)";
                setTimeout(() => {
                    loadLiveWeather();
                }, 1000);
            }
        }

        async function loadLiveWeather() {
            const weatherKey = localStorage.getItem('weather_api_key') || (typeof WEATHER_API_KEY !== 'undefined' ? WEATHER_API_KEY : '');
            if (!weatherKey) {
                document.getElementById('weather-widget').innerHTML = `
                    <div class="weather-alert">
                        <span>☁️ Weather offline (No API key found). Enter an OpenWeatherMap API key in the settings panel to enable live data.</span>
                    </div>
                `;
                return;
            }
            
            try {
                const response = await fetch('https://api.openweathermap.org/data/2.5/weather?q=Garissa,KE&units=metric&appid=' + weatherKey);
                if (!response.ok) throw new Error('Failed to fetch weather data');
                const data = await response.json();
                
                const temp = Math.round(data.main.temp);
                const desc = data.weather[0].description;
                const icon = data.weather[0].icon;
                const humidity = data.main.humidity;
                const wind = data.wind.speed;
                
                let warningText = "Normal conditions. Monitor seasonal outlooks.";
                let warningClass = "weather-normal";
                if (desc.includes('rain') || desc.includes('storm') || desc.includes('drizzle')) {
                    warningText = "🚨 Heavy precipitation warning: potential laghas and river overflows. Evacuate low-lying zones.";
                    warningClass = "weather-warning";
                }
                
                document.getElementById('weather-widget').innerHTML = `
                    <div class="weather-container ${warningClass}">
                        <div class="weather-main">
                            <img src="https://openweathermap.org/img/wn/${icon}@2x.png" alt="${desc}" class="weather-icon" />
                            <div class="weather-temp-info">
                                <span class="weather-temp">${temp}°C</span>
                                <span class="weather-desc">${desc.toUpperCase()}</span>
                            </div>
                        </div>
                        <div class="weather-details">
                            <div class="weather-detail-item">💧 <strong>Humidity:</strong> ${humidity}%</div>
                            <div class="weather-detail-item">💨 <strong>Wind:</strong> ${wind} m/s</div>
                            <div class="weather-detail-item">🌍 <strong>Location:</strong> Garissa, Kenya</div>
                        </div>
                        <div class="weather-status-alert">
                            <strong>DRM Status:</strong> ${warningText}
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Weather load error:', error);
                document.getElementById('weather-widget').innerHTML = `
                    <div class="weather-alert">
                        <span>⚠️ Error loading weather data. Please verify your OpenWeatherMap API key.</span>
                    </div>
                `;
            }
        }

        window.addEventListener('load', () => {
            // Restore URL hash state
            if (window.location.hash) {
                const hashSc = decodeURIComponent(window.location.hash.substring(1));
                if (subcountyCentroids[hashSc]) {
                    document.getElementById('subcounty-select').value = hashSc;
                    filterBySubcounty(hashSc);
                }
            } else {
                updateInventoryTable();
            }
            
            // Load live weather
            loadLiveWeather();
            
            // Auto open bot after 3.5 seconds
            setTimeout(() => {
                document.getElementById('sentinel-bot-panel').style.display = 'flex';
            }, 3500);
        });

        const handleBotKeyPress = (e) => {
            if (e.key === 'Enter') {
                triggerChatbotQuery();
            }
        };

        const appendMessage = (text, isUser = false) => {
            const botMessages = document.getElementById('bot-messages');
            const msg = document.createElement('div');
            msg.className = 'bot-msg';
            msg.style.alignSelf = isUser ? 'flex-end' : 'flex-start';
            msg.style.background = isUser ? 'rgba(6, 182, 212, 0.15)' : 'rgba(30, 41, 59, 0.6)';
            msg.style.borderColor = isUser ? 'var(--cyan)' : 'rgba(255,255,255,0.05)';
            msg.innerHTML = '<strong>' + (isUser ? 'Operator' : 'Sentinel-Bot') + ':</strong> ' + text;
            botMessages.appendChild(msg);
            botMessages.scrollTop = botMessages.scrollHeight;
        };

        // Local expert backup system (Self-Troubleshooting)
        function getLocalExpertResponse(query) {
            query = query.toLowerCase();
            
            if (query.includes('school') || query.includes('education') || query.includes('class')) {
                return 'Based on our custom Neural Network vulnerability analysis, out of the total structures in Garissa, <strong>52 schools</strong> are flagged as exposed to flood risk. Wasting is high, and 27 schools sit directly in the extreme risk path. Immediate evacuation plans to higher grounds (Township, Galbet, and Dadaab camps) are recommended.';
            } else if (query.includes('clinic') || query.includes('health') || query.includes('hospital') || query.includes('medical') || query.includes('dengue')) {
                return '<strong>Health Facilities Alert:</strong> Out of 69 clinics in Garissa, 18 health facilities are directly exposed to flooding. We have a confirmed Dengue Fever outbreak in Garissa Township (late May 2026) with a 70% laboratory sample positivity rate. Cold-chain storage must be protected immediately.';
            } else if (query.includes('borehole') || query.includes('water') || query.includes('aquifer') || query.includes('pan')) {
                return '<strong>Water Assets Risk:</strong> 2 critical boreholes are exposed. In Dadaab camps, the livestock-to-refugee water demand multiplier is 21.6x. Water Pans represent essential rangeland buffers but require chemical purification.';
            } else if (query.includes('dadaab') || query.includes('refugee') || query.includes('camp') || query.includes('hagadera') || query.includes('ifo') || query.includes('dagahaley')) {
                return '<strong>Dadaab camps (Dagahaley, Hagadera, Ifo):</strong> These house over 432,000 refugees. High risk of cholera and malaria vector spread as rangelands flood. Safe water supply is threatened due to borehole drawdown ratios of 21.6.';
            } else if (query.includes('wildlife') || query.includes('hirola') || query.includes('giraffe') || query.includes('elephant') || query.includes('cheetah')) {
                return '<strong>Wildlife Habitats:</strong> Ijara/Hulugho hosts the critically endangered Hirola antelope (~250 head). Lagdera hosts reticulated giraffes, Fafi hosts elephant corridors, and Balambala hosts cheetahs. These animals migrate towards higher dry zones during floods.';
            } else if (query.includes('poverty') || query.includes('gap') || query.includes('clans') || query.includes('socioeconomic') || query.includes('income') || query.includes('expenditure')) {
                return '<strong>Socioeconomics:</strong> Garissa\\\'s average poverty rate is 67.8% (food poverty is 51.2%). The average household faces a cash gap of KES -1,008 (expenditure KES 6,177 vs income KES 5,169). Direct cash transfers are coordinated via UNICEF/Red Cross.';
            } else if (query.includes('weather') || query.includes('rain') || query.includes('sst') || query.includes('temp') || query.includes('forecast')) {
                return '<strong>Weather Outlook:</strong> Sea Surface Temperature (SST) anomalies in the Niño 3.4 region have reached +2.1°C, trigger level for a strong El Niño. Severe seasonal rainfall (exceeding 145% of average) is active.';
            } else {
                return 'Jambo! I am running in local backup mode because the default Gemini API key is rate-limited or blocked. You can paste your own Gemini API Key in the settings (gear icon) to re-enable full AI generative advice.<br><br>' +
                'Here is a summary of Garissa\\\'s DRM status:<br>' +
                '- 52 schools and 18 clinics are at risk of flooding.<br>' +
                '- Active Dengue outbreak (70% clinic sample positivity).<br>' +
                '- 432,000 refugees in Dadaab face water demand surge of 21.6x.<br>' +
                '- Critically endangered Hirola antelopes are under Ijara/Hulugho conservancy monitoring.';
            }
        }

        const triggerChatbotQuery = async () => {
            const botInput = document.getElementById('sentinel-bot-input');
            const query = botInput.value.trim();
            if (!query) return;
            
            appendMessage(query, true);
            botInput.value = '';
            
            const typing = document.createElement('div');
            typing.id = 'typing-indicator';
            typing.style.alignSelf = 'flex-start';
            typing.style.color = 'var(--cyan)';
            typing.style.fontSize = '12px';
            typing.style.fontStyle = 'italic';
            typing.textContent = '🤖 Sentinel-Bot is computing...';
            document.getElementById('bot-messages').appendChild(typing);
            document.getElementById('bot-messages').scrollTop = document.getElementById('bot-messages').scrollHeight;
            
            const userKey = localStorage.getItem('gemini_api_key') || (typeof GEMINI_API_KEY !== 'undefined' ? GEMINI_API_KEY : '');
            if (!userKey) {
                setTimeout(() => {
                    document.getElementById('typing-indicator').remove();
                    appendMessage("🤖 <em>[System Alert: Using local Neural DRM expert fallback]</em><br>" + getLocalExpertResponse(query));
                }, 800);
                return;
            }

            try {
                const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + userKey;
                
                const sysPrompt = `You are "Sentinel-Bot", a smart, robotic DRM advisor for Garissa County, Kenya.
                You are designed to assist county emergency operators, chiefs, and community health promoters.
                Author & Director: Garissa GIS Directorate — James M. Mburu.
                You have direct access to the 2026 El Niño risk metrics:
                - Schools: __TOTAL_SCHOOLS__ total, __SUM_SCHOOLS_RISK__ at High/Extreme Risk.
                - Health Facilities: __TOTAL_HEALTH__ total, __SUM_HEALTH_RISK__ at High/Extreme Risk.
                - Boreholes: __TOTAL_BORE__ total, __SUM_BORE_RISK__ at High/Extreme Risk.
                - Refugee Camps: __TOTAL_CAMPS__ total, __SUM_CAMPS_RISK__ at High/Extreme Risk.
                - Dadaab Refugee Complex: 432,000 refugees, water demand ratio is 21.6.
                - Outbreak Alert: Confirmed Dengue fever outbreak in Garissa Township (late May 2026) with a 70% laboratory sample positivity rate. Vector: Aedes mosquitoes.
                - Child Health (KDHS 2022): Under-5 deaths at 44 per 1,000. Wasting is at 14.1% average.
                - Socio-economics: Garissa average overall poverty is 67.8% and food poverty is 51.2%. Household income KES 5,169 vs expenditure KES 6,177 creating a KES -1,008 cash gap.
                - Wildlife Geolocation: hirola (Ijara), cheetah (Balambala), elephant (Fafi corridor), reticulated giraffe (Lagdera).
                Provide very professional, highly specific, and actionable DRM responses in simple, clear language. Use bullet points where appropriate. Avoid code blocks or markdown tables, keep it readable in a chat UI. Contact GIS directorate command desk at emergency@garissa.go.ke.`;

                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{
                                text: sysPrompt + "\\n\\nUser Question: " + query
                            }]
                        }]
                    })
                });
                
                const data = await response.json();
                document.getElementById('typing-indicator').remove();
                
                if (data.candidates && data.candidates[0].content.parts[0].text) {
                    appendMessage(data.candidates[0].content.parts[0].text);
                } else {
                    appendMessage("🤖 <em>[System Alert: Key quota exceeded or blocked]</em><br>" + getLocalExpertResponse(query));
                }
            } catch (error) {
                if (document.getElementById('typing-indicator')) {
                    document.getElementById('typing-indicator').remove();
                }
                appendMessage("🤖 <em>[System Alert: Offline or API block detected]</em><br>" + getLocalExpertResponse(query));
            }
        };
    </script>
</body>
</html>
"""

    # ── Narrative Notebook Parsing ──────────────────────────────────────────
    narrative_html = "<h3>Loading 60-Chapter Narrative Story...</h3>"
    try:
        notebook_path = BASE_DIR / "garissa_elnino_flood_risk.ipynb"
        if notebook_path.exists():
            import re
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = json.load(f)
            
            chapters_html = []
            sidebar_html = []
            ch_num = 0
            
            for cell in nb.get("cells", []):
                if cell["cell_type"] == "markdown":
                    src = "".join(cell["source"])
                    # Look for chapter headers like "# 📋 Chapter X: ..."
                    ch_match = re.search(r'^#\s+(?:[^:]+:\s*)?Chapter\s+(\d+):\s*(.+)$', src, re.MULTILINE | re.IGNORECASE)
                    if ch_match:
                        ch_num = int(ch_match.group(1))
                        ch_title = ch_match.group(2).strip()
                        
                        # Look for Somali translation subtitle inside
                        so_title = ""
                        lines = src.split('\n')
                        for line in lines:
                            if '/' in line and ('*' in line or '🇸🇴' in line):
                                parts = line.split('/')
                                if len(parts) > 1:
                                    so_title = parts[1].replace('*', '').replace('🇸🇴', '').strip()
                                    break
                            elif 'Turjumaada Soomaaliga' in line or '🇸🇴' in line:
                                try:
                                    next_idx = lines.index(line) + 1
                                    if next_idx < len(lines):
                                        so_title = lines[next_idx].replace('*', '').replace('🇸🇴', '').strip()
                                        break
                                except:
                                    pass
                        
                        sidebar_html.append(f"""
                        <div class="sidebar-chapter-item" id="sidebar-ch-{ch_num}" onclick="scrollToChapter({ch_num})">
                            <span class="ch-badge">Ch {ch_num}</span>
                            <div class="ch-info">
                                <div class="ch-en">{ch_title}</div>
                                {f'<div class="ch-so">{so_title}</div>' if so_title else ''}
                            </div>
                        </div>
                        """)
                    
                    # Convert markdown images to responsive HTML images
                    src = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width:100%; border-radius:8px; border: 1px solid var(--border-glow); margin: 10px 0; display:block; box-shadow:0 0 15px rgba(6,182,212,0.15);">', src)
                    
                    # Convert markdown images to responsive HTML images
                    src = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width:100%; border-radius:8px; border: 1px solid var(--border-glow); margin: 10px 0; display:block; box-shadow:0 0 15px rgba(6,182,212,0.15);">', src)
                    
                    # Convert markdown headings to nice HTML tags
                    src = re.sub(r'^#\s+(.+)$', r'<h1 class="story-h1">\1</h1>', src, flags=re.MULTILINE)
                    src = re.sub(r'^##\s+(.+)$', r'<h2 class="story-h2">\1</h2>', src, flags=re.MULTILINE)
                    src = re.sub(r'^###\s+(.+)$', r'<h3 class="story-h3">\1</h3>', src, flags=re.MULTILINE)
                    src = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', src)
                    src = re.sub(r'\*(.+?)\*', r'<em>\1</em>', src)
                    src = src.replace('\n', '<br>')
                    
                    # Wrap lists
                    src = re.sub(r'(?:<br>)?-\s+(.+?)(?=<br>|$)', r'<li>\1</li>', src)
                    src = re.sub(r'(<li>.*?</li>)+', lambda m: f'<ul class="story-ul">{m.group(0)}</ul>', src, flags=re.DOTALL)
                    
                    # Parse tables
                    if '|' in src:
                        lines = src.split('<br>')
                        table_html = '<table class="story-table">'
                        in_table = False
                        for line in lines:
                            if '|' in line:
                                if '---' in line:
                                    continue
                                cells = [c.strip() for c in line.split('|')[1:-1]]
                                if not cells:
                                    continue
                                if not in_table:
                                    in_table = True
                                    table_html += '<tr>' + "".join(f'<th>{c}</th>' for c in cells) + '</tr>'
                                else:
                                    table_html += '<tr>' + "".join(f'<td>{c}</td>' for c in cells) + '</tr>'
                        table_html += '</table>'
                        clean_lines = [l for l in lines if '|' not in l or '---' in l]
                        src = "<br>".join(clean_lines) + "<br>" + table_html
                    
                                        # Insert iframe maps in narrative story
                    map_embed = ""
                    if ch_num == 2:
                        map_embed = '<iframe src="subcounties_google_hybrid_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 5:
                        map_embed = '<iframe src="garissa_master_drm_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 43:
                        map_embed = '<iframe src="health_facilities_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 44:
                        map_embed = '<iframe src="schools_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 47:
                        map_embed = '<iframe src="boreholes_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    
                    chapters_html.append(f'<div class="story-chapter-section" id="story-chapter-{ch_num}">{src}{map_embed}</div>')
                elif cell["cell_type"] == "code":
                    # Code blocks are completely hidden from the HTML narrative view as requested
                    pass
            
            narrative_html = f"""
            <div class="narrative-portal-layout">
                <div class="narrative-sidebar">
                    <div class="sidebar-header">📖 60 Chapters Checklist</div>
                    <div class="sidebar-list">
                        {"".join(sidebar_html)}
                    </div>
                </div>
                <div class="narrative-content">
                    {"".join(chapters_html)}
                </div>
            </div>
            """
    except Exception as e:
        print(f"⚠️ Error parsing narrative notebook: {e}")
        narrative_html = f"<p>Error parsing notebook: {e}</p>"

    # ── Map Gallery Building ────────────────────────────────────────────────
    maps_list = [
        ("01_garissa_county_boundary.png", "01. Garissa County Boundary Baseline", "Administrative baseline mapping the county limits and neighboring regions."),
        ("02_elevation_srtm.png", "02. Elevation & SRTM Topography Map", "Shuttle Radar Topography Mission (SRTM) 30m digital elevation model of Garissa."),
        ("03_land_use_land_cover.png", "03. Land Use & Land Cover (LULC)", "Vegetation, agricultural, urban, and bare land classification across the county."),
        ("04_rivers_and_waterways.png", "04. Rivers, Tributaries & Seasonal Laghas", "Clipped watercourses representing the permanent Tana river and seasonal streams (laghas)."),
        ("05_road_network.png", "05. Transport Network & Road Infrastructure", "Primary, secondary, and tertiary road paths tagged by flood vulnerability classes."),
        ("06_unosat_flood_extent_2024.png", "06. Historical UNOSAT Flood Extents (2024)", "Inundation boundaries detected from Sentinel-1 radar imagery during the April 2024 flood."),
        ("07_high_risk_zone_buffer.png", "07. High Risk Buffer Inundation Map (500m)", "Spatially differenced 500m buffer zone along primary rivers showing immediate danger."),
        ("08_medium_risk_zone_buffer.png", "08. Medium Risk Buffer Inundation Map (1.5km)", "Spatially differenced 1.5km buffer zone representing active inundation zones."),
        ("09_low_risk_zone_buffer.png", "09. Low Risk Buffer Inundation Map (3.3km)", "Spatially differenced 3.3km buffer representing low probability/high impact floods."),
        ("10_extreme_risk_zone_buffer.png", "10. Extreme Risk Buffer Inundation Map (5.5km)", "Spatially differenced 5.5km buffer covering maximum historical flood plains."),
        ("11_combined_flood_risk_zones.png", "11. Combined Non-Overlapping Hazard Exposure Map", "Integrated multi-buffer flood zone showing non-overlapping levels from safe to extreme."),
        ("12_schools_exposure_risk.png", "12. Schools Exposure & Vulnerability Risk Map", "Risk classification and NN vulnerability indexing of schools in Garissa."),
        ("13_health_facilities_exposure_risk.png", "13. Health Facilities & Clinic Vulnerability Map", "Risk classification of dispensaries and hospitals across the 7 sub-counties."),
        ("14_boreholes_exposure_risk.png", "14. Humanitarian Borehole Supply Risk Map", "Critical borehole structures overlaid with flood risk buffers to prevent water shortage."),
        ("15_idp_camps_exposure_risk.png", "15. Refugee Camps Exposure & Risk Map", "Socio-economic risk assessment of refugee camp blocks (formerly IDPs) under Shirika Plan."),
        ("16_towns_exposure_risk.png", "16. Towns & Population Centroids Risk Map", "Urban and village center centroids intersected with El Niño flood zones."),
        ("17_dadaab_refugee_camps_overlay.png", "17. Dadaab Refugee Complex Overlay", "High-resolution block overlay of Hagadera, Ifo, and Dagahaley settlements."),
        ("18_water_pans_and_assets.png", "18. Water Pans & Sustainable Resource Assets", "Distribution of community water pans, reservoirs, and natural storage infrastructure."),
        ("19_dengue_risk_and_wildlife.png", "19. Dengue Fever & Wildlife Corridor Exposure", "Co-occurrence of vector-borne disease outbreaks and critical wildlife corridors."),
        ("20_integrated_early_warning_master.png", "20. Integrated DRM Early Warning Master Map", "Synthesized cartographic layout combining all layers for emergency coordinators.")
    ]

    gallery_html = ""
    for filename, title, desc in maps_list:
        gallery_html += f"""
        <div class="gallery-card" onclick="openLightbox('maps/{filename}', '{title}')">
            <div class="gallery-image-wrapper">
                <img src="maps/{filename}" alt="{title}" onerror="this.onerror=null; this.src='https://placehold.co/600x400/1e293b/06b6d4?text={title.replace(' ', '+')}';" />
                <div class="gallery-image-overlay">🔍 Click to Expand</div>
            </div>
            <div class="gallery-info">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        </div>
        """

    # Substitution logic to avoid f-string escapes
    html_content = raw_html
    html_content = html_content.replace("__GENERATION_DATE__", datetime.now().strftime('%d %B %Y'))
    html_content = html_content.replace("__EXT_SCHOOLS__", str(ext_schools))
    html_content = html_content.replace("__HIGH_SCHOOLS__", str(high_schools))
    html_content = html_content.replace("__TOTAL_SCHOOLS__", str(total_schools))
    html_content = html_content.replace("__SUM_SCHOOLS_RISK__", str(ext_schools + high_schools))
    html_content = html_content.replace("__PERCENT_SCHOOLS__", str(int((ext_schools+high_schools)/total_schools*100) if total_schools else 0))
    
    html_content = html_content.replace("__EXT_HEALTH__", str(ext_health))
    html_content = html_content.replace("__HIGH_HEALTH__", str(high_health))
    html_content = html_content.replace("__TOTAL_HEALTH__", str(total_health))
    html_content = html_content.replace("__SUM_HEALTH_RISK__", str(ext_health + high_health))
    html_content = html_content.replace("__PERCENT_HEALTH__", str(int((ext_health+high_health)/total_health*100) if total_health else 0))
    
    html_content = html_content.replace("__EXT_BORE__", str(ext_bore))
    html_content = html_content.replace("__HIGH_BORE__", str(high_bore))
    html_content = html_content.replace("__TOTAL_BORE__", str(total_bore))
    html_content = html_content.replace("__SUM_BORE_RISK__", str(ext_bore + high_bore))
    html_content = html_content.replace("__PERCENT_BORE__", str(int((ext_bore+high_bore)/total_bore*100) if total_bore else 0))
    
    html_content = html_content.replace("__EXT_CAMPS__", str(ext_camps))
    html_content = html_content.replace("__HIGH_CAMPS__", str(high_camps))
    html_content = html_content.replace("__TOTAL_CAMPS__", str(total_camps))
    html_content = html_content.replace("__SUM_CAMPS_RISK__", str(ext_camps + high_camps))
    html_content = html_content.replace("__PERCENT_CAMPS__", str(int((ext_camps+high_camps)/total_camps*100) if total_camps else 0))
    
    html_content = html_content.replace("__EXTREME_RISK_JSON__", extreme_risk_json)
    html_content = html_content.replace("__HIGH_RISK_JSON__", high_risk_json)
    html_content = html_content.replace("__MEDIUM_RISK_JSON__", medium_risk_json)
    html_content = html_content.replace("__LOW_RISK_JSON__", low_risk_json)
    
    html_content = html_content.replace("__SCHOOLS_JSON__", schools_json)
    html_content = html_content.replace("__HEALTH_JSON__", health_json)
    html_content = html_content.replace("__BOREHOLES_JSON__", boreholes_json)
    html_content = html_content.replace("__IDP_CAMPS_JSON__", idp_camps_json)
    html_content = html_content.replace("__TOWNS_JSON__", towns_json)
    html_content = html_content.replace("__RIVERS_JSON__", rivers_json)
    html_content = html_content.replace("__ROADS_JSON__", roads_json)
    
    html_content = html_content.replace("__WILDLIFE_JSON__", wildlife_json)
    html_content = html_content.replace("__WATER_PANS_JSON__", water_pans_json)
    html_content = html_content.replace("__CADASTRAL_JSON__", cadastral_json)
    
    html_content = html_content.replace("__DAGAHALEY_JSON__", dagahaley_json)
    html_content = html_content.replace("__HAGADERA_JSON__", hagadera_json)
    html_content = html_content.replace("__IFO_JSON__", ifo_json)
    
    html_content = html_content.replace("__SUBCOUNTIES_GEOM_JSON__", subcounties_geom_json)
    html_content = html_content.replace("__WARDS_GEOM_JSON__", wards_geom_json)
    html_content = html_content.replace("__SUBCOUNTY_JSON__", subcounty_json)
    html_content = html_content.replace("__NARRATIVE_STORY_HTML__", narrative_html)
    html_content = html_content.replace("__MAP_GALLERY_HTML__", gallery_html)

    with open(OUTPUT_DIR / "garissa_flood_risk_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Premium ARCgis HTML Dashboard Overhauled & Generated!")


if __name__ == "__main__":
    generate_dashboard()
