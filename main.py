import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from rdkit.Chem.Draw import rdMolDraw2D

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
</style>
""", unsafe_allow_html=True)


# ── Preset molecules ──────────────────────────────────────────────────────────
PRESET_MOLECULES = {
    "L-Alanine":        "N[C@@H](C)C(=O)O",
    "D-Alanine":        "N[C@H](C)C(=O)O",
    "L-Phenylalanine":  "N[C@@H](Cc1ccccc1)C(=O)O",
    "Glucose (D)":      "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
    "Cocaine":          "COC(=O)[C@H]1[C@@H]2CC[C@@H](C1)N2C",
    "Thalidomide":      "O=C1CCC(=O)N1[C@@H]1C(=O)Nc2ccccc21",
    "Ibuprofen (S)":    "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "Limonene (R)":     "CC(=C)[C@@H]1CCC(=CC1)C",
    "Camphor":          "O=C1C[C@@H]2CC1(C)C2(C)C",
    "Aspartame":        "COC(=O)[C@@H](Cc1ccccc1)NC(=O)[C@@H](N)CC(=O)O",
    "Morphine":         "O=C1OC[C@H]2c3ccc(O)c(O)c3CC[C@@H]12",
    "Penicillin G":     "O=C(O)[C@@H]1[C@H]2SC(C)(C)[C@@H](N2C1=O)C(=O)Nc1ccccc1",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_chiral_info(mol):
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    centres = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    return [{"idx": idx, "symbol": mol.GetAtomWithIdx(idx).GetSymbol(), "config": cfg}
            for idx, cfg in centres]


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
    st.markdown("""
    <div style='font-family:Space Mono,monospace;font-size:.7rem;color:#5a6080;line-height:1.8'>
    <b style='color:#e8eaf0'>R/S Assignment</b><br>
    Based on CIP priority rules.<br>
    Atoms highlighted directly on the 2-D structure.<br><br>
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
  <p class='hero-sub'>Stereochemistry · R/S Configuration · 2-D Visualization</p>
</div>
""", unsafe_allow_html=True)

col_in, _ = st.columns([3, 1])
with col_in:
    default_smiles = PRESET_MOLECULES.get(preset, "") if preset != "— enter SMILES —" else ""
    smiles_input = st.text_input(
        "SMILES string",
        value=default_smiles,
        placeholder="e.g.  N[C@@H](C)C(=O)O",
        label_visibility="collapsed",
    )

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

        # Stats row
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

        left, right = st.columns([1.3, 1])

        with left:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>2-D Structure with Stereo Highlights</div>",
                        unsafe_allow_html=True)

            ha, hc = build_highlight_map(chiral_info)
            svg = mol_to_svg(mol, width=img_w, height=img_h,
                             highlight_atoms=ha, highlight_colors=hc)
            svg_styled = svg.replace("<svg ", "<svg style='background:#ffffff;border-radius:12px;' ", 1)
            st.components.v1.html(svg_styled, height=img_h + 20, scrolling=False)

            st.markdown("""
            <div class='legend'>
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

            # Chiral centres
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
        Chiral centres · R/S labels · 2-D structure
      </div>
    </div>
    """, unsafe_allow_html=True)