import re
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")

def patch_file(path: Path, replacements: list):
    if not path.exists():
        print(f"⚠️ File not found: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_len = len(content)
    for old, new in replacements:
        content = content.replace(old, new)
    
    if len(content) != original_len or any(old in content for old, _ in replacements):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Patched: {path.name}")
        return True
    else:
        print(f"ℹ️ No changes needed or already patched: {path.name}")
        return False

def main():
    print("🚀 Patching codebase for Garissa Early Warning and Adaptation System (GEWAS)...")

    # 1. Patch run_full_pipeline.sh
    run_full_pipeline_path = BASE_DIR / "run_full_pipeline.sh"
    replacements_sh = [
        ("echo \"🌍 GARISSA DIGITAL TWIN - LOCAL FLOOD RISK PIPELINE\"", "echo \"🌍 GARISSA EARLY WARNING & ADAPTATION SYSTEM (GEWAS) - LOCAL FLOOD RISK PIPELINE\""),
        ("jupyter nbconvert --to html garissa_elnino_flood_risk.ipynb --output garissa_flood_risk_story.html", 
         "jupyter nbconvert --to html --no-input garissa_elnino_flood_risk.ipynb --output garissa_flood_risk_story.html")
    ]
    patch_file(run_full_pipeline_path, replacements_sh)

    # 2. Patch restructure_notebook.py
    restructure_path = BASE_DIR / "restructure_notebook.py"
    replacements_restructure = [
        ("🛰️ Advanced Digital Twin Platform", "🛰️ Garissa Early Warning & Adaptation System (GEWAS)"),
        ("✅ 60-Chapter Digital Twin Report Restructured!", "✅ 60-Chapter Early Warning & Adaptation System (GEWAS) Restructured!")
    ]
    patch_file(restructure_path, replacements_restructure)

    # 3. Patch 6_generate_maps.py
    generate_maps_path = BASE_DIR / "6_generate_maps.py"
    replacements_maps = [
        ("Integrated Digital Twin Early Warning Master Map", "Garissa Early Warning & Adaptation System Master Map")
    ]
    patch_file(generate_maps_path, replacements_maps)

    # 4. Patch 5_generate_dashboard.py
    dashboard_path = BASE_DIR / "5_generate_dashboard.py"
    
    # Let's read the dashboard file to do specific replacements
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the replacements in 5_generate_dashboard.py
    replacements_dashboard = [
        # Title & Headings
        ("<title>Garissa County El Niño DRM Digital Twin</title>", "<title>Garissa Early Warning and Adaptation System (GEWAS)</title>"),
        ("<h1>GARISSA County El Niño DRM Digital Twin</h1>", "<h1>GARISSA EARLY WARNING AND ADAPTATION SYSTEM (GEWAS)</h1>"),
        ('<button class="nav-tab active" onclick="switchPage(\'page-digital-twin\')">🛰️ Digital Twin Map & Dashboard</button>', 
         '<button class="nav-tab active" onclick="switchPage(\'page-digital-twin\')">🛰️ Interactive Early Warning Map</button>'),
        ('<div class="map-title">🌍 Map Viewer: Interactive Digital Twin</div>', 
         '<div class="map-title">🌍 Interactive Early Warning & Adaptation System Map</div>'),
        ('<span class="bot-title">🤖 Sentinel-Bot AI DRM Advisor</span>', 
         '<span class="bot-title">🤖 GEWAS AI DRM Sentinel-Bot</span>'),
        ("title: 'Garissa County El Niño DRM Digital Twin',", "title: 'Garissa Early Warning and Adaptation System (GEWAS)',"),
        ('"🌍 GARISSA COUNTY EL NIÑO DRM DIGITAL TWIN - REPORT GENERATOR\\n" +', 
         '"🌍 GARISSA EARLY WARNING & ADAPTATION SYSTEM (GEWAS) - REPORT GENERATOR\\n" +'),
    ]

    for old, new in replacements_dashboard:
        content = content.replace(old, new)

    # Add api_keys.js script reference to head
    if 'src="api_keys.js"' not in content:
        content = content.replace("</head>", "    <!-- API keys configuration for local and server environments -->\n    <script src=\"api_keys.js\"></script>\n</head>")

    # Insert Weather CSS in stylesheet section
    weather_css = """
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
"""
    if '.weather-container' not in content:
        content = content.replace("        .ops-card {", weather_css + "\n        .ops-card {")

    # Insert Weather widget HTML card
    weather_widget_html = """
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
"""
    if 'LIVE GARISSA WEATHER' not in content:
        # Find closing tag of infographics-card and insert it there
        infographics_block_end = """                <div class="desc-box rangeland-advisory" style="margin-top:8px; padding:6px; background:rgba(16, 185, 129, 0.05); border-color:rgba(16, 185, 129, 0.2);">
                    <strong>🌿 Rangeland Advisory:</strong> rangeland vegetation greens index is high. Shift herds toward higher ground.
                </div>
            </div>"""
        content = content.replace(infographics_block_end, infographics_block_end + "\n" + weather_widget_html)

    # Insert Mission, Vision, and What We Do banner in Operations Hub
    ops_banner_html = """        <!-- System Mandate & Vision Banner -->
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
"""
    if 'STRATEGIC MANDATE & MISSION STATEMENTS' not in content:
        content = content.replace('<div class="operations-grid">', ops_banner_html + "\n        <div class=\"operations-grid\">")

    # Update settings panel HTML
    old_bot_settings = """        <!-- API settings slide panel -->
        <div id="bot-api-settings" class="bot-api-settings">
            <label style="font-weight:bold; color:var(--cyan);">CUSTOM GEMINI API KEY:</label>
            <div style="display:flex; gap:6px;">
                <input id="custom-api-key-input" type="password" placeholder="AIzaSy..." style="flex:1; padding:4px 8px; border-radius:4px; background:#0f172a; border:1px solid #334155; color:white; font-size:10px;" />
                <button onclick="saveCustomAPIKey()" style="background:var(--emerald); border:none; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer;">Save</button>
            </div>
            <span id="api-key-status" style="color:var(--text-muted); font-size:9px;">Enter your key to unlock live generative advice.</span>
        </div>"""
        
    new_bot_settings = """        <!-- API settings slide panel -->
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
        </div>"""
    content = content.replace(old_bot_settings, new_bot_settings)

    # Update settings JS functions
    old_js_settings_funcs = """        function toggleBotSettings() {
            const apiSettings = document.getElementById('bot-api-settings');
            apiSettings.style.display = (apiSettings.style.display === 'none' || !apiSettings.style.display) ? 'flex' : 'none';
            
            const savedKey = localStorage.getItem('gemini_api_key');
            if (savedKey) {
                document.getElementById('custom-api-key-input').value = savedKey;
                document.getElementById('api-key-status').textContent = "Saved custom API key active.";
                document.getElementById('api-key-status').style.color = "var(--emerald)";
            }
        }

        function saveCustomAPIKey() {
            const key = document.getElementById('custom-api-key-input').value.trim();
            if (key) {
                localStorage.setItem('gemini_api_key', key);
                document.getElementById('api-key-status').textContent = "Key saved to local storage!";
                document.getElementById('api-key-status').style.color = "var(--emerald)";
                setTimeout(() => {
                    document.getElementById('bot-api-settings').style.display = 'none';
                }, 1500);
            } else {
                localStorage.removeItem('gemini_api_key');
                document.getElementById('api-key-status').textContent = "Default key reverted.";
                document.getElementById('api-key-status').style.color = "var(--text-muted)";
            }
        }"""
        
    new_js_settings_funcs = """        function toggleBotSettings() {
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
        }"""
    content = content.replace(old_js_settings_funcs, new_js_settings_funcs)

    # Update onload handler
    old_onload = """        window.addEventListener('load', () => {
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
            
            // Auto open bot after 3.5 seconds
            setTimeout(() => {
                document.getElementById('sentinel-bot-panel').style.display = 'flex';
            }, 3500);
        });"""
        
    new_onload = """        window.addEventListener('load', () => {
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
        });"""
    content = content.replace(old_onload, new_onload)

    # Update Gemini key fallback in triggerChatbotQuery
    content = content.replace("localStorage.getItem('gemini_api_key') || 'AIzaSyDDZludrLe0owCB3jFvPWSp8b3ZBx5hBmQ'", 
                              "localStorage.getItem('gemini_api_key') || (typeof GEMINI_API_KEY !== 'undefined' ? GEMINI_API_KEY : '')")

    # Update setupAttributePopup function
    old_setup_popup = """        const setupAttributePopup = (feature, layer, icon) => {
            if (feature.properties) {
                let p = feature.properties;
                // Resolve borehole or school actual name
                let name = p.Camps_Name || p.IDP_Camp_N || p.Name_of_B || p.Borehole_N || p.school_nam || p.health_fac || p.town_name || p.parcel_id || p.name || p.Name || 'Asset';
                if (name === 'null' || name === 'nil' || name === 'None' || name === '' || name === 'Asset') {
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
                
                // Concise tooltip on hover (actual name, risk level)
                layer.bindTooltip(\'<div style="font-family:Inter; font-size:10px; font-weight:bold;">\' + name + \' (\' + risk.replace(\' Risk\', \'\') + \')</div>\', { permanent: false, direction: \'top\' });
            }
        };"""

    new_setup_popup = """        const setupAttributePopup = (feature, layer, icon) => {
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
                
                let tooltipHtml = '<div style="font-family:\'Inter\', sans-serif; font-size:11px; padding:6px; line-height:1.4; color:#ffffff; background:#0f172a; border-radius:4px; border: 1px solid var(--cyan); box-shadow: 0 4px 6px rgba(0,0,0,0.3);">';
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
        };"""
    content = content.replace(old_setup_popup, new_setup_popup)

    # Hide code blocks in the narrative story tab (line 3098 to 3105)
    old_notebook_code_parser = """                elif cell["cell_type"] == "code":
                    code_src = "".join(cell["source"]).replace("<", "&lt;").replace(">", "&gt;")
                    chapters_html.append(f\"\"\"
                    <details class="story-code-block">
                        <summary>💻 View Python Executable Code (Colab)</summary>
                        <pre><code class="language-python">{code_src}</code></pre>
                    </details>
                    \"\"\")"""
                    
    new_notebook_code_parser = """                elif cell["cell_type"] == "code":
                    # Code blocks are completely hidden from the HTML narrative view as requested
                    pass"""
    content = content.replace(old_notebook_code_parser, new_notebook_code_parser)

    # Add api_keys.js builder code before writing html
    api_keys_writer = """    # Write api_keys.js file (gitignored) to the output directory
    api_keys_js = \"\"\"// Auto-generated API keys for local workspace testing (Git-ignored)
const GEMINI_API_KEY = "";
const WEATHER_API_KEY = "";
\"\"\"
    with open(OUTPUT_DIR / "api_keys.js", "w", encoding="utf-8") as f:
        f.write(api_keys_js)
    print("🔑 Local api_keys.js file written.")
"""
    if 'api_keys.js' not in content:
        content = content.replace('with open(OUTPUT_DIR / "garissa_flood_risk_dashboard.html", "w", encoding="utf-8") as f:', 
                                  api_keys_writer + '\n    with open(OUTPUT_DIR / "garissa_flood_risk_dashboard.html", "w", encoding="utf-8") as f:')

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Finished patching 5_generate_dashboard.py!")

if __name__ == "__main__":
    main()
