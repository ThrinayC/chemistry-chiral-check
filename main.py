import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from urllib.parse import quote
import json
import requests



# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChiralSense",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg:       #0a0c10;
    --surface:  #111318;
    --border:   #1e2230;
    --accent:   #00e5a0;
    --accent2:  #ff4d6d;
    --accent3:  #7b61ff;
    --text:     #e8eaf0;
    --muted:    #5a6080;
    --r-color:  #ff4d6d;
    --s-color:  #00e5a0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,229,160,.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3.2rem;
    letter-spacing: -2px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent3) 50%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    color: var(--muted);
    font-size: .85rem;
    margin-top: .6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3), var(--accent2));
}
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .8rem;
}

.chiral-badge {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .4rem .9rem;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: .9rem;
    font-weight: 700;
    margin: .3rem .2rem;
    border: 1.5px solid;
}
.badge-R  { color: var(--r-color); border-color: var(--r-color); background: rgba(255,77,109,.08); }
.badge-S  { color: var(--s-color); border-color: var(--s-color); background: rgba(0,229,160,.08); }
.badge-none { color: var(--muted); border-color: var(--border); background: transparent; }

.stats-strip { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: .5rem; }
.stat-box {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .6rem 1rem;
    flex: 1;
    min-width: 100px;
    text-align: center;
}
.stat-val { font-family: 'Space Mono', monospace; font-size: 1.5rem; font-weight: 700; color: var(--accent); }
.stat-lbl { font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; }

.smiles-box {
    font-family: 'Space Mono', monospace;
    font-size: .85rem;
    color: var(--accent);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .8rem 1rem;
    word-break: break-all;
    line-height: 1.7;
}

.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: .9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,160,.15) !important;
}
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent3)) !important;
    color: #000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .6rem 2rem !important;
    font-size: 1rem !important;
    transition: opacity .2s !important;
    width: 100%;
}
.stButton > button:hover { opacity: .85 !important; }

.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

.error-box {
    background: rgba(255,77,109,.08);
    border: 1px solid rgba(255,77,109,.3);
    border-radius: 10px;
    padding: .8rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: .85rem;
    color: var(--r-color);
}

.legend { display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap; }
.legend-item {
    display: flex; align-items: center; gap: .4rem;
    font-family: 'Space Mono', monospace; font-size: .75rem; color: var(--muted);
}
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-R      { background: var(--r-color); }
.dot-S      { background: var(--s-color); }
.dot-chiral { background: var(--accent3); }

/* Tab overrides */
[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace !important;
    font-size: .75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

.viewer-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    position: relative;
}
.viewer-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3), var(--accent2));
    z-index: 10;
}
.viewer-controls {
    display: flex; gap: .6rem; flex-wrap: wrap;
    padding: .8rem 1rem;
    background: var(--bg);
    border-top: 1px solid var(--border);
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    color: var(--muted);
    align-items: center;
}
.ctrl-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: .2rem .6rem;
    font-size: .68rem;
    color: var(--text);
}
</style>
""", unsafe_allow_html=True)



PRESET_MOLECULES = {
    "Cocaine": "CN1[C@H]2CC[C@@H]1C[C@H](OC(=O)c1ccccc1)[C@@H]2OC(=O)C",
    "Loxoprofen":       "OC(=O)[C@@H](C)c1ccc(CC2CCCC2=O)cc1",
    "L-Alanine":        "N[C@@H](C)C(=O)O",
    "D-Alanine":        "N[C@H](C)C(=O)O",
    "L-Phenylalanine":  "N[C@@H](Cc1ccccc1)C(=O)O",
    "Glucose (D)":      "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
    "Thalidomide":      "O=C1CCC(=O)N1[C@@H]1C(=O)Nc2ccccc21",
    "Ibuprofen (S)":    "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "Limonene (R)":     "CC(=C)[C@@H]1CCC(=CC1)C",
    "Camphor":          "O=C1C[C@@H]2CC1(C)C2(C)C",
    "Aspartame":        "COC(=O)[C@@H](Cc1ccccc1)NC(=O)[C@@H](N)CC(=O)O",
    "Penicillin G":     "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)Cc1ccccc1)C(=O)O)C",
    # ── New additions ──────────────────────────────────────────────────────
    "Naproxen":         "COc1ccc2cc([C@@H](C)C(=O)O)ccc2c1",
    "Amoxicillin":      "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](N)c1ccc(O)cc1)C(=O)O)C",
    "Morphine":         "[C@@H]1(O)([C@]23CCN(CC2=CC=C[C@H]3O1)C)",
    "Taxol (Paclitaxel)": "OC(=O)[C@@H]1C[C@]2(OC(=O)c3ccccc3)[C@H](OC(C)=O)[C@@H](O)[C@@]4(C)[C@@H](OC(=O)[C@H](O)[C@@H](NC(=O)c3ccccc3)c3ccccc3)CC[C@]4(C)[C@H]2[C@@H]1C",
    "Testosterone":     "O=C1CC[C@H]2[C@@H]3CC[C@@](O)(C(=O)C)[C@@H]3CC[C@@H]2[C@@H]1",
    "Carvone (R)":      "O=C1CC(=C)[C@@H](CC1)C(=C)C",
}



# ── Helpers ───────────────────────────────────────────────────────────────────
def get_chiral_info(mol):
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    centres = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    return [{"idx": idx, "symbol": mol.GetAtomWithIdx(idx).GetSymbol(), "config": cfg}
            for idx, cfg in centres]

def name_to_smiles(name):
    try:
        encoded = quote(name.strip())
        # Step 1: get CID
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/cids/JSON"
        r = requests.get(cid_url, timeout=10)
        if r.status_code != 200:
            return None
        cid = r.json()["IdentifierList"]["CID"][0]

        # Step 2: get SDF with 3D coords (has full stereo info)
        sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
        r2 = requests.get(sdf_url, timeout=10)
        if r2.status_code == 200:
            # parse SDF and extract SMILES with stereo assigned from 3D
            mol = Chem.MolFromMolBlock(r2.text, removeHs=False)
            if mol:
                AllChem.AssignStereochemistryFrom3D(mol)
                Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
                return Chem.MolToSmiles(mol, isomericSmiles=True)

        # Step 3: fallback to plain SMILES if no 3D available
        smi_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES/JSON"
        r3 = requests.get(smi_url, timeout=10)
        if r3.status_code == 200:
            props = r3.json()["PropertyTable"]["Properties"][0]
            return props.get("IsomericSMILES") or props.get("SMILES")
        return None
    except Exception as e:
        return None

def mol_to_svg(mol, width=600, height=400, highlight_atoms=None, highlight_colors=None):
    AllChem.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.drawOptions().addStereoAnnotation = True
    drawer.drawOptions().bondLineWidth = 2.0
    if highlight_atoms and highlight_colors:
        atom_radii = {a: 0.4 for a in highlight_atoms}
        drawer.DrawMolecule(mol,
                            highlightAtoms=highlight_atoms,
                            highlightAtomColors=highlight_colors,
                            highlightBonds=[],
                            highlightBondColors={},
                            highlightAtomRadii=atom_radii)
    else:
        drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


def build_highlight_map(chiral_info):
    highlight_atoms, highlight_colors = [], {}
    for c in chiral_info:
        idx = c["idx"]
        highlight_atoms.append(idx)
        if c["config"] == "R":
            highlight_colors[idx] = (1.0, 0.30, 0.43)
        elif c["config"] == "S":
            highlight_colors[idx] = (0.0, 0.90, 0.63)
        else:
            highlight_colors[idx] = (0.48, 0.38, 1.0)
    return highlight_atoms, highlight_colors


def mol_to_molblock(mol):
    """Generate a 3D molblock from a molecule using ETKDG."""
    mol3d = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol3d, params)
    if result == -1:
        # fallback: try without Hs
        result = AllChem.EmbedMolecule(mol, params)
        if result == -1:
            return None
        AllChem.MMFFOptimizeMolecule(mol)
        return Chem.MolToMolBlock(mol)
    AllChem.MMFFOptimizeMolecule(mol3d)
    return Chem.MolToMolBlock(mol3d)


def build_3d_viewer_html(molblock, chiral_info, width="100%", height=480, spin=True):
    """
    Build a self-contained HTML string with a 3Dmol.js viewer.
    Chiral centres are highlighted with coloured spheres + labels.
    molblock: SDF/mol string with 3D coordinates
    chiral_info: list of {idx, symbol, config}
    """
    # Map config → colour (hex string for 3Dmol)
    config_colors = {"R": "0xff4d6d", "S": "0x00e5a0", "?": "0x7b61ff"}
    label_bg      = {"R": "0x200010", "S": "0x001a0f", "?": "0x0d0b20"}
    label_fg      = {"R": "#ff4d6d",  "S": "#00e5a0",  "?": "#7b61ff"}

    # Build JS snippets for each chiral atom
    highlight_js = ""
    label_js     = ""

    # We need to find 3D coordinates for each chiral atom index.
    # Parse the molblock to get atom coords (atoms in V2000 SDF are listed after the counts line).
    # We'll pass the atom index list and let JS find them via getAtoms({serial: N+1}).
    for c in chiral_info:
        idx    = c["idx"]
        serial = idx + 1        # 3Dmol uses 1-based serial for SDF
        cfg    = c["config"]
        col    = config_colors.get(cfg, "0x7b61ff")
        fg     = label_fg.get(cfg, "#7b61ff")
        bg     = label_bg.get(cfg, "0x0d0b20")
        sym    = c["symbol"]

        highlight_js += f"""
  viewer.setStyle({{serial: {serial}}}, {{
    stick: {{radius: 0.15, colorscheme: "Jmol"}},
    sphere: {{radius: 0.55, color: "{col}", opacity: 0.88}}
  }});
"""
        label_js += f"""
  viewer.addLabel("({cfg}) {sym}{serial}", {{
    serial: {serial},
    fontSize: 13,
    fontColor: "{fg}",
    backgroundColor: "{bg}",
    backgroundOpacity: 0.88,
    borderColor: "{fg}",
    borderThickness: 1,
    padding: 4,
    inFront: true
  }});
"""

    spin_js = "viewer.spin('y', 0.6);" if spin else ""

    # Escape the molblock for embedding in JS
    molblock_escaped = molblock.replace('\\', '\\\\').replace('`', '\\`')

    legend_items = ""
    seen_configs = {c["config"] for c in chiral_info}
    if "R" in seen_configs:
        legend_items += "<div class='leg-item'><div class='leg-dot' style='background:#ff4d6d'></div>(R) centre</div>"
    if "S" in seen_configs:
        legend_items += "<div class='leg-item'><div class='leg-dot' style='background:#00e5a0'></div>(S) centre</div>"
    if "?" in seen_configs:
        legend_items += "<div class='leg-item'><div class='leg-dot' style='background:#7b61ff'></div>Unassigned</div>"
    legend_items += "<div class='leg-item'><div class='leg-dot' style='background:#aaa'></div>Other atoms</div>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://3dmol.org/build/3Dmol-min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0c10; font-family: 'Space Mono', monospace; }}

  #viewer-wrap {{
    width: 100%;
    height: {height}px;
    position: relative;
  }}
  #viewer {{
    width: 100%;
    height: 100%;
  }}

  .overlay-controls {{
    position: absolute;
    top: 12px; right: 12px;
    display: flex; flex-direction: column; gap: 6px;
    z-index: 100;
  }}
  .ctrl-btn {{
    background: rgba(17,19,24,0.88);
    border: 1px solid #1e2230;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 11px;
    color: #e8eaf0;
    cursor: pointer;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    transition: border-color .2s, color .2s;
    white-space: nowrap;
  }}
  .ctrl-btn:hover {{ border-color: #00e5a0; color: #00e5a0; }}
  .ctrl-btn.active {{ border-color: #00e5a0; color: #00e5a0; }}

  .legend {{
    position: absolute;
    bottom: 12px; left: 12px;
    background: rgba(17,19,24,0.88);
    border: 1px solid #1e2230;
    border-radius: 10px;
    padding: 10px 14px;
    z-index: 100;
    display: flex; flex-direction: column; gap: 5px;
  }}
  .leg-item {{
    display: flex; align-items: center; gap: 7px;
    font-size: 11px; color: #8a90a8;
    font-family: 'Space Mono', monospace;
  }}
  .leg-dot {{
    width: 10px; height: 10px; border-radius: 50%;
    flex-shrink: 0;
  }}

  .hint {{
    position: absolute;
    bottom: 12px; right: 12px;
    font-size: 10px; color: #2e3350;
    font-family: 'Space Mono', monospace;
    text-align: right; line-height: 1.7;
    z-index: 100;
  }}
</style>
</head>
<body>
<div id="viewer-wrap">
  <div id="viewer"></div>

  <!-- Overlay controls -->
  <div class="overlay-controls">
    <button class="ctrl-btn active" id="btn-spin" onclick="toggleSpin()">⟳ SPIN</button>
    <button class="ctrl-btn" id="btn-surface" onclick="toggleSurface()">◈ SURFACE</button>
    <button class="ctrl-btn" id="btn-style" onclick="cycleStyle()">◉ STYLE</button>
    <button class="ctrl-btn" onclick="resetView()">⊙ RESET</button>
  </div>

  <!-- Legend -->
  <div class="legend">
    {legend_items}
  </div>

  <!-- Hint -->
  <div class="hint">
    drag · scroll · right-drag
  </div>
</div>

<script>
$(function() {{
  let viewer = $3Dmol.createViewer("viewer", {{
    backgroundColor: "0x0a0c10"
  }});

  let molblock = `{molblock_escaped}`;
  viewer.addModel(molblock, "mol");

  // Base style: ball-and-stick
  viewer.setStyle({{}}, {{
    stick: {{ radius: 0.12, colorscheme: "Jmol" }},
    sphere: {{ radius: 0.28, colorscheme: "Jmol" }}
  }});

  // Chiral centre highlights
  {highlight_js}

  // Chiral centre labels
  {label_js}

  viewer.zoomTo();
  viewer.zoom(0.9);
  viewer.render();
  {spin_js}

  // ── Controls ──────────────────────────────────────────────────────────
  let spinning = {"true" if spin else "false"};
  let surfaceOn = false;
  let surfaceObj = null;
  let styleIdx = 0;
  const styles = ["ball-stick", "stick", "sphere", "line"];

  window.toggleSpin = function() {{
    if (spinning) {{
      viewer.spin(false);
      spinning = false;
      document.getElementById("btn-spin").classList.remove("active");
    }} else {{
      viewer.spin("y", 0.6);
      spinning = true;
      document.getElementById("btn-spin").classList.add("active");
    }}
  }};

  window.toggleSurface = function() {{
    if (surfaceOn) {{
      viewer.removeSurface(surfaceObj);
      surfaceOn = false;
      document.getElementById("btn-surface").classList.remove("active");
    }} else {{
      surfaceObj = viewer.addSurface($3Dmol.SurfaceType.VDW, {{
        opacity: 0.28,
        colorscheme: {{ prop: "partialCharge", gradient: "rwb" }}
      }});
      surfaceOn = true;
      document.getElementById("btn-surface").classList.add("active");
    }}
    viewer.render();
  }};

  window.cycleStyle = function() {{
    styleIdx = (styleIdx + 1) % styles.length;
    let s = styles[styleIdx];
    if (s === "ball-stick") {{
      viewer.setStyle({{}}, {{ stick: {{ radius:0.12, colorscheme:"Jmol" }}, sphere: {{ radius:0.28, colorscheme:"Jmol" }} }});
    }} else if (s === "stick") {{
      viewer.setStyle({{}}, {{ stick: {{ radius:0.15, colorscheme:"Jmol" }} }});
    }} else if (s === "sphere") {{
      viewer.setStyle({{}}, {{ sphere: {{ colorscheme:"Jmol" }} }});
    }} else {{
      viewer.setStyle({{}}, {{ line: {{ colorscheme:"Jmol" }} }});
    }}
    // Re-apply chiral highlights on top
    {highlight_js}
    viewer.render();
  }};

  window.resetView = function() {{
    viewer.zoomTo();
    viewer.zoom(0.9);
    viewer.render();
  }};
}});
</script>
</body>
</html>
"""
    return html


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem 0 1.5rem'>
      <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.4rem;
                  background:linear-gradient(135deg,#00e5a0,#7b61ff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;'>ChiralSense</div>
      <div style='font-family:Space Mono,monospace;font-size:.65rem;
                  color:#5a6080;letter-spacing:2px;text-transform:uppercase;
                  margin-top:.2rem;'>Stereochemistry Explorer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Preset Molecules**")
    preset = st.selectbox("Choose a preset", ["— enter SMILES —"] + list(PRESET_MOLECULES.keys()))

    st.markdown("<hr style='border-color:#1e2230'>", unsafe_allow_html=True)
    st.markdown("**Image Size**")
    img_w = st.slider("Width",  400, 900, 650, 50)
    img_h = st.slider("Height", 300, 700, 430, 50)

    st.markdown("<hr style='border-color:#1e2230'>", unsafe_allow_html=True)
    st.markdown("**3D Viewer**")
    viewer_h   = st.slider("Viewer height (px)", 350, 700, 480, 50)
    auto_spin  = st.toggle("Auto-spin", value=True)

    st.markdown("<hr style='border-color:#1e2230'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:Space Mono,monospace;font-size:.7rem;color:#5a6080;line-height:1.8'>
    <b style='color:#e8eaf0'>R/S Assignment</b><br>
    Based on CIP priority rules.<br>
    Atoms highlighted on both 2D and 3D structures.<br><br>
    <b style='color:#e8eaf0'>Colour key</b><br>
    🔴 R-centre<br>
    🟢 S-centre<br>
    🟣 Unassigned
    </div>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <h1 class='hero-title'>ChiralSense</h1>
  <p class='hero-sub'>Stereochemistry · R/S Configuration · 2-D &amp; 3-D Visualization</p>
</div>
""", unsafe_allow_html=True)

col_in, _ = st.columns([3, 1])
with col_in:
    default_smiles = PRESET_MOLECULES.get(preset, "") if preset != "— enter SMILES —" else ""
    smiles_input = st.text_input(
        "SMILES string",
        value=st.session_state.get("fetched_smiles", default_smiles),
        placeholder="e.g.  N[C@@H](C)C(=O)O",
        label_visibility="collapsed",
    )
    col_name, col_fetch = st.columns([3, 1])
    with col_name:
        mol_name = st.text_input("Or search by name", placeholder="e.g. aspirin, dopamine, caffeine")
    with col_fetch:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Fetch SMILES"):
            if mol_name.strip():
                with st.spinner("Fetching from PubChem..."):
                    fetched = name_to_smiles(mol_name.strip())
                if fetched:
                    st.session_state["fetched_smiles"] = fetched
                    st.success(f"Found: `{fetched}`")
                else:
                    st.markdown("<div class='error-box'>✗ Molecule not found on PubChem.</div>",
                                unsafe_allow_html=True)

col_btn, _ = st.columns([1, 3])
with col_btn:
    analyse = st.button("⚗ Analyse Molecule")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── Analysis ──────────────────────────────────────────────────────────────────
if analyse and smiles_input.strip():
    mol = Chem.MolFromSmiles(smiles_input.strip())

    if mol is None:
        st.markdown("""
        <div class='error-box'>✗ Invalid SMILES — please check your input and try again.</div>
        """, unsafe_allow_html=True)
    else:
        chiral_info  = get_chiral_info(mol)
        canon_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        n_R   = sum(1 for c in chiral_info if c["config"] == "R")
        n_S   = sum(1 for c in chiral_info if c["config"] == "S")
        n_un  = sum(1 for c in chiral_info if c["config"] == "?")
        n_ch  = len(chiral_info)

        # ── Stats row ──────────────────────────────────────────────────────
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Molecule Summary</div>", unsafe_allow_html=True)
        cols = st.columns(5)
        for col, (val, lbl) in zip(cols, [
            (n_ch,               "Chiral Centres"),
            (n_R,                "R Centres"),
            (n_S,                "S Centres"),
            (n_un,               "Unassigned"),
            (mol.GetNumAtoms(),  "Heavy Atoms"),
        ]):
            col.markdown(f"""
            <div class='stat-box'>
              <div class='stat-val'>{val}</div>
              <div class='stat-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Tabs: 2D / 3D / Details ────────────────────────────────────────
        tab2d, tab3d, tab_det = st.tabs(["⬡  2D Structure", "⬡  3D Interactive", "⬡  Centre Details"])

        # ════════════════════════════════════════════════════════════════════
        # TAB 1 — 2D
        # ════════════════════════════════════════════════════════════════════
        with tab2d:
            left, right = st.columns([1.3, 1])

            with left:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>2-D Structure with Stereo Highlights</div>",
                            unsafe_allow_html=True)

                ha, hc = build_highlight_map(chiral_info)
                svg = mol_to_svg(mol, width=img_w, height=img_h,
                                 highlight_atoms=ha, highlight_colors=hc)
                svg_styled = svg.replace(
                    "<svg ",
                    "<svg style='background:#ffffff;border-radius:12px;width:100%;height:auto;' ", 1
                )
                st.components.v1.html(svg_styled, height=img_h + 20, scrolling=False)

                st.markdown("""
                <div class='legend' style='margin-top:.8rem;'>
                  <div class='legend-item'><div class='dot dot-R'></div>R-centre</div>
                  <div class='legend-item'><div class='dot dot-S'></div>S-centre</div>
                  <div class='legend-item'><div class='dot dot-chiral'></div>Unassigned</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                # SMILES
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>Canonical SMILES (with stereo)</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='smiles-box'>{canon_smiles}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Chiral centres list
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>Chiral Centre Details</div>", unsafe_allow_html=True)
                if chiral_info:
                    for c in chiral_info:
                        cfg  = c["config"]
                        cls  = {"R": "badge-R", "S": "badge-S"}.get(cfg, "badge-none")
                        icon = {"R": "🔴", "S": "🟢"}.get(cfg, "🟣")
                        st.markdown(f"""
                        <div style='display:flex;align-items:center;gap:.8rem;
                                    padding:.5rem 0;border-bottom:1px solid #1e2230;'>
                          <span class='chiral-badge {cls}'>{icon} {cfg}</span>
                          <span style='font-family:Space Mono,monospace;font-size:.8rem;color:#e8eaf0'>
                            Atom <b>{c["idx"]}</b> — <b>{c["symbol"]}</b>
                          </span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='font-family:Space Mono,monospace;font-size:.85rem;color:#5a6080;
                                padding:.5rem 0;'>No chiral centres found.</div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Stereoisomer space
                if n_ch > 0:
                    max_iso = 2 ** n_ch
                    st.markdown(f"""
                    <div class='card'>
                      <div class='card-title'>Stereoisomer Space</div>
                      <div style='font-family:Space Mono,monospace;font-size:.85rem;
                                   color:#e8eaf0;line-height:1.8'>
                        Max possible stereoisomers:<br>
                        <span style='font-size:1.6rem;font-weight:700;color:#7b61ff'>
                          2<sup>{n_ch}</sup> = {max_iso}
                        </span><br>
                        <span style='color:#5a6080;font-size:.75rem'>
                          (before meso / symmetry reduction)
                        </span>
                      </div>
                    </div>""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # TAB 2 — 3D
        # ════════════════════════════════════════════════════════════════════
        with tab3d:
            with st.spinner("Generating 3D coordinates…"):
                mol2d = Chem.MolFromSmiles(canon_smiles)
                molblock = mol_to_molblock(mol2d)

            if molblock is None:
                st.markdown("""
                <div class='error-box'>
                  ✗ Could not generate 3D coordinates for this molecule.<br>
                  Try a different SMILES or a simpler molecule.
                </div>""", unsafe_allow_html=True)
            else:
                viewer_html = build_3d_viewer_html(
                    molblock, chiral_info,
                    height=viewer_h,
                    spin=auto_spin
                )

                st.markdown("<div class='viewer-card'>", unsafe_allow_html=True)
                st.components.v1.html(viewer_html, height=viewer_h + 4, scrolling=False)
                st.markdown("</div>", unsafe_allow_html=True)

                # Info strip below viewer
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                    <div class='card' style='text-align:center;margin-top:.8rem;'>
                      <div class='card-title'>Method</div>
                      <div style='font-family:Space Mono,monospace;font-size:.8rem;color:#00e5a0;'>
                        ETKDG v3<br>+ MMFF
                      </div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class='card' style='text-align:center;margin-top:.8rem;'>
                      <div class='card-title'>Chiral Centres</div>
                      <div style='font-family:Space Mono,monospace;font-size:1.4rem;
                                  font-weight:700;color:#7b61ff;'>{n_ch}</div>
                    </div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class='card' style='text-align:center;margin-top:.8rem;'>
                      <div class='card-title'>R Centres</div>
                      <div style='font-family:Space Mono,monospace;font-size:1.4rem;
                                  font-weight:700;color:#ff4d6d;'>{n_R}</div>
                    </div>""", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                    <div class='card' style='text-align:center;margin-top:.8rem;'>
                      <div class='card-title'>S Centres</div>
                      <div style='font-family:Space Mono,monospace;font-size:1.4rem;
                                  font-weight:700;color:#00e5a0;'>{n_S}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("""
                <div style='font-family:Space Mono,monospace;font-size:.7rem;color:#2e3350;
                             text-align:center;padding:.5rem 0;'>
                  SPIN · SURFACE · STYLE · RESET — controls available in viewer overlay
                </div>""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # TAB 3 — Centre Details
        # ════════════════════════════════════════════════════════════════════
        with tab_det:
            if not chiral_info:
                st.markdown("""
                <div style='text-align:center;padding:3rem;font-family:Space Mono,monospace;
                             font-size:.9rem;color:#5a6080;'>
                  No chiral centres found in this molecule.
                </div>""", unsafe_allow_html=True)
            else:
                for i, c in enumerate(chiral_info):
                    cfg  = c["config"]
                    col  = {"R": "#ff4d6d", "S": "#00e5a0"}.get(cfg, "#7b61ff")
                    icon = {"R": "🔴", "S": "🟢"}.get(cfg, "🟣")
                    atom = mol.GetAtomWithIdx(c["idx"])
                    neighbours = [
                        f"{mol.GetAtomWithIdx(n.GetIdx()).GetSymbol()}({n.GetIdx()})"
                        for n in atom.GetNeighbors()
                    ]

                    st.markdown(f"""
                    <div class='card' style='border-left:3px solid {col};'>
                      <div style='display:flex;align-items:center;gap:1rem;margin-bottom:.8rem;'>
                        <span class='chiral-badge {"badge-R" if cfg=="R" else "badge-S" if cfg=="S" else "badge-none"}'>{icon} {cfg}</span>
                        <span style='font-family:Space Mono,monospace;font-size:.85rem;color:#e8eaf0;'>
                          Centre {i+1} — Atom <b>{c["idx"]}</b> ({c["symbol"]})
                        </span>
                      </div>
                      <div style='font-family:Space Mono,monospace;font-size:.78rem;color:#5a6080;line-height:2;'>
                        <b style='color:#8a90a8;'>Neighbours:</b> {", ".join(neighbours)}<br>
                        <b style='color:#8a90a8;'>Configuration:</b>
                        <span style='color:{col};font-weight:700;'> ({cfg})</span>
                        {"— clockwise priority sequence" if cfg == "R" else "— anticlockwise priority sequence" if cfg == "S" else "— stereochemistry unassigned"}<br>
                        <b style='color:#8a90a8;'>CIP Rule:</b>
                        {"Rotate 1→2→3 away from lowest priority. Clockwise = R." if cfg == "R" else "Rotate 1→2→3 away from lowest priority. Anticlockwise = S." if cfg == "S" else "Configuration could not be assigned from SMILES."}
                      </div>
                    </div>""", unsafe_allow_html=True)

                # Stereoisomer table
                if n_ch > 0:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='card-title'>Stereoisomer Enumeration</div>", unsafe_allow_html=True)
                    max_iso = 2 ** n_ch
                    st.markdown(f"""
                    <div style='font-family:Space Mono,monospace;font-size:.82rem;color:#8a90a8;line-height:2;'>
                      {n_ch} chiral centre{"s" if n_ch>1 else ""} → maximum
                      <span style='color:#7b61ff;font-size:1.1rem;font-weight:700;'> 2<sup>{n_ch}</sup> = {max_iso} </span>
                      stereoisomers<br>
                      <span style='color:#5a6080;font-size:.72rem;'>
                        Actual count may be lower due to meso forms or molecular symmetry.
                      </span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

elif not smiles_input.strip() and analyse:
    st.markdown("""
    <div class='error-box'>✗ Please enter a SMILES string or choose a preset molecule.</div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:4rem 1rem;'>
      <div style='font-size:4rem;margin-bottom:1rem'>🔬</div>
      <div style='font-family:Syne,sans-serif;font-size:1.3rem;color:#5a6080'>
        Enter a SMILES string or pick a preset, then click
        <b style='color:#00e5a0'>Analyse Molecule</b>
      </div>
      <div style='font-family:Space Mono,monospace;font-size:.75rem;color:#2e3350;
                  margin-top:.8rem;letter-spacing:2px;text-transform:uppercase;'>
        Chiral centres · R/S labels · 2-D &amp; 3-D structure
      </div>
    </div>
    """, unsafe_allow_html=True)