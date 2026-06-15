#!/usr/bin/env python3
"""
Automated Interactive HTML Map Generator for Garissa Early Warning Portal.
Generates 7 advanced interactive HTML maps featuring:
1. Google Hybrid satellite default with base switchers (Google Streets, Dark Matter, OSM).
2. Collapsible layers selection tree.
3. Rotating compass, scales, fullscreen, and GeoJSON downloads.
4. Rich HTML popups with neural-network risk disclosures.
5. Bidirectional iframe-to-parent message communication.
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
        if stat.st_size > 5 * 1024 * 1024 and (stat.st_blocks * 512) < (stat.st_size * 0.3):
            return {"type": "FeatureCollection", "features": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading GeoJSON {path.name}: {e}")
        return {"type": "FeatureCollection", "features": []}

def get_leaflet_template(title, caption, map_config_js, geojson_vars_js, layers_addition_js, download_filename):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Leaflet & Fonts -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <style>
        :root {{
            --bg-glass: rgba(15, 23, 42, 0.85);
            --border-glow: rgba(6, 182, 212, 0.3);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --cyan: #06b6d4;
        }}

        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: 'Inter', sans-serif;
            background-color: #020617;
            color: var(--text-main);
            overflow: hidden;
        }}

        #map {{
            height: 100%;
            width: 100%;
            z-index: 1;
        }}

        .glass-panel {{
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 12px 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            z-index: 1000;
            pointer-events: auto;
        }}

        .map-header {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 700px;
            text-align: center;
        }}

        .map-header h1 {{
            font-family: 'Orbitron', sans-serif;
            font-size: 15px;
            margin: 0 0 4px 0;
            letter-spacing: 1.2px;
            background: linear-gradient(to right, #ffffff, var(--cyan), #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}

        .map-caption {{
            font-size: 9px;
            color: var(--text-muted);
            margin: 0;
            line-height: 1.3;
            font-weight: 500;
        }}

        .compass-overlay {{
            position: absolute;
            bottom: 25px;
            right: 25px;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1000;
        }}

        .compass-needle {{
            width: 5px;
            height: 36px;
            background: linear-gradient(to bottom, #ef4444 50%, #94a3b8 50%);
            clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
            transform: rotate(0deg);
            transition: transform 0.2s ease-out;
        }}

        .compass-label {{
            position: absolute;
            top: 3px;
            font-family: 'Orbitron', sans-serif;
            font-size: 8px;
            font-weight: bold;
            color: #ef4444;
        }}

        .map-controls {{
            position: absolute;
            bottom: 25px;
            left: 25px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-width: 250px;
        }}

        .control-btn {{
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid var(--border-glow);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 9px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}

        .control-btn:hover {{
            background: var(--cyan);
            color: #020617;
            box-shadow: 0 0 10px var(--cyan);
            border-color: var(--cyan);
        }}

        .custom-tooltip {{
            background: rgba(15, 23, 42, 0.95) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            border-radius: 4px !important;
            padding: 2px 6px !important;
            font-size: 9px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4) !important;
        }}

        /* Leaflet Controls Overrides */
        .leaflet-control-layers {{
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            border-radius: 8px !important;
            font-size: 9px !important;
            font-weight: bold !important;
            font-family: monospace !important;
        }}

        .leaflet-control-layers-list {{
            padding: 5px;
        }}

        .leaflet-control-layers-group-name {{
            color: var(--cyan) !important;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 8px;
            margin-top: 5px;
            display: block;
            border-bottom: 1px solid rgba(6,182,212,0.15);
            padding-bottom: 2px;
        }}

        .leaflet-popup-content-wrapper {{
            background: var(--bg-glass) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--border-glow) !important;
            color: var(--text-main) !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            padding: 5px !important;
        }}

        .leaflet-popup-tip {{
            background: var(--bg-glass) !important;
            border-left: 1px solid var(--border-glow) !important;
            border-bottom: 1px solid var(--border-glow) !important;
        }}

        .popup-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 6px;
            border-bottom: 1px solid var(--border-glow);
            padding-bottom: 4px;
            color: var(--cyan);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .popup-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9px;
        }}

        .popup-table td {{
            padding: 3px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        .popup-table td.label {{
            color: var(--text-muted);
            font-weight: 500;
        }}

        .popup-table td.val {{
            text-align: right;
            font-family: monospace;
            font-weight: bold;
        }}
    </style>
</head>
<body>

    <div id="map"></div>

    <!-- HEADER BANNER -->
    <div class="glass-panel map-header">
        <h1>{title}</h1>
        <p class="map-caption">{caption}</p>
    </div>

    <!-- rotating COMPASS -->
    <div class="glass-panel compass-overlay" onclick="resetBearing()">
        <span class="compass-label">N</span>
        <div class="compass-needle" id="compass-needle"></div>
    </div>

    <!-- MAP UTILITIES -->
    <div class="map-controls">
        <button class="control-btn" id="btn-fullscreen" onclick="toggleFullscreen()">
            🖥️ Fullscreen Map
        </button>
        <button class="control-btn" onclick="downloadLayerData()">
            💾 Download Vector Layer
        </button>
    </div>

    <script>
        // Inject GeoJSON Layer Variables
        {geojson_vars_js}

        // Initialize Map
        const map = L.map('map', {{
            center: [-0.45, 39.65],
            zoom: 9,
            zoomControl: true,
            minZoom: 7,
            maxZoom: 16
        }});

        // Basemaps list (Google Hybrid satellite default)
        const hybridBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Imagery &copy; Google Hybrid'
        }}).addTo(map);

        const streetsBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Map &copy; Google Streets'
        }});

        const darkBasemap = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CARTO dark_matter'
        }});

        const osmBasemap = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors'
        }});

        const baseMaps = {{
            "Google Hybrid (Satellite)": hybridBasemap,
            "Google Streets": streetsBasemap,
            "CartoDB Dark Matter": darkBasemap,
            "OpenStreetMap": osmBasemap
        }};

        // Master overlays controls dictionary
        const overlays = {{}};

        // Helper function to build marker popup tables
        function buildPopupTable(name, code, status, risk, dist, vuln, typeIcon) {{
            let riskColor = risk.includes('Safe') ? '#10b981' : (risk.includes('Low') ? '#fbbf24' : '#ef4444');
            let statusColor = status.includes('FUNCTIONAL') || status.includes('ACTIVE') ? '#10b981' : '#f97316';
            return `
                <div class="popup-title">${{typeIcon}} ${{name}}</div>
                <table class="popup-table">
                    <tr><td class="label">Code ID</td><td class="val">${{code}}</td></tr>
                    <tr><td class="label">Status</td><td class="val" style="color:${{statusColor}};">${{status}}</td></tr>
                    <tr><td class="label">Flood Risk</td><td class="val" style="color:${{riskColor}};">${{risk}}</td></tr>
                    <tr><td class="label">Dist to Flood</td><td class="val">${{dist}} km</td></tr>
                    <tr><td class="label">Vulnerability NN</td><td class="val" style="color:var(--cyan);">${{vuln}}</td></tr>
                </table>
            `;
        }}

        // Send Click events to Parent frame (postMessage)
        function notifyParent(feature, layerName) {{
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'marker_click',
                    layer: layerName,
                    properties: feature.properties
                }}, '*');
            }}
        }}

        // Listen for zoom/center messages from Parent
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

        // Fullscreen Toggle Action
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
                    btn.textContent = "🖥️ Fullscreen Map";
                }});
            }}
        }}

        // Layers additions logic
        {layers_addition_js}

        // Add Leaflet Layer Control
        L.control.layers(baseMaps, overlays, {{ collapsed: false, position: 'topleft' }}).addTo(map);
        L.control.scale({{ position: 'bottomleft' }}).addTo(map);

        // Download GeoJSON layer utility
        function downloadLayerData() {{
            const activeLayerName = "{download_filename}";
            // Find active GeoJSON variable
            let targetData = null;
            try {{
                targetData = {map_config_js};
            }} catch(e) {{}}
            
            if (!targetData) {{
                alert("GeoJSON layer data is not available for direct download on this map configuration.");
                return;
            }}
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(targetData));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", activeLayerName + ".geojson");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }}
    </script>
</body>
</html>
"""

def generate_all_interactive_maps():
    print("⏳ Loading spatial layers into memory...")
    
    # Load files
    schools = load_geojson_safe(OUTPUT_DIR / "schools_risk_assessed.geojson")
    health = load_geojson_safe(OUTPUT_DIR / "health_facilities_risk_assessed.geojson")
    boreholes = load_geojson_safe(OUTPUT_DIR / "boreholes_risk_assessed.geojson")
    camps = load_geojson_safe(OUTPUT_DIR / "idp_camps_risk_assessed.geojson")
    towns = load_geojson_safe(OUTPUT_DIR / "towns_risk_assessed.geojson")
    water_pans = load_geojson_safe(OUTPUT_DIR / "water_pans_risk_assessed.geojson")
    wildlife = load_geojson_safe(OUTPUT_DIR / "wildlife_risk_assessed.geojson")
    roads = load_geojson_safe(OUTPUT_DIR / "roads_risk_assessed.geojson")
    rivers = load_geojson_safe(OUTPUT_DIR / "rivers.geojson")
    subcounties = load_geojson_safe(OUTPUT_DIR / "garissa_subcounties.geojson")
    wards = load_geojson_safe(OUTPUT_DIR / "garissa_wards.geojson")
    
    extreme_zone = load_geojson_safe(OUTPUT_DIR / "extreme_risk_zone.geojson")
    high_zone = load_geojson_safe(OUTPUT_DIR / "high_risk_zone.geojson")
    medium_zone = load_geojson_safe(OUTPUT_DIR / "medium_risk_zone.geojson")
    low_zone = load_geojson_safe(OUTPUT_DIR / "low_risk_zone.geojson")

    # Read the historical UNOSAT flood extent (from shapefile, load via geopandas and save to geojson in python variable)
    flood_extents_path = BASE_DIR / "flood_extents.shp"
    flood_geojson = {"type": "FeatureCollection", "features": []}
    if flood_extents_path.exists():
        try:
            fgdf = gpd.read_file(flood_extents_path)
            if fgdf.crs is None or fgdf.crs.to_string() != "EPSG:4326":
                fgdf = fgdf.to_crs("EPSG:4326")
            # Simplify geometry to keep file lightweight
            fgdf['geometry'] = fgdf['geometry'].simplify(0.001)
            # Remove date columns that cause JSON format issues
            for col in fgdf.columns:
                if col != 'geometry':
                    fgdf[col] = fgdf[col].astype(str)
            flood_geojson = json.loads(fgdf.to_json())
        except Exception as e:
            print(f"Error loading flood shapefile: {e}")

    # Standard styling logic script for Leaflet
    leaflet_styles_js = """
        // Risk assessment color palette
        const riskColors = {
            'Extreme Risk (Super El Niño)': '#bd00ff',
            'High Risk': '#ef4444',
            'Medium Risk': '#f97316',
            'Low Risk': '#fbbf24',
            'Safe': '#10b981'
        };

        // Custom SVGs builders
        function getSVGIcon(color, char) {
            return L.divIcon({
                className: 'custom-div-icon',
                html: `<div style="display:flex; align-items:center; justify-content:center; width:20px; height:20px;">
                    <svg viewBox="0 0 30 42" width="18" height="24">
                        <path d="M15 3 Q 15 3 27 20 A 12 12 0 1 1 3 20 A 12 12 0 0 1 15 3 Z" fill="${color}" stroke="#000" stroke-width="1.5"/>
                        <text x="15" y="27" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">${char}</text>
                    </svg>
                </div>`,
                iconSize: [18, 24],
                iconAnchor: [9, 24]
            });
        }
    """

    # Helper layers logic for leaflet
    wards_layer_js = """
        if (typeof wardsData !== 'undefined' && wardsData.features.length > 0) {
            overlays["Wards Boundaries"] = L.geoJSON(wardsData, {
                style: { color: '#fbbf24', fillColor: 'transparent', weight: 1.0, dashArray: '3,3' },
                onEachFeature: function(f, l) {
                    l.bindTooltip(f.properties.ward || 'Ward', { sticky: true, className: 'custom-tooltip' });
                }
            }).addTo(map);
        }
    """
    
    subcounties_layer_js = """
        if (typeof subcountiesData !== 'undefined' && subcountiesData.features.length > 0) {
            overlays["Sub-Counties Boundaries"] = L.geoJSON(subcountiesData, {
                style: { color: '#06b6d4', fillColor: 'transparent', weight: 1.8 },
                onEachFeature: function(f, l) {
                    const name = f.properties.sub_county || 'Sub-County';
                    l.bindTooltip(name, { permanent: true, direction: 'center', className: 'custom-tooltip' });
                }
            }).addTo(map);
        }
    """

    rivers_layer_js = """
        if (typeof riversData !== 'undefined' && riversData.features.length > 0) {
            overlays["Rivers & Drainage"] = L.geoJSON(riversData, {
                style: { color: '#38bdf8', weight: 1.5, opacity: 0.85 },
                onEachFeature: function(f, l) {
                    l.bindTooltip("Rivers/Laghas Drainage", { sticky: true, className: 'custom-tooltip' });
                }
            }).addTo(map);
        }
    """

    flood_zones_layer_js = """
        if (typeof extremeZoneData !== 'undefined') {
            overlays["🟣 Extreme Risk Zone (~5.5km)"] = L.geoJSON(extremeZoneData, {
                style: { color: '#bd00ff', fillColor: '#bd00ff', fillOpacity: 0.08, weight: 1 }
            });
        }
        if (typeof lowZoneData !== 'undefined') {
            overlays["🟡 Low Risk Zone (~3.3km)"] = L.geoJSON(lowZoneData, {
                style: { color: '#fef08a', fillColor: '#fef08a', fillOpacity: 0.1, weight: 0.8 }
            });
        }
        if (typeof medZoneData !== 'undefined') {
            overlays["🟠 Medium Risk Zone (~1.5km)"] = L.geoJSON(medZoneData, {
                style: { color: '#fed7aa', fillColor: '#fed7aa', fillOpacity: 0.15, weight: 0.8 }
            });
        }
        if (typeof highZoneData !== 'undefined') {
            overlays["🔴 High Risk Zone (~500m)"] = L.geoJSON(highZoneData, {
                style: { color: '#fca5a5', fillColor: '#fca5a5', fillOpacity: 0.2, weight: 1.0 }
            }).addTo(map);
        }
    """

    # 1. schools_risk_map.html
    print("📁 Creating schools_risk_map.html...")
    geojson_vars_schools = f"""
        const schoolsData = {json.dumps(schools)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
        const extremeZoneData = {json.dumps(extreme_zone)};
        const lowZoneData = {json.dumps(low_zone)};
        const medZoneData = {json.dumps(medium_zone)};
        const highZoneData = {json.dumps(high_zone)};
    """
    layers_addition_schools = leaflet_styles_js + wards_layer_js + subcounties_layer_js + flood_zones_layer_js + """
        if (schoolsData.features.length > 0) {
            overlays["🏫 Schools (Styled Risk)"] = L.geoJSON(schoolsData, {
                pointToLayer: function(feature, latlng) {
                    const risk = feature.properties.Risk_Level || 'Safe';
                    const color = riskColors[risk] || '#9ca3af';
                    const icon = getSVGIcon(color, 'S');
                    const marker = L.marker(latlng, { icon: icon });
                    marker.bindTooltip(feature.properties.school_nam || 'School', { className: 'custom-tooltip' });
                    return marker;
                },
                onEachFeature: function(feature, layer) {
                    const p = feature.properties;
                    layer.bindPopup(buildPopupTable(
                        p.school_nam || 'School', 
                        p.code || 'N/A', 
                        p.status || 'ACTIVE', 
                        p.Risk_Level || 'Safe', 
                        p.Distance_to_Flood_km || '0.0', 
                        p.Vulnerability_Index || p.NN_Vulnerability_Score || '0.0', 
                        '🏫'
                    ));
                    layer.on('click', () => {
                        notifyParent(feature, 'Schools');
                    });
                }
            }).addTo(map);
        }
    """
    with open(OUTPUT_DIR / "schools_risk_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🏫 Garissa County Schools Flood Risk Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Defaults to Google Hybrid Base Imagery.",
            "schoolsData",
            geojson_vars_schools,
            layers_addition_schools,
            "Garissa_Schools_Risk_Assessed"
        ))

    # 2. health_facilities_risk_map.html
    print("📁 Creating health_facilities_risk_map.html...")
    geojson_vars_health = f"""
        const healthData = {json.dumps(health)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
        const extremeZoneData = {json.dumps(extreme_zone)};
        const lowZoneData = {json.dumps(low_zone)};
        const medZoneData = {json.dumps(medium_zone)};
        const highZoneData = {json.dumps(high_zone)};
    """
    layers_addition_health = leaflet_styles_js + wards_layer_js + subcounties_layer_js + flood_zones_layer_js + """
        if (healthData.features.length > 0) {
            overlays["🏥 Health Facilities (Styled Risk)"] = L.geoJSON(healthData, {
                pointToLayer: function(feature, latlng) {
                    const risk = feature.properties.Risk_Level || 'Safe';
                    const color = riskColors[risk] || '#9ca3af';
                    const icon = getSVGIcon(color, 'H');
                    const marker = L.marker(latlng, { icon: icon });
                    marker.bindTooltip(feature.properties.health_fac || 'Health Clinic', { className: 'custom-tooltip' });
                    return marker;
                },
                onEachFeature: function(feature, layer) {
                    const p = feature.properties;
                    layer.bindPopup(buildPopupTable(
                        p.health_fac || 'Clinic', 
                        p.code || 'N/A', 
                        p.status || 'ACTIVE', 
                        p.Risk_Level || 'Safe', 
                        p.Distance_to_Flood_km || '0.0', 
                        p.Vulnerability_Index || p.NN_Vulnerability_Score || '0.0', 
                        '🏥'
                    ));
                    layer.on('click', () => {
                        notifyParent(feature, 'Health Facilities');
                    });
                }
            }).addTo(map);
        }
    """
    with open(OUTPUT_DIR / "health_facilities_risk_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🏥 Garissa Health Clinics Inundation Exposure Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Defaults to Google Hybrid Base Imagery.",
            "healthData",
            geojson_vars_health,
            layers_addition_health,
            "Garissa_Health_Facilities_Risk_Assessed"
        ))

    # 3. boreholes_risk_map.html
    print("📁 Creating boreholes_risk_map.html...")
    geojson_vars_boreholes = f"""
        const boreholesData = {json.dumps(boreholes)};
        const waterPansData = {json.dumps(water_pans)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
        const extremeZoneData = {json.dumps(extreme_zone)};
        const lowZoneData = {json.dumps(low_zone)};
        const medZoneData = {json.dumps(medium_zone)};
        const highZoneData = {json.dumps(high_zone)};
    """
    layers_addition_boreholes = leaflet_styles_js + wards_layer_js + subcounties_layer_js + flood_zones_layer_js + """
        if (boreholesData.features.length > 0) {
            overlays["💧 Boreholes (Styled Risk)"] = L.geoJSON(boreholesData, {
                pointToLayer: function(feature, latlng) {
                    const risk = feature.properties.Risk_Level || 'Safe';
                    const color = riskColors[risk] || '#9ca3af';
                    const icon = getSVGIcon(color, 'B');
                    const marker = L.marker(latlng, { icon: icon });
                    marker.bindTooltip(feature.properties.name || 'Borehole', { className: 'custom-tooltip' });
                    return marker;
                },
                onEachFeature: function(feature, layer) {
                    const p = feature.properties;
                    layer.bindPopup(buildPopupTable(
                        p.name || 'Borehole Unit', 
                        p.code || 'N/A', 
                        p.status || 'FUNCTIONAL', 
                        p.Risk_Level || 'Safe', 
                        p.Distance_to_Flood_km || '0.0', 
                        p.Vulnerability_Index || p.NN_Vulnerability_Score || '0.0', 
                        '💧'
                    ));
                    layer.on('click', () => {
                        notifyParent(feature, 'Boreholes');
                    });
                }
            }).addTo(map);
        }
        if (waterPansData.features.length > 0) {
            overlays["🪣 Rangeland Water Pans"] = L.geoJSON(waterPansData, {
                pointToLayer: function(feature, latlng) {
                    return L.circleMarker(latlng, {
                        radius: 6,
                        color: '#0ea5e9',
                        fillColor: '#0ea5e9',
                        fillOpacity: 0.6
                    });
                },
                onEachFeature: function(f, l) {
                    l.bindTooltip(f.properties.name || 'Water Pan', { className: 'custom-tooltip' });
                }
            }).addTo(map);
        }
    """
    with open(OUTPUT_DIR / "boreholes_risk_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "💧 Garissa County Humanitarian Borehole Supply Map",
            "Projected El Niño 2026 Inundation Exposure Risk. Defaults to Google Hybrid Base Imagery.",
            "boreholesData",
            geojson_vars_boreholes,
            layers_addition_boreholes,
            "Garissa_Boreholes_Risk_Assessed"
        ))

    # 4. map_1_flood_baseline.html
    print("📁 Creating map_1_flood_baseline.html...")
    geojson_vars_baseline = f"""
        const baselineFloodData = {json.dumps(flood_geojson)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
        const riversData = {json.dumps(rivers)};
    """
    layers_addition_baseline = leaflet_styles_js + wards_layer_js + subcounties_layer_js + rivers_layer_js + """
        if (baselineFloodData.features.length > 0) {
            overlays["🌊 April 2024 Flood Baseline"] = L.geoJSON(baselineFloodData, {
                style: { color: '#2563eb', fillColor: '#3b82f6', fillOpacity: 0.45, weight: 1.5 }
            }).addTo(map);
        }
    """
    with open(OUTPUT_DIR / "map_1_flood_baseline.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🌊 Garissa County Baseline Flood Inundation Map",
            "UNOSAT April 2024 Historical Flood Extent. Defaults to Google Hybrid Base Imagery.",
            "baselineFloodData",
            geojson_vars_baseline,
            layers_addition_baseline,
            "Garissa_UNOSAT_Flood_Baseline_2024"
        ))

    # 5. rivers_and_laghas_map.html
    print("📁 Creating rivers_and_laghas_map.html...")
    geojson_vars_rivers = f"""
        const riversData = {json.dumps(rivers)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
    """
    layers_addition_rivers = leaflet_styles_js + wards_layer_js + subcounties_layer_js + rivers_layer_js
    with open(OUTPUT_DIR / "rivers_and_laghas_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🏞️ Garissa County Rivers & Laghas Drainage Map",
            "Clipped drainage network for Tana River basin and seasonal watercourses. Defaults to Google Hybrid.",
            "riversData",
            geojson_vars_rivers,
            layers_addition_rivers,
            "Garissa_Hydrography_Clipped_Rivers"
        ))

    # 6. subcounties_google_hybrid_map.html
    print("📁 Creating subcounties_google_hybrid_map.html...")
    geojson_vars_subcounties = f"""
        const subcountiesData = {json.dumps(subcounties)};
        const wardsData = {json.dumps(wards)};
        const riversData = {json.dumps(rivers)};
    """
    layers_addition_subcounties = leaflet_styles_js + wards_layer_js + subcounties_layer_js + rivers_layer_js
    with open(OUTPUT_DIR / "subcounties_google_hybrid_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🗺️ Garissa Administrative Subcounties Base Map",
            "Topological Voronoi boundary cells and centroids overlaid on high-resolution Google Hybrid Satellite imagery.",
            "subcountiesData",
            geojson_vars_subcounties,
            layers_addition_subcounties,
            "Garissa_Subcounties_Voronoi_Boundaries"
        ))

    # 7. garissa_master_drm_map.html
    print("📁 Creating garissa_master_drm_map.html...")
    geojson_vars_master = f"""
        const schoolsData = {json.dumps(schools)};
        const healthData = {json.dumps(health)};
        const boreholesData = {json.dumps(boreholes)};
        const campsData = {json.dumps(camps)};
        const townsData = {json.dumps(towns)};
        const waterPansData = {json.dumps(water_pans)};
        const wildlifeData = {json.dumps(wildlife)};
        const roadsData = {json.dumps(roads)};
        const riversData = {json.dumps(rivers)};
        const wardsData = {json.dumps(wards)};
        const subcountiesData = {json.dumps(subcounties)};
        const extremeZoneData = {json.dumps(extreme_zone)};
        const lowZoneData = {json.dumps(low_zone)};
        const medZoneData = {json.dumps(medium_zone)};
        const highZoneData = {json.dumps(high_zone)};
    """
    layers_addition_master = leaflet_styles_js + wards_layer_js + subcounties_layer_js + rivers_layer_js + flood_zones_layer_js + """
        if (typeof roadsData !== 'undefined' && roadsData.features.length > 0) {
            overlays["🛣️ Roads Network"] = L.geoJSON(roadsData, {
                style: { color: '#4b5563', weight: 1.0, opacity: 0.6 }
            });
        }
        if (schoolsData.features.length > 0) {
            overlays["🏫 Schools (Styled)"] = L.geoJSON(schoolsData, {
                pointToLayer: function(f, latlng) {
                    const risk = f.properties.Risk_Level || 'Safe';
                    return L.marker(latlng, { icon: getSVGIcon(riskColors[risk] || '#9ca3af', 'S') });
                },
                onEachFeature: function(f, l) {
                    l.bindPopup(buildPopupTable(f.properties.school_nam || 'School', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || '0.0', '🏫'));
                    l.on('click', () => notifyParent(f, 'Schools'));
                }
            }).addTo(map);
        }
        if (healthData.features.length > 0) {
            overlays["🏥 Health Clinics (Styled)"] = L.geoJSON(healthData, {
                pointToLayer: function(f, latlng) {
                    const risk = f.properties.Risk_Level || 'Safe';
                    return L.marker(latlng, { icon: getSVGIcon(riskColors[risk] || '#9ca3af', 'H') });
                },
                onEachFeature: function(f, l) {
                    l.bindPopup(buildPopupTable(f.properties.health_fac || 'Clinic', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || '0.0', '🏥'));
                    l.on('click', () => notifyParent(f, 'Health Facilities'));
                }
            }).addTo(map);
        }
        if (boreholesData.features.length > 0) {
            overlays["💧 Boreholes (Styled)"] = L.geoJSON(boreholesData, {
                pointToLayer: function(f, latlng) {
                    const risk = f.properties.Risk_Level || 'Safe';
                    return L.marker(latlng, { icon: getSVGIcon(riskColors[risk] || '#9ca3af', 'B') });
                },
                onEachFeature: function(f, l) {
                    l.bindPopup(buildPopupTable(f.properties.name || 'Borehole', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || '0.0', '💧'));
                    l.on('click', () => notifyParent(f, 'Boreholes'));
                }
            }).addTo(map);
        }
        if (campsData.features.length > 0) {
            overlays["⛺ Refugee & IDP Settlements"] = L.geoJSON(campsData, {
                pointToLayer: function(f, latlng) {
                    const risk = f.properties.Risk_Level || 'Safe';
                    return L.marker(latlng, { icon: getSVGIcon(riskColors[risk] || '#9ca3af', 'C') });
                },
                onEachFeature: function(f, l) {
                    l.bindPopup(buildPopupTable(f.properties.name || 'Camp', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || '0.0', '⛺'));
                }
            }).addTo(map);
        }
        if (waterPansData.features.length > 0) {
            overlays["🪣 Rangeland Water Pans"] = L.geoJSON(waterPansData, {
                pointToLayer: function(f, latlng) {
                    return L.circleMarker(latlng, { radius: 5, color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.6 });
                }
            });
        }
        if (wildlifeData.features.length > 0) {
            overlays["🦒 Wildlife corridors"] = L.geoJSON(wildlifeData, {
                pointToLayer: function(f, latlng) {
                    return L.circleMarker(latlng, { radius: 5, color: '#10b981', fillColor: '#10b981', fillOpacity: 0.7 });
                }
            });
        }
        if (townsData.features.length > 0) {
            overlays["🏘️ Township Center Hubs"] = L.geoJSON(townsData, {
                pointToLayer: function(f, latlng) {
                    return L.circleMarker(latlng, { radius: 6, color: '#cbd5e1', fillColor: '#334155', fillOpacity: 0.8 });
                },
                onEachFeature: function(f, l) {
                    l.bindTooltip(f.properties.town_name || 'Town Center', { className: 'custom-tooltip' });
                }
            });
        }
    """
    with open(OUTPUT_DIR / "garissa_master_drm_map.html", "w", encoding="utf-8") as f:
        f.write(get_leaflet_template(
            "🗺️ Integrated early warning & Adaptation Master Map",
            "Garissa County Early Warning & Adaptation System (GEWAS). Defaults to Google Hybrid imagery with interactive layers.",
            "schoolsData",
            geojson_vars_master,
            layers_addition_master,
            "Garissa_GEWAS_Early_Warning_Master_Layers"
        ))

    print("🎉 All 7 interactive HTML maps successfully generated!")

if __name__ == "__main__":
    generate_all_interactive_maps()
