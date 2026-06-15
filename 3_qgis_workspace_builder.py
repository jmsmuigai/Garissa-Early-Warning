#!/usr/bin/env python3
"""
Step 3: QGIS Workspace Builder via PyQGIS (Advanced)
Loads all risk layers, flood zones, infrastructure, rivers, roads, towns,
and the new wildlife, water pans, and cadastral datasets.
Applies professional risk-based color symbology automatically.
Author: Garissa GIS Directorate — James M. Mburu
"""
from pathlib import Path
import os

try:
    from qgis.core import (
        QgsProject,
        QgsVectorLayer,
        QgsRasterLayer,
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsSymbol,
        QgsRendererCategory,
        QgsCategorizedSymbolRenderer,
        QgsSingleSymbolRenderer,
        QgsSimpleFillSymbolLayer,
        QgsSimpleLineSymbolLayer,
        QgsSimpleMarkerSymbolLayer,
        QgsMarkerSymbol,
        QgsFillSymbol,
        QgsLineSymbol,
        QgsRuleBasedRenderer,
        QgsPalLayerSettings,
        QgsTextFormat,
        QgsTextBufferSettings,
        QgsVectorLayerSimpleLabeling,
        QgsCoordinateReferenceSystem,
    )
    from qgis.PyQt.QtGui import QColor, QFont
    from qgis.PyQt.QtCore import QVariant
except ImportError:
    print("⚠️ QGIS Python modules not found. This script must be run inside QGIS or via qgis_mcp.")
    import sys
    sys.exit(0)

try:
    from qgis.utils import iface
except ImportError:
    iface = None

try:
    BASE_DIR = Path(__file__).parent
except NameError:
    BASE_DIR = Path('/Users/james/Library/CloudStorage/GoogleDrive-jmsmuigai@gmail.com/My Drive/GARISSADRM')
OUTPUT_DIR = BASE_DIR / "OUTPUT"

# ═══════════════════════════════════════════════════════════════════════════
# COLOR PALETTE — Vibrant risk-based colors
# ═══════════════════════════════════════════════════════════════════════════
RISK_COLORS = {
    "Extreme Risk (Super El Niño)": QColor(147, 51, 234, 200), # Vivid purple
    "High Risk":    QColor(220, 38, 38, 200),     # Vivid red
    "Medium Risk":  QColor(245, 158, 11, 200),     # Warm orange
    "Low Risk":     QColor(250, 204, 21, 200),     # Bright yellow
    "Safe":         QColor(34, 197, 94, 200),      # Emerald green
}

FLOOD_ZONE_COLORS = {
    "extreme_risk_zone": QColor(168, 85, 247, 100), # Semi-transparent purple
    "high_risk_zone":   QColor(239, 68, 68, 80),   # Semi-transparent red
    "medium_risk_zone": QColor(251, 146, 60, 60),   # Semi-transparent orange
    "low_risk_zone":    QColor(253, 224, 71, 40),   # Semi-transparent yellow
}


def _set_html_map_tip(layer):
    """Configure dynamic HTML Map Tips showing all attributes on hover."""
    fields = [field.name() for field in layer.fields()]
    rows_html = ""
    for f in fields:
        if f.lower() not in ['geometry', 'geom', 'fid', 'id', 'objectid', 'marker_emoji', 'author']:
            rows_html += f"<tr><td style='padding:4px; font-weight:bold; border-bottom:1px solid #ddd; color:#0f172a;'>{f}:</td><td style='padding:4px; border-bottom:1px solid #ddd; color:#334155;'>[% \"{f}\" %]</td></tr>"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; font-size: 11px; background-color: #ffffff; border: 2px solid #0ea5e9; border-radius: 8px; padding: 10px; min-width: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
        <table style="width: 100%; border-collapse: collapse;">
            {rows_html}
        </table>
        <div style="margin-top: 5px; font-size: 8px; color: #64748b; font-weight: bold; font-family: monospace;">Garissa GIS Directorate — James M. Mburu</div>
    </div>
    """
    layer.setMapTipTemplate(html_content)


def _apply_risk_symbology(layer, geom_type="point", marker_name="circle"):
    """Apply categorized risk-based color symbology to a layer with custom marker shapes."""
    categories = []
    
    for risk_level, color in RISK_COLORS.items():
        if geom_type == "point":
            symbol = QgsMarkerSymbol.createSimple({
                'name': marker_name,
                'size': '5.0' if marker_name != 'circle' else '4.5',
                'color': color.name(),
                'outline_color': '#ffffff',
                'outline_width': '0.5',
            })
        else:
            symbol = QgsFillSymbol.createSimple({
                'color': color.name(),
                'outline_color': '#1e293b',
                'outline_width': '0.5',
            })
        
        cat = QgsRendererCategory(risk_level, symbol, risk_level)
        categories.append(cat)
    
    renderer = QgsCategorizedSymbolRenderer('Risk_Level', categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def _style_subcounties(layer):
    """Apply outline and label formatting to Subcounties layer."""
    symbol = QgsFillSymbol.createSimple({
        'color': '0,0,0,0',
        'outline_color': '#06b6d4', # Cyan
        'outline_width': '1.2',
        'outline_style': 'solid',
    })
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Inter", 10))
    text_format.setSize(10)
    text_format.setColor(QColor("#06b6d4"))
    
    font = text_format.font()
    font.setBold(True)
    text_format.setFont(font)
    
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1.5)
    buffer_settings.setColor(QColor("#020617"))
    text_format.setBuffer(buffer_settings)
    
    settings = QgsPalLayerSettings()
    settings.fieldName = "sub_county"
    settings.isExpression = False
    settings.setFormat(text_format)
    
    labeling = QgsVectorLayerSimpleLabeling(settings)
    layer.setLabeling(labeling)
    layer.setLabelsEnabled(True)
    layer.triggerRepaint()


def _style_wards(layer):
    """Apply outline and label formatting to Wards layer."""
    symbol = QgsFillSymbol.createSimple({
        'color': '0,0,0,0',
        'outline_color': '#f97316', # Orange
        'outline_width': '0.8',
        'outline_style': 'dash',
    })
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Inter", 8))
    text_format.setSize(8)
    text_format.setColor(QColor("#f97316"))
    
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1.2)
    buffer_settings.setColor(QColor("#020617"))
    text_format.setBuffer(buffer_settings)
    
    settings = QgsPalLayerSettings()
    settings.fieldName = "ward"
    settings.isExpression = False
    settings.setFormat(text_format)
    
    labeling = QgsVectorLayerSimpleLabeling(settings)
    layer.setLabeling(labeling)
    layer.setLabelsEnabled(True)
    layer.triggerRepaint()


def _load_vector(filepath, name, group, project, style_func=None, filter_expr=None):
    """Load a vector layer, disable labels, configure Map Tips, and add to group."""
    if not filepath.exists():
        print(f"   ⚠️  Not found: {filepath.name}")
        return None
    
    print(f"   ⏳ Loading {name} ({filepath.name})...", end="", flush=True)
    
    layer = QgsVectorLayer(str(filepath), name, "ogr")
    if not layer.isValid():
        print(f"\r   ❌ Invalid layer: {filepath.name}       ")
        return None
    
    if filter_expr:
        layer.setSubsetString(filter_expr)
        
    project.addMapLayer(layer, False)
    group.insertChildNode(-1, QgsLayerTreeLayer(layer))
    
    layer.setLabelsEnabled(False)
    _set_html_map_tip(layer)
    
    if style_func:
        style_func(layer)
    
    print(f"\r   ✅ Loaded {name} (Ready)       ")
    return layer


def _load_raster(filepath, name, group, project, style_func=None):
    """Load a raster layer, apply optional styling, and add to group."""
    if not filepath.exists():
        print(f"   ⚠️  Not found: {filepath.name}")
        return None
    
    print(f"   ⏳ Loading {name} ({filepath.name})...", end="", flush=True)
    
    layer = QgsRasterLayer(str(filepath), name)
    if not layer.isValid():
        print(f"\r   ❌ Invalid layer: {filepath.name}       ")
        return None
        
    project.addMapLayer(layer, False)
    group.insertChildNode(-1, QgsLayerTreeLayer(layer))
    
    if style_func:
        style_func(layer)
    
    print(f"\r   ✅ Loaded {name} (Ready)       ")
    return layer


def build_qgis_workspace():
    """Build a professionally styled QGIS workspace for Garissa DRM."""
    
    if iface is not None:
        iface.mapCanvas().freeze(True)
    
    try:
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        
        print("🧹 Clearing old workspace layers to prevent duplicates...")
        project.removeAllMapLayers()
        root = project.layerTreeRoot()
        root.removeAllChildren()
        
        # ── Create layer tree groups ──────────────────────────────────────
        infra_group     = root.insertGroup(0, "🏫 Infrastructure Risk Profiles")
        wildlife_group  = root.insertGroup(1, "🦒 Wildlife & Sanctuaries")
        settle_group    = root.insertGroup(2, "🏘️ Settlements & Camps")
        hazard_group    = root.insertGroup(3, "🌊 Flood Hazard Zones")
        transport_group = root.insertGroup(4, "🛣️ Transport & Utilities")
        base_group      = root.insertGroup(5, "🗺️ Base Layers")
        
        print("=" * 60)
        print("🌍 GARISSA DRM — Building Complete QGIS Workspace")
        print("=" * 60)
        
        # ── Base Layers ───────────────────────────────────────────────────
        print("\n📍 Loading Base Layers...")
        
        # Garissa boundary
        county_layer = _load_vector(
            BASE_DIR / "garissa_county.shp",
            "Garissa County Boundary",
            base_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsFillSymbol.createSimple({
                    'color': '0,0,0,0',
                    'outline_color': '#0ea5e9',
                    'outline_width': '1.5',
                    'outline_style': 'solid',
                })
            ))
        )
        
        # Subcounty boundaries
        _load_vector(
            OUTPUT_DIR / "garissa_subcounties.geojson",
            "Garissa Subcounties",
            base_group, project,
            style_func=_style_subcounties
        )
        
        # Ward boundaries
        _load_vector(
            OUTPUT_DIR / "garissa_wards.geojson",
            "Garissa Wards",
            base_group, project,
            style_func=_style_wards
        )
        
        # Rivers & Waterways (Clipped in analysis)
        _load_vector(
            OUTPUT_DIR / "rivers.geojson",
            "Rivers & Waterways",
            base_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsLineSymbol.createSimple({
                    'color': '#0ea5e9',
                    'width': '1.0',
                })
            ))
        )
        
        # Buildings
        _load_vector(
            OUTPUT_DIR / "PROJECTED BUILDINGS.gpkg",
            "Buildings",
            base_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsFillSymbol.createSimple({
                    'color': '#475569',
                    'outline_color': '#334155',
                    'outline_width': '0.3',
                })
            ))
        )
        
        # Elevation
        _load_raster(
            OUTPUT_DIR / "PROJECTED SRTM.tif",
            "Elevation",
            base_group, project
        )
        
        # Land Use Land Cover
        _load_raster(
            OUTPUT_DIR / "Clipped Land Use.tif",
            "Land Use Land Cover",
            base_group, project
        )
        
        # Google Hybrid XYZ Tile Layer
        print("   ⏳ Loading Google Hybrid Tiles...")
        google_url = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dy%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=20&zmin=0"
        google_hybrid = QgsRasterLayer(google_url, "Google Hybrid", "wms")
        if google_hybrid.isValid():
            project.addMapLayer(google_hybrid, False)
            base_group.insertChildNode(-1, QgsLayerTreeLayer(google_hybrid))
            print("   ✅ Google Hybrid loaded.")
            
        # ── Transport & Utilities ─────────────────────────────────────────
        print("\n🛣️  Loading Transport...")
        roads_subgroup = transport_group.insertGroup(0, "Roads")
        
        _load_vector(
            OUTPUT_DIR / "roads_risk_assessed.geojson",
            "Primary Roads", roads_subgroup, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsLineSymbol.createSimple({
                    'color': '#f87171',
                    'width': '0.8',
                })
            ))
        )
        
        # ── Settlements & Camps ───────────────────────────────────────────
        print("\n🏘️  Loading Settlements & Camps...")
        
        # Towns - Risk Assessed
        _load_vector(
            OUTPUT_DIR / "towns_risk_assessed.geojson",
            "Towns", settle_group, project,
            style_func=lambda l: _apply_risk_symbology(l, "point", "square")
        )
        
        # Refugee Camps - Risk Assessed
        _load_vector(
            OUTPUT_DIR / "idp_camps_risk_assessed.geojson",
            "Refugee Camps", settle_group, project,
            style_func=lambda l: _apply_risk_symbology(l, "point", "triangle")
        )
        
        # Dadaab Camp blocks
        dadaab_blocks = [
            ("Dagahaley.geojson", "Dagahaley Camp Block"),
            ("Hagadera.geojson", "Hagadera Camp Block"),
            ("Ifo.geojson", "Ifo Camp Block")
        ]
        for fname, lname in dadaab_blocks:
            _load_vector(
                OUTPUT_DIR / fname,
                lname, settle_group, project,
                style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                    QgsFillSymbol.createSimple({
                        'color': '#f472b650',
                        'outline_color': '#db2777',
                        'outline_width': '0.6',
                    })
                ))
            )
            
        # Cadastral Parcels Layer (Township)
        _load_vector(
            OUTPUT_DIR / "cadastral_parcels_risk_assessed.geojson",
            "Garissa Township Cadastral Map",
            settle_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsFillSymbol.createSimple({
                    'color': '0,0,0,0',
                    'outline_color': '#f59e0b',
                    'outline_width': '0.8',
                    'outline_style': 'dash',
                })
            ))
        )
        
        # ── Flood Hazard Zones (Non-overlapping bands) ────────────────────
        print("\n🌊 Loading Flood Hazard Zones...")
        
        _load_vector(
            BASE_DIR / "flood_extents.shp",
            "⚠️ UNOSAT April 2024 Flood Extent",
            hazard_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsFillSymbol.createSimple({
                    'color': '#3b82f640',
                    'outline_color': '#1d4ed8',
                    'outline_width': '1.0',
                })
            ))
        )
        
        zones = [
            ("high_risk_zone.geojson",   "High Risk Zone (~500m)",    FLOOD_ZONE_COLORS["high_risk_zone"]),
            ("medium_risk_zone.geojson", "Medium Risk Zone (~1.5km)", FLOOD_ZONE_COLORS["medium_risk_zone"]),
            ("low_risk_zone.geojson",    "Low Risk Zone (~3.3km)",    FLOOD_ZONE_COLORS["low_risk_zone"]),
            ("extreme_risk_zone.geojson", "Extreme Risk Zone (~5.5km)", FLOOD_ZONE_COLORS["extreme_risk_zone"])
        ]
        for fname, lname, color in zones:
            _load_vector(
                OUTPUT_DIR / fname, lname, hazard_group, project,
                style_func=lambda l, c=color: l.setRenderer(QgsSingleSymbolRenderer(
                    QgsFillSymbol.createSimple({
                        'color': f'{c.red()},{c.green()},{c.blue()},{c.alpha()}',
                        'outline_color': c.name(),
                        'outline_width': '0.5',
                        'outline_style': 'dash',
                    })
                ))
            )
            
        # ── Wildlife & Sanctuaries ────────────────────────────────────────
        print("\n🦒 Loading Wildlife & Sanctuaries...")
        _load_vector(
            OUTPUT_DIR / "wildlife_risk_assessed.geojson",
            "Wildlife Habitat corridors",
            wildlife_group, project,
            style_func=lambda l: l.setRenderer(QgsSingleSymbolRenderer(
                QgsMarkerSymbol.createSimple({
                    'name': 'star',
                    'size': '5.0',
                    'color': '#10b981',
                    'outline_color': '#ffffff',
                })
            ))
        )
        
        # ── Infrastructure Risk Profiles ──────────────────────────────────
        print("\n🏫 Loading Infrastructure Risk Profiles...")
        
        infra_risk_layers = [
            ("schools_risk_assessed.geojson",          "Schools - Risk Assessment"),
            ("health_facilities_risk_assessed.geojson", "Health Facilities - Risk Assessment"),
            ("boreholes_risk_assessed.geojson",         "Boreholes - Risk Assessment"),
            ("water_pans_risk_assessed.geojson",        "Water Pans - Risk Assessment")
        ]
        for fname, lname in infra_risk_layers:
            marker = 'circle'
            if 'schools' in fname:
                marker = 'diamond'
            elif 'health_facilities' in fname:
                marker = 'cross'
            elif 'water_pans' in fname:
                marker = 'hexagon'
            elif 'boreholes' in fname:
                marker = 'circle'
                
            _load_vector(
                OUTPUT_DIR / fname, lname, infra_group, project,
                style_func=lambda l, m=marker: _apply_risk_symbology(l, "point", m)
            )
        
        if county_layer and iface:
            canvas = iface.mapCanvas()
            canvas.setExtent(county_layer.extent())
            canvas.refresh()
            print("\n🔍 Zoomed to Garissa County extent")
        
        # Save project
        project_path = str(BASE_DIR / "GarissaDRM_ElNino_2026.qgz")
        project.write(project_path)
        print(f"\n💾 Project saved → GarissaDRM_ElNino_2026.qgz")
        
        print("\n" + "=" * 60)
        print("✅ GARISSA DRM WORKSPACE READY!")
        print("   Author: Garissa GIS Directorate — James M. Mburu")
        print("=" * 60)
        
        if iface is not None:
            iface.messageBar().pushMessage(
                "🌍 Garissa DRM",
                "Complete early warning workspace loaded! Author: Garissa GIS Directorate — James M. Mburu",
                level=0, duration=8
            )
    
    finally:
        if iface is not None:
            iface.mapCanvas().freeze(False)
            iface.mapCanvas().refresh()


# Execute when loaded in QGIS console
build_qgis_workspace()
