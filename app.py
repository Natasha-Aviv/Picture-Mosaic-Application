import streamlit as st
from PIL import Image, ImageOps, ImageStat, ImageChops, ImageFilter, ImageDraw, ImageFont
import numpy as np
import random
import hashlib
from scipy.spatial import KDTree
from datetime import datetime
from io import BytesIO
import tempfile
import os
import uuid
import pandas as pd
from pathlib import Path

MAX_IMAGES = 500

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Mosaic Studio Pro",
    page_icon="🖼️",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "processing" not in st.session_state:
    st.session_state.processing = False

if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

if "download_ready" not in st.session_state:
    st.session_state.download_ready = False

# ---------------- IMMERSIVE CUSTOM WEBSITE UI ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Playfair+Display:wght@600;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(56,189,248,0.22), transparent 28%),
            radial-gradient(circle at 90% 8%, rgba(139,92,246,0.26), transparent 30%),
            radial-gradient(circle at 50% 95%, rgba(34,197,94,0.10), transparent 28%),
            linear-gradient(135deg, #050816 0%, #0f172a 45%, #020617 100%);
        color: #f8fafc;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3.5rem;
        max-width: 1240px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.3rem 2.4rem;
        border-radius: 32px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.72), rgba(30,41,59,0.48)),
            linear-gradient(135deg, rgba(56,189,248,0.20), rgba(139,92,246,0.22));
        border: 1px solid rgba(255,255,255,0.16);
        box-shadow: 0 28px 80px rgba(0,0,0,0.42);
        margin-bottom: 1.2rem;
    }

    .hero:before {
        content: "";
        position: absolute;
        inset: -80px;
        background-image:
            linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
        background-size: 34px 34px;
        mask-image: linear-gradient(90deg, rgba(0,0,0,0.55), transparent 78%);
        opacity: 0.45;
    }

    .hero-content {
        position: relative;
        z-index: 1;
        max-width: 860px;
    }

    .eyebrow {
        display: inline-flex;
        gap: 0.5rem;
        align-items: center;
        padding: 0.45rem 0.78rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        color: #dbeafe;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: clamp(2.4rem, 5vw, 4.6rem);
        line-height: 0.96;
        font-weight: 700;
        color: white;
        margin: 0 0 0.85rem 0;
        letter-spacing: -0.04em;
    }

    .hero p {
        font-size: 1.08rem;
        line-height: 1.75;
        color: #cbd5e1;
        max-width: 760px;
        margin: 0;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1.35rem;
    }

    .pill {
        padding: 0.62rem 0.9rem;
        border-radius: 999px;
        background: rgba(2,6,23,0.42);
        border: 1px solid rgba(255,255,255,0.12);
        color: #e2e8f0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .flow-card, .glass-card {
        padding: 1.35rem 1.45rem;
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(15,23,42,0.78), rgba(30,41,59,0.58));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 16px 44px rgba(0,0,0,0.28);
        margin: 1rem 0;
    }

    .step-row {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }

    .step-badge {
        flex: 0 0 auto;
        width: 46px;
        height: 46px;
        display: grid;
        place-items: center;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(56,189,248,0.95), rgba(139,92,246,0.95));
        color: white;
        font-weight: 900;
        box-shadow: 0 12px 26px rgba(56,189,248,0.22);
    }

    .step-title {
        color: white;
        font-size: 1.28rem;
        font-weight: 850;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .muted-text {
        color: #aebbd0;
        font-size: 0.96rem;
        line-height: 1.65;
    }

    .metric-card {
        padding: 1.1rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(2,6,23,0.52), rgba(30,41,59,0.70));
        border: 1px solid rgba(255,255,255,0.12);
        text-align: center;
        margin-bottom: 0.8rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
    }

    .metric-card h3 {
        color: white;
        margin: 0;
        font-size: 1.65rem;
        font-weight: 900;
        letter-spacing: -0.03em;
    }

    .metric-card p {
        color: #94a3b8;
        margin: 0.35rem 0 0 0;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .download-panel {
        margin-top: 1.3rem;
        padding: 1.65rem;
        border-radius: 30px;
        background:
            radial-gradient(circle at 10% 10%, rgba(34,197,94,0.26), transparent 30%),
            linear-gradient(135deg, rgba(15,23,42,0.86), rgba(22,101,52,0.38));
        border: 1px solid rgba(187,247,208,0.22);
        text-align: center;
        box-shadow: 0 22px 60px rgba(0,0,0,0.38);
    }

    .download-panel h2 {
        color: white;
        margin: 0 0 0.4rem 0;
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: -0.03em;
    }

    .download-panel p {
        color: #cbd5e1;
        font-size: 1rem;
        margin: 0;
    }

    .form-card {
        margin-top: 1rem;
        padding: 1.45rem;
        border-radius: 26px;
        background: rgba(2, 6, 23, 0.68);
        border: 1px solid rgba(255,255,255,0.14);
        box-shadow: 0 18px 45px rgba(0,0,0,0.35);
    }

    .form-card h3 {
        color: white;
        margin: 0 0 0.25rem 0;
        font-weight: 850;
    }

    .form-card p {
        color: #94a3b8;
        margin: 0;
    }

    div.stButton > button {
        border-radius: 16px;
        min-height: 3.15rem;
        font-weight: 850;
        border: 1px solid rgba(255,255,255,0.16);
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        box-shadow: 0 14px 28px rgba(37,99,235,0.25);
        transition: transform 0.15s ease, filter 0.15s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
        color: white;
        border: 1px solid rgba(255,255,255,0.22);
    }

    div[data-testid="stDownloadButton"] > button {
        border-radius: 20px;
        min-height: 4.2rem;
        font-size: 1.15rem;
        font-weight: 950;
        background: linear-gradient(135deg, #22c55e, #16a34a) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.26) !important;
        box-shadow: 0 18px 42px rgba(34,197,94,0.35) !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 50% 0%, rgba(139,92,246,0.20), transparent 38%),
            linear-gradient(180deg, #020617, #0f172a);
        border-right: 1px solid rgba(255,255,255,0.10);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    [data-testid="stFileUploader"] {
        border-radius: 24px;
        padding: 0.4rem;
        background: rgba(255,255,255,0.03);
    }

    [data-testid="stImage"] img {
        border-radius: 22px;
        box-shadow: 0 20px 55px rgba(0,0,0,0.35);
    }

    input, textarea, select {
        border-radius: 14px !important;
    }

    [data-testid="stStatusWidget"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        background-color: rgba(15, 23, 42, 0.96) !important;
        border: 1px solid rgba(255,255,255,0.16) !important;
        padding: 22px 44px !important;
        border-radius: 20px !important;
        z-index: 99999 !important;
        box-shadow: 0 24px 70px rgba(0,0,0,0.58) !important;
    }

    [data-testid="stStatusWidget"] label {
        font-size: 1.1rem !important;
        color: white !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

Image.MAX_IMAGE_PIXELS = None

# ---------------- MOSAIC FOOTER QUOTES ----------------

MOSAIC_QUOTES = [
    "A thousand tiny squares, a thousand different days, one single masterpiece.",
    "Up close, it’s a collection of our favorite moments; from afar, it’s the shape of our lives.",
    "Every little photo is a puzzle piece; you need every single one to see the real picture.",
    "Look closely: the details hold the memories; step back: the whole holds the beauty.",
    "We are a mosaic of everywhere we’ve been and every tiny moment we’ve captured along the way.",
    "No single snapshot defines the whole story; we are the sum of a thousand little frames.",
    "A single beautiful image, built entirely out of a thousand reasons to smile.",
    "It’s not just one big picture on the wall; it’s an entire gallery of joy hiding in plain sight.",
    "The bigger picture is stunning, but the tiny hidden moments it’s made of are what matter most.",
    "Every pixel is a story, every grid is a timeline, and every mosaic is a lifetime.",
    "A macro view of who we are right now, built from the micro moments of exactly how we got here.",
    "It takes hundreds of snapshots to make one perfect memory; zoom in to remember, zoom out to appreciate.",
    "Small flashes of time, gathered together to form one brilliant image.",
    "Every tiny square is a second of joy, stacked beautifully side by side.",
    "We don’t just capture time; we weave it all together into a single view.",
    "Alone, they are just fragments; together, they are a masterpiece.",
    "The beauty of a mosaic isn’t just the final picture, but the patience of putting the pieces together.",
    "Like stained glass, our memories shine brightest when they are placed right next to each other.",
    "The grand design is always made of tiny, seemingly ordinary moments.",
    "Step close to remember the day; step back to see the journey.",
    "It’s an illusion made of truth: one giant photograph woven from hundreds of real memories.",
    "A mosaic is proof that the little things always add up to something magnificent.",
    "Look at the whole to see where we are; look at the pieces to see exactly how we got here.",
    "Hundreds of little memories, held tightly together by one big feeling.",
    "Infinite tiny stories hidden within one beautiful frame.",
    "We are all just mosaics — a beautiful collection of every little moment we’ve ever lived."
]


def get_font(size, style="serif", bold=False):
    """
    Safely load premium fonts.
    For calligraphy, put any of these fonts inside assets/fonts/:
    - GreatVibes-Regular.ttf
    - Allura-Regular.ttf
    - DancingScript-Regular.ttf
    - Parisienne-Regular.ttf
    """
    font_dirs = [
        Path("assets/fonts"),
        Path("fonts"),
        Path("."),
        Path("C:/Windows/Fonts"),
    ]

    if style == "script":
        possible_fonts = [
            "GreatVibes-Regular.ttf",
            "Allura-Regular.ttf",
            "DancingScript-Regular.ttf",
            "Parisienne-Regular.ttf",
            "Pacifico-Regular.ttf",
            "Sacramento-Regular.ttf",
            "Segoe Script.ttf",
            "segoesc.ttf",
            "Brush Script MT.ttf",
            "BRUSHSCI.TTF",
            "ariali.ttf",
            "Arial Italic.ttf",
            "DejaVuSerif-Italic.ttf",
        ]
    elif style == "serif":
        possible_fonts = [
            "Georgia.ttf",
            "georgia.ttf",
            "Times New Roman.ttf",
            "times.ttf",
            "DejaVuSerif.ttf",
            "NotoSerif-Regular.ttf",
        ]
    else:
        possible_fonts = [
            "arialbd.ttf" if bold else "arial.ttf",
            "Arial Bold.ttf" if bold else "Arial.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf",
        ]

    # First try bundled / local font files.
    for folder in font_dirs:
        for font_name in possible_fonts:
            font_path = folder / font_name
            try:
                if font_path.exists():
                    return ImageFont.truetype(str(font_path), size)
            except Exception:
                pass

    # Then try system font lookup by name.
    for font_name in possible_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            continue

    return ImageFont.load_default()


def draw_text_with_tracking(draw, position, text, font, fill, tracking=0):
    """Draw single-line text with small letter spacing."""
    x, y = position
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), char, font=font)
        x += (bbox[2] - bbox[0]) + tracking


def text_width_with_tracking(draw, text, font, tracking=0):
    width = 0
    for char in text:
        bbox = draw.textbbox((0, 0), char, font=font)
        width += (bbox[2] - bbox[0]) + tracking
    return max(0, width - tracking)




def get_dynamic_footer_colors(reference_image):
    """
    Creates a soft footer background based on the dominant mood of the portrait.
    Red/warm portraits become light red/peach; blue portraits become light blue; green portraits become light green.
    """
    try:
        img = reference_image.convert("RGB")
        img.thumbnail((180, 180), Image.Resampling.LANCZOS)
        arr = np.asarray(img).reshape(-1, 3).astype(np.float32)

        brightness = arr.mean(axis=1)
        useful = arr[(brightness > 35) & (brightness < 235)]
        if len(useful) < 50:
            useful = arr

        max_c = useful.max(axis=1)
        min_c = useful.min(axis=1)
        saturation = max_c - min_c
        weights = 1.0 + (saturation / 255.0) * 2.5
        avg = np.average(useful, axis=0, weights=weights)

        r, g, b = avg
        total = r + g + b + 1e-6
        r_ratio, g_ratio, b_ratio = r / total, g / total, b / total

        # 80% white + 20% portrait color tint.
        tint_strength = 0.20
        white_base = np.array([255, 255, 255], dtype=np.float32)
        footer_bg_arr = white_base * (1 - tint_strength) + avg * tint_strength

        if r_ratio > 0.42 and r > g * 1.10 and r > b * 1.10:
            footer_bg = (255, 226, 226)
        elif g_ratio > 0.40 and g > r * 1.08 and g > b * 1.08:
            footer_bg = (226, 248, 229)
        elif b_ratio > 0.40 and b > r * 1.08 and b > g * 1.08:
            footer_bg = (226, 235, 255)
        else:
            footer_bg = tuple(np.clip(footer_bg_arr, 224, 255).astype(int))

        quote_color = (45, 42, 38)
        soft_color = (88, 80, 72)
        signature_color = (28, 25, 23)
        divider_color = tuple(int(max(170, c * 0.84)) for c in footer_bg)

        return footer_bg, quote_color, soft_color, signature_color, divider_color

    except Exception:
        return (250, 248, 243), (50, 47, 42), (92, 84, 74), (31, 27, 24), (214, 205, 190)


def add_mosaic_footer(image, reference_image=None):
    """
    Compact premium footer with fixed 80%-20% layout:
    - Quote stays as one straight sentence on the left 80%.
    - Regards + calligraphy Team Aviv stays unchanged on the right 20%.
    - Quote font auto-shrinks only if a long quote needs fitting.
    """
    img = image.convert("RGB")
    width, height = img.size

    # Smaller footer than before, with proportional scaling.
    footer_height = max(150, int(height * 0.065))
    padding_x = max(52, int(width * 0.045))
    inner_top = max(22, int(footer_height * 0.18))
    inner_bottom = max(20, int(footer_height * 0.16))

    # Dynamic footer color based on the selected portrait/mosaic mood.
    color_source = reference_image if reference_image is not None else img
    footer_bg, quote_color, soft_color, signature_color, divider_color = get_dynamic_footer_colors(color_source)

    final_with_footer = Image.new("RGB", (width, height + footer_height), footer_bg)
    final_with_footer.paste(img, (0, 0))

    draw = ImageDraw.Draw(final_with_footer)

    # Thin divider, gently inset with equal padding.
    line_y = height + max(12, int(footer_height * 0.10))
    draw.line(
        (padding_x, line_y, width - padding_x, line_y),
        fill=divider_color,
        width=max(1, int(width * 0.00055))
    )

    quote = random.choice(MOSAIC_QUOTES).replace("\n", " ").strip()

    # 80%-20% fixed layout.
    left_width = int(width * 0.80)
    right_width = width - left_width

    quote_area_x = padding_x
    quote_area_right = left_width - max(18, int(width * 0.012))
    quote_max_width = max(80, quote_area_right - quote_area_x)

    # Smaller typography for a more elegant footer.
    base_quote_font_size = max(20, int(width * 0.0135))
    min_quote_font_size = max(12, int(base_quote_font_size * 0.62))
    regards_font_size = max(17, int(width * 0.0105))
    signature_font_size = max(30, int(width * 0.0205))

    # Auto-fit quote so it remains a single straight line inside the left 80%.
    quote_font_size = base_quote_font_size
    quote_font = get_font(quote_font_size, style="serif")
    quote_bbox = draw.textbbox((0, 0), quote, font=quote_font)
    quote_w = quote_bbox[2] - quote_bbox[0]

    while quote_w > quote_max_width and quote_font_size > min_quote_font_size:
        quote_font_size -= 1
        quote_font = get_font(quote_font_size, style="serif")
        quote_bbox = draw.textbbox((0, 0), quote, font=quote_font)
        quote_w = quote_bbox[2] - quote_bbox[0]

    # If even the minimum font is too wide, trim cleanly with ellipsis.
    if quote_w > quote_max_width:
        ellipsis = "…"
        trimmed_quote = quote
        while trimmed_quote and draw.textbbox((0, 0), trimmed_quote + ellipsis, font=quote_font)[2] > quote_max_width:
            trimmed_quote = trimmed_quote[:-1].rstrip()
        quote = trimmed_quote + ellipsis
        quote_bbox = draw.textbbox((0, 0), quote, font=quote_font)

    regards_font = get_font(regards_font_size, style="sans", bold=False)
    signature_font = get_font(signature_font_size, style="script")
    signature_gap = max(3, int(signature_font_size * 0.08))

    usable_h_start = height + inner_top
    usable_h_end = height + footer_height - inner_bottom
    usable_h = usable_h_end - usable_h_start

    # Draw quote as a single straight sentence in the left 80%.
    quote_h = quote_bbox[3] - quote_bbox[1]
    quote_y = usable_h_start + max(0, (usable_h - quote_h) // 2)

    draw.text(
        (quote_area_x, quote_y),
        quote,
        fill=quote_color,
        font=quote_font
    )

    # Right side: keep Regards + Team Aviv style unchanged, fixed inside 20% block.
    regards_line = "Regards,"
    signature_line = "Team Aviv"
    tracking = max(1, int(regards_font_size * 0.07))

    regards_w = text_width_with_tracking(draw, regards_line, regards_font, tracking)
    regards_bbox = draw.textbbox((0, 0), regards_line, font=regards_font)
    regards_h = regards_bbox[3] - regards_bbox[1]

    sig_bbox = draw.textbbox((0, 0), signature_line, font=signature_font)
    sig_w = sig_bbox[2] - sig_bbox[0]
    sig_h = sig_bbox[3] - sig_bbox[1]

    block_h = regards_h + signature_gap + sig_h
    block_y = usable_h_start + max(0, (usable_h - block_h) // 2)

    right_area_x = left_width
    right_area_right = width - padding_x
    right_center_x = right_area_x + max(0, (right_area_right - right_area_x) // 2)

    regards_x = right_center_x - (regards_w // 2)
    signature_x = right_center_x - (sig_w // 2)

    # Safety clamp so signature never crosses too far outside the fixed right area.
    regards_x = max(right_area_x, min(regards_x, right_area_right - regards_w))
    signature_x = max(right_area_x, min(signature_x, right_area_right - sig_w))

    draw_text_with_tracking(
        draw,
        (regards_x, block_y),
        regards_line,
        regards_font,
        soft_color,
        tracking=tracking
    )

    draw.text(
        (signature_x, block_y + regards_h + signature_gap),
        signature_line,
        fill=signature_color,
        font=signature_font
    )

    return final_with_footer


# ---------------- CORE FUNCTIONS ----------------

def save_to_excel(name, email, file_name):
    path = Path("mosaic_leads.xlsx")

    new_data = pd.DataFrame([{
        "Name": name.strip(),
        "Email": email.strip(),
        "File": file_name,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    try:
        if path.exists():
            old_data = pd.read_excel(path)
            final_data = pd.concat([old_data, new_data], ignore_index=True)
        else:
            final_data = new_data

        final_data.to_excel(path, index=False)
        return True, None

    except PermissionError:
        backup_path = Path(f"mosaic_leads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        new_data.to_excel(backup_path, index=False)
        return False, f"Main Excel file is open/locked. Data saved to backup file: {backup_path}"

    except Exception as e:
        backup_path = Path(f"mosaic_leads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        new_data.to_excel(backup_path, index=False)
        return False, f"Lead data could not be saved to the main Excel file. Backup saved as: {backup_path}. Reason: {e}"


@st.cache_data(show_spinner=False)
def process_tile_library(file_items, tile_size):
    processed_tiles = {}

    for item in file_items:
        try:
            item.seek(0)
            sample_bytes = item.read(8192)
            file_hash_prefix = hashlib.md5(sample_bytes).hexdigest()

            file_id = f"{item.name}_{item.size}_{file_hash_prefix}"

            if file_id in processed_tiles:
                continue

            item.seek(0)
            img = Image.open(item).convert("RGB")

            # IMPORTANT QUALITY FIX:
            # Keep the full-resolution uploaded image for portrait suggestions.
            # The square `tile` below is only for mosaic tile matching and preview.
            original_img = img.copy()

            tile = ImageOps.fit(
                img,
                (tile_size, tile_size),
                Image.Resampling.LANCZOS
            )

            avg_color = np.array(tile).mean(axis=(0, 1))
            stddev = ImageStat.Stat(tile.convert("L")).stddev[0]

            processed_tiles[file_id] = {
                "img": tile,                 # resized square tile for mosaic cells
                "original": original_img,    # full-quality photo for suggested main portrait
                "color": avg_color,
                "stddev": stddev
            }

        except Exception:
            continue

    return list(processed_tiles.values())


@st.cache_resource(show_spinner=False)
def build_kdtree(color_array):
    return KDTree(color_array)


def apply_luminosity_blend(mosaic_img, target_img):
    mosaic_rgb = mosaic_img.convert("RGB")
    target_rgb = target_img.convert("RGB")

    multiplied = ImageChops.multiply(mosaic_rgb, target_rgb)

    return Image.blend(mosaic_rgb, multiplied, alpha=0.6)


# ---------------- HEADER ----------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">✨ Immersive Mosaic Experience</div>
            <h1>Mosaic Studio Pro</h1>
            <p>
                Transform hundreds of personal photos into a premium, print-ready mosaic artwork
                with elegant quote footer branding and high-resolution export.
            </p>
            <div class="hero-pills">
                <div class="pill">🖼️ High-resolution output</div>
                <div class="pill">🎨 Luxury quote footer</div>
                <div class="pill">⚡ Guided 3-step flow</div>
                <div class="pill">⬇️ Download-ready artwork</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🎛️ Artwork Controls")
    st.caption("Tune the look, detail level, blending style, and final export format.")

    tile_res = st.select_slider(
        "Tile Resolution (px)",
        options=[16, 32, 64, 128],
        value=64,
        help="Size of each tiny photo tile."
    )

    density = st.slider(
        "Grid Density Across",
        min_value=40,
        max_value=300,
        value=150,
        help="Higher value gives more detail but creates a larger file."
    )

    st.divider()

    st.markdown("### ✨ Sharpening & Blending")

    target_sharpness = st.slider(
        "Pre-Sharpen Main Photo",
        min_value=0,
        max_value=300,
        value=150,
        help="Improves facial edges before mosaic generation."
    )

    random_k = st.slider(
        "Texture Variety",
        min_value=1,
        max_value=10,
        value=2,
        help="Lower value gives better color accuracy. Higher value gives more variety."
    )

    blend_mode = st.radio(
        "Blending Method",
        ["Luminosity Multiply (Sharp)", "Alpha Overlay"]
    )

    alpha_mix = st.slider(
        "Overlay Strength",
        min_value=0.0,
        max_value=1.0,
        value=0.15,
        help="Adds original image visibility over the mosaic."
    )

    export_fmt = st.selectbox(
        "Export Format",
        ["JPEG", "PNG", "TIFF"]
    )


# ---------------- LOAD TILE LIBRARY ----------------

st.markdown(
    """
    <div class="flow-card">
        <div class="step-row">
            <div class="step-badge">1</div>
            <div>
                <div class="step-title">Upload your memory tiles</div>
                <div class="muted-text">
                    Add the photos that will become the tiny building blocks of your final mosaic.
                    For best results, upload 20–80 clear images.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

files_to_process = []
file_hash = None

uploaded = st.file_uploader(
    "Upload tile photos (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded and len(uploaded) > MAX_IMAGES:
    st.error(f"Maximum {MAX_IMAGES} tile images allowed for stable website performance.")
    st.stop()

if uploaded:
    files_to_process = uploaded

    file_hash = hashlib.md5(
        "".join([
            f"{f.name}{f.size}{f.type}"
            for f in uploaded
        ]).encode()
    ).hexdigest()

    st.success(f"✅ {len(files_to_process)} images uploaded successfully!")

else:
    st.info("👆 Upload at least 20–50 images for best mosaic quality.")


# ---------------- RESET SESSION ----------------

if "current_hash" not in st.session_state or st.session_state.current_hash != file_hash:
    st.session_state.current_hash = file_hash

    for key in [
        "top_picks",
        "active_target",
        "tiles",
        "built_res",
        "final_image_bytes",
        "final_file_name",
        "final_mime",
        "preview_image",
        "crop_img"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.show_popup = False
    st.session_state.download_ready = False
    st.session_state.processing = False


# ---------------- PROCESS TILE LIBRARY ----------------

if files_to_process:
    if "tiles" not in st.session_state or st.session_state.get("built_res") != tile_res:
        with st.spinner("Analyzing your photo library..."):
            st.session_state.tiles = process_tile_library(files_to_process, tile_res)
            st.session_state.built_res = tile_res

    tiles = st.session_state.tiles

    if not tiles:
        st.error("No valid images found.")

    else:
        st.success(f"✅ Processed {len(tiles)} usable tile images.")

        if "top_picks" not in st.session_state:
            scored = sorted(
                tiles,
                key=lambda x: x["stddev"],
                reverse=True
            )
            st.session_state.top_picks = scored[:3]

        selection_container = st.expander(
            "Step 2 · Choose Your Main Portrait",
            expanded=("active_target" not in st.session_state)
        )

        with selection_container:
            cols = st.columns(3)

            for i, pick in enumerate(st.session_state.top_picks):
                with cols[i]:
                    # Show the original image in suggestions so the preview does not look compressed.
                    st.image(pick.get("original", pick["img"]), use_container_width=True)

                    if st.button(f"Use Photo #{i + 1}", key=f"pick_{i}"):
                        st.session_state.active_target = pick["img"]
                        st.session_state.show_popup = False
                        st.session_state.download_ready = False
                        st.rerun()

            st.divider()

            custom_target_file = st.file_uploader(
                "🎯 Or upload a specific main photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="custom_target"
            )

            if custom_target_file:
                custom_img = Image.open(custom_target_file).convert("RGB")

                col_preview, col_btn = st.columns([1, 4])

                with col_preview:
                    st.image(custom_img, use_container_width=True)

                with col_btn:
                    if st.button("✅ Set as Main Portrait", type="primary"):
                        st.session_state.active_target = custom_img
                        st.session_state.show_popup = False
                        st.session_state.download_ready = False
                        st.rerun()


# ---------------- GENERATOR ----------------

if "active_target" in st.session_state and "tiles" in st.session_state:
    st.divider()

    st.markdown(
        """
        <div class="flow-card">
            <div class="step-row">
                <div class="step-badge">3</div>
                <div>
                    <div class="step-title">Generate your final artwork</div>
                    <div class="muted-text">
                        Review the selected portrait, confirm export size, and create your high-density mosaic master file.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_tgt, col_info = st.columns([1, 5])

    preview_target = st.session_state.active_target.copy()

    if target_sharpness > 0:
        preview_target = preview_target.filter(
            ImageFilter.UnsharpMask(
                radius=2,
                percent=target_sharpness,
                threshold=3
            )
        )

    with col_tgt:
        st.caption("Active Portrait Preview")
        st.image(preview_target, use_container_width=True)

    with col_info:
        st.success("Ready to generate mosaic.")

        target = st.session_state.active_target.convert("RGB")
        w, h = target.size

        grid_h_preview = max(1, int(density * (h / w)))
        full_w_preview = density * tile_res
        full_h_preview = grid_h_preview * tile_res

        estimated_mp = (full_w_preview * full_h_preview) / 1_000_000

        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>{full_w_preview}</h3>
                    <p>Width px</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>{full_h_preview}</h3>
                    <p>Height px</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>{estimated_mp:.1f}</h3>
                    <p>Megapixels</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        if estimated_mp > 80:
            st.warning(
                "⚠️ Very high quality selected. This may be slow or fail on free hosting."
            )

        if st.session_state.processing:
            st.warning("⚠️ Processing is already running. Please wait.")
            generate = False
        else:
            generate = st.button(
                "✨ Create My Mosaic Artwork",
                type="primary",
                use_container_width=True
            )

    if generate and not st.session_state.processing:
        st.session_state.processing = True
        st.session_state.show_popup = False
        st.session_state.download_ready = False

        try:
            tiles = st.session_state.tiles

            tile_colors = np.array([t["color"] for t in tiles])
            tree = build_kdtree(tile_colors)

            target = st.session_state.active_target.convert("RGB")

            w, h = target.size

            grid_h = max(1, int(density * (h / w)))

            full_w = density * tile_res
            full_h = grid_h * tile_res

            target_res = target.resize(
                (full_w, full_h),
                Image.Resampling.LANCZOS
            )

            if target_sharpness > 0:
                target_res = target_res.filter(
                    ImageFilter.UnsharpMask(
                        radius=2,
                        percent=target_sharpness,
                        threshold=3
                    )
                )

            target_rgb = np.array(target_res)

            target_blocks = target_rgb.reshape(
                grid_h,
                tile_res,
                density,
                tile_res,
                3
            ).mean(axis=(1, 3))

            placed_indices = np.zeros((grid_h, density), dtype=int)

            temp_dir = tempfile.gettempdir()
            memmap_path = os.path.join(
                temp_dir,
                f"mosaic_engine_cache_{uuid.uuid4().hex}.dat"
            )

            canvas_mem = np.memmap(
                memmap_path,
                dtype="uint8",
                mode="w+",
                shape=(full_h, full_w, 3)
            )

            status_text = st.empty()
            progress_bar = st.empty()

            status_text.info(
                f"Rendering {full_w} × {full_h} mosaic directly to temporary storage..."
            )

            pb = progress_bar.progress(0)

            for y in range(grid_h):
                for x in range(density):
                    reg_color = target_blocks[y, x]

                    _, idxs = tree.query(
                        reg_color,
                        k=min(random_k + 4, len(tiles))
                    )

                    idxs = np.atleast_1d(idxs)

                    target_box = (
                        x * tile_res,
                        y * tile_res,
                        (x + 1) * tile_res,
                        (y + 1) * tile_res
                    )

                    target_crop = target_res.crop(target_box)

                    neighbors = set()

                    for dy, dx in [(0, -1), (-1, -1), (-1, 0), (-1, 1)]:
                        ny = y + dy
                        nx = x + dx

                        if 0 <= ny < grid_h and 0 <= nx < density:
                            neighbors.add(placed_indices[ny, nx])

                    candidates = [i for i in idxs if i not in neighbors]

                    if not candidates:
                        candidates = [idxs[0]]

                    best_idx = int(random.choice(candidates[:random_k]))
                    placed_indices[y, x] = best_idx

                    raw_tile = tiles[best_idx]["img"]

                    if raw_tile.size != target_crop.size:
                        raw_tile = raw_tile.resize(
                            target_crop.size,
                            Image.Resampling.LANCZOS
                        )

                    if blend_mode == "Luminosity Multiply (Sharp)":
                        blended = apply_luminosity_blend(raw_tile, target_crop)

                        if alpha_mix > 0:
                            final_tile = Image.blend(
                                blended,
                                target_crop,
                                alpha=alpha_mix
                            )
                        else:
                            final_tile = blended

                    else:
                        final_tile = Image.blend(
                            raw_tile,
                            target_crop,
                            alpha=alpha_mix
                        )

                    canvas_mem[
                        y * tile_res:(y + 1) * tile_res,
                        x * tile_res:(x + 1) * tile_res
                    ] = np.array(final_tile)

                canvas_mem.flush()

                if y % max(1, grid_h // 20) == 0 or y == grid_h - 1:
                    pb.progress((y + 1) / grid_h)

            status_text.empty()
            progress_bar.empty()

            final_output = Image.fromarray(np.array(canvas_mem).copy())

            # Add random quote footer below the completed mosaic.
            final_output = add_mosaic_footer(final_output, reference_image=target)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = export_fmt.lower()

            if export_fmt == "JPEG":
                final_output = final_output.convert("RGB")
                ext = "jpg"

            buf = BytesIO()

            save_kwargs = {
                "format": export_fmt
            }

            if export_fmt == "JPEG":
                save_kwargs["quality"] = 95
                save_kwargs["optimize"] = True

            final_output.save(buf, **save_kwargs)

            st.session_state.final_image_bytes = buf.getvalue()
            st.session_state.final_file_name = f"mosaic_{ts}.{ext}"
            st.session_state.final_mime = f"image/{ext}"

            preview_image = final_output.copy()
            preview_image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            st.session_state.preview_image = preview_image

            cx = final_output.width // 2
            cy = final_output.height // 2

            sz = min(
                400,
                final_output.width // 2,
                final_output.height // 2
            )

            st.session_state.crop_img = final_output.crop(
                (cx - sz, cy - sz, cx + sz, cy + sz)
            )

            del final_output
            del canvas_mem

            try:
                os.remove(memmap_path)
            except Exception:
                pass

            st.session_state.processing = False
            st.rerun()

        except Exception as e:
            st.session_state.processing = False
            st.error(f"Something went wrong while generating the mosaic: {e}")


# ---------------- FINAL OUTPUT + DOWNLOAD ----------------

if "final_image_bytes" in st.session_state:
    st.markdown(
        """
        <div class="flow-card">
            <div class="step-row">
                <div class="step-badge">✓</div>
                <div>
                    <div class="step-title">Your mosaic is ready</div>
                    <div class="muted-text">
                        Preview the completed artwork, inspect a 1:1 crop, then unlock the high-resolution download.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        st.session_state.preview_image,
        caption="Web Preview - downscaled for browser",
        use_container_width=True
    )

    st.subheader("🔍 1:1 Detail Preview")

    st.image(
        st.session_state.crop_img,
        caption="Central Detail from Master File"
    )

    st.markdown(
        """
        <div class="download-panel">
            <h2>Download your finished artwork</h2>
            <p>Your high-resolution mosaic is ready. Enter your name and email to unlock the master file.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Unlock Download", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.download_ready = False

    if st.session_state.show_popup:
        st.markdown(
            """
            <div class="form-card">
                <h3>Almost done</h3>
                <p>Name and email are required before download.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        name = st.text_input("Name *", key="download_name")
        email = st.text_input("Email *", key="download_email")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_popup = False
                st.session_state.download_ready = False
                st.rerun()

        with col2:
            if st.button("Continue", use_container_width=True):
                if not name.strip():
                    st.error("Name is required to continue.")
                elif not email.strip():
                    st.error("Email is required to continue.")
                else:
                    saved, message = save_to_excel(
                        name=name,
                        email=email,
                        file_name=st.session_state.final_file_name
                    )

                    if not saved:
                        st.warning(message)
                    else:
                        st.success("✅ Details saved successfully!")

                    st.session_state.show_popup = False
                    st.session_state.download_ready = True
                    st.rerun()

    if st.session_state.download_ready:
        st.success("✅ Download unlocked!")

        st.download_button(
            label="⬇️ Download High-Resolution Artwork",
            data=st.session_state.final_image_bytes,
            file_name=st.session_state.final_file_name,
            mime=st.session_state.final_mime,
            use_container_width=True
        )
