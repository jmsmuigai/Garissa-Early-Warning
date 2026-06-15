import json
from pathlib import Path

notebook_path = Path("/Users/james/garissa_local_workdir/garissa_elnino_flood_risk.ipynb")

if not notebook_path.exists():
    print("❌ Notebook file not found!")
    exit(1)

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# 1. Define the make_folium_popup helper to inject in imports (cell 3)
popup_helper = '''
def make_folium_popup(row, name_col, risk_col, color, icon):
    p = row.to_dict()
    name = str(p.get(name_col, 'Asset')).strip()
    risk = p.get(risk_col, 'Safe')
    v = p.get('NN_Vulnerability_Score', p.get('Vulnerability_Index', '0.0'))
    
    vuln_badge = f'<div style="background:{color}; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; margin-bottom:8px; display:inline-block; font-size:10px;">NN VULNERABILITY: {v}</div>'
    
    # Add Shirika Plan caption if this is a Refugee Camp
    if icon in ['🏕️', '⛺'] or 'camp' in name.lower() or ('Type' in p and 'camp' in str(p['Type']).lower()):
        vuln_badge += '<div style="background:#0d9488; color:white; padding:6px 10px; border-radius:4px; font-weight:bold; margin-bottom:8px; font-size:10px; line-height:1.4;">🎪 SHIRIKA PLAN INTEGRATION: Transitioning Dadaab camps from restricted encampments to integrated socio-economic settlements.</div>'
        
    rows = ""
    skip_keys = ['geometry', 'geom', 'fid', 'id', 'objectid', 'Vulnerability_Index', 'marker_emoji', 'Author', name_col, risk_col, 'NN_Vulnerability_Score', 'NN_Risk_Class']
    for key, val in p.items():
        if key not in skip_keys and val not in [None, 'null', 'nil', 'None', '']:
            nice_key = key.replace('_', ' ').upper()
            rows += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px; font-weight:bold; color:#06b6d4;">{nice_key}:</td><td style="padding:4px; color:#ffffff;">{val}</td></tr>'
            
    content = f"""
    <div style="font-family: Arial, sans-serif; font-size: 11px; max-width: 250px; padding: 5px; color:#f8fafc; background-color:#0f172a; border-radius:8px;">
        <h4 style="margin: 0 0 6px; color: {color}; font-weight:700; border-bottom: 1px solid rgba(14, 165, 233, 0.25); padding-bottom: 4px;">{icon} {name}</h4>
        {vuln_badge}
        <div style="max-height: 150px; overflow-y: auto;">
            <table style="width:100%; border-collapse:collapse;">
                {rows}
            </table>
        </div>
    </div>
    """
    import folium
    return folium.Popup(content, max_width=250)
'''

# 2. Iterate and patch cells
patched_count = 0
for i, cell in enumerate(nb.get("cells", [])):
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        
        # Inject popup helper to imports cell (typically cell 3)
        if "from folium.plugins import MarkerCluster" in source and "make_folium_popup" not in source:
            cell["source"].append("\n# Enriched popup builder\n" + popup_helper + "\n")
            print(f"✅ Injected popup helper into cell {i}")
            patched_count += 1
            
        # Patch Health Facilities map (cell 49)
        elif "🏥 Generating Interactive Health Facilities Risk Map..." in source:
            source = source.replace("tiles='CartoDB dark_matter'", "tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid Satellite', name='Google Hybrid'")
            # Add TileLayer for dark matter as alternative
            source = source.replace("m_health = folium.Map(", "m_health = folium.Map(")
            source = source.replace("name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_health)", "name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_health)\n\nfolium.TileLayer('CartoDB dark_matter', name='Dark Matter').add_to(m_health)\nfolium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m_health)")
            
            # Replace popup builder
            old_popup_block = """        popup_html = f\"\"\"
        <div style="font-family: Arial, sans-serif; font-size: 12px;">
            <h4 style="margin: 0; color: {color};">{name}</h4>
            <b>Level:</b> {level}<br>
            <b>Risk Status:</b> {risk}<br>
            <b>Distance to Flood:</b> {dist} km
        </div>
        \"\"\"
        
        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(h_cluster)"""
        
            new_popup_block = """        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=make_folium_popup(row, 'health_fac', 'Risk_Level', color, '🏥')
        ).add_to(h_cluster)"""
            source = source.replace(old_popup_block, new_popup_block)
            cell["source"] = [line + "\n" for line in source.split("\n") if line]
            print(f"✅ Patched Health Facilities map in cell {i}")
            patched_count += 1
            
        # Patch Schools map (cell 52)
        elif "🏫 Generating Interactive Schools Risk Map..." in source:
            source = source.replace("tiles='CartoDB dark_matter'", "tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid Satellite', name='Google Hybrid'")
            source = source.replace("name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_schools)", "name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_schools)\n\nfolium.TileLayer('CartoDB dark_matter', name='Dark Matter').add_to(m_schools)\nfolium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m_schools)")
            
            old_popup_block = """        popup_html = f\"\"\"
        <div style="font-family: Arial, sans-serif; font-size: 12px;">
            <h4 style="margin: 0; color: {color};">{name}</h4>
            <b>Level:</b> {level}<br>
            <b>Risk Status:</b> {risk}<br>
            <b>Distance to Flood:</b> {dist} km
        </div>
        \"\"\"
        
        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(marker_cluster)"""
            
            new_popup_block = """        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=make_folium_popup(row, 'school_nam', 'Risk_Level', color, '🏫')
        ).add_to(marker_cluster)"""
            source = source.replace(old_popup_block, new_popup_block)
            cell["source"] = [line + "\n" for line in source.split("\n") if line]
            print(f"✅ Patched Schools map in cell {i}")
            patched_count += 1
            
        # Patch Boreholes map (cell 56)
        elif "💧 Generating Interactive Boreholes Risk Map..." in source:
            source = source.replace("tiles='CartoDB dark_matter'", "tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid Satellite', name='Google Hybrid'")
            source = source.replace("name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_boreholes)", "name='🟣 Extreme Risk Zone (~5.5km)'\n    ).add_to(m_boreholes)\n\nfolium.TileLayer('CartoDB dark_matter', name='Dark Matter').add_to(m_boreholes)\nfolium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m_boreholes)")
            
            old_popup_block = """        popup_html = f\"\"\"
        <div style="font-family: Arial, sans-serif; font-size: 12px;">
            <h4 style="margin: 0; color: {color};">{name} ({code})</h4>
            <b>Risk Status:</b> {risk}<br>
            <b>Distance to Flood:</b> {dist} km
        </div>
        \"\"\"
        
        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(b_cluster)"""
            
            new_popup_block = """        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=make_folium_popup(row, 'name', 'Risk_Level', color, '💧')
        ).add_to(b_cluster)"""
            source = source.replace(old_popup_block, new_popup_block)
            cell["source"] = [line + "\n" for line in source.split("\n") if line]
            print(f"✅ Patched Boreholes map in cell {i}")
            patched_count += 1
            
        # Patch Master Map (cell 73)
        elif "🗺️  Assembling Master Operational Risk Map..." in source:
            source = source.replace("tiles='CartoDB dark_matter'", "tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid Satellite', name='Google Hybrid'")
            source = source.replace("name='📍 Garissa County Boundary'\n    ).add_to(m_master)", "name='📍 Garissa County Boundary'\n    ).add_to(m_master)\n\nfolium.TileLayer('CartoDB dark_matter', name='Dark Matter').add_to(m_master)\nfolium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m_master)")
            
            # Replace popups for schools, health, boreholes in master map
            source = source.replace('popup=f"🏫 <b>{row.get(\'school_nam\', \'School\')}</b><br>Risk: {risk}"', "popup=make_folium_popup(row, 'school_nam', 'Risk_Level', color, '🏫')")
            source = source.replace('popup=f"🏥 <b>{row.get(\'health_fac\', \'Health Facility\')}</b><br>Risk: {risk}"', "popup=make_folium_popup(row, 'health_fac', 'Risk_Level', color, '🏥')")
            source = source.replace('popup=f"💧 <b>{row.get(\'name\', \'Borehole\')}</b><br>Risk: {risk}"', "popup=make_folium_popup(row, 'name', 'Risk_Level', color, '💧')")
            
            cell["source"] = [line + "\n" for line in source.split("\n") if line]
            print(f"✅ Patched Master Operational Map in cell {i}")
            patched_count += 1

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print(f"🎉 Successfully completed patching of {patched_count} items in notebook!")
