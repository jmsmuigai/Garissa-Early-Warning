#!/usr/bin/env python3
"""
Generates the overhualed Community Dashboard with enlarged font, voice broadcast,
interactive checklist, and Google Hybrid map showing humanitarian risk triggers.
Author: Garissa GIS Directorate — James M. Mburu
"""
import json
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    print("📁 Generating Community Dashboard HTML...")

    # Load assets risk to display in lists
    boreholes_path = OUTPUT_DIR / "boreholes_risk_assessed.geojson"
    schools_path = OUTPUT_DIR / "schools_risk_assessed.geojson"
    health_path = OUTPUT_DIR / "health_facilities_risk_assessed.geojson"

    def count_risk(path):
        if not path.exists(): return 0, 0
        try:
            import geopandas as gpd
            gdf = gpd.read_file(path)
            total = len(gdf)
            exposed = len(gdf[gdf['Risk_Level'].isin(['High Risk', 'Extreme Risk (Super El Niño)'])])
            return total, exposed
        except:
            return 0, 0

    tot_bh, exp_bh = count_risk(boreholes_path)
    tot_sch, exp_sch = count_risk(schools_path)
    tot_hlth, exp_hlth = count_risk(health_path)

    # Convert geojsons to string inline to load on the map
    def load_str(path):
        if not path.exists(): return '{"type":"FeatureCollection","features":[]}'
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    bh_json = load_str(boreholes_path)
    sch_json = load_str(schools_path)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garissa Community Early Warning Dashboard (GEWAS)</title>
    
    <!-- Leaflet & Fonts -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        :root {{
            --bg-slate: #020617;
            --bg-card: rgba(15, 23, 42, 0.9);
            --border-glow: rgba(14, 165, 233, 0.3);
            --text-light: #f8fafc;
            --text-gray: #94a3b8;
            --cyan: #06b6d4;
            --red: #ef4444;
            --emerald: #10b981;
            --yellow: #f59e0b;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-slate);
            background-image: 
                radial-gradient(at 0% 0%, rgba(239, 68, 68, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
            color: var(--text-light);
            margin: 0;
            padding: 20px;
            font-size: 16px; /* Enlarged font size for readability */
            line-height: 1.6;
        }}

        .dashboard-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 900px) {{
            .dashboard-container {{
                grid-template-columns: 1fr;
            }}
        }}

        .glass-box {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }}

        .full-span {{
            grid-column: 1 / -1;
        }}

        /* ALERT PANEL */
        .alarm-banner {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(15, 23, 42, 0.9));
            border: 2px solid var(--red);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.25);
            animation: pulse-border 2s infinite alternate;
        }}

        @keyframes pulse-border {{
            0% {{ border-color: rgba(239, 68, 68, 0.5); }}
            100% {{ border-color: rgba(239, 68, 68, 1); box-shadow: 0 0 35px rgba(239, 68, 68, 0.4); }}
        }}

        .alarm-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 20px;
            font-weight: 900;
            color: var(--red);
            margin: 0 0 5px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .alarm-desc {{
            font-size: 14px;
            color: var(--text-gray);
            margin: 0;
        }}

        /* VOICE BROADCAST APPLET */
        .voice-box {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .btn-voice {{
            background: #ef4444;
            border: 2px solid #dc2626;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 13px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        }}

        .btn-voice:hover {{
            background: #dc2626;
            transform: scale(1.05);
        }}

        .btn-voice.somali {{
            background: #0ea5e9;
            border-color: #0284c7;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
        }}

        .btn-voice.somali:hover {{
            background: #0284c7;
        }}

        /* METRICS BLOCK */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}

        .metric-card {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-3px);
            border-color: var(--cyan);
        }}

        .metric-num {{
            font-family: 'Orbitron', sans-serif;
            font-size: 36px;
            font-weight: 900;
            margin-bottom: 2px;
        }}

        .metric-label {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: bold;
            color: var(--text-gray);
            letter-spacing: 0.5px;
        }}

        /* INTERACTIVE MAP */
        #community-map {{
            height: 480px;
            border-radius: 12px;
            border: 1px solid var(--border-glow);
            overflow: hidden;
            margin-bottom: 15px;
            z-index: 10;
        }}

        /* INTERACTIVE CHECKLIST */
        .checklist-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 800;
            color: var(--cyan);
            border-bottom: 1px solid var(--border-glow);
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 15px;
        }}

        .checklist-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 12px;
            background: rgba(30, 41, 59, 0.25);
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.03);
            cursor: pointer;
            transition: background 0.2s ease;
        }}

        .checklist-item:hover {{
            background: rgba(6, 182, 212, 0.05);
        }}

        .checklist-item input[type="checkbox"] {{
            margin-top: 4px;
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}

        .checklist-text {{
            font-size: 13px;
        }}

        .checklist-text strong {{
            color: var(--cyan);
            display: block;
            margin-bottom: 2px;
        }}

        /* GENERAL DETAILS */
        .sub-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 800;
            color: var(--yellow);
            margin-top: 0;
            border-bottom: 1px solid var(--border-glow);
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}

        .desc-p {{
            font-size: 14px;
            color: #cbd5e1;
            margin-bottom: 15px;
        }}

        /* CUSTOM TOOLTIPS */
        .c-tooltip {{
            background: rgba(15, 23, 42, 0.9) !important;
            border: 1px solid var(--border-glow) !important;
            color: #f8fafc !important;
            padding: 3px 8px !important;
            font-size: 11px !important;
            font-weight: bold !important;
        }}
    </style>
</head>
<body>

    <div class="dashboard-container">
        
        <!-- 1. ALARM BANNER (FULL SPAN) -->
        <div class="glass-box alarm-banner full-span">
            <div>
                <h2 class="alarm-title">🚨 GEWAS EARLY WARNING ALERT: CATASTROPHIC INUNDATION</h2>
                <p class="alarm-desc">
                    Super El Niño Warning Active for Garissa County. High-Ground Evacuations Advised for Riverine Communities (Mororo, Madogo, Saka, Masalani).
                </p>
            </div>
            
            <div class="voice-box">
                <button class="btn-voice" onclick="speakWarning('en')">
                    🔊 Read English Warning
                </button>
                <button class="btn-voice somali" onclick="speakWarning('so')">
                    🔊 Codka digniinta (Somali)
                </button>
            </div>
        </div>

        <!-- 2. LEFT SIDE: INTERACTIVE GOOGLE HYBRID MAP -->
        <div class="glass-box">
            <h3 class="checklist-title">🗺️ Interactive Early Warning Map</h3>
            <p class="desc-p">
                Double-click points or hover to inspect water pans and schools. Defaults to Google Hybrid. Use map controls to switch layers.
            </p>
            
            <div id="community-map"></div>
            
            <div class="metrics-grid">
                <div class="metric-card" style="border-top: 3px solid var(--red);">
                    <div class="metric-num" style="color: var(--red);">{exp_sch}</div>
                    <div class="metric-label">Schools at Risk</div>
                </div>
                <div class="metric-card" style="border-top: 3px solid var(--yellow);">
                    <div class="metric-num" style="color: var(--yellow);">{exp_hlth}</div>
                    <div class="metric-label">Clinics at Risk</div>
                </div>
                <div class="metric-card" style="border-top: 3px solid var(--cyan);">
                    <div class="metric-num" style="color: var(--cyan);">{exp_bh}</div>
                    <div class="metric-label">Boreholes at Risk</div>
                </div>
            </div>
        </div>

        <!-- 3. RIGHT SIDE: ACTION CHECKLIST & STORY GUIDANCE -->
        <div class="glass-box">
            <h3 class="checklist-title">📋 Family Preparedness & Evacuation Checklist</h3>
            
            <div class="checklist-item" onclick="toggleCheck(this)">
                <input type="checkbox" id="check-1">
                <div class="checklist-text">
                    <strong>📦 Pack Emergency Supplies:</strong>
                    Collect water bottles, dry food, medical supplies, blankets, and place in a floating plastic bag.
                </div>
            </div>

            <div class="checklist-item" onclick="toggleCheck(this)">
                <input type="checkbox" id="check-2">
                <div class="checklist-text">
                    <strong>🐫 Move Livestock to High Ground:</strong>
                    Drive cows, goats, and camels away from low-lying riverbanks and seasonal lagha corridors immediately.
                </div>
            </div>

            <div class="checklist-item" onclick="toggleCheck(this)">
                <input type="checkbox" id="check-3">
                <div class="checklist-text">
                    <strong>💧 Chlorinate Drinking Water:</strong>
                    Obtain chlorine tablets from the local health worker to treat water from panels and open shallow wells.
                </div>
            </div>

            <div class="checklist-item" onclick="toggleCheck(this)">
                <input type="checkbox" id="check-4">
                <div class="checklist-text">
                    <strong>🚸 Identify Safe Shelter:</strong>
                    Locate the nearest designated school or clinic on high ground. Avoid driving or walking through moving lagha currents.
                </div>
            </div>
            
            <h3 class="sub-title" style="margin-top: 25px;">📢 Community early Warning Guidance</h3>
            <p class="desc-p">
                Under the <strong>Garissa County DRM Policy 2026</strong>, early cash transfers are triggered once precipitation parameters cross 150mm. Coordinate with local chiefs and elders to organize mutual support groups, focusing on protecting vulnerable children, disabled persons, and elderly families.
            </p>
            
            <div style="display:flex; justify-content:space-between; gap:10px; font-size:12px; color:var(--text-gray); border-top:1px solid rgba(255,255,255,0.05); padding-top:10px; font-family:monospace;">
                <span>Garissa GIS Directorate</span>
                <span>James M. Mburu</span>
            </div>
        </div>

    </div>

    <script>
        // Inject data
        const boreholesData = {bh_json};
        const schoolsData = {sch_json};

        // Initialize Map
        const map = L.map('community-map', {{
            center: [-0.45, 39.65],
            zoom: 8,
            zoomControl: true
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

        const baseMaps = {{
            "Google Hybrid (Satellite)": hybridBasemap,
            "Google Streets": streetsBasemap,
            "CartoDB Dark Matter": darkBasemap
        }};

        L.control.layers(baseMaps, null, {{ collapsed: true, position: 'topright' }}).addTo(map);

        // Add assets
        if (boreholesData.features.length > 0) {{
            L.geoJSON(boreholesData, {{
                pointToLayer: function(f, latlng) {{
                    const risk = f.properties.Risk_Level || 'Safe';
                    const color = risk === 'Safe' ? '#10b981' : (risk === 'Low Risk' ? '#fbbf24' : '#ef4444');
                    return L.circleMarker(latlng, {{
                        radius: 6,
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.85
                    }});
                }},
                onEachFeature: function(f, l) {{
                    l.bindTooltip("💧 Borehole: " + (f.properties.name || 'Borehole'), {{ className: 'c-tooltip' }});
                }}
            }}).addTo(map);
        }}

        if (schoolsData.features.length > 0) {{
            L.geoJSON(schoolsData, {{
                pointToLayer: function(f, latlng) {{
                    const risk = f.properties.Risk_Level || 'Safe';
                    const color = risk === 'Safe' ? '#10b981' : (risk === 'Low Risk' ? '#fbbf24' : '#ef4444');
                    return L.circleMarker(latlng, {{
                        radius: 5,
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.75,
                        weight: 1.5,
                        dashArray: '2,2'
                    }});
                }},
                onEachFeature: function(f, l) {{
                    l.bindTooltip("🏫 School: " + (f.properties.school_nam || 'School'), {{ className: 'c-tooltip' }});
                }}
            }}).addTo(map);
        }}

        // Text-to-Speech (TTS) Voice Broadcast
        function speakWarning(lang) {{
            if (!('speechSynthesis' in window)) {{
                alert("Your browser does not support text-to-speech voice synthesis.");
                return;
            }}
            
            // Cancel current speech
            window.speechSynthesis.cancel();
            
            let message = "";
            let voiceLang = "en-US";
            
            if (lang === 'so') {{
                message = "Attention please. Digniinta daadka ee Garissa. Fadlan ka fogow webiga oo u guur dhul sare deg deg. Badbaadi carruurta iyo xoolaha. Ka fogow kanaalada biyaha oo ku xirnaada waayeelka tuulada. Mahadsanid.";
                voiceLang = "so-SO"; // Somali fallback
            }} else {{
                message = "Attention please. Emergency flood warning for Garissa County. Extreme risk of inundation is projected. All families near river banks must evacuate immediately to higher grounds and safe shelters. Protect your livestock, save clean water, and follow directives from local chiefs. Thank you.";
                voiceLang = "en-US";
            }}
            
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.lang = voiceLang;
            utterance.rate = 0.95; // Slightly slower for clarity
            utterance.pitch = 1.0;
            
            window.speechSynthesis.speak(utterance);
        }}

        // Toggle checkbox helper
        function toggleCheck(card) {{
            const box = card.querySelector('input[type="checkbox"]');
            box.checked = !box.checked;
        }}
    </script>
</body>
</html>
"""

    with open(OUTPUT_DIR / "community_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Premium Community Dashboard compiled successfully!")

if __name__ == "__main__":
    main()
