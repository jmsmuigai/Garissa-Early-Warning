import os

with open('generate_all_interactive_maps.py', 'r') as f:
    content = f.read()

# 1. Add the waterDropIcon
target_icon_inject = "        function initAllLayers() {\n            overlays = {};"
replacement_icon_inject = """        const waterDropIcon = L.divIcon({
            className: 'custom-water-drop',
            html: `<svg viewBox="0 0 24 24" width="24" height="24"><path fill="rgba(14, 165, 233, 0.4)" stroke="#0ea5e9" stroke-width="2" d="M12,21.5c-3.6,0-6.5-2.9-6.5-6.5c0-4.1,6.5-13.5,6.5-13.5s6.5,9.4,6.5,13.5C18.5,18.6,15.6,21.5,12,21.5z"/><circle cx="12" cy="16" r="2.5" fill="#38bdf8"/></svg>`,
            iconSize: [24, 24],
            iconAnchor: [12, 24],
            popupAnchor: [0, -24]
        });

        function initAllLayers() {
            overlays = {};"""

content = content.replace(target_icon_inject, replacement_icon_inject)

# 2. Update Boreholes layer
old_boreholes = """            if (typeof boreholesData !== 'undefined' && boreholesData.features && boreholesData.features.length > 0) {
                overlays["💧 Boreholes (Styled)"] = L.geoJSON(boreholesData, {
                    pointToLayer: function(f, latlng) {
                        const risk = f.properties.Risk_Level || 'Safe';
                        return L.marker(latlng, { icon: getCyberIcon(riskColors[risk] || '#9ca3af', 'B') });
                    },
                    onEachFeature: function(f, l) {
                        l.bindPopup(buildPopupTable(f.properties.name || 'Borehole', f.properties.code || 'N/A', f.properties.status || 'ACTIVE', f.properties.Risk_Level || 'Safe', f.properties.Distance_to_Flood_km || '0.0', f.properties.Vulnerability_Index || f.properties.NN_Vulnerability_Score || '0.0', '💧'));
                        l.on('click', () => notifyParent(f, 'Boreholes'));
                    }
                });
            }"""

new_boreholes = """            if (typeof boreholesData !== 'undefined' && boreholesData.features && boreholesData.features.length > 0) {
                overlays["💧 Boreholes (2022 Update)"] = L.geoJSON(boreholesData, {
                    pointToLayer: function(f, latlng) {
                        return L.marker(latlng, { icon: waterDropIcon });
                    },
                    onEachFeature: function(f, l) {
                        const name = f.properties.Village || 'Unnamed Borehole';
                        const status = f.properties.Status || 'UNKNOWN';
                        const yield_m3 = f.properties.Yield_m3_hr || 'N/A';
                        const depth = f.properties.Depth_m || 'N/A';
                        l.bindPopup(buildPopupTable(name, `Yield: ${yield_m3} m³/hr`, status, `Depth: ${depth}m`, 'N/A', 'N/A', '💧'));
                        l.bindTooltip(`Borehole: ${name}`, { className: 'custom-tooltip' });
                        l.on('click', () => notifyParent(f, 'Boreholes'));
                    }
                });
            }"""

content = content.replace(old_boreholes, new_boreholes)

# 3. Update Water Pans layer
old_waterpans = """            if (typeof waterPansData !== 'undefined' && waterPansData.features && waterPansData.features.length > 0) {
                overlays["🪣 Rangeland Water Pans"] = L.geoJSON(waterPansData, {
                    pointToLayer: function(f, latlng) {
                        return L.circleMarker(latlng, { radius: 5, color: '#00f3ff', fillColor: '#00f3ff', fillOpacity: 0.6 });
                    },
                    onEachFeature: function(f, l) {
                        l.bindTooltip("Water Pan: " + (f.properties.name || 'Unit'), { className: 'custom-tooltip' });
                    }
                });
            }"""

new_waterpans = """            if (typeof waterPansData !== 'undefined' && waterPansData.features && waterPansData.features.length > 0) {
                overlays["🪣 Water Pans (2023 Update)"] = L.geoJSON(waterPansData, {
                    pointToLayer: function(f, latlng) {
                        return L.marker(latlng, { icon: waterDropIcon });
                    },
                    onEachFeature: function(f, l) {
                        const name = f.properties.Name || 'Unnamed Water Pan';
                        const capacity = f.properties.Capacity_m3 || 'N/A';
                        l.bindPopup(buildPopupTable(name, `Capacity: ${capacity} m³`, f.properties.Status || 'UNKNOWN', 'Water Pan', 'N/A', 'N/A', '🪣'));
                        l.bindTooltip(`Water Pan: ${name}`, { className: 'custom-tooltip' });
                    }
                });
            }"""

content = content.replace(old_waterpans, new_waterpans)

# 4. Update the layer strings in default maps at the bottom
content = content.replace('"💧 Boreholes (Styled)"', '"💧 Boreholes (2022 Update)"')
content = content.replace('"🪣 Rangeland Water Pans"', '"🪣 Water Pans (2023 Update)"')

# 5. Fix file name loading in the array fallback
content = content.replace("['boreholesData', 'boreholes_risk_assessed.geojson']", "['boreholesData', 'boreholes_updated.geojson']")
content = content.replace("['waterPansData', 'water_pans_risk_assessed.geojson']", "['waterPansData', 'water_pans_updated.geojson']")

with open('generate_all_interactive_maps.py', 'w') as f:
    f.write(content)

print("Patched generate_all_interactive_maps.py")
