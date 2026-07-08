import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, rdDepictor  # <-- add rdDepictor here
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import Draw, AllChem, rdDepictor, Descriptors, rdMolDescriptors
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
/* --- Welcome Overlay & Pop-up --- */
#welcome-overlay {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(10, 12, 16, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999999;
    animation: fadeIn 0.5s ease;
    pointer-events: all;
}

.welcome-card {
    background: #111318;
    border: 1px solid #1e2230;
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    max-width: 450px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
    z-index: 1000000;
}

.welcome-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #00e5a0, #7b61ff, #ff4d6d);
}

.welcome-card h2 {
    font-family: 'Syne', sans-serif;
    color: #e8eaf0;
    margin-bottom: 1.5rem;
    font-size: 1.8rem;
}

.welcome-info {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    color: #8a90a8;
    line-height: 1.8;
}

.welcome-info b { color: #00e5a0; }

.close-welcome {
    margin-top: 2rem;
    background: linear-gradient(135deg, #00e5a0, #7b61ff);
    color: #000;
    border: none;
    padding: 0.8rem 2.5rem;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.2s;
}

.close-welcome:hover { transform: scale(1.05); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
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
    "Naproxen":         "COc1ccc2cc([C@@H](C)C(=O)O)ccc2c1",
    "Amoxicillin":      "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](N)c1ccc(O)cc1)C(=O)O)C",
    "Morphine":         "[C@@H]1(O)([C@]23CCN(CC2=CC=C[C@H]3O1)C)",
    "Taxol (Paclitaxel)": "OC(=O)[C@@H]1C[C@]2(OC(=O)c3ccccc3)[C@H](OC(C)=O)[C@@H](O)[C@@]4(C)[C@@H](OC(=O)[C@H](O)[C@@H](NC(=O)c3ccccc3)c3ccccc3)CC[C@]4(C)[C@H]2[C@@H]1C",
    "Testosterone":     "O=C1CC[C@H]2[C@@H]3CC[C@@](O)(C(=O)C)[C@@H]3CC[C@@H]2[C@@H]1",
    "Carvone (R)":      "O=C1CC(=C)[C@@H](CC1)C(=C)C",
}
MOLECULE_NOTES = {
    "Cocaine": "⚠️ Potent CNS stimulant and local anesthetic. Highly addictive schedule II narcotic (illegal for recreational use). Acts as a dopamine reuptake inhibitor.",
    "Thalidomide": "☣️ Infamous teratogen. The (R)-enantiomer is a safe sedative, but the (S)-enantiomer causes severe birth defects. Now used strictly for multiple myeloma.",
    "Ibuprofen (S)": "💊 The biologically active enantiomer of the common painkiller. Your body actually converts the inactive (R)-form into this (S)-form slowly over time.",
    "Limonene (R)": "🍋 Smells strongly of oranges! Interestingly, its mirror image (S-Limonene) smells like pine needles and turpentine.",
    "Aspartame": "🍬 Common artificial sweetener. It must be strictly in this L,L-configuration to taste sweet; its other stereoisomers taste horribly bitter.",
    "Morphine": "⚠️ Extremely powerful opiate analgesic derived from the poppy plant. Highly addictive and strictly regulated.",
    "Taxol (Paclitaxel)": "🧪 Complex chemotherapy medication originally isolated from the bark of the Pacific yew tree.",
    "Testosterone": "💪 Primary male sex hormone and naturally occurring anabolic steroid.",
    "Penicillin G": "🦠 The first naturally occurring antibiotic discovered by Alexander Fleming.",
    "Camphor": "🌲 Waxy, flammable solid with a strong aroma. Used in Vicks VapoRub and traditional medicine.",
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
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/cids/JSON"
        r = requests.get(cid_url, timeout=10)
        if r.status_code != 200:
            return None
        cid = r.json()["IdentifierList"]["CID"][0]

        sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
        r2 = requests.get(sdf_url, timeout=10)
        if r2.status_code == 200:
            mol = Chem.MolFromMolBlock(r2.text, removeHs=False)
            if mol:
                AllChem.AssignStereochemistryFrom3D(mol)
                Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
                return Chem.MolToSmiles(mol, isomericSmiles=True)

        smi_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES/JSON"
        r3 = requests.get(smi_url, timeout=10)
        if r3.status_code == 200:
            props = r3.json()["PropertyTable"]["Properties"][0]
            return props.get("IsomericSMILES") or props.get("SMILES")
        return None
    except Exception:
        return None
    
@st.cache_data(ttl=3600) # Cache so we don't spam the API
def get_pubchem_description(name):
    try:
        encoded = quote(name.strip())
        # Step 1: Get the CID
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/cids/JSON"
        r = requests.get(cid_url, timeout=5)
        if r.status_code != 200:
            return None
        cid = r.json()["IdentifierList"]["CID"][0]

        # Step 2: Fetch the text description for that CID
        desc_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
        r2 = requests.get(desc_url, timeout=5)
        if r2.status_code == 200:
            info_list = r2.json()["InformationList"]["Information"]
            for info in info_list:
                # Grab the first actual paragraph of text we find
                if "Description" in info:
                    return info["Description"]
        return None
    except Exception:
        return None

def mol_to_svg(mol, width=1000, height=800, highlight_atoms=None, highlight_colors=None):
    # Enable the advanced CoordGen library to untangle giant macrocycles
    rdDepictor.SetPreferCoordGen(True)
    AllChem.Compute2DCoords(mol)
    
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    
    opts = drawer.drawOptions()
    opts.addStereoAnnotation = True
    opts.bondLineWidth = 1.5
    opts.clearBackground = False

    if highlight_atoms is not None and len(highlight_atoms) > 0 and highlight_colors:
        rad = 0.25 if mol.GetNumHeavyAtoms() > 30 else 0.35
        atom_radii = {a: rad for a in highlight_atoms}
        
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


def build_highlight_map(chiral_info, configs=("R", "S", "?")):
    highlight_atoms, highlight_colors = [], {}
    # Reverted to safe 3-tuple (RGB) to prevent RDKit rendering failures.
    # Colors are slightly softened to look good even when close together.
    color_map = {
        "R": (1.0, 0.35, 0.45),  # Soft Pink/Red
        "S": (0.0, 0.85, 0.60),  # Soft Teal/Green
        "?": (0.55, 0.45, 1.0),  # Soft Purple
    }
    for c in chiral_info:
        cfg = c["config"]
        if cfg in configs:
            highlight_atoms.append(c["idx"])
            highlight_colors[c["idx"]] = color_map.get(cfg, (0.55, 0.45, 1.0))
    return highlight_atoms, highlight_colors

def mol_to_molblock(mol):
    mol3d = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol3d, params)
    if result == -1:
        result = AllChem.EmbedMolecule(mol, params)
        if result == -1:
            return None
        AllChem.MMFFOptimizeMolecule(mol)
        return Chem.MolToMolBlock(mol)
    AllChem.MMFFOptimizeMolecule(mol3d)
    return Chem.MolToMolBlock(mol3d)


def svg_wrap(svg_text, svg_id, hidden=False):
    styled = svg_text.replace(
        "<svg ",
        f"<svg style='background:#ffffff;border-radius:12px;width:100%;height:auto;' ", 1
    )
    display = "none" if hidden else "block"
    return f"<div id='{svg_id}' style='display:{display};'>{styled}</div>"


def build_2d_viewer_html(mol, chiral_info, img_w, img_h):
    """
    FIX: Blink mode now generates TWO svgs (with and without highlights) and
    alternates between them using JS setInterval — no CSS animation on the
    container div, so only the highlight circles flash, not the whole structure.
    """
    has_r = any(c["config"] == "R" for c in chiral_info)
    has_s = any(c["config"] == "S" for c in chiral_info)

    # SVG: all highlights (R + S + unassigned)
    ha_all, hc_all = build_highlight_map(chiral_info, configs=("R", "S", "?"))
    svg_all = mol_to_svg(mol, img_w, img_h, ha_all, hc_all)

    # SVG: R only
    ha_r, hc_r = build_highlight_map(chiral_info, configs=("R",))
    svg_r = mol_to_svg(mol, img_w, img_h, ha_r if ha_r else None, hc_r if hc_r else None)

    # SVG: S only
    ha_s, hc_s = build_highlight_map(chiral_info, configs=("S",))
    svg_s = mol_to_svg(mol, img_w, img_h, ha_s if ha_s else None, hc_s if hc_s else None)

    # SVG: plain (no highlights) — used as the "off" frame during blink
    svg_plain = mol_to_svg(mol, img_w, img_h, None, None)

    # We embed all 4 divs; JS toggles display between them
    div_all   = svg_wrap(svg_all,   "svg-all",   hidden=False)
    div_r     = svg_wrap(svg_r,     "svg-r",     hidden=True)
    div_s     = svg_wrap(svg_s,     "svg-s",     hidden=True)
    div_plain = svg_wrap(svg_plain, "svg-plain", hidden=True)

    init_r = 1 if has_r else 0
    init_s = 1 if has_s else 0

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0a0c10; font-family: 'Space Mono', monospace; padding: 0; }}

.toggle-bar {{
    display: flex;
    gap: 8px;
    padding: 10px 4px 8px;
    align-items: center;
    flex-wrap: wrap;
}}

.tog-btn {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 16px 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    transition: all 0.18s ease;
    user-select: none;
    border: 2px solid;
    position: relative;
}}

.tog-btn.r-btn                  {{ color:#804040; border-color:#4a2030; background:rgba(255,77,109,0.04); }}
.tog-btn.r-btn.state-highlight  {{ color:#ff4d6d; border-color:#ff4d6d; background:rgba(255,77,109,0.16); box-shadow:0 0 12px rgba(255,77,109,0.35); }}
.tog-btn.r-btn.state-blink      {{ color:#ff4d6d; border-color:#ff4d6d; background:rgba(255,77,109,0.16); box-shadow:0 0 18px rgba(255,77,109,0.6); animation:pulseR 0.7s ease-in-out infinite; }}

.tog-btn.s-btn                  {{ color:#307060; border-color:#1a4035; background:rgba(0,229,160,0.04); }}
.tog-btn.s-btn.state-highlight  {{ color:#00e5a0; border-color:#00e5a0; background:rgba(0,229,160,0.16); box-shadow:0 0 12px rgba(0,229,160,0.35); }}
.tog-btn.s-btn.state-blink      {{ color:#00e5a0; border-color:#00e5a0; background:rgba(0,229,160,0.16); box-shadow:0 0 18px rgba(0,229,160,0.6); animation:pulseS 0.7s ease-in-out infinite; }}

@keyframes pulseR {{
  0%,100% {{ box-shadow:0 0 8px rgba(255,77,109,0.3); }}
  50%     {{ box-shadow:0 0 22px rgba(255,77,109,0.85), 0 0 6px rgba(255,77,109,0.5); }}
}}
@keyframes pulseS {{
  0%,100% {{ box-shadow:0 0 8px rgba(0,229,160,0.3); }}
  50%     {{ box-shadow:0 0 22px rgba(0,229,160,0.85), 0 0 6px rgba(0,229,160,0.5); }}
}}

.tog-btn:hover {{ filter: brightness(1.15); }}

.led {{ width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; transition:all 0.18s; }}
.r-btn .led                 {{ background:#4a2030; }}
.r-btn.state-highlight .led {{ background:#ff4d6d; box-shadow:0 0 5px #ff4d6d; }}
.r-btn.state-blink .led     {{ background:#ff4d6d; box-shadow:0 0 8px #ff4d6d; animation:blinkLedR 0.7s ease-in-out infinite; }}
.s-btn .led                 {{ background:#1a4035; }}
.s-btn.state-highlight .led {{ background:#00e5a0; box-shadow:0 0 5px #00e5a0; }}
.s-btn.state-blink .led     {{ background:#00e5a0; box-shadow:0 0 8px #00e5a0; animation:blinkLedS 0.7s ease-in-out infinite; }}

@keyframes blinkLedR {{
  0%,100% {{ opacity:1; box-shadow:0 0 4px #ff4d6d; }}
  50%     {{ opacity:0.2; box-shadow:none; }}
}}
@keyframes blinkLedS {{
  0%,100% {{ opacity:1; box-shadow:0 0 4px #00e5a0; }}
  50%     {{ opacity:0.2; box-shadow:none; }}
}}

.state-label {{
    font-size: 9px;
    color: #2e3350;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-left: 2px;
    min-width: 52px;
}}
.hint-label {{
    font-size: 10px;
    color: #2e3350;
    letter-spacing: 1px;
    margin-left: 4px;
}}
</style>
</head>
<body>
<div class="toggle-bar">
    <button class="tog-btn r-btn {'state-highlight' if has_r else ''}" id="btn-r" onclick="cycleR()" {'disabled' if not has_r else ''}>
        <span class="led"></span> R <span class="state-label" id="lbl-r">{'HIGHLIGHT' if has_r else 'OFF'}</span>
    </button>
    <button class="tog-btn s-btn {'state-highlight' if has_s else ''}" id="btn-s" onclick="cycleS()" {'disabled' if not has_s else ''}>
        <span class="led"></span> S <span class="state-label" id="lbl-s">{'HIGHLIGHT' if has_s else 'OFF'}</span>
    </button>
    <span class="hint-label">· click to cycle: off → highlight → blink</span>
</div>

<div id="svg-container" style="position:relative;">
{div_all}
{div_r}
{div_s}
{div_plain}
</div>

<script>
// Per-button states: 0=off, 1=highlight, 2=blink
const hasR = {'true' if has_r else 'false'};
const hasS = {'true' if has_s else 'false'};
let stateR = {init_r};
let stateS = {init_s};

const STATES = ['', 'state-highlight', 'state-blink'];
const LABELS = ['OFF', 'HIGHLIGHT', 'BLINK'];

// Blink: we alternate between the "highlight" svg and the "plain" svg
// using a JS interval — this makes ONLY the highlight circles flash,
// not the entire molecule structure.
let blinkInterval = null;
let blinkPhase = true; // true = show highlighted frame

function isOn(s) {{ return s > 0; }}

// Which svg div to show when NOT in blink mode (or on the "on" phase of blink)
function getHighlightId() {{
    const rOn = isOn(stateR);
    const sOn = isOn(stateS);
    if (rOn && sOn)  return 'svg-all';
    if (rOn && !sOn) return 'svg-r';
    if (!rOn && sOn) return 'svg-s';
    return 'svg-plain';
}}

function hideAll() {{
    ['svg-all','svg-r','svg-s','svg-plain'].forEach(id => {{
        document.getElementById(id).style.display = 'none';
    }});
}}

function stopBlink() {{
    if (blinkInterval) {{
        clearInterval(blinkInterval);
        blinkInterval = null;
    }}
}}

function startBlink() {{
    stopBlink();
    blinkPhase = true;
    blinkInterval = setInterval(function() {{
        blinkPhase = !blinkPhase;
        hideAll();
        // On "on" phase show the highlight SVG; on "off" phase show plain
        // This makes only the coloured highlight circles appear/disappear —
        // the bond/atom skeleton stays completely still.
        document.getElementById(blinkPhase ? getHighlightId() : 'svg-plain').style.display = 'block';
    }}, 500);
}}

function updateView() {{
    stopBlink();
    hideAll();
    const anyBlink = (stateR === 2 || stateS === 2);
    if (anyBlink) {{
        // Show highlighted frame immediately, then start alternating
        document.getElementById(getHighlightId()).style.display = 'block';
        startBlink();
    }} else {{
        document.getElementById(getHighlightId()).style.display = 'block';
    }}
}}

function applyBtnState(btnId, lblId, state) {{
    const btn = document.getElementById(btnId);
    btn.classList.remove('state-highlight', 'state-blink');
    if (state > 0) btn.classList.add(STATES[state]);
    document.getElementById(lblId).textContent = LABELS[state];
}}

function cycleR() {{
    if (!hasR) return;
    stateR = (stateR + 1) % 3;
    applyBtnState('btn-r', 'lbl-r', stateR);
    updateView();
}}

function cycleS() {{
    if (!hasS) return;
    stateS = (stateS + 1) % 3;
    applyBtnState('btn-s', 'lbl-s', stateS);
    updateView();
}}

// Init
updateView();
</script>
</body>
</html>"""
    return html


def build_3d_viewer_html(molblock, chiral_info, height=480, spin=True):
    """
    Centre cards shown as vertical lists on left (R) and right (S) sides.
    Clicking a card isolates that single centre as a yellow sphere, greying
    everything else. Controls (spin/surface/style/reset/all-R/all-S) sit top-right.
    """
    has_r = any(c["config"] == "R" for c in chiral_info)
    has_s = any(c["config"] == "S" for c in chiral_info)

    r_centres = [c for c in chiral_info if c["config"] == "R"]
    s_centres = [c for c in chiral_info if c["config"] == "S"]
    u_centres = [c for c in chiral_info if c["config"] not in ("R", "S")]
    all_centres = chiral_info  # full ordered list for indexing

    def js_centre_data(centres):
        items = []
        for c in centres:
            items.append(
                '{' + f'serial:{c["idx"]+1},cfg:"{c["config"]}",sym:"{c["symbol"]}",idx:{c["idx"]}' + '}'
            )
        return "[" + ",".join(items) + "]"

    all_centres_js = js_centre_data(all_centres)
    r_centres_js   = js_centre_data(r_centres)
    s_centres_js   = js_centre_data(s_centres)
    u_centres_js   = js_centre_data(u_centres)

    spin_js = "viewer.spin('y', 0.6);" if spin else ""
    molblock_escaped = molblock.replace("\\", "\\\\").replace("`", "\\`")

    # Build R card HTML (left panel)
    r_cards_html = ""
    for c in r_centres:
        r_cards_html += f"""
        <div class="centre-card r-card" onclick="selectCentre({c['idx']+1})" id="card-{c['idx']+1}">
          <div class="cc-badge r-badge">R</div>
          <div class="cc-info">
            <div class="cc-atom">{c['symbol']}<span class="cc-num">{c['idx']+1}</span></div>
            <div class="cc-sub">centre</div>
          </div>
        </div>"""

    # Build S card HTML (right panel)
    s_cards_html = ""
    for c in s_centres:
        s_cards_html += f"""
        <div class="centre-card s-card" onclick="selectCentre({c['idx']+1})" id="card-{c['idx']+1}">
          <div class="cc-badge s-badge">S</div>
          <div class="cc-info">
            <div class="cc-atom">{c['symbol']}<span class="cc-num">{c['idx']+1}</span></div>
            <div class="cc-sub">centre</div>
          </div>
        </div>"""

    # Unassigned cards go below R panel
    u_cards_html = ""
    for c in u_centres:
        u_cards_html += f"""
        <div class="centre-card u-card" onclick="selectCentre({c['idx']+1})" id="card-{c['idx']+1}">
          <div class="cc-badge u-badge">?</div>
          <div class="cc-info">
            <div class="cc-atom">{c['symbol']}<span class="cc-num">{c['idx']+1}</span></div>
            <div class="cc-sub">unassigned</div>
          </div>
        </div>"""

    left_panel  = (r_cards_html + u_cards_html) if (r_cards_html or u_cards_html) else ""
    right_panel = s_cards_html

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://3dmol.org/build/3Dmol-min.js"></script>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0a0c10; font-family:'Space Mono',monospace; overflow:hidden; }}

#viewer-wrap {{ width:100%; height:{height}px; position:relative; }}
#viewer {{ width:100%; height:100%; }}

/* ── Left centre panel (R) ── */
.left-panel {{
    position:absolute; top:12px; left:12px;
    display:flex; flex-direction:column; gap:6px;
    z-index:100; max-height:calc(100% - 60px); overflow-y:auto;
}}

/* ── Right centre panel (S) ── */
.right-panel {{
    position:absolute; top:12px; right:130px;
    display:flex; flex-direction:column; gap:6px;
    z-index:100; max-height:calc(100% - 60px); overflow-y:auto;
}}

/* ── Centre card ── */
.centre-card {{
    display:flex; align-items:center; gap:8px;
    background:rgba(14,16,22,0.90);
    border:1.5px solid #252840;
    border-radius:10px;
    padding:7px 10px;
    cursor:pointer;
    transition:all 0.18s ease;
    min-width:82px;
    user-select:none;
}}
.centre-card:hover {{
    border-color:#5a6080;
    background:rgba(30,34,48,0.95);
    transform:translateX(2px);
}}
.centre-card.selected {{
    border-color:#f5c518 !important;
    background:rgba(245,197,24,0.10) !important;
    box-shadow:0 0 14px rgba(245,197,24,0.45);
}}
.right-panel .centre-card:hover {{ transform:translateX(-2px); }}

.cc-badge {{
    width:22px; height:22px; border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    font-size:11px; font-weight:700; flex-shrink:0;
    letter-spacing:0;
}}
.r-badge {{ background:rgba(255,77,109,0.18); color:#ff4d6d; border:1px solid rgba(255,77,109,0.4); }}
.s-badge {{ background:rgba(0,229,160,0.18); color:#00e5a0; border:1px solid rgba(0,229,160,0.4); }}
.u-badge {{ background:rgba(123,97,255,0.18); color:#7b61ff; border:1px solid rgba(123,97,255,0.4); }}

.centre-card.selected .cc-badge {{
    background:rgba(245,197,24,0.25) !important;
    color:#f5c518 !important;
    border-color:rgba(245,197,24,0.6) !important;
}}

.cc-info {{ display:flex; flex-direction:column; gap:1px; }}
.cc-atom {{ font-size:12px; font-weight:700; color:#c8cad8; letter-spacing:0.5px; }}
.cc-num  {{ font-size:10px; color:#5a6080; margin-left:2px; }}
.cc-sub  {{ font-size:9px; color:#3a4060; letter-spacing:1px; text-transform:uppercase; }}

.centre-card.selected .cc-atom {{ color:#f5c518; }}

/* ── Panel header label ── */
.panel-hdr {{
    font-size:9px; letter-spacing:2px; text-transform:uppercase;
    color:#2e3350; padding:0 2px 2px;
}}

/* ── Controls top-right ── */
.overlay-controls {{
    position:absolute; top:12px; right:12px;
    display:flex; flex-direction:column; gap:5px; z-index:100;
}}
.ctrl-btn {{
    background:rgba(14,16,22,0.92);
    border:1.5px solid #252840;
    border-radius:8px;
    padding:5px 11px;
    font-size:10px; color:#6a708a;
    cursor:pointer;
    font-family:'Space Mono',monospace;
    letter-spacing:1px;
    transition:all 0.18s ease;
    white-space:nowrap; text-align:left;
    display:flex; align-items:center; gap:6px;
}}
.ctrl-btn:hover {{ border-color:#5a6080; color:#c0c4d8; }}
.ctrl-btn.active {{ border-color:#00e5a0; color:#00e5a0; }}
.btn-led {{
    width:6px; height:6px; border-radius:50%;
    display:inline-block; flex-shrink:0; background:#252840; transition:all 0.18s;
}}
.ctrl-btn.active .btn-led {{ background:#00e5a0; box-shadow:0 0 4px #00e5a0; }}
.divider-line {{ border-top:1px solid #1e2230; margin:1px 0; }}

/* ── Bottom hint ── */
.hint {{
    position:absolute; bottom:10px; right:12px;
    font-size:9px; color:#1e2230; z-index:100; line-height:1.7;
}}

/* ── Reset notice ── */
#reset-notice {{
    position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
    font-size:10px; color:#f5c518; letter-spacing:1px;
    opacity:0; transition:opacity 0.3s; pointer-events:none; z-index:100;
    background:rgba(14,16,22,0.85); padding:4px 10px; border-radius:6px;
    border:1px solid rgba(245,197,24,0.3);
}}

/* ── Custom Scrollbar ── */
::-webkit-scrollbar {{
    width: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent; 
}}
::-webkit-scrollbar-thumb {{
    background: #252840; 
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: #5a6080; 
}}

</style>
</head>
<body>
<div id="viewer-wrap">
  <div id="viewer"></div>

  {'<div class="left-panel"><div class="panel-hdr">R centres</div>' + left_panel + '</div>' if left_panel else ''}

  {'<div class="right-panel"><div class="panel-hdr">S centres</div>' + right_panel + '</div>' if right_panel else ''}

  <div class="overlay-controls">
    <button class="ctrl-btn {'active' if spin else ''}" id="btn-spin" onclick="toggleSpin()">
      <span class="btn-led"></span> SPIN
    </button>
    <button class="ctrl-btn" id="btn-surface" onclick="toggleSurface()">
      <span class="btn-led"></span> SURFACE
    </button>
    <button class="ctrl-btn" onclick="cycleStyle()">◉ STYLE</button>
    <div class="divider-line"></div>
    <button class="ctrl-btn" onclick="highlightAllR()" style="color:#ff4d6d;border-color:rgba(255,77,109,0.3)">🔴 ALL R</button>
    <button class="ctrl-btn" onclick="highlightAllS()" style="color:#00e5a0;border-color:rgba(0,229,160,0.3)">🟢 ALL S</button>
    <div class="divider-line"></div>
    <button class="ctrl-btn" onclick="clearSelection()">✕ CLEAR</button>
    <button class="ctrl-btn" onclick="resetView()">⊙ RESET</button>
  </div>

  <div id="reset-notice">click a centre card to isolate</div>
  <div class="hint">drag · scroll · right-drag</div>
</div>

<script>
$(function() {{
  let viewer = $3Dmol.createViewer("viewer", {{ backgroundColor:"0x0a0c10" }});
  viewer.addModel(`{molblock_escaped}`, "mol");

  const allCentres = {all_centres_js};
  const rCentres   = {r_centres_js};
  const sCentres   = {s_centres_js};
  const uCentres   = {u_centres_js};

  let selectedMode = null;   // null, "ALL_R", "ALL_S", or a specific serial number
  let spinning = {'true' if spin else 'false'};
  let surfaceOn = false;
  let surfaceObj = null;
  let styleIdx = 0;
  const styles = ["ball-stick","stick","sphere","line"];
  
  // Theme colors
  const YELLOW = '0xf5c518';
  const COLOR_R = '0xff4d6d';
  const COLOR_S = '0x00e5a0';

  // ── Base molecule style ─────────────────────────────────────────────────
  function baseStyle() {{
    const s = styles[styleIdx];
    if (s === "ball-stick") {{
      viewer.setStyle({{}}, {{ stick:{{radius:0.12,colorscheme:"Jmol"}}, sphere:{{radius:0.28,colorscheme:"Jmol"}} }});
    }} else if (s === "stick") {{
      viewer.setStyle({{}}, {{ stick:{{radius:0.15,colorscheme:"Jmol"}} }});
    }} else if (s === "sphere") {{
      viewer.setStyle({{}}, {{ sphere:{{colorscheme:"Jmol"}} }});
    }} else {{
      viewer.setStyle({{}}, {{ line:{{colorscheme:"Jmol"}} }});
    }}
  }}

  function greyAll() {{
    viewer.setStyle({{}}, {{ stick:{{radius:0.08,color:'0x1a1e2e'}}, sphere:{{radius:0.18,color:'0x1a1e2e',opacity:0.35}} }});
  }}

  function addCenterLabel(c, hexColor) {{
    viewer.addLabel('(' + c.cfg + ') ' + c.sym + c.serial, {{
      serial: c.serial,
      fontSize: 13,
      fontColor: hexColor,
      backgroundColor: '#1a1500',
      backgroundOpacity: 0.92,
      borderColor: hexColor,
      borderThickness: 1,
      padding: 4,
      inFront: true
    }});
  }}

  // ── Redraw based on current selectedMode ────────────────────────────────
  function redraw() {{
    viewer.removeAllLabels();
    
    if (selectedMode === null) {{
      // No selection — show full molecule with all centre spheres
      baseStyle();
      allCentres.forEach(function(c) {{
        const col = c.cfg === 'R' ? COLOR_R : c.cfg === 'S' ? COLOR_S : '0x7b61ff';
        viewer.setStyle({{serial:c.serial}}, {{
          stick: {{radius:0.15, colorscheme:'Jmol'}},
          sphere: {{radius:0.52, color:col, opacity:0.88}}
        }});
      }});
      
    }} else if (selectedMode === 'ALL_R') {{
      // Highlight ALL R centres
      greyAll();
      rCentres.forEach(function(c) {{
        viewer.setStyle({{serial:c.serial}}, {{
          stick: {{radius:0.18, colorscheme:'Jmol'}},
          sphere: {{radius:0.68, color:COLOR_R, opacity:0.95}}
        }});
        addCenterLabel(c, '#ff4d6d');
      }});
      
    }} else if (selectedMode === 'ALL_S') {{
      // Highlight ALL S centres
      greyAll();
      sCentres.forEach(function(c) {{
        viewer.setStyle({{serial:c.serial}}, {{
          stick: {{radius:0.18, colorscheme:'Jmol'}},
          sphere: {{radius:0.68, color:COLOR_S, opacity:0.95}}
        }});
        addCenterLabel(c, '#00e5a0');
      }});
      
    }} else {{
      // Isolation mode (Single card clicked) — grey everything, yellow sphere on selected only
      greyAll();
      viewer.setStyle({{serial:selectedMode}}, {{
        stick: {{radius:0.18, colorscheme:'Jmol'}},
        sphere: {{radius:0.68, color:YELLOW, opacity:0.95}}
      }});
      const c = allCentres.find(function(x) {{ return x.serial === selectedMode; }});
      if (c) addCenterLabel(c, '#f5c518');
    }}
    
    viewer.render();
  }}

  // ── Selections ───────────────────────────────────────────────────────────
  function deselectCards() {{
    document.querySelectorAll('.centre-card').forEach(function(el) {{
      el.classList.remove('selected');
    }});
  }}

  window.selectCentre = function(serial) {{
    if (selectedMode === serial) {{
      selectedMode = null;
      deselectCards();
    }} else {{
      selectedMode = serial;
      deselectCards();
      const card = document.getElementById('card-' + serial);
      if (card) card.classList.add('selected');
    }}
    redraw();
  }};

  window.highlightAllR = function() {{
    selectedMode = 'ALL_R';
    deselectCards();
    redraw();
  }};

  window.highlightAllS = function() {{
    selectedMode = 'ALL_S';
    deselectCards();
    redraw();
  }};

  window.clearSelection = function() {{
    selectedMode = null;
    deselectCards();
    redraw();
  }};

  // ── Other controls ────────────────────────────────────────────────────────
  window.toggleSpin = function() {{
    if (spinning) {{
      viewer.spin(false); spinning = false;
      document.getElementById('btn-spin').classList.remove('active');
      document.getElementById('btn-spin').querySelector('.btn-led').style.background = '#252840';
      document.getElementById('btn-spin').querySelector('.btn-led').style.boxShadow = 'none';
    }} else {{
      viewer.spin('y', 0.6); spinning = true;
      document.getElementById('btn-spin').classList.add('active');
    }}
  }};

  window.toggleSurface = function() {{
    if (surfaceOn) {{
      viewer.removeSurface(surfaceObj); surfaceOn = false;
      document.getElementById('btn-surface').classList.remove('active');
    }} else {{
      surfaceObj = viewer.addSurface($3Dmol.SurfaceType.VDW, {{
        opacity:0.25, colorscheme:{{prop:"partialCharge", gradient:"rwb"}}
      }});
      surfaceOn = true;
      document.getElementById('btn-surface').classList.add('active');
    }}
    viewer.render();
  }};

  window.cycleStyle = function() {{
    styleIdx = (styleIdx + 1) % styles.length;
    redraw();
  }};

  window.resetView = function() {{
    viewer.zoomTo(); viewer.zoom(0.9); viewer.render();
  }};

  // ── Show hint briefly on load ────────────────────────────────────────────
  const notice = document.getElementById('reset-notice');
  notice.style.opacity = '1';
  setTimeout(function() {{ notice.style.opacity = '0'; }}, 2800);

  // ── Init ─────────────────────────────────────────────────────────────────
  redraw();
  viewer.zoomTo();
  viewer.zoom(0.9);
  viewer.render();
  {spin_js}
}});
</script>
</body>
</html>"""
    return html

# ── Sidebar ───────────────────────────────────────────────────────────────────
# ── Hidden default variables to replace the removed sliders ───────────────────
img_w, img_h = 1000, 800  # High-res base, CSS scales it down dynamically
viewer_h = 480
auto_spin = True

# ── Hidden default variables ──────────────────────────────────────────────────
img_w, img_h = 1000, 800
viewer_h = 480
auto_spin = True

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
    preset = st.selectbox("Choose a preset", ["— Select a Molecule —"] + list(PRESET_MOLECULES.keys()))

    st.markdown("<hr style='border-color:#1e2230'>", unsafe_allow_html=True)
    
    # Create an empty slot to inject our dynamic stats later!
    sidebar_stats = st.empty()
    
    st.markdown("<hr style='border-color:#1e2230'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:Space Mono,monospace;font-size:.7rem;color:#5a6080;line-height:1.8'>
        <b style='color:#e8eaf0'>Colour key</b><br>
        🔴 R-centre<br>
        🟢 S-centre<br>
        🟣 Unassigned
    </div>
    """, unsafe_allow_html=True)


# --- Welcome Pop-up Logic ---
if "welcome_shown" not in st.session_state:
    st.session_state["welcome_shown"] = False

if not st.session_state["welcome_shown"]:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                /* Hide normal UI */
                [data-testid="stSidebar"], [data-testid="stHeader"] {display: none;}
                
                .splash-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    width: 100vw;
                    background: #0a0c10;
                    position: fixed;
                    top: 0; left: 0;
                    z-index: 99;
                }
                .splash-card {
                    background: #111318;
                    border: 1px solid #1e2230;
                    border-radius: 24px;
                    padding: 50px 50px 100px 50px; /* Extra bottom padding for button space */
                    box-shadow: 0 20px 60px rgba(0,0,0,0.7);
                    border-top: 4px solid #00e5a0;
                    max-width: 450px;
                    text-align: center;
                    font-family: 'Syne', sans-serif;
                }
                .splash-title { font-size: 2.8rem; margin: 0; color: white; letter-spacing: -2px; }
                .splash-sub { color: #5a6080; font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 4px; margin-bottom: 30px; text-transform: uppercase; }
                .splash-info { font-family: 'Space Mono', monospace; line-height: 1.8; color: #e8eaf0; }
                
                /* Position the REAL Streamlit button over the splash card */
                div.stButton {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, 125px); /* Moves it exactly into the card bottom */
                    z-index: 100;
                    width: 300px;
                }
                div.stButton > button {
                    width: 100% !important;
                    background: linear-gradient(135deg, #00e5a0, #7b61ff) !important;
                    color: black !important;
                    font-weight: 800 !important;
                    border: none !important;
                    height: 45px;
                    border-radius: 12px;
                }
            </style>
            <div class="splash-container">
                <div class="splash-card">
                    <h1 class="splash-title">ChiralSense</h1>
                    <p class="splash-sub">STEREOCID EXPLORER</p>
                    <div class="splash-info">
                        <span style="color: #8a90a8; font-size: 0.9rem;">Project Developed By:</span><br>
                        <b style="font-size: 1.5rem; color: #00e5a0; display: block; margin-bottom: 5px;">C Thrinay </b>
                        <code style="color: #7b61ff; background: transparent; font-size: 1rem;">RA2511026050052</code><br>
                        <span style="font-size: 0.9rem; color: #8a90a8; display: block; margin-top: 10px;">Class: AIML - "A"</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # This button now gets 'teleported' into the card by the CSS above
        if st.button("ENTER EXPLORER"):
            st.session_state["welcome_shown"] = True
            placeholder.empty()
            st.rerun()
    
    st.stop()  
# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <h1 class='hero-title'>ChiralSense</h1>
  <p class='hero-sub'>Stereochemistry · R/S Configuration · 2-D &amp; 3-D Visualization</p>
</div>
""", unsafe_allow_html=True)

# ── Preset bug fix ────────────────────────────────────────────────────────────
if "last_preset" not in st.session_state:
    st.session_state["last_preset"] = preset

if preset != st.session_state["last_preset"]:
    st.session_state["fetched_smiles"] = ""
    st.session_state["last_preset"] = preset

if st.session_state.get("fetched_smiles", ""):
    default_smiles = st.session_state["fetched_smiles"]
elif preset != "— Select a Molecule —":
    default_smiles = PRESET_MOLECULES.get(preset, "")
else:
    default_smiles = ""

col_in, _ = st.columns([3, 1])
with col_in:
    smiles_input = st.text_input(
        "SMILES string",
        value=default_smiles,
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
                    st.session_state["last_preset"] = preset
                    st.session_state["pubchem_found_name"] = mol_name.strip()
                    st.rerun()
                else:
                    st.markdown("<div class='error-box'>✗ Molecule not found on PubChem.</div>",
                                unsafe_allow_html=True)

# ── PubChem found banner ──────────────────────────────────────────────────────
if st.session_state.get("pubchem_found_name") and st.session_state.get("fetched_smiles"):
    found_name = st.session_state["pubchem_found_name"]
    found_smi  = st.session_state["fetched_smiles"]
    st.markdown(f"""
    <div style='
        display:flex; align-items:center; gap:12px;
        background:rgba(0,229,160,0.07);
        border:1px solid rgba(0,229,160,0.3);
        border-left:4px solid #00e5a0;
        border-radius:10px;
        padding:.65rem 1rem;
        margin-bottom:.6rem;
        font-family:Space Mono,monospace;
        font-size:.8rem;
        animation: fadeSlideIn 0.4s ease;
    '>
        <span style='font-size:1.2rem;'>🔬</span>
        <div>
            <span style='color:#00e5a0;font-weight:700;letter-spacing:1px;'>
                MOLECULE FOUND
            </span>
            &nbsp;·&nbsp;
            <span style='color:#e8eaf0;'>{found_name.title()}</span>
            <div style='color:#5a6080;font-size:.7rem;margin-top:2px;
                        max-width:500px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>
                {found_smi}
            </div>
        </div>
    </div>
    <style>
    @keyframes fadeSlideIn {{
        from {{ opacity:0; transform:translateY(-6px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)

col_btn, _ = st.columns([1, 3])
with col_btn:
    analyse = st.button("⚗ Analyse Molecule")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── Analysis ──────────────────────────────────────────────────────────────────
if analyse and smiles_input.strip():
    mol = Chem.MolFromSmiles(smiles_input.strip())

    if mol is None:
        st.markdown("<div class='error-box'>✗ Invalid SMILES — please check your input and try again.</div>",
                    unsafe_allow_html=True)
    else:
        chiral_info  = get_chiral_info(mol)
        canon_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        n_R   = sum(1 for c in chiral_info if c["config"] == "R")
        n_S   = sum(1 for c in chiral_info if c["config"] == "S")
        n_un  = sum(1 for c in chiral_info if c["config"] == "?")
        n_ch  = len(chiral_info)

        # --- Calculate Dynamic Stats for the Sidebar ---
        formula = rdMolDescriptors.CalcMolFormula(mol)
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        tpsa = Descriptors.TPSA(mol)
        hbd = rdMolDescriptors.CalcNumLipinskiHBD(mol)
        hba = rdMolDescriptors.CalcNumLipinskiHBA(mol)

    # Try to figure out the molecule's name
        current_name = None
        if preset and preset != "— Select a Molecule —":
            current_name = preset
        elif st.session_state.get("pubchem_found_name") and st.session_state.get("fetched_smiles") == smiles_input.strip():
            current_name = st.session_state["pubchem_found_name"].title()
        
        # 1. Grab our hardcoded fun fact (if it exists)
        custom_note = MOLECULE_NOTES.get(current_name)
        
        # 2. Grab the official PubChem description
        pubchem_note = None
        if current_name:
            fetched_note = get_pubchem_description(current_name)
            if fetched_note:
                pubchem_note = fetched_note[:350] + "..." if len(fetched_note) > 350 else fetched_note
        
        # 3. Combine them beautifully
        notes_html = ""
        if custom_note:
            notes_html += f"<div style='margin-bottom:12px;'><span style='color:#ff4d6d;font-weight:700;'> 💡Quick Fact</span><br>{custom_note}</div>"
        if pubchem_note:
            notes_html += f"<div><span style='color:#00e5a0;font-weight:700;'>⭕ PubChem Summary</span><br>{pubchem_note}</div>"
            
        if not notes_html:
            notes_html = "No real-world data available for this specific structure."
            current_name = "Custom Molecule" if not current_name else current_name

        sidebar_stats.markdown(f"""
        <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e8eaf0;margin-bottom:0.8rem;'>
            Molecule Properties
        </div>
        <div style='background:rgba(14,16,22,0.6); border:1px solid #1e2230; border-radius:10px; padding:1rem; font-family:Space Mono,monospace; font-size:0.75rem; line-height:2; margin-bottom:1.5rem;'>
            <div style='color:#5a6080; border-bottom:1px dashed #1e2230; padding-bottom:4px; margin-bottom:4px;'>
                Formula <span style='float:right; color:#00e5a0; font-weight:700; font-size:0.85rem;'>{formula}</span>
            </div>
            <div style='color:#8a90a8;'>Mol Weight <span style='float:right; color:#e8eaf0;'>{mw:.2f} g/mol</span></div>
            <div style='color:#8a90a8;'>LogP <span style='float:right; color:#e8eaf0;'>{logp:.2f}</span></div>
            <div style='color:#8a90a8;'>TPSA <span style='float:right; color:#e8eaf0;'>{tpsa:.1f} &Aring;&sup2;</span></div>
            <div style='color:#8a90a8;'>H-Bond Donors <span style='float:right; color:#e8eaf0;'>{hbd}</span></div>
            <div style='color:#8a90a8;'>H-Bond Acceptors <span style='float:right; color:#e8eaf0;'>{hba}</span></div>
        </div>

        <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e8eaf0;margin-bottom:0.8rem;'>
             Bioactivity & Notes
        </div>
        <div style='background:rgba(255,77,109,0.05); border:1px solid rgba(255,77,109,0.2); border-left:3px solid #ff4d6d; border-radius:8px; padding:0.8rem 1rem; font-family:Space Mono,monospace; font-size:0.75rem; color:#c8cad8; line-height:1.6;'>
            <div style='font-family:Syne,sans-serif; font-size:1.1rem; color:#e8eaf0; font-weight:800; margin-bottom:8px;'>{current_name}</div>
            {notes_html}
        </div>
        """, unsafe_allow_html=True)        


        # Stats row
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Molecule Summary</div>", unsafe_allow_html=True)
        cols = st.columns(5)
        for col, (val, lbl) in zip(cols, [
            (n_ch, "Chiral Centres"), (n_R, "R Centres"), (n_S, "S Centres"),
            (n_un, "Unassigned"), (mol.GetNumAtoms(), "Heavy Atoms"),
        ]):
            col.markdown(f"""
            <div class='stat-box'>
              <div class='stat-val'>{val}</div>
              <div class='stat-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        tab2d, tab3d, tab_det = st.tabs(["⬡  2D Structure", "⬡  3D Interactive", "⬡  Centre Details"])

        # ── TAB 1: 2D ──────────────────────────────────────────────────────
        with tab2d:
            left, right = st.columns([1.3, 1])

            with left:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>2-D Structure with Stereo Highlights</div>",
                            unsafe_allow_html=True)

                viewer_2d_html = build_2d_viewer_html(mol, chiral_info, img_w, img_h)
                st.components.v1.html(viewer_2d_html, height=img_h + 75, scrolling=False)

                st.markdown("""
                <div class='legend' style='margin-top:.8rem;'>
                  <div class='legend-item'><div class='dot dot-R'></div>R-centre</div>
                  <div class='legend-item'><div class='dot dot-S'></div>S-centre</div>
                  <div class='legend-item'><div class='dot dot-chiral'></div>Unassigned</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>Canonical SMILES (with stereo)</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='smiles-box'>{canon_smiles}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

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
                    st.markdown("<div style='font-family:Space Mono,monospace;font-size:.85rem;"
                                "color:#5a6080;padding:.5rem 0;'>No chiral centres found.</div>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

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

        # ── TAB 2: 3D ──────────────────────────────────────────────────────
        with tab3d:
            with st.spinner("Generating 3D coordinates…"):
                mol2d = Chem.MolFromSmiles(canon_smiles)
                molblock = mol_to_molblock(mol2d)

            if molblock is None:
                st.markdown("<div class='error-box'>✗ Could not generate 3D coordinates for this molecule.</div>",
                            unsafe_allow_html=True)
            else:
                viewer_html = build_3d_viewer_html(molblock, chiral_info, height=viewer_h, spin=auto_spin)

                st.markdown("<div class='viewer-card'>", unsafe_allow_html=True)
                st.components.v1.html(viewer_html, height=viewer_h + 4, scrolling=False)
                st.markdown("</div>", unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                for col, (val, lbl, color) in zip([c1, c2, c3, c4], [
                    ("ETKDG v3\n+ MMFF", "Method",         "#00e5a0"),
                    (n_ch,               "Chiral Centres",  "#7b61ff"),
                    (n_R,                "R Centres",       "#ff4d6d"),
                    (n_S,                "S Centres",       "#00e5a0"),
                ]):
                    col.markdown(f"""
                    <div class='card' style='text-align:center;margin-top:.8rem;'>
                      <div class='card-title'>{lbl}</div>
                      <div style='font-family:Space Mono,monospace;font-size:{"0.75rem" if isinstance(val, str) else "1.4rem"};
                                  font-weight:700;color:{color};white-space:pre;'>{val}</div>
                    </div>""", unsafe_allow_html=True)

        # ── TAB 3: Details ─────────────────────────────────────────────────
        with tab_det:
            if not chiral_info:
                st.markdown("""<div style='text-align:center;padding:3rem;font-family:Space Mono,monospace;
                             font-size:.9rem;color:#5a6080;'>No chiral centres found.</div>""",
                            unsafe_allow_html=True)
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
                        {"— clockwise priority sequence" if cfg=="R" else "— anticlockwise priority sequence" if cfg=="S" else "— stereochemistry unassigned"}<br>
                        <b style='color:#8a90a8;'>CIP Rule:</b>
                        {"Rotate 1→2→3 away from lowest priority. Clockwise = R." if cfg=="R" else "Rotate 1→2→3 away from lowest priority. Anticlockwise = S." if cfg=="S" else "Configuration could not be assigned from SMILES."}
                      </div>
                    </div>""", unsafe_allow_html=True)

                if n_ch > 0:
                    max_iso = 2 ** n_ch
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='card-title'>Stereoisomer Enumeration</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='font-family:Space Mono,monospace;font-size:.82rem;color:#8a90a8;line-height:2;'>
                      {n_ch} chiral centre{"s" if n_ch>1 else ""} → maximum
                      <span style='color:#7b61ff;font-size:1.1rem;font-weight:700;'> 2<sup>{n_ch}</sup> = {max_iso} </span>
                      stereoisomers<br>
                      <span style='color:#5a6080;font-size:.72rem;'>
                        Actual count may be lower due to meso forms or molecular symmetry.
                      </span>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

elif not smiles_input.strip() and analyse:
    st.markdown("<div class='error-box'>✗ Please enter a SMILES string or choose a preset molecule.</div>",
                unsafe_allow_html=True)

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
