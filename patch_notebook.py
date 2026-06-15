from pathlib import Path

notebook_path = Path("/Users/james/garissa_local_workdir/garissa_elnino_flood_risk.ipynb")

if notebook_path.exists():
    with open(notebook_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    replacements = [
        ("🛰️ Advanced Digital Twin Platform", "🛰️ Garissa Early Warning & Adaptation System (GEWAS)"),
        ("60-Chapter Digital Twin Report Restructured!", "60-Chapter Early Warning & Adaptation System (GEWAS) Restructured!"),
        ("Garissa County El Niño DRM Digital Twin", "Garissa Early Warning and Adaptation System (GEWAS)"),
        ("DRM Multi-Hazard Decision Support Platform", "Early Warning and Adaptation Decision Support Platform")
    ]
    
    original_len = len(content)
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(notebook_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Patched garissa_elnino_flood_risk.ipynb successfully!")
else:
    print("⚠️ Notebook file not found!")
