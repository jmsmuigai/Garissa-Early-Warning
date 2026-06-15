import re
from pathlib import Path

file_path = Path("/Users/james/garissa_local_workdir/5_generate_dashboard.py")

if not file_path.exists():
    print("❌ 5_generate_dashboard.py not found!")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Patch markdown parser to support images
old_markdown_parser = """                    # Convert markdown headings to nice HTML tags
                    src = re.sub(r'^#\\s+(.+)$', r'<h1 class="story-h1">\\1</h1>', src, flags=re.MULTILINE)
                    src = re.sub(r'^##\\s+(.+)$', r'<h2 class="story-h2">\\1</h2>', src, flags=re.MULTILINE)
                    src = re.sub(r'^###\\s+(.+)$', r'<h3 class="story-h3">\\1</h3>', src, flags=re.MULTILINE)
                    src = re.sub(r'\\*\\*(.+?)\\*\\*', r'<strong>\\1</strong>', src)
                    src = re.sub(r'\\*(.+?)\\*', r'<em>\\1</em>', src)
                    src = src.replace('\\n', '<br>')"""

# Note the extra escapes for regex strings in python script
new_markdown_parser = """                    # Convert markdown images to responsive HTML images
                    src = re.sub(r'!\\[(.*?)\\]\\((.*?)\\)', r'<img src="\\2" alt="\\1" style="max-width:100%; border-radius:8px; border: 1px solid var(--border-glow); margin: 10px 0; display:block; box-shadow:0 0 15px rgba(6,182,212,0.15);">', src)
                    
                    # Convert markdown headings to nice HTML tags
                    src = re.sub(r'^#\\s+(.+)$', r'<h1 class="story-h1">\\1</h1>', src, flags=re.MULTILINE)
                    src = re.sub(r'^##\\s+(.+)$', r'<h2 class="story-h2">\\1</h2>', src, flags=re.MULTILINE)
                    src = re.sub(r'^###\\s+(.+)$', r'<h3 class="story-h3">\\1</h3>', src, flags=re.MULTILINE)
                    src = re.sub(r'\\*\\*(.+?)\\*\\*', r'<strong>\\1</strong>', src)
                    src = re.sub(r'\\*(.+?)\\*', r'<em>\\1</em>', src)
                    src = src.replace('\\n', '<br>')"""

if old_markdown_parser in content or old_markdown_parser.replace("\\s", "\s") in content:
    content = content.replace(old_markdown_parser, new_markdown_parser)
    # also try unescaped one just in case
    content = content.replace(old_markdown_parser.replace("\\s", "\s"), new_markdown_parser)
    print("✅ Patched markdown parser with image support.")
else:
    # Let's search using a direct replace
    content = content.replace(
        'src = re.sub(r\'^#\s+(.+)$\', r\'<h1 class="story-h1">\\1</h1>\', src, flags=re.MULTILINE)',
        'src = re.sub(r\'!\[(.*?)\]\((.*?)\)\', r\'<img src="\\2" alt="\\1" style="max-width:100%; border-radius:8px; border: 1px solid var(--border-glow); margin: 10px 0; display:block; box-shadow:0 0 15px rgba(6,182,212,0.15);">\', src)\n                    src = re.sub(r\'^#\s+(.+)$\', r\'<h1 class="story-h1">\\1</h1>\', src, flags=re.MULTILINE)'
    )
    print("✅ Executed fallback heading replace.")

# 2. Patch chapter append block to include maps
old_append_block = 'chapters_html.append(f\'<div class="story-chapter-section" id="story-chapter-{ch_num}">{src}</div>\')'
new_append_block = """                    # Insert iframe maps in narrative story
                    map_embed = ""
                    if ch_num == 2:
                        map_embed = '<iframe src="subcounties_google_hybrid_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 5:
                        map_embed = '<iframe src="garissa_master_drm_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 43:
                        map_embed = '<iframe src="health_facilities_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 44:
                        map_embed = '<iframe src="schools_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    elif ch_num == 47:
                        map_embed = '<iframe src="boreholes_risk_map.html" style="width:100%; height:500px; border:1px solid var(--border-glow); border-radius:12px; margin-top:15px; box-shadow:0 4px 15px rgba(6,182,212,0.1);"></iframe>'
                    
                    chapters_html.append(f'<div class="story-chapter-section" id="story-chapter-{ch_num}">{src}{map_embed}</div>')"""

if old_append_block in content:
    content = content.replace(old_append_block, new_append_block)
    print("✅ Patched chapter HTML append block.")
else:
    # Try alternative string
    content = content.replace(
        'chapters_html.append(f\'<div class="story-chapter-section" id="story-chapter-{ch_num}">{src}</div>\')',
        new_append_block
    )
    print("✅ Executed fallback chapter append block replace.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("🎉 dashboard patching script finished.")
