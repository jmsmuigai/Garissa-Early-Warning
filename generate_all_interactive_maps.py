#!/usr/bin/env python3
"""
Automated Interactive HTML Map Generator for Garissa Early Warning Portal.
Generates 7 advanced interactive HTML maps featuring:
1. Google Hybrid satellite default with base switchers (Google Streets, Dark Matter).
2. Collapsible layers selection tree with ALL available layers toggleable.
3. Rotating compass, scales, fullscreen, and GeoJSON downloads.
4. Rich HTML popups with neural-network risk disclosures.
5. Bidirectional iframe-to-parent message communication.
6. 3D Holographic Perspective View with tilt/rotation controls and neon scanning grid.
7. Split Cyber Console with searchable asset lists, precipitation gauge, and water level charts.
8. Interactive Buffer Risk Query Tool.

Author: Garissa GIS Directorate — James M. Mburu
"""
import json
import os
import geopandas as gpd
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

# Risk color configurations
RISK_COLORS = {
    'Extreme Risk (Super El Niño)': '#bd00ff',
    'High Risk': '#ef4444',
    'Medium Risk': '#f97316',
    'Low Risk': '#fbbf24',
    'Safe': '#10b981'
}

def load_geojson_safe(path):
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    try:
        # Avoid size provider read locks
        stat = path.stat()
        if stat.st_size > 10 * 1024 * 1024 and (stat.st_blocks * 512) < (stat.st_size * 0.3):
            return {"type": "FeatureCollection", "features": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading GeoJSON {path.name}: {e}")
        return {"type": "FeatureCollection", "features": []}

def get_leaflet_template(title, caption, download_filename, default_layers_json, map_download_var):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Leaflet & Fonts -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <style>
        :root {{
            --bg-glass: rgba(10, 15, 30, 0.9);
            --border-glow: rgba(0, 243, 255, 0.4);
            --border-pink: rgba(255, 0, 127, 0.4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --cyan: #00f3ff;
            --pink: #ff007f;
            --lime: #39ff14;
            --purple: #bd00ff;
            --yellow: #fbbf24;
            --orange: #f97316;
            --red: #ef4444;
        }}

        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: 'Inter', sans-serif;
            background-color: #02040a;
            color: var(--text-main);
            overflow: hidden;
        }}

        #app-container {{
            display: flex;
            width: 100%;
            height: 100%;
            position: relative;
        }}

        #map-wrapper {{
            flex: 1;
            height: 100%;
            position: relative;
            transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            perspective: 1500px;
        }}

        #map {{
            height: 100%;
            width: 100%;
            z-index: 1;
            transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.6s ease;
        }}

        /* 3D TACTICAL VIEW CLASS */
        .map-3d {{
            transform: rotateX(var(--tilt, 50deg)) rotateZ(var(--rotate, -10deg)) scale(1.02);
            box-shadow: 0 50px 100px rgba(0,0,0,0.9), 0 0 50px rgba(0, 243, 255, 0.25);
            border: 2px solid var(--cyan) !important;
            border-radius: 16px;
        }}

        .map-3d-active-banner {{
            position: absolute;
            top: 85px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 0, 127, 0.25);
            border: 1px solid var(--pink);
            color: var(--pink);
            padding: 4px 15px;
            border-radius: 20px;
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            z-index: 1000;
            pointer-events: none;
            display: none;
            box-shadow: 0 0 15px rgba(255, 0, 127, 0.3);
            animation: pulse-glow-text 1.5s infinite alternate;
        }}

        @keyframes pulse-glow-text {{
            0% {{ opacity: 0.6; box-shadow: 0 0 5px rgba(255, 0, 127, 0.2); }}
            100% {{ opacity: 1; box-shadow: 0 0 15px rgba(255, 0, 127, 0.5); }}
        }}

        /* SCANLINE EFFECTS */
        .scanlines {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 243, 255, 0.05) 50%);
            background-size: 100% 4px;
            z-index: 999;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.5s ease;
        }}

        .scanlines.active {{
            opacity: 1;
        }}

        /* RADAR SWEEP EFFECT */
        .radar-sweep {{
            position: absolute;
            top: 50%; left: 50%;
            width: 160vmax; height: 160vmax;
            margin-left: -80vmax; margin-top: -80vmax;
            background: conic-gradient(from 0deg, rgba(0, 243, 255, 0.12) 0deg, rgba(0, 243, 255, 0) 120deg, rgba(0, 243, 255, 0) 360deg);
            border-radius: 50%;
            z-index: 2;
            pointer-events: none;
            animation: radar-sweep-anim 10s linear infinite;
            display: none;
        }}

        @keyframes radar-sweep-anim {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* GLASS PANELS */
        .glass-panel {{
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 12px 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            z-index: 1000;
            pointer-events: auto;
        }}

        .map-header {{
            position: absolute;
            top: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 750px;
            text-align: center;
            border-left: 4px solid var(--cyan);
            border-right: 4px solid var(--pink);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
        }}

        .map-header h1 {{
            font-family: 'Orbitron', sans-serif;
            font-size: 18px;
            margin: 0 0 4px 0;
            letter-spacing: 1.5px;
            background: linear-gradient(to right, #ffffff, var(--cyan), var(--pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 950;
            text-shadow: 0 0 10px rgba(0,243,255,0.2);
        }}

        .map-caption {{
            font-size: 10px;
            color: var(--text-muted);
            margin: 0;
            line-height: 1.3;
            font-weight: 600;
            font-family: 'Share Tech Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .system-online-badge {{
            position: absolute;
            top: 15px;
            left: 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(10, 15, 30, 0.85);
            border: 1px solid var(--lime);
            border-radius: 20px;
            padding: 4px 10px;
            font-family: 'Orbitron', sans-serif;
            font-size: 9px;
            font-weight: bold;
            color: var(--lime);
            box-shadow: 0 0 10px rgba(57, 255, 20, 0.2);
        }}

        .blink-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--lime);
            animation: pulse-dot 1.2s infinite alternate;
        }}

        @keyframes pulse-dot {{
            0% {{ opacity: 0.3; }}
            100% {{ opacity: 1; }}
        }}

        /* VIEW SWITCHER FLOATING PANEL */
        .view-switcher-panel {{
            position: absolute;
            top: 15px;
            right: 20px;
            z-index: 1000;
            display: flex;
            gap: 5px;
            background: rgba(10, 15, 30, 0.85);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-glow);
        }}

        .view-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-family: 'Orbitron', sans-serif;
            font-size: 9px;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 0.8px;
        }}

        .view-btn:hover {{
            color: white;
            background: rgba(255, 255, 255, 0.05);
        }}

        .view-btn.active {{
            background: var(--cyan);
            color: #02040a;
            box-shadow: 0 0 10px var(--cyan);
        }}

        /* 3D TILT CONTROLS */
        .tilt-controls-panel {{
            position: absolute;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: none;
            flex-direction: row;
            gap: 20px;
            width: 90%;
            max-width: 450px;
            align-items: center;
            background: rgba(10, 15, 30, 0.9);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 10px 20px;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
        }}

        .slider-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
            font-family: 'Share Tech Mono', monospace;
            font-size: 10px;
            color: var(--cyan);
        }}

        .slider-group label {{
            white-space: nowrap;
        }}

        .slider-group input[type="range"] {{
            width: 100%;
            background: #1e293b;
            height: 4px;
            border-radius: 2px;
            outline: none;
            -webkit-appearance: none;
        }}

        .slider-group input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--pink);
            cursor: pointer;
            box-shadow: 0 0 6px var(--pink);
        }}

        /* ROTATING COMPASS */
        .compass-overlay {{
            position: absolute;
            bottom: 25px;
            right: 25px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1000;
            border: 1px solid var(--border-glow);
            background: rgba(10, 15, 30, 0.8);
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
        }}

        .compass-needle {{
            width: 5px;
            height: 38px;
            background: linear-gradient(to bottom, var(--pink) 50%, var(--text-muted) 50%);
            clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
            transform: rotate(0deg);
            transition: transform 0.2s ease-out;
        }}

        .compass-label {{
            position: absolute;
            top: 2px;
            font-family: 'Orbitron', sans-serif;
            font-size: 8px;
            font-weight: 900;
            color: var(--pink);
            text-shadow: 0 0 5px var(--pink);
        }}

        /* COORD TELEMETRY DISPLAY */
        .coord-overlay {{
            position: absolute;
            bottom: 25px;
            left: 25px;
            z-index: 1000;
            font-family: 'Share Tech Mono', monospace;
            font-size: 11px;
            color: var(--cyan);
            background: rgba(10, 15, 30, 0.85);
            border: 1px solid var(--border-glow);
            padding: 4px 10px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
            letter-spacing: 0.8px;
        }}

        /* MAP UTILITIES PANEL */
        .map-controls {{
            position: absolute;
            bottom: 100px;
            right: 25px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 1000;
        }}

        .control-btn {{
            background: rgba(10, 15, 30, 0.9);
            border: 1px solid var(--border-glow);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 10px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            letter-spacing: 0.5px;
        }}

        .control-btn:hover {{
            background: var(--cyan);
            color: #02040a;
            box-shadow: 0 0 12px var(--cyan);
            border-color: var(--cyan);
        }}

        .control-btn.pink-btn {{
            border-color: var(--pink);
            color: var(--pink);
        }}

        .control-btn.pink-btn:hover {{
            background: var(--pink);
            color: #02040a;
            box-shadow: 0 0 12px var(--pink);
        }}

        /* BUFFER PANEL */
        .buffer-config-card {{
            position: absolute;
            bottom: 100px;
            left: 25px;
            z-index: 1000;
            display: none;
            flex-direction: column;
            width: 250px;
            background: rgba(10, 15, 30, 0.95);
            border: 1px solid var(--pink);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.25);
        }}

        .buffer-config-card h4 {{
            margin: 0 0 10px 0;
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            color: var(--pink);
            border-bottom: 1px solid rgba(255,0,127,0.2);
            padding-bottom: 5px;
        }}

        .buffer-config-card select {{
            background: #090f1e;
            border: 1px solid var(--border-glow);
            color: white;
            padding: 5px;
            border-radius: 4px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 11px;
            margin-bottom: 10px;
            outline: none;
        }}

        /* CYBER DATA DRAWER PANEL (SPLIT CONSOLE) */
        #cyber-panel {{
            width: 360px;
            height: 100%;
            background: rgba(5, 10, 20, 0.95);
            border-left: 2px solid var(--border-glow);
            display: none;
            flex-direction: column;
            padding: 20px;
            box-sizing: border-box;
            z-index: 1000;
            overflow-y: auto;
            box-shadow: -10px 0 30px rgba(0,0,0,0.8);
        }}

        .drawer-section-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            font-weight: 900;
            color: var(--pink);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(255, 0, 127, 0.2);
            padding-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .cyber-alert-banner {{
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.15), rgba(10, 15, 30, 0));
            border-left: 3px solid var(--red);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 15px;
            line-height: 1.4;
            color: #fca5a5;
        }}

        /* SVG GAUGE CHART */
        .gauge-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.02);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.03);
        }}

        .gauge-val {{
            font-family: 'Share Tech Mono', monospace;
            font-size: 18px;
            font-weight: bold;
            color: var(--cyan);
        }}

        /* SEARCHABLE ASSETS LIST */
        .search-container {{
            margin-bottom: 15px;
        }}

        .search-container input {{
            width: 100%;
            background: #090f1e;
            border: 1px solid var(--border-glow);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 12px;
            outline: none;
            box-sizing: border-box;
            transition: all 0.2s ease;
        }}

        .search-container input:focus {{
            border-color: var(--pink);
            box-shadow: 0 0 8px rgba(255, 0, 127, 0.3);
        }}

        .assets-list {{
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding-right: 5px;
            max-height: 220px;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
            padding: 8px;
        }}

        .asset-list-item {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255,255,255,0.02);
            border-radius: 6px;
            padding: 8px 10px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            transition: all 0.2s ease;
        }}

        .asset-list-item:hover {{
            background: rgba(0, 243, 255, 0.08);
            border-color: var(--cyan);
            transform: translateX(3px);
        }}

        .asset-name {{
            font-weight: bold;
            color: var(--text-main);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 180px;
        }}

        .asset-type {{
            font-family: 'Share Tech Mono', monospace;
            font-size: 9px;
            color: var(--text-muted);
            background: rgba(255,255,255,0.05);
            padding: 2px 5px;
            border-radius: 3px;
        }}

        .asset-risk {{
            font-weight: bold;
            font-size: 9px;
        }}

        /* ADVANCED POPUPS & LEAFLET CUSTOMS */
        .leaflet-popup-content-wrapper {{
            background: var(--bg-glass) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid var(--border-glow) !important;
            color: var(--text-main) !important;
            border-radius: 10px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
            padding: 4px !important;
        }}

        .leaflet-popup-tip {{
            background: var(--bg-glass) !important;
            border-left: 1px solid var(--border-glow) !important;
            border-bottom: 1px solid var(--border-glow) !important;
        }}

        .popup-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 6px;
            border-bottom: 1px solid var(--border-pink);
            padding-bottom: 5px;
            color: var(--pink);
            display: flex;
            align-items: center;
            gap: 6px;
            text-shadow: 0 0 5px rgba(255,0,127,0.2);
        }}

        .popup-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
        }}

        .popup-table td {{
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        .popup-table td.label {{
            color: var(--text-muted);
            font-weight: bold;
        }}

        .popup-table td.val {{
            text-align: right;
            font-family: 'Share Tech Mono', monospace;
            font-weight: bold;
        }}

        .custom-tooltip {{
            background: rgba(10, 15, 30, 0.95) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            border-radius: 4px !important;
            padding: 3px 7px !important;
            font-size: 10px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.5) !important;
        }}

        .leaflet-control-layers {{
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            border-radius: 8px !important;
            font-size: 9px !important;
            font-weight: bold !important;
            font-family: 'Share Tech Mono', monospace !important;
        }}

        .leaflet-control-layers-group-name {{
            color: var(--pink) !important;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 8px;
            margin-top: 5px;
            display: block;
            border-bottom: 1px solid rgba(255,0,127,0.2);
            padding-bottom: 2px;
        }}

        /* NEON PULSING MARKERS CSS */
        @keyframes pulse-ring {{
            0% {{ transform: scale(0.6); opacity: 0.8; }}
            100% {{ transform: scale(2.2); opacity: 0; }}
        }}

        .pulsing-ring {{
            position: absolute;
            width: 32px;
            height: 32px;
            border: 2px solid var(--pulse-color);
            border-radius: 50%;
            animation: pulse-ring 2.2s infinite ease-out;
            pointer-events: none;
            top: -5px;
            left: -5px;
            box-shadow: 0 0 8px var(--pulse-color);
        }}

        /* SCROLLBAR CUSTOMS */
        ::-webkit-scrollbar {{
            width: 5px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--cyan);
        }}
    </style>
</head>
<body>

    <div id="app-container">
        
        <!-- MAIN LEAFLET MAP WRAPPER -->
        <div id="map-wrapper">
            <div id="map"></div>
            <div class="radar-sweep" id="radar-scanner"></div>
            <div class="scanlines" id="grid-scan"></div>
            
            <!-- BLINKING STATUS BADGE -->
            <div class="system-online-badge">
                <div class="blink-dot"></div>
                <span>● GEWAS PORTAL SYSTEM ACTIVE</span>
            </div>

            <!-- TACTICAL 3D BANNER -->
            <div class="map-3d-active-banner" id="banner-3d">
                📡 TACTICAL HUD: HOLOGRAPHIC 3D SCAN ACTIVE // READ-ONLY MODE
            </div>

            <!-- HEADER BANNER -->
            <div class="glass-panel map-header">
                <h1>{title}</h1>
                <p class="map-caption">{caption}</p>
            </div>

            <!-- VIEW SWITCHER OVERLAY -->
            <div class="view-switcher-panel">
                <button class="view-btn active" id="btn-view-2d" onclick="switchView('2d')">2D Flat</button>
                <button class="view-btn" id="btn-view-3d" onclick="switchView('3d')">3D Tactical</button>
                <button class="view-btn" id="btn-view-split" onclick="switchView('split')">Split Console</button>
            </div>

            <!-- rotating COMPASS -->
            <div class="compass-overlay" onclick="resetBearing()">
                <span class="compass-label">N</span>
                <div class="compass-needle" id="compass-needle"></div>
            </div>

            <!-- COORDINATE TELEMETRY DISPLAY -->
            <div class="coord-overlay" id="coord-display">LAT: -0.45000 | LNG: 39.65000</div>

            <!-- MAP UTILITIES -->
            <div class="map-controls">
                <button class="control-btn" id="btn-fullscreen" onclick="toggleFullscreen()">
                    🖥️ Fullscreen
                </button>
                <button class="control-btn pink-btn" id="btn-buffer-tool" onclick="toggleBufferTool()">
                    ⭕ Buffer Tool [OFF]
                </button>
                <button class="control-btn" onclick="downloadActiveLayer()">
                    💾 Export Vector
                </button>
            </div>

            <!-- 3D ROTATE CONTROLS PANEL -->
            <div class="tilt-controls-panel" id="tilt-panel">
                <div class="slider-group">
                    <label for="slider-tilt">3D Tilt: <span id="val-tilt">50</span>°</label>
                    <input type="range" id="slider-tilt" min="15" max="75" value="50" oninput="adjust3DTransforms()">
                </div>
                <div class="slider-group">
                    <label for="slider-rotate">Rotate: <span id="val-rotate">-10</span>°</label>
                    <input type="range" id="slider-rotate" min="-180" max="180" value="-10" oninput="adjust3DTransforms()">
                </div>
            </div>

            <!-- BUFFER CONFIG CARD -->
            <div class="buffer-config-card" id="buffer-card">
                <h4>⭕ Radial Buffer Analysis</h4>
                <div style="font-size:10px; color:var(--text-muted); margin-bottom:8px; line-height:1.3;">
                    Click anywhere on the map to calculate flood risk buffers and identify exposed facilities.
                </div>
                <label style="font-size:10px; font-weight:bold; color:var(--cyan); margin-bottom:3px;">Select Buffer Radius:</label>
                <select id="buffer-radius" onchange="recalculateBuffer()">
                    <option value="1.5">1.5 Kilometers</option>
                    <option value="3.0">3.0 Kilometers</option>
                    <option value="5.0">5.0 Kilometers</option>
                </select>
                <div id="buffer-results" style="border-top: 1px solid rgba(255,255,255,0.05); padding-top:8px; margin-top:5px;">
                    <div style="font-size: 10px; color:var(--text-muted); text-align:center;">Click map to start...</div>
                </div>
            </div>

        </div>

        <!-- RIGHT DATA PANEL DRAWER -->
        <div id="cyber-panel">
            <div class="drawer-section-title">
                <span>📡 HUD Telemetry Console</span>
                <span style="color:var(--cyan); font-family:'Share Tech Mono';">ONLINE</span>
            </div>

            <div class="cyber-alert-banner">
                <strong>⚠️ EL NIÑO PREPAREDNESS ACTIVE</strong><br>
                Rangeland water pans and schools along the Tana floodplains are monitored for trigger values exceeding 150mm.
            </div>

            <!-- METRIC DIALS -->
            <div class="drawer-section-title">💧 Live Rainfall & Water level Gauges</div>
            <div class="gauge-container">
                <div style="text-align: center;">
                    <svg viewBox="0 0 100 60" width="80" height="50">
                        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#1e293b" stroke-width="8" />
                        <path d="M 10 50 A 40 40 0 0 1 70 20" fill="none" stroke="var(--cyan)" stroke-width="8" stroke-dasharray="80" />
                        <text x="50" y="45" fill="white" font-size="10" font-family="Orbitron" text-anchor="middle">168mm</text>
                    </svg>
                    <div class="gauge-val">168 mm</div>
                    <div style="font-size: 8px; color: var(--text-muted); text-transform: uppercase;">Rain Forecast</div>
                </div>
                <div style="text-align: center;">
                    <svg viewBox="0 0 100 60" width="80" height="50">
                        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#1e293b" stroke-width="8" />
                        <path d="M 10 50 A 40 40 0 0 1 85 35" fill="none" stroke="var(--pink)" stroke-width="8" />
                        <text x="50" y="45" fill="white" font-size="10" font-family="Orbitron" text-anchor="middle">5.82m</text>
                    </svg>
                    <div class="gauge-val" style="color: var(--pink);">5.82 m</div>
                    <div style="font-size: 8px; color: var(--text-muted); text-transform: uppercase;">River Level</div>
                </div>
            </div>

            <!-- ASSETS TELEMETRY BLOCK -->
            <div class="drawer-section-title">📱 Selected Asset Diagnostics</div>
            <div id="side-telemetry-body" style="font-size: 11px; color: var(--text-muted); line-height: 1.5; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.03); min-height:85px; margin-bottom:15px;">
                No asset selected. Click on a marker in the viewport or search below to stream vulnerability neural network indicators.
            </div>

            <!-- SEARCHABLE LIST -->
            <div class="drawer-section-title">🔍 Search Critical Assets</div>
            <div class="search-container">
                <input type="text" id="asset-search" placeholder="Type school, clinic, or borehole name..." onkeyup="filterAssetsList()">
            </div>
            <div class="assets-list" id="assets-list-container">
                <!-- Filled dynamically -->
            </div>
        </div>

    </div>

    <script>
        // Data variables placeholders, fetched dynamically on window load
        let schoolsData = {{ "type": "FeatureCollection", "features": [] }};
        let healthData = {{ "type": "FeatureCollection", "features": [] }};
        let boreholesData = {{ "type": "FeatureCollection", "features": [] }};
        let campsData = {{ "type": "FeatureCollection", "features": [] }};
        let townsData = {{ "type": "FeatureCollection", "features": [] }};
        let waterPansData = {{ "type": "FeatureCollection", "features": [] }};
        let wildlifeData = {{ "type": "FeatureCollection", "features": [] }};
        let roadsData = {{ "type": "FeatureCollection", "features": [] }};
        let riversData = {{ "type": "FeatureCollection", "features": [] }};
        let subcountiesData = {{ "type": "FeatureCollection", "features": [] }};
        let wardsData = {{ "type": "FeatureCollection", "features": [] }};
        let extremeZoneData = {{ "type": "FeatureCollection", "features": [] }};
        let medZoneData = {{ "type": "FeatureCollection", "features": [] }};
        let highZoneData = {{ "type": "FeatureCollection", "features": [] }};
        let lowZoneData = {{ "type": "FeatureCollection", "features": [] }};
        let baselineFloodData = {{ "type": "FeatureCollection", "features": [] }};

        // Initialize Map
        const map = L.map('map', {{
            center: [-0.45, 39.65],
            zoom: 9,
            zoomControl: true,
            minZoom: 7,
            maxZoom: 16
        }});

        // Basemaps (Google Hybrid Satellite default)
        const hybridBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Imagery &copy; Google Hybrid'
        }}).addTo(map);

        const streetsBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Map &copy; Google Streets'
        }});

        const darkBasemap = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CARTO dark_matter'
        }});

        const baseMaps = {{
            "Google Hybrid (Satellite)": hybridBasemap,
            "Google Streets": streetsBasemap,
            "CartoDB Dark Matter": darkBasemap
        }};

        // Master overlays controls dictionary
        const overlays = {{}};

        // Color palettes
        const riskColors = {{
            'Extreme Risk (Super El Niño)': '#bd00ff',
            'High Risk': '#ef4444',
            'Medium Risk': '#f97316',
            'Low Risk': '#fbbf24',
            'Safe': '#10b981'
        }};

        // Custom Div Icons with Pulsing Rings
        function getCyberIcon(color, char) {{
            return L.divIcon({{
                className: 'custom-cyber-icon',
                html: `
                    <div style="position: relative; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center;">
                        <div class="pulsing-ring" style="--pulse-color: ${{color}};"></div>
                        <svg viewBox="0 0 30 30" width="22" height="22" style="z-index: 10;">
                            <polygon points="15,2 28,9 28,23 15,30 2,23 2,9" fill="${{color}}" stroke="#000" stroke-width="1.5"/>
                            <text x="15" y="19" fill="#ffffff" font-size="10" font-family="'Orbitron', sans-serif" font-weight="900" text-anchor="middle">${{char}}</text>
                        </svg>
                    </div>
                `,
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            }});
        }}

        // Helper to build futuristic popup table
        function buildPopupTable(name, code, status, risk, dist, vulnerability, icon) {{
            let riskColor = riskColors[risk] || '#9ca3af';
            let statusColor = status.includes('FUNCTIONAL') || status.includes('ACTIVE') ? '#39ff14' : '#f97316';
            return `
                <div class="popup-title">${{icon}} ${{name}}</div>
                <table class="popup-table">
                    <tr><td class="label">CODE ID</td><td class="val" style="color:var(--cyan);">${{code}}</td></tr>
                    <tr><td class="label">STATUS</td><td class="val" style="color:${{statusColor}};">${{status}}</td></tr>
                    <tr><td class="label">FLOOD RISK</td><td class="val" style="color:${{riskColor}};">${{risk}}</td></tr>
                    <tr><td class="label">DISTANCE</td><td class="val">${{dist}} km</td></tr>
                    <tr><td class="label">VULNERABILITY NN</td><td class="val" style="color:var(--cyan);">${{vulnerability}}</td></tr>
                </table>
            `;
        }}

        // Send Click events to Parent frame (postMessage)
        function notifyParent(feature, layerName) {{
            const p = feature.properties;
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'marker_click',
                    layer: layerName,
                    properties: p
                }}, '*');
            }}
            
            // Populate our own cyber drawer if visible
            let riskCol = riskColors[p.Risk_Level] || '#fff';
            let contents = `
                <div style="font-weight:bold; font-size:12px; color:var(--pink); margin-bottom:5px; font-family:'Orbitron';">
                    ${{p.school_nam || p.health_fac || p.name || 'Critical Asset'}}
                </div>
                <strong>Layer:</strong> ${{layerName}}<br>
                <strong>Sub-County:</strong> ${{p.sub_county || 'Garissa'}}<br>
                <strong>Risk:</strong> <span style="color:${{riskCol}}; font-weight:bold;">${{p.Risk_Level || 'Safe'}}</span><br>
                <strong>Distance to Flood:</strong> ${{p.Distance_to_Flood_km || '0.0'}} km<br>
                <strong>Vulnerability Score:</strong> ${{p.Vulnerability_Index || p.NN_Vulnerability_Score || '0.0'}}
            `;
            document.getElementById('side-telemetry-body').innerHTML = contents;
        }}

        // Initialize layers list
        function initAllLayers() {{
            // 1. Administrative boundaries
            if (typeof wardsData !== 'undefined' && wardsData.features && wardsData.features.length > 0) {{
                overlays["Wards Boundaries"] = L.geoJSON(wardsData, {{
                    style: {{ color: '#f59e0b', fillColor: 'transparent', weight: 1.0, dashArray: '3,3' }},
                    onEachFeature: function(f, l) {{
                        l.bindTooltip(f.properties.ward || 'Ward', {{ sticky: true, className: 'custom-tooltip' }});
                    }}
                }});
            }}

            if (typeof subcountiesData !== 'undefined' && subcountiesData.features && subcountiesData.features.length > 0) {{
                overlays["Sub-Counties Boundaries"] = L.geoJSON(subcountiesData, {{
                    style: {{ color: '#00f3ff', fillColor: 'transparent', weight: 1.8 }},
                    onEachFeature: function(f, l) {{
                        const name = f.properties.sub_county || 'Sub-County';
                        l.bindTooltip(name, {{ permanent: true, direction: 'center', className: 'custom-tooltip' }});
                    }}
                }});
            }}

            // 2. Hydrology & Flood lines
            if (typeof riversData !== 'undefined' && riversData.features && riversData.features.length > 0) {{
                overlays["Rivers & Drainage"] = L.geoJSON(riversData, {{
                    style: {{ color: '#00f3ff', weight: 1.5, opacity: 0.85 }},
                    onEachFeature: function(f, l) {{
                        l.bindTooltip("Rivers/Laghas Drainage", {{ sticky: true, className: 'custom-tooltip' }});
                    }}
                }});
            }}

            if (typeof baselineFloodData !== 'undefined' && baselineFloodData.features && baselineFloodData.features.length > 0) {{
                overlays["🌊 April 2024 Flood Baseline"] = L.geoJSON(baselineFloodData, {{
                    style: {{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.3, weight: 1.5 }}
                }});
            }}

            // 3. Risk zones
            if (typeof extremeZoneData !== 'undefined' && extremeZoneData.features && extremeZoneData.features.length > 0) {{
                overlays["🟣 Extreme Risk Zone (~5.5km)"] = L.geoJSON(extremeZoneData, {{
                    style: {{ color: '#bd00ff', fillColor: '#bd00ff', fillOpacity: 0.08, weight: 1 }}
                }});
            }}
            if (typeof lowZoneData !== 'undefined' && lowZoneData.features && lowZoneData.features.length > 0) {{
                overlays["🟡 Low Risk Zone (~3.3km)"] = L.geoJSON(lowZoneData, {{
                    style: {{ color: '#fef08a', fillColor: '#fef08a', fillOpacity: 0.06, weight: 0.8 }}
                }});
            }}
            if (typeof medZoneData !== 'undefined' && medZoneData.features && medZoneData.features.length > 0) {{
                overlays["🟠 Medium Risk Zone (~1.5km)"] = L.geoJSON(medZoneData, {{
                    style: {{ color: '#fed7aa', fillColor: '#fed7aa', fillOpacity: 0.1, weight: 0.8 }}
                }});
            }}
            if (typeof highZoneData !== 'undefined' && highZoneData.features && highZoneData.features.length > 0) {{
                overlays["🔴 High Risk Zone (~500m)"] = L.geoJSON(highZoneData, {{
                    style: {{ color: '#fca5a5', fillColor: '#fca5a5', fillOpacity: 0.15, weight: 1.0 }}
                }});
            }}

            // 4. Critical assets
            if (typeof schoolsData !== 'undefined' && schoolsData.features && schoolsData.features.length > 0) {{
                overlays["🏫 Schools (Styled)"] = L.geoJSON(schoolsData, {{
                    pointToLayer: function(f, latlng) {{
                        const risk = f.properties.Risk_Level || 'Safe';
                        return L.marker(latlng, {{ icon: getCyberIcon(riskColors[risk] || '#9ca3af', 'S') }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindPopup(buildPopupTable(f.properties.school_nam || 'School', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏫'));
                        l.on('click', () => notifyParent(f, 'Schools'));
                    }}
                }});
            }}

            if (typeof healthData !== 'undefined' && healthData.features && healthData.features.length > 0) {{
                overlays["🏥 Health Clinics (Styled)"] = L.geoJSON(healthData, {{
                    pointToLayer: function(f, latlng) {{
                        const risk = f.properties.Risk_Level || 'Safe';
                        return L.marker(latlng, {{ icon: getCyberIcon(riskColors[risk] || '#9ca3af', 'H') }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindPopup(buildPopupTable(f.properties.health_fac || 'Clinic', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏥'));
                        l.on('click', () => notifyParent(f, 'Health Facilities'));
                    }}
                }});
            }}

            if (typeof boreholesData !== 'undefined' && boreholesData.features && boreholesData.features.length > 0) {{
                overlays["💧 Boreholes (Styled)"] = L.geoJSON(boreholesData, {{
                    pointToLayer: function(f, latlng) {{
                        const risk = f.properties.Risk_Level || 'Safe';
                        return L.marker(latlng, {{ icon: getCyberIcon(riskColors[risk] || '#9ca3af', 'B') }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindPopup(buildPopupTable(f.properties.name || 'Borehole', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '💧'));
                        l.on('click', () => notifyParent(f, 'Boreholes'));
                    }}
                }});
            }}

            if (typeof campsData !== 'undefined' && campsData.features && campsData.features.length > 0) {{
                overlays["⛺ Refugee & IDP Settlements"] = L.geoJSON(campsData, {{
                    pointToLayer: function(f, latlng) {{
                        const risk = f.properties.Risk_Level || 'Safe';
                        return L.marker(latlng, {{ icon: getCyberIcon(riskColors[risk] || '#9ca3af', 'C') }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindPopup(buildPopupTable(f.properties.name || 'Camp', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || '0.0', '⛺'));
                    }}
                }});
            }}

            if (typeof waterPansData !== 'undefined' && waterPansData.features && waterPansData.features.length > 0) {{
                overlays["🪣 Rangeland Water Pans"] = L.geoJSON(waterPansData, {{
                    pointToLayer: function(f, latlng) {{
                        return L.circleMarker(latlng, {{ radius: 5, color: '#00f3ff', fillColor: '#00f3ff', fillOpacity: 0.6 }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindTooltip("Water Pan: " + (f.properties.name || 'Unit'), {{ className: 'custom-tooltip' }});
                    }}
                }});
            }}

            if (typeof wildlifeData !== 'undefined' && wildlifeData.features && wildlifeData.features.length > 0) {{
                overlays["🦒 Wildlife corridors"] = L.geoJSON(wildlifeData, {{
                    pointToLayer: function(f, latlng) {{
                        return L.circleMarker(latlng, {{ radius: 5, color: '#39ff14', fillColor: '#39ff14', fillOpacity: 0.7 }});
                    }}
                }});
            }}

            if (typeof townsData !== 'undefined' && townsData.features && townsData.features.length > 0) {{
                overlays["🏘️ Township Center Hubs"] = L.geoJSON(townsData, {{
                    pointToLayer: function(f, latlng) {{
                        return L.circleMarker(latlng, {{ radius: 6, color: '#cbd5e1', fillColor: '#1e293b', fillOpacity: 0.8 }});
                    }},
                    onEachFeature: function(f, l) {{
                        l.bindTooltip(f.properties.town_name || 'Town Center', {{ className: 'custom-tooltip' }});
                    }}
                }});
            }}

            if (typeof roadsData !== 'undefined' && roadsData.features && roadsData.features.length > 0) {{
                overlays["🛣️ Roads Network"] = L.geoJSON(roadsData, {{
                    style: {{ color: '#4b5563', weight: 1.2, opacity: 0.6 }}
                }});
            }}

            // Add layers according to default parameters
            const defaults = {default_layers_json};
            for (let name in overlays) {{
                if (defaults.includes(name)) {{
                    overlays[name].addTo(map);
                }}
            }}
        }}

        // Setup Leaflet Controls
        L.control.scale({{ position: 'bottomleft' }}).addTo(map);

        // Listen for messages from Parent
        window.addEventListener('message', (event) => {{
            if (event.data && event.data.type === 'zoom_to') {{
                map.setView([event.data.lat, event.data.lng], event.data.zoom || 13);
            }}
        }});

        // Dynamic Compass movement
        map.on('move', () => {{
            const center = map.getCenter();
            const angle = (center.lng * 25) % 360;
            document.getElementById('compass-needle').style.transform = `rotate(${{angle}}deg)`;
        }});

        function resetBearing() {{
            map.setView([-0.45, 39.65], 9);
            document.getElementById('compass-needle').style.transform = 'rotate(0deg)';
        }}

        // Fullscreen Toggle
        function toggleFullscreen() {{
            const elem = document.documentElement;
            const btn = document.getElementById('btn-fullscreen');
            
            if (!document.fullscreenElement) {{
                elem.requestFullscreen().then(() => {{
                    btn.textContent = "🖥️ Exit Fullscreen";
                }}).catch(err => {{
                    console.error("Fullscreen error", err);
                }});
            }} else {{
                document.exitFullscreen().then(() => {{
                    btn.textContent = "🖥️ Fullscreen";
                }});
            }}
        }}

        // Coordinate Tracker
        map.on('mousemove', (e) => {{
            document.getElementById('coord-display').textContent = `LAT: ${{e.latlng.lat.toFixed(5)}} | LNG: ${{e.latlng.lng.toFixed(5)}}`;
        }});

        // SWITCH VIEW (2D, 3D, Split Console)
        function switchView(viewType) {{
            const mapEl = document.getElementById('map');
            const mapWrapper = document.getElementById('map-wrapper');
            const cyberPanel = document.getElementById('cyber-panel');
            const tiltPanel = document.getElementById('tilt-panel');
            const radarScanner = document.getElementById('radar-scanner');
            const gridScan = document.getElementById('grid-scan');
            const banner3d = document.getElementById('banner-3d');

            // Reset buttons
            document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));

            if (viewType === '2d') {{
                document.getElementById('btn-view-2d').classList.add('active');
                mapEl.classList.remove('map-3d');
                banner3d.style.display = 'none';
                tiltPanel.style.display = 'none';
                radarScanner.style.display = 'none';
                gridScan.classList.remove('active');
                cyberPanel.style.display = 'none';
                map.invalidateSize();
            }} else if (viewType === '3d') {{
                document.getElementById('btn-view-3d').classList.add('active');
                mapEl.classList.add('map-3d');
                banner3d.style.display = 'block';
                tiltPanel.style.display = 'flex';
                radarScanner.style.display = 'block';
                gridScan.classList.add('active');
                cyberPanel.style.display = 'none';
                adjust3DTransforms();
                map.invalidateSize();
            }} else if (viewType === 'split') {{
                document.getElementById('btn-view-split').classList.add('active');
                mapEl.classList.remove('map-3d');
                banner3d.style.display = 'none';
                tiltPanel.style.display = 'none';
                radarScanner.style.display = 'none';
                gridScan.classList.remove('active');
                
                // Show drawer split
                cyberPanel.style.display = 'flex';
                map.invalidateSize();
                
                // Populate Assets List
                populateAssetsList();
            }}
        }}

        // Adjust CSS 3D skew properties
        function adjust3DTransforms() {{
            const tilt = document.getElementById('slider-tilt').value;
            const rotate = document.getElementById('slider-rotate').value;
            
            document.getElementById('val-tilt').textContent = tilt;
            document.getElementById('val-rotate').textContent = rotate;
            
            const mapEl = document.getElementById('map');
            mapEl.style.setProperty('--tilt', tilt + 'deg');
            mapEl.style.setProperty('--rotate', rotate + 'deg');
        }}

        // BUFFER RISK QUERY TOOL
        let bufferToolActive = false;
        let activeBufferCircle = null;

        function toggleBufferTool() {{
            const btn = document.getElementById('btn-buffer-tool');
            const card = document.getElementById('buffer-card');
            
            bufferToolActive = !bufferToolActive;
            if (bufferToolActive) {{
                btn.classList.add('active');
                btn.textContent = "⭕ Buffer Tool [ON]";
                card.style.display = 'flex';
            }} else {{
                btn.classList.remove('active');
                btn.textContent = "⭕ Buffer Tool [OFF]";
                card.style.display = 'none';
                if (activeBufferCircle) {{
                    map.removeLayer(activeBufferCircle);
                    activeBufferCircle = null;
                }}
            }}
        }}

        map.on('click', (e) => {{
            if (!bufferToolActive) return;
            
            const radiusKm = parseFloat(document.getElementById('buffer-radius').value);
            
            if (activeBufferCircle) {{
                map.removeLayer(activeBufferCircle);
            }}
            
            activeBufferCircle = L.circle(e.latlng, {{
                radius: radiusKm * 1000,
                color: '#ff007f',
                fillColor: '#ff007f',
                fillOpacity: 0.15,
                weight: 2,
                dashArray: '4,4'
            }}).addTo(map);
            
            // Perform distance queries on loaded layers
            let schoolsCount = 0;
            let clinicsCount = 0;
            let boreholesCount = 0;

            if (typeof schoolsData !== 'undefined' && schoolsData.features) {{
                schoolsData.features.forEach(f => {{
                    let dist = getDistanceKm(e.latlng.lat, e.latlng.lng, f.geometry.coordinates[1], f.geometry.coordinates[0]);
                    if (dist <= radiusKm) schoolsCount++;
                }});
            }}
            if (typeof healthData !== 'undefined' && healthData.features) {{
                healthData.features.forEach(f => {{
                    let dist = getDistanceKm(e.latlng.lat, e.latlng.lng, f.geometry.coordinates[1], f.geometry.coordinates[0]);
                    if (dist <= radiusKm) clinicsCount++;
                }});
            }}
            if (typeof boreholesData !== 'undefined' && boreholesData.features) {{
                boreholesData.features.forEach(f => {{
                    let dist = getDistanceKm(e.latlng.lat, e.latlng.lng, f.geometry.coordinates[1], f.geometry.coordinates[0]);
                    if (dist <= radiusKm) boreholesCount++;
                }});
            }}

            document.getElementById('buffer-results').innerHTML = `
                <div style="font-weight:bold; color:var(--pink); margin-bottom:5px;">📍 BUFFER RISK RESULTS</div>
                <div style="font-size:10px; line-height:1.4;">
                    <strong>Center:</strong> \${{e.latlng.lat.toFixed(4)}}, \${{e.latlng.lng.toFixed(4)}}<br>
                    <strong>Exposed Schools:</strong> <span style="color:var(--pink)">\${{schoolsCount}}</span><br>
                    <strong>Exposed Clinics:</strong> <span style="color:var(--orange)">\${{clinicsCount}}</span><br>
                    <strong>Exposed Boreholes:</strong> <span style="color:var(--cyan)">\${{boreholesCount}}</span>
                </div>
                <div style="font-size:9px; color:var(--text-muted); margin-top:5px; font-style:italic;">
                    Protocol: Cash trigger threshold crossed within buffer.
                </div>
            `;
        }});

        function recalculateBuffer() {{
            if (activeBufferCircle) {{
                const latlng = activeBufferCircle.getLatLng();
                const radiusKm = parseFloat(document.getElementById('buffer-radius').value);
                activeBufferCircle.setRadius(radiusKm * 1000);
                map.fireEvent('click', {{ latlng: latlng }});
            }}
        }}

        function getDistanceKm(lat1, lon1, lat2, lon2) {{
            const R = 6371; // Radius of the earth in km
            const dLat = deg2rad(lat2-lat1);
            const dLon = deg2rad(lon2-lon1); 
            const a = 
              Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
              Math.sin(dLon/2) * Math.sin(dLon/2); 
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
            return R * c;
        }}

        function deg2rad(deg) {{
            return deg * (Math.PI/180);
        }}

        // SEARCHABLE ASSETS DIRECTORY
        let searchableAssets = [];
        function populateAssetsList() {{
            searchableAssets = [];
            
            if (typeof schoolsData !== 'undefined' && schoolsData.features) {{
                schoolsData.features.forEach(f => {{
                    searchableAssets.push({{
                        name: f.properties.school_nam || 'School Unit',
                        type: 'School',
                        risk: f.properties.Risk_Level || 'Safe',
                        lat: f.geometry.coordinates[1],
                        lng: f.geometry.coordinates[0],
                        feature: f
                    }});
                }});
            }}
            if (typeof healthData !== 'undefined' && healthData.features) {{
                healthData.features.forEach(f => {{
                    searchableAssets.push({{
                        name: f.properties.health_fac || 'Health Clinic',
                        type: 'Clinic',
                        risk: f.properties.Risk_Level || 'Safe',
                        lat: f.geometry.coordinates[1],
                        lng: f.geometry.coordinates[0],
                        feature: f
                    }});
                }});
            }}
            if (typeof boreholesData !== 'undefined' && boreholesData.features) {{
                boreholesData.features.forEach(f => {{
                    searchableAssets.push({{
                        name: f.properties.name || 'Borehole unit',
                        type: 'Borehole',
                        risk: f.properties.Risk_Level || 'Safe',
                        lat: f.geometry.coordinates[1],
                        lng: f.geometry.coordinates[0],
                        feature: f
                    }});
                }});
            }}

            filterAssetsList();
        }}

        function filterAssetsList() {{
            const query = document.getElementById('asset-search').value.toLowerCase();
            const listEl = document.getElementById('assets-list-container');
            listEl.innerHTML = '';
            
            const filtered = searchableAssets.filter(item => item.name.toLowerCase().includes(query));
            
            filtered.forEach(item => {{
                let riskColor = riskColors[item.risk] || '#fff';
                const row = document.createElement('div');
                row.className = 'asset-list-item';
                row.onclick = () => focusAsset(item);
                row.innerHTML = `
                    <div style="display:flex; flex-direction:column;">
                        <span class="asset-name">\${{item.name}}</span>
                        <span class="asset-type">\${{item.type}}</span>
                    </div>
                    <span class="asset-risk" style="color:\${{riskColor}}">\${{item.risk}}</span>
                `;
                listEl.appendChild(row);
            }});
        }}

        function focusAsset(item) {{
            map.setView([item.lat, item.lng], 14);
            notifyParent(item.feature, item.type === 'School' ? 'Schools' : (item.type === 'Clinic' ? 'Health Facilities' : 'Boreholes'));
            
            if (window.focusIndicator) {{
                map.removeLayer(window.focusIndicator);
            }}
            window.focusIndicator = L.circleMarker([item.lat, item.lng], {{
                radius: 18,
                color: '#ff007f',
                fillColor: 'transparent',
                weight: 2,
                dashArray: '3,3'
            }}).addTo(map);
        }}

        // GeoJSON Downloader
        function downloadActiveLayer() {{
            let targetVarName = "{map_download_var}";
            let targetData = null;
            try {{
                if (targetVarName === 'schoolsData') targetData = schoolsData;
                else if (targetVarName === 'healthData') targetData = healthData;
                else if (targetVarName === 'boreholesData') targetData = boreholesData;
                else if (targetVarName === 'riversData') targetData = riversData;
                else if (targetVarName === 'subcountiesData') targetData = subcountiesData;
                else if (targetVarName === 'baselineFloodData') targetData = baselineFloodData;
                else targetData = schoolsData; // Fallback
            }} catch(e) {{}}
            
            if (!targetData) {{
                alert("GeoJSON layer data is not loaded yet.");
                return;
            }}
            
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(targetData));
            const dl = document.createElement('a');
            dl.setAttribute("href", dataStr);
            dl.setAttribute("download", "{download_filename}.geojson");
            document.body.appendChild(dl);
            dl.click();
            dl.remove();
        }}

        // Asynchronous Dynamic Data Loader
        async function loadDataAndInit() {{
            if (window.parent && window.parent.schoolsData) {{
                schoolsData = window.parent.schoolsData;
                healthData = window.parent.healthData;
                boreholesData = window.parent.boreholesData;
                campsData = window.parent.campsData;
                townsData = window.parent.townsData;
                waterPansData = window.parent.waterPansData;
                wildlifeData = window.parent.wildlifeData;
                roadsData = window.parent.roadsData;
                riversData = window.parent.riversData;
                subcountiesData = window.parent.subcountiesData;
                wardsData = window.parent.wardsData;
                extremeZoneData = window.parent.extremeZoneData;
                medZoneData = window.parent.medZoneData;
                highZoneData = window.parent.highZoneData;
                lowZoneData = window.parent.lowZoneData;
                baselineFloodData = window.parent.baselineFloodData || {{ "type": "FeatureCollection", "features": [] }};
                
                initAllLayers();
                L.control.layers(baseMaps, overlays, {{ collapsed: false, position: 'topleft' }}).addTo(map);
            }} else {{
                // Standalone fallback: Fetch from same directory
                try {{
                    const files = [
                        ['schoolsData', 'schools_risk_assessed.geojson'],
                        ['healthData', 'health_facilities_risk_assessed.geojson'],
                        ['boreholesData', 'boreholes_risk_assessed.geojson'],
                        ['campsData', 'idp_camps_risk_assessed.geojson'],
                        ['townsData', 'towns_risk_assessed.geojson'],
                        ['waterPansData', 'water_pans_risk_assessed.geojson'],
                        ['wildlifeData', 'wildlife_risk_assessed.geojson'],
                        ['roadsData', 'roads_risk_assessed.geojson'],
                        ['riversData', 'rivers.geojson'],
                        ['subcountiesData', 'garissa_subcounties.geojson'],
                        ['wardsData', 'garissa_wards.geojson'],
                        ['extremeZoneData', 'extreme_risk_zone.geojson'],
                        ['medZoneData', 'medium_risk_zone.geojson'],
                        ['highZoneData', 'high_risk_zone.geojson'],
                        ['lowZoneData', 'low_risk_zone.geojson']
                    ];
                    for (let [varName, filename] of files) {{
                        let res = await fetch(filename);
                        if (res.ok) {{
                            window[varName] = await res.json();
                        }}
                    }}
                    schoolsData = window.schoolsData;
                    healthData = window.healthData;
                    boreholesData = window.boreholesData;
                    campsData = window.campsData;
                    townsData = window.townsData;
                    waterPansData = window.waterPansData;
                    wildlifeData = window.wildlifeData;
                    roadsData = window.roadsData;
                    riversData = window.riversData;
                    subcountiesData = window.subcountiesData;
                    wardsData = window.wardsData;
                    extremeZoneData = window.extremeZoneData;
                    medZoneData = window.medZoneData;
                    highZoneData = window.highZoneData;
                    lowZoneData = window.lowZoneData;
                    baselineFloodData = window.baselineFloodData || {{ "type": "FeatureCollection", "features": [] }};
                    
                    initAllLayers();
                    L.control.layers(baseMaps, overlays, {{ collapsed: false, position: 'topleft' }}).addTo(map);
                }} catch(e) {{
                    console.error("Standalone data fetch failed", e);
                }}
            }}
        }}

        window.addEventListener('DOMContentLoaded', loadDataAndInit);
    </script>
</body>
</html>
"""

def generate_all_interactive_maps():
    # Keep output lines matching original script but with overhauled content template
    print("📁 Overhauling schools_risk_map.html...")
    default_layers_schools = json.dumps([
        "🏫 Schools (Styled)", "Wards Boundaries", "Sub-Counties Boundaries",
        "🔴 High Risk Zone (~500m)", "🟠 Medium Risk Zone (~1.5km)", "🟣 Extreme Risk Zone (~5.5km)"
    ])
    with open(OUTPUT_DIR / "schools_risk_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🏫 Garissa County Schools Flood Risk Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Superbright neon HUD template.",
            "Garissa_Schools_Risk_Assessed",
            default_layers_schools,
            "schoolsData"
        )
        f.write(html)

    # 2. health_facilities_risk_map.html
    print("📁 Overhauling health_facilities_risk_map.html...")
    default_layers_health = json.dumps([
        "🏥 Health Clinics (Styled)", "Wards Boundaries", "Sub-Counties Boundaries",
        "🔴 High Risk Zone (~500m)", "🟠 Medium Risk Zone (~1.5km)", "🟣 Extreme Risk Zone (~5.5km)"
    ])
    with open(OUTPUT_DIR / "health_facilities_risk_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🏥 Garissa Health Clinics Inundation Exposure Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Superbright neon HUD template.",
            "Garissa_Health_Facilities_Risk_Assessed",
            default_layers_health,
            "healthData"
        )
        f.write(html)

    # 3. boreholes_risk_map.html
    print("📁 Overhauling boreholes_risk_map.html...")
    default_layers_boreholes = json.dumps([
        "💧 Boreholes (Styled)", "🪣 Rangeland Water Pans", "Wards Boundaries", "Sub-Counties Boundaries",
        "🔴 High Risk Zone (~500m)", "🟠 Medium Risk Zone (~1.5km)", "🟣 Extreme Risk Zone (~5.5km)"
    ])
    with open(OUTPUT_DIR / "boreholes_risk_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "💧 Garissa County Humanitarian Borehole Supply Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Superbright neon HUD template.",
            "Garissa_Boreholes_Risk_Assessed",
            default_layers_boreholes,
            "boreholesData"
        )
        f.write(html)

    # 4. map_1_flood_baseline.html
    print("📁 Overhauling map_1_flood_baseline.html...")
    default_layers_baseline = json.dumps([
        "🌊 April 2024 Flood Baseline", "Wards Boundaries", "Sub-Counties Boundaries", "Rivers & Drainage"
    ])
    with open(OUTPUT_DIR / "map_1_flood_baseline.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🌊 Garissa County Baseline Flood Inundation Map",
            "UNOSAT April 2024 Historical Flood Extent. Superbright neon HUD template.",
            "Garissa_UNOSAT_Flood_Baseline_2024",
            default_layers_baseline,
            "baselineFloodData"
        )
        f.write(html)

    # 5. rivers_and_laghas_map.html
    print("📁 Overhauling rivers_and_laghas_map.html...")
    default_layers_rivers = json.dumps([
        "Rivers & Drainage", "Wards Boundaries", "Sub-Counties Boundaries"
    ])
    with open(OUTPUT_DIR / "rivers_and_laghas_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🏞️ Garissa County Rivers & Laghas Drainage Map",
            "Clipped drainage network for Tana River basin and seasonal watercourses.",
            "Garissa_Hydrography_Clipped_Rivers",
            default_layers_rivers,
            "riversData"
        )
        f.write(html)

    # 6. subcounties_google_hybrid_map.html
    print("📁 Overhauling subcounties_google_hybrid_map.html...")
    default_layers_subcounties = json.dumps([
        "Sub-Counties Boundaries", "Wards Boundaries", "Rivers & Drainage"
    ])
    with open(OUTPUT_DIR / "subcounties_google_hybrid_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🗺️ Garissa Administrative Subcounties Base Map",
            "Topological Voronoi boundary cells and centroids overlaid on high-resolution Google Hybrid Satellite imagery.",
            "Garissa_Subcounties_Voronoi_Boundaries",
            default_layers_subcounties,
            "subcountiesData"
        )
        f.write(html)

    # 7. garissa_master_drm_map.html
    print("📁 Overhauling garissa_master_drm_map.html...")
    default_layers_master = json.dumps([
        "🏫 Schools (Styled)", "🏥 Health Clinics (Styled)", "💧 Boreholes (Styled)",
        "⛺ Refugee & IDP Settlements", "Wards Boundaries", "Sub-Counties Boundaries",
        "Rivers & Drainage", "🔴 High Risk Zone (~500m)", "🌊 April 2024 Flood Baseline"
    ])
    with open(OUTPUT_DIR / "garissa_master_drm_map.html", "w", encoding="utf-8") as f:
        html = get_leaflet_template(
            "🗺️ Integrated early warning & Adaptation Master Map",
            "Garissa County Early Warning & Adaptation System (GEWAS). Defaults to Google Hybrid imagery with interactive layers.",
            "Garissa_GEWAS_Early_Warning_Master_Layers",
            default_layers_master,
            "schoolsData"
        )
        f.write(html)

    print("🎉 All 7 interactive HTML maps successfully overhauled with Neon-Robotic HUD layouts!")

if __name__ == "__main__":
    generate_all_interactive_maps()
