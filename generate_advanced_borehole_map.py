#!/usr/bin/env python3
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "OUTPUT"
GEOJSON_PATH = OUTPUT_DIR / "boreholes_risk_assessed.geojson"
HTML_OUTPUT_PATH = OUTPUT_DIR / "boreholes_risk_map.html"

def main():
    print("💧 Generating Advanced Boreholes Early Warning Map...")
    
    if not GEOJSON_PATH.exists():
        print(f"❌ Assessed borehole layer missing at {GEOJSON_PATH}. Run risk analysis first.")
        return
        
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Risk Color configuration
    risk_colors_json = json.dumps({
        'Extreme Risk (Super El Niño)': '#bd00ff',
        'High Risk': '#ef4444',
        'Medium Risk': '#f97316',
        'Low Risk': '#fbbf24',
        'Safe': '#10b981'
    })

    # Embedded HTML Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garissa County Humanitarian Borehole Supply Map</title>
    
    <!-- Leaflet & Fonts -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;800&display=swap" rel="stylesheet">
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    
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

        /* GLASSMORPHIC OVERLAYS */
        .glass-panel {{
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            z-index: 1000;
            pointer-events: auto;
        }}

        /* MAP TITLE & CAPTION BANNERS */
        .map-header {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 650px;
            text-align: center;
        }}

        .map-header h1 {{
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            margin: 0 0 6px 0;
            letter-spacing: 1px;
            color: var(--text-main);
            background: linear-gradient(to right, #ffffff, var(--cyan), #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}

        .map-caption {{
            font-size: 10px;
            color: var(--text-muted);
            margin: 0;
            line-height: 1.4;
        }}

        /* FLOATING COMPASS */
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
        }}

        .compass-needle {{
            width: 6px;
            height: 40px;
            background: linear-gradient(to bottom, #ef4444 50%, #94a3b8 50%);
            clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
            transform: rotate(0deg);
            transition: transform 0.2s ease-out;
        }}

        .compass-label {{
            position: absolute;
            top: 4px;
            font-family: 'Orbitron', sans-serif;
            font-size: 8px;
            font-weight: bold;
            color: #ef4444;
        }}

        /* FULLSCREEN & DOWNLOAD OVERLAY CONTROL */
        .map-controls {{
            position: absolute;
            bottom: 25px;
            left: 25px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 280px;
        }}

        .control-btn {{
            background: rgba(15, 23, 42, 0.9);
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
            gap: 8px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}

        .control-btn:hover {{
            background: var(--cyan);
            color: #020617;
            box-shadow: 0 0 10px var(--cyan);
            border-color: var(--cyan);
        }}

        /* BOREHOLE LABELS ON MAP */
        .borehole-tooltip {{
            background: rgba(15, 23, 42, 0.9) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            border-radius: 4px !important;
            padding: 2px 6px !important;
            font-size: 9px !important;
            font-family: monospace !important;
            font-weight: bold !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4) !important;
        }}

        .borehole-tooltip::before {{
            border-right-color: var(--border-glow) !important;
        }}

        /* CUSTOM SVG WATER DROP ICON */
        .water-drop-icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
        }}

        /* LEGEND OVERLAY */
        .legend-box {{
            position: absolute;
            top: 100px;
            right: 20px;
            font-size: 10px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 170px;
        }}

        .legend-title {{
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 9px;
            color: var(--cyan);
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .legend-color {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.2);
        }}

        /* POPUP FORMATTING */
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

    <!-- MAP CONTAINMENT -->
    <div id="map"></div>

    <!-- GLASS OVERLAYS: HEADER -->
    <div class="glass-panel map-header">
        <h1>💧 Garissa County Humanitarian Borehole Supply Map</h1>
        <p class="map-caption">
            Projected El Niño 2026 Inundation Exposure Risk. Defaults to Google Hybrid Base Imagery.
            Cites: Garissa Water (GAWASCO) & NDMA.
        </p>
    </div>

    <!-- GLASS OVERLAYS: LEGEND -->
    <div class="glass-panel legend-box">
        <div class="legend-title">💧 Risk Category</div>
        <div class="legend-item"><span class="legend-color" style="background:#bd00ff;"></span>Extreme Risk (~5.5km)</div>
        <div class="legend-item"><span class="legend-color" style="background:#ef4444;"></span>High Risk (~500m)</div>
        <div class="legend-item"><span class="legend-color" style="background:#f97316;"></span>Medium Risk (~1.5km)</div>
        <div class="legend-item"><span class="legend-color" style="background:#fbbf24;"></span>Low Risk (~3.3km)</div>
        <div class="legend-item"><span class="legend-color" style="background:#10b981;"></span>Safe Zone</div>
    </div>

    <!-- COMPASS NEEDLE -->
    <div class="glass-panel compass-overlay" onclick="resetBearing()">
        <span class="compass-label">N</span>
        <div class="compass-needle" id="compass-needle"></div>
    </div>

    <!-- SIDE CONTROLS -->
    <div class="map-controls">
        <button class="control-btn" id="btn-fullscreen" onclick="toggleFullscreen()">
            🖥️ Maximize Map / Fullscreen
        </button>
        <button class="control-btn" onclick="downloadGeoJSON()">
            💾 Download GeoJSON Vector Layer
        </button>
    </div>

    <script>
        const boreholesGeoJSON = {json.dumps(geojson_data)};
        const riskColors = {risk_colors_json};

        // Initialize Map
        const map = L.map('map', {{
            center: [-0.45, 39.65],
            zoom: 9,
            zoomControl: true,
            minZoom: 7,
            maxZoom: 16
        }});

        // Basemaps Setup
        const hybridBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Map imagery &copy; Google Hybrid Satellite'
        }}).addTo(map);

        const streetsBasemap = L.tileLayer('http://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: 'Map data &copy; Google Streets'
        }});

        const darkBasemap = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CARTO dark_matter'
        }});

        const baseMaps = {{
            "Google Hybrid (Satellite)": hybridBasemap,
            "Google Streets (Roads)": streetsBasemap,
            "CartoDB Dark Matter": darkBasemap
        }};

        L.control.layers(baseMaps, null, {{ collapsed: false, position: 'topleft' }}).addTo(map);
        L.control.scale({{ position: 'bottomleft' }}).addTo(map);

        // Compass tracking
        map.on('move', () => {{
            // Standard compass points north, no rotate API inside standard Leaflet map,
            // but we add slight inertia tilt response on pan to feel dynamic.
            const center = map.getCenter();
            const angle = (center.lng * 20) % 360;
            document.getElementById('compass-needle').style.transform = `rotate(${{angle}}deg)`;
        }});

        function resetBearing() {{
            map.setView([-0.45, 39.65], 9);
            document.getElementById('compass-needle').style.transform = 'rotate(0deg)';
        }}

        // Render Water Drop Custom SVGs
        function createWaterDropSVG(color) {{
            return L.divIcon({{
                className: 'custom-div-icon',
                html: `<div class="water-drop-icon">
                    <svg viewBox="0 0 30 42" width="16" height="20">
                        <path d="M15 3 Q 15 3 27 20 A 12 12 0 1 1 3 20 A 12 12 0 0 1 15 3 Z" fill="${{color}}" stroke="#000" stroke-width="1.5"/>
                        <circle cx="15" cy="22" r="3" fill="#ffffff" opacity="0.8"/>
                    </svg>
                </div>`,
                iconSize: [16, 20],
                iconAnchor: [8, 20]
            }});
        }}

        // Inject Layer Points
        L.geoJSON(boreholesGeoJSON, {{
            pointToLayer: function(feature, latlng) {{
                const risk = feature.properties.Risk_Level || 'Safe';
                const color = riskColors[risk] || '#9ca3af';
                const icon = createWaterDropSVG(color);
                
                const marker = L.marker(latlng, {{ icon: icon }});
                
                // Add name label tooltip visible on hover
                const name = feature.properties.name || feature.properties.Name || 'Unnamed Borehole';
                marker.bindTooltip(name, {{
                    permanent: false,
                    direction: 'right',
                    className: 'borehole-tooltip'
                }});
                
                return marker;
            }},
            onEachFeature: function(feature, layer) {{
                const p = feature.properties;
                const name = p.name || p.Name || 'Borehole Unit';
                const code = p.code || 'N/A';
                const status = (p.status || 'functional').replace('_', ' ').toUpperCase();
                const risk = p.Risk_Level || 'Safe';
                const dist = p.Distance_to_Flood_km || '0.0';
                const subcounty = p.sub_county || 'Garissa Sub County';
                const nnScore = p.NN_Vulnerability_Score || p.Vulnerability_Index || '0.0';
                
                let statusColor = '#10b981'; // Green
                if (status.includes('REPAIR') || status.includes('MAINTENANCE')) statusColor = '#fbbf24'; // Orange
                if (status.includes('NON') || status.includes('BROKEN')) statusColor = '#ef4444'; // Red

                let popupContent = `
                    <div class="popup-title">💧 ${{name}}</div>
                    <table class="popup-table">
                        <tr><td class="label">Borehole Code</td><td class="val">${{code}}</td></tr>
                        <tr><td class="label">Sub-County</td><td class="val">${{subcounty}}</td></tr>
                        <tr>
                            <td class="label">Status</td>
                            <td class="val" style="color: ${{statusColor}};">${{status}}</td>
                        </tr>
                        <tr>
                            <td class="label">Risk Category</td>
                            <td class="val" style="color: ${{(risk === 'Safe' ? '#10b981' : '#ef4444')}};">${{risk}}</td>
                        </tr>
                        <tr><td class="label">Distance to Flood</td><td class="val">${{dist}} km</td></tr>
                        <tr><td class="label">Vulnerability Score</td><td class="val">${{nnScore}}</td></tr>
                    </table>
                `;
                layer.bindPopup(popupContent);
            }}
        }}).addTo(map);

        // Fullscreen Toggle Action
        function toggleFullscreen() {{
            const elem = document.documentElement;
            const btn = document.getElementById('btn-fullscreen');
            
            if (!document.fullscreenElement) {{
                elem.requestFullscreen().then(() => {{
                    btn.textContent = "🖥️ Exit Fullscreen Map";
                }}).catch(err => {{
                    console.error("Fullscreen error", err);
                }});
            }} else {{
                document.exitFullscreen().then(() => {{
                    btn.textContent = "🖥️ Maximize Map / Fullscreen";
                }});
            }}
        }}

        // Download GeoJSON layer directly
        function downloadGeoJSON() {{
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(boreholesGeoJSON));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", "Garissa_Boreholes_Assessed_2026.geojson");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }}
    </script>
</body>
</html>
"""
    
    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Advanced Boreholes Map generated at {HTML_OUTPUT_PATH.name}")

if __name__ == "__main__":
    main()
