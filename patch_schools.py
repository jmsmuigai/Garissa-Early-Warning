import os

with open('generate_all_interactive_maps.py', 'r') as f:
    content = f.read()

# 1. Update Schools popup to include distance to borehole
old_schools = """                    onEachFeature: function(f, l) {
                        l.bindPopup(buildPopupTable(f.properties.school_nam || 'School', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏫'));
                        l.on('click', () => notifyParent(f, 'Schools'));
                    }"""

new_schools = """                    onEachFeature: function(f, l) {
                        const nearestBorehole = f.properties.Nearest_Borehole || 'Unknown';
                        const distBorehole = f.properties.Dist_to_Borehole_km ? f.properties.Dist_to_Borehole_km + ' km' : 'N/A';
                        const extraRow = `<tr><td style="padding:4px;border-bottom:1px solid rgba(255,255,255,0.1);">Nearest Borehole</td><td style="padding:4px;border-bottom:1px solid rgba(255,255,255,0.1);font-weight:bold;color:var(--cyan);">${nearestBorehole} (${distBorehole})</td></tr>`;
                        
                        let popupHtml = buildPopupTable(f.properties.school_nam || 'School', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏫');
                        popupHtml = popupHtml.replace('</tbody>', extraRow + '</tbody>');
                        
                        l.bindPopup(popupHtml);
                        l.on('click', () => notifyParent(f, 'Schools'));
                    }"""

content = content.replace(old_schools, new_schools)

# 2. Update Health Clinics popup to include distance to borehole
old_health = """                    onEachFeature: function(f, l) {
                        l.bindPopup(buildPopupTable(f.properties.health_fac || 'Clinic', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏥'));
                        l.on('click', () => notifyParent(f, 'Health Facilities'));
                    }"""

new_health = """                    onEachFeature: function(f, l) {
                        const nearestBorehole = f.properties.Nearest_Borehole || 'Unknown';
                        const distBorehole = f.properties.Dist_to_Borehole_km ? f.properties.Dist_to_Borehole_km + ' km' : 'N/A';
                        const extraRow = `<tr><td style="padding:4px;border-bottom:1px solid rgba(255,255,255,0.1);">Nearest Borehole</td><td style="padding:4px;border-bottom:1px solid rgba(255,255,255,0.1);font-weight:bold;color:var(--cyan);">${nearestBorehole} (${distBorehole})</td></tr>`;
                        
                        let popupHtml = buildPopupTable(f.properties.health_fac || 'Clinic', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '🏥');
                        popupHtml = popupHtml.replace('</tbody>', extraRow + '</tbody>');
                        
                        l.bindPopup(popupHtml);
                        l.on('click', () => notifyParent(f, 'Health Facilities'));
                    }"""

content = content.replace(old_health, new_health)

with open('generate_all_interactive_maps.py', 'w') as f:
    f.write(content)

print("Patched popups in generate_all_interactive_maps.py")
