#!/usr/bin/env bash
# Garissa DRM - Complete Pipeline Execution (Local Workdir version)
# End-to-end automation of the El Niño early warning system

echo "======================================================================"
echo "🌍 GARISSA EARLY WARNING & ADAPTATION SYSTEM (GEWAS) - LOCAL FLOOD RISK PIPELINE"
echo "======================================================================"

# 1. Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Local virtual environment activated."
else
    echo "❌ Local virtual environment .venv not found!"
    exit 1
fi

# 2. Ingest Data (conditional check)
echo -e "\n[1/6] Ingesting and Cleaning Data..."
if [ -d "GARISSA BORE HOLES" ] && [ -d "Garissa Schools" ]; then
    python3 1_data_ingestion.py
else
    echo "ℹ️  Raw shapefiles not found in local workdir. Reusing cached ingestion outputs in OUTPUT/ folder."
fi

# 3. Analyze Flood Risk
echo -e "\n[2/6] Performing Enhanced Flood Risk Analysis..."
python3 2_flood_risk_analysis.py

# 3b. Generate All 7 Interactive HTML Leaflet Maps
echo -e "\n[2b/6] Generating All 7 Interactive Leaflet Maps..."
python3 generate_all_interactive_maps.py

# 4. Generate HTML Digital Twin & Community Dashboards
echo -e "\n[3/6] Generating HTML Dashboards..."
python3 5_generate_dashboard.py
python3 generate_community_dashboard.py

# 5. Programmatic Map Generation (40 Maps & Infographics)
echo -e "\n[4/6] Generating 40 Programmatic Maps & Infographics..."
python3 6_generate_maps.py

# 6. Compile Narrative Story HTML & Post-Process
echo -e "\n[5/6] Compiling Jupyter Notebook Narrative..."
jupyter nbconvert --to html --no-input garissa_elnino_flood_risk.ipynb --output OUTPUT/garissa_flood_risk_story.html
python3 post_process_narrative.py

# 7. Export to Looker Studio
echo -e "\n[6/6] Preparing Looker Studio Exports..."
if python3 -c "import ee; ee.Initialize()" 2>/dev/null; then
    python3 4_looker_export.py
else
    echo "ℹ️  Earth Engine credentials not found or uninitialized. Skipping Looker export."
fi

echo -e "\n======================================================================"
echo "🎉 PIPELINE COMPLETE!"
echo "======================================================================"
echo "Next Steps:"
echo "1. Share the dashboard: OUTPUT/garissa_flood_risk_dashboard.html"
echo "2. View narrative story: garissa_flood_risk_story.html"
echo "3. View QGIS Workspace: Run 3_qgis_workspace_builder.py inside QGIS"
echo "4. Present Notebook: Open garissa_elnino_flood_risk.ipynb in Jupyter"
echo "======================================================================"
