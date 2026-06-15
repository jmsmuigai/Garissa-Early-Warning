#!/usr/bin/env python3
"""
Post-processes the compiled Jupyter story (garissa_flood_risk_story.html):
1. Renames it to community_participatory_maps.html
2. Injects custom CSS for a modern, colorful glassmorphic layout.
3. Adds a "Hide/Show Python Code" toggle button.
4. Adds interactive Voice Read-Aloud buttons for each chapter (TTS SpeechSynthesis).
5. Auto-inserts the 40 generated maps and infographics under their respective chapters.
Author: Garissa GIS Directorate — James M. Mburu
"""
import re
from pathlib import Path

BASE_DIR = Path("/Users/james/garissa_local_workdir")
OUTPUT_DIR = BASE_DIR / "OUTPUT"
INPUT_HTML = OUTPUT_DIR / "garissa_flood_risk_story.html"
OUTPUT_HTML = OUTPUT_DIR / "community_participatory_maps.html"

def main():
    print("🪄 Post-processing compiled Jupyter story...")
    
    if not INPUT_HTML.exists():
        print(f"❌ Input HTML missing at {INPUT_HTML}. Run nbconvert first.")
        return
        
    with open(INPUT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inject styling & show/hide code logic in <head>
    head_inject = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=Orbitron:wght@600;800;900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif !important;
            background-color: #020617 !important;
            color: #f8fafc !important;
            padding: 30px !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
            line-height: 1.6 !important;
        }
        
        /* Jupyter overrides */
        .container, #notebook, .jp-Notebook {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        .cell, .jp-Cell {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            margin-bottom: 25px !important;
        }
        
        h1, h2, h3, h4, .jp-RenderedHTMLCommon h1, .jp-RenderedHTMLCommon h2, .jp-RenderedHTMLCommon h3 {
            font-family: 'Orbitron', sans-serif !important;
            color: #06b6d4 !important;
            font-weight: 800 !important;
            margin-top: 35px !important;
            border-bottom: 1px solid rgba(6, 182, 212, 0.25) !important;
            padding-bottom: 8px !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        p, .jp-RenderedHTMLCommon p {
            font-size: 14px !important;
            color: #cbd5e1 !important;
            margin-bottom: 15px !important;
        }

        /* HIDE CODE CELLS BY DEFAULT */
        .input, .input_area, .jp-Cell-inputWrapper, .jp-InputArea {
            display: none !important;
        }
        
        /* SHOW CODE ACTIVE CLASS */
        body.show-code .input, 
        body.show-code .input_area, 
        body.show-code .jp-Cell-inputWrapper, 
        body.show-code .jp-InputArea {
            display: block !important;
            background-color: #0f172a !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 8px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
        }
        
        /* FLOATING UTILITIES BARS */
        .utility-bar {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 9999;
        }
        
        .util-btn {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(6, 182, 212, 0.3);
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: all 0.2s ease;
        }
        
        .util-btn:hover {
            background: #06b6d4;
            color: #020617;
            box-shadow: 0 0 10px #06b6d4;
            border-color: #06b6d4;
        }
        
        /* CHAPTER VOICE BUTTON */
        .chapter-tts-btn {
            background: rgba(15,23,42,0.6);
            border: 1px solid rgba(255,255,255,0.1);
            color: #10b981;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 10px;
            font-family: 'Orbitron', sans-serif;
            cursor: pointer;
            margin-left: 15px;
            transition: all 0.2s;
        }
        
        .chapter-tts-btn:hover {
            background: #10b981;
            color: #020617;
            box-shadow: 0 0 8px #10b981;
        }
        
        /* RESPONSIVE IMAGES */
        .narrative-image {
            width: 100%;
            max-width: 800px;
            border-radius: 12px;
            border: 1px solid rgba(6, 182, 212, 0.2);
            box-shadow: 0 4px 15px rgba(6,182,212,0.15);
            margin: 15px 0 25px 0;
            display: block;
        }
        
        .image-caption {
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
            margin-top: -15px;
            margin-bottom: 25px;
            font-style: italic;
        }
    </style>
    <script>
        function toggleCode() {
            document.body.classList.toggle('show-code');
            const btn = document.getElementById('btn-code-toggle');
            if (document.body.classList.contains('show-code')) {
                btn.textContent = '🙈 Hide Python Code';
            } else {
                btn.textContent = '💻 Show Python Code';
            }
        }
        
        function readText(textId) {
            if (!('speechSynthesis' in window)) {
                alert("Text-to-speech not supported in this browser.");
                return;
            }
            window.speechSynthesis.cancel();
            
            const element = document.getElementById(textId);
            if (!element) return;
            
            // Get text, clean out HTML tags
            let text = element.innerText || element.textContent;
            // Remove the Read Aloud button text from the string
            text = text.replace(/Read Aloud|Codka Akhri/gi, '').trim();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.95;
            window.speechSynthesis.speak(utterance);
        }
    </script>
    """

    # Inject styles and scripts before the closing </head>
    html = html.replace("</head>", head_inject + "\n</head>")

    # 2. Inject the code toggle utility bar right after <body> starts
    util_bar_html = """
    <div class="utility-bar">
        <button class="util-btn" id="btn-code-toggle" onclick="toggleCode()">💻 Show Python Code</button>
    </div>
    """
    html = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + util_bar_html, html)

    # 3. Add IDs to chapter headings and append Speech synthesis buttons
    # Pattern to match Chapter headings (h1, h2, h3)
    # Examples: Chapter 1: ..., Chapter 2: ...
    chapter_pattern = r"(<h[123][^>]*>)(Chapter\s+\d+:\s*.*?)(</h[123] text-align[^>]*>|</h[123]>)"
    
    chapter_counter = 0
    def replace_chapter(match):
        nonlocal chapter_counter
        chapter_counter += 1
        start_tag = match.group(1)
        title_text = match.group(2)
        end_tag = match.group(3)
        
        # We wrap the content below this chapter in a div so we can speech-read it
        text_id = f"chapter-text-{chapter_counter}"
        
        # Add a TTS button inside the header
        tts_btn = f'<button class="chapter-tts-btn" onclick="readText(\'{text_id}\')">🔊 Read Aloud</button>'
        
        # Return modified header
        return f'</div><div id="{text_id}">{start_tag}{title_text}{tts_btn}{end_tag}'

    html = re.sub(chapter_pattern, replace_chapter, html)

    # 4. Auto-insert the 40 maps and charts
    # We will search for chapter headers and insert corresponding image tags right after them
    map_embeddings = {
        1: ("21_subcounty_poverty_rates.png", "Map 21: Sub-County Population Distribution Infographic"),
        2: ("01_garissa_county_boundary.png", "Map 1: Garissa County & Subcounty boundaries reference"),
        3: ("02_elevation_srtm.png", "Map 2: Digital Elevation Terrain Model (SRTM)"),
        4: ("03_land_use_land_cover.png", "Map 3: Land Use & Land Cover Classification"),
        5: ("04_rivers_and_waterways.png", "Map 4: Hydrographic Rivers & Seasonal Channels"),
        6: ("05_road_network.png", "Map 5: Primary Transportation Network"),
        7: ("06_unosat_flood_extent_2024.png", "Map 6: UNOSAT April 2024 Historical Flood Inundation"),
        8: ("07_high_risk_zone_buffer.png", "Map 7: Early Action High Risk Zone (~500m concentric buffer)"),
        9: ("08_medium_risk_zone_buffer.png", "Map 8: Alert Level Medium Risk Zone (~1.5km concentric buffer)"),
        10: ("09_low_risk_zone_buffer.png", "Map 9: Advisory Level Low Risk Zone (~3.3km concentric buffer)"),
        11: ("10_extreme_risk_zone_buffer.png", "Map 10: Catastrophic Extreme Risk Zone (~5.5km concentric buffer)"),
        12: ("12_schools_exposure_risk.png", "Map 12: Schools Exposure & Vulnerability Risk Index"),
        13: ("13_health_facilities_exposure_risk.png", "Map 13: Health Facilities Cold-Chain Exposure"),
        14: ("14_boreholes_exposure_risk.png", "Map 14: Clean Water Boreholes Vulnerability"),
        15: ("15_idp_camps_exposure_risk.png", "Map 15: IDP Settlements Inundation Risk Profiles"),
        16: ("16_towns_exposure_risk.png", "Map 16: Township Center Hubs Risk Exposure"),
        17: ("17_dadaab_refugee_camps_overlay.png", "Map 17: Dadaab Refugee Complex Blocks Overlay"),
        18: ("18_water_pans_and_assets.png", "Map 18: Rangeland Water Pans & Water Assets Map"),
        19: ("19_dengue_risk_and_wildlife.png", "Map 19: Dengue Fever & Wildlife Habitats Map"),
        20: ("20_integrated_early_warning_master.png", "Map 20: Master early warning early action response map"),
        21: ("22_subcounty_food_poverty.png", "Map 22: Poverty Headcount Rate (%) by Sub-County"),
        22: ("23_subcounty_malnutrition_wasting.png", "Map 23: Food Poverty Headcount Index (%) by Sub-County"),
        23: ("24_monthly_precipitation_baseline.png", "Map 24: Under-5 Malnutrition Wasting Rates (%) by Sub-County"),
        24: ("25_monthly_temperature_baseline.png", "Map 25: Garissa Monthly Climate Baseline Rainfall (mm)"),
        25: ("26_rangeland_ndvi_anomaly.png", "Map 26: Garissa Monthly Climate Baseline Temperature (°C)"),
        26: ("27_evacuation_centers_shelters.png", "Map 27: Community Safe Evacuation Assembly Shelters"),
        27: ("28_soil_permeability_risk.png", "Map 28: Soil Permeability & Hydrological Inundation Risk"),
        28: ("29_groundwater_depth_yield.png", "Map 29: Groundwater Depth and Aquifer Yield Potential"),
        29: ("30_road_network_isolation_cuts.png", "Map 30: Flood Exposed Transport Network Cut-offs"),
        30: ("31_market_supply_chain_hubs.png", "Map 31: Socio-Economic Market Centers Risk Exposure"),
        31: ("32_dadaab_refugee_displacement_risk.png", "Map 32: Dadaab Camp Blocks Population Displacement Risk"),
        32: ("33_livestock_migration_paths.png", "Map 33: Livestock Migratory Paths and Veterinary Corridors"),
        33: ("34_telecom_phone_network_towers.png", "Map 34: Emergency Telecommunication Towers Coverage Areas"),
        34: ("35_malaria_vector_exposure_zones.png", "Map 35: Dengue & Rift Valley Fever Breeding Hazard Zones"),
        35: ("36_multi_hazard_early_action_matrix.png", "Map 36: DRR Early Action Trigger Levels Matrix"),
        36: ("37_schools_disruption_index.png", "Map 37: Schools Projected Inundation Displacement Projections"),
        37: ("38_health_vaccine_cold_chains_at_risk.png", "Map 38: Clinics Vaccine Cold-Chain Fridges Exposed to Inundation"),
        38: ("39_water_pan_depletion_projections.png", "Map 39: Water Pan Evaporation & Storage Depletion Projections"),
        39: ("40_comprehensive_early_warning_summary.png", "Map 40: Multi-Sector Early Warning Summary Infographic"),
    }

    # Iterate over the dict and replace in HTML
    for ch_num, (img_file, caption_text) in map_embeddings.items():
        # Search for the closing header tag for Chapter X
        header_regex = rf'(<div id="chapter-text-{ch_num}">.*?<\/h[123] text-align[^>]*>|<\/h[123]>)'
        img_html = f'\n<img src="maps/{img_file}" class="narrative-image" alt="{caption_text}" onerror="this.style.display=\'none\';"><p class="image-caption">{caption_text}</p>\n'
        
        # Inject the image right after the header ends
        html = re.sub(
            rf'(<div id="chapter-text-{ch_num}">.*?<\/h[123] text-align[^>]*>)',
            lambda m: m.group(1) + img_html,
            html,
            flags=re.DOTALL
        )

    # 5. Clean up first unmatched </div> at the very beginning
    html = html.replace("</div><div id=\"chapter-text-1\">", "<div id=\"chapter-text-1\">", 1)

    # 6. Save modified file
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
        
    # Copy to root as well
    with open(BASE_DIR / "community_participatory_maps.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ Enhanced Narrative Story saved to {OUTPUT_HTML.name} & root!")

if __name__ == "__main__":
    main()
