import streamlit as st
from PIL import Image, ImageDraw
from typing import List, Dict, Any
from dataclasses import dataclass, field
import json
import os

st.set_page_config(page_title="AI Outfit & Style Recommender", page_icon="👗", layout="wide")

# -----------------------------
# Data Models
# -----------------------------
@dataclass
class Outfit:
    name: str = ""
    style: str = ""
    gender: str = ""
    occasions: List[str] = field(default_factory=list)
    pieces: List[str] = field(default_factory=list)
    footwear: List[str] = field(default_factory=list)
    accessories: List[str] = field(default_factory=list)
    makeup_grooming: List[str] = field(default_factory=list)
    fit_tips: List[str] = field(default_factory=list)
    body_notes: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    thumbnail: str = ""

# -----------------------------
# Utilities
# -----------------------------
def load_rules(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Fix 'occasion' → 'occasions' and remove unknown keys
    for outfit in data.get("outfits", []):
        if "occasion" in outfit:
            outfit["occasions"] = [outfit.pop("occasion")]
        valid_keys = Outfit.__dataclass_fields__.keys()
        for key in list(outfit.keys()):
            if key not in valid_keys:
                outfit.pop(key)
    return data

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def palette_image(colors: List[Dict[str, str]], width=900, height=140) -> Image.Image:
    n = len(colors) if colors else 1
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    sw = max(1, width // n)
    for i, c in enumerate(colors):
        rgb = hex_to_rgb(c["hex"])
        draw.rectangle([i*sw, 0, (i+1)*sw, height], fill=rgb)
    return img

def outfit_matches(outfit: Outfit, occasion: str, style_pref: str, gender: str) -> bool:
    if style_pref != "Any" and outfit.style != style_pref:
        return False
    if outfit.gender not in ("Unisex", gender):
        return False
    if occasion not in outfit.occasions and "All" not in outfit.occasions:
        return False
    return True

# -----------------------------
# App
# -----------------------------
RULES_PATH = "rules.json"   # JSON file in same folder
rules = load_rules(RULES_PATH)

st.title("👗 AI Outfit & Style Recommender (Visual)")

with st.sidebar:
    occasion = st.selectbox("Occasion / Event", rules["occasions"])
    gender = st.selectbox("Presentation", ["Female", "Male", "Unisex"])
    style_pref = st.selectbox("Preferred Style", ["Any", "Western", "Ethnic", "Fusion"])
    skin_tone = st.selectbox("Skin Tone", list(rules["skin_tone_palettes"].keys()))
    body_type = st.selectbox("Body Type", rules["body_types"])

palette = rules["skin_tone_palettes"].get(skin_tone, [])
st.subheader("🎨 Suggested Color Palette")
st.image(palette_image(palette), use_container_width=True)

matches: List[Outfit] = []
for item in rules["outfits"]:
    # Clean the item to match Outfit dataclass
    clean_item = {k:v for k,v in item.items() if k in Outfit.__dataclass_fields__}
    out = Outfit(**clean_item)
    if outfit_matches(out, occasion, style_pref, gender):
        matches.append(out)

if not matches:
    st.warning("No exact matches found.")
else:
    st.subheader("🧭 Recommended Looks")
    for idx, out in enumerate(matches[:3], 1):
        st.markdown(f"### Look {idx}: {out.name}")
        st.write("Pieces:", ", ".join(out.pieces))
        st.write("Footwear:", ", ".join(out.footwear))
        st.write("Accessories:", ", ".join(out.accessories))
        st.write("Makeup/Grooming:", ", ".join(out.makeup_grooming))
        st.write("Fit Tips:", ", ".join(out.fit_tips))
        st.write("Body Notes:", out.body_notes.get(body_type, "No notes"))




