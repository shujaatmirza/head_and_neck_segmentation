#!/usr/bin/env python3
"""
Convert the HTML presentation to PowerPoint (PPTX) format.

Recreates all 13 slides from presentation.html with matching:
- Color scheme (notebook tabs theme)
- Layout structure (titles, cards, tables, bar charts)
- Content and data
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Theme Colors ──────────────────────────────────────────────────────────────
BG_OUTER = RGBColor(0x2D, 0x2D, 0x2D)
BG_PAGE = RGBColor(0xF8, 0xF6, 0xF1)
BG_PAGE_ALT = RGBColor(0xF3, 0xF0, 0xE8)
TEXT_PRIMARY = RGBColor(0x1A, 0x1A, 0x1A)
TEXT_SECONDARY = RGBColor(0x55, 0x55, 0x55)
TEXT_MUTED = RGBColor(0x99, 0x99, 0x99)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Tab / accent colors
TAB_INTRO = RGBColor(0x98, 0xD4, 0xBB)
TAB_DATA = RGBColor(0xC7, 0xB8, 0xEA)
TAB_MODEL = RGBColor(0xF4, 0xB8, 0xC5)
TAB_RESULTS = RGBColor(0xA8, 0xD8, 0xEA)
TAB_END = RGBColor(0xFF, 0xE6, 0xA7)

ACCENT_GREEN = RGBColor(0x2A, 0x6B, 0x5A)
ACCENT_LAV = RGBColor(0x6B, 0x5C, 0xA5)
ACCENT_PINK = RGBColor(0xB8, 0x5C, 0x6E)
ACCENT_SKY = RGBColor(0x3A, 0x7C, 0xA5)
ACCENT_AMBER = RGBColor(0xB8, 0x86, 0x0B)
ACCENT_RED = RGBColor(0xC0, 0x39, 0x2B)

# Tag background colors (lighter versions)
TAG_INTRO_BG = RGBColor(0xE0, 0xF3, 0xEB)
TAG_DATA_BG = RGBColor(0xEC, 0xE6, 0xF7)
TAG_MODEL_BG = RGBColor(0xFB, 0xE8, 0xED)
TAG_RESULTS_BG = RGBColor(0xE2, 0xF1, 0xF7)
TAG_END_BG = RGBColor(0xFD, 0xF5, 0xDC)

TAG_INTRO_FG = RGBColor(0x1A, 0x5C, 0x47)
TAG_DATA_FG = RGBColor(0x4A, 0x3D, 0x7A)
TAG_MODEL_FG = RGBColor(0x7A, 0x3D, 0x4D)
TAG_RESULTS_FG = RGBColor(0x2D, 0x6A, 0x8A)
TAG_END_FG = RGBColor(0x7A, 0x65, 0x20)

# Bar fill colors
BAR_GREEN = RGBColor(0x2A, 0x6B, 0x5A)
BAR_SKY = RGBColor(0x3A, 0x7C, 0xA5)
BAR_LAV = RGBColor(0x6B, 0x5C, 0xA5)
BAR_AMBER = RGBColor(0xB8, 0x86, 0x0B)
BAR_RED = RGBColor(0xC0, 0x39, 0x2B)

# Slide dimensions (16:9)
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def set_slide_bg(slide, color):
    """Set a solid background color on a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color=None, line_color=None, line_width=None):
    """Add a rectangle shape."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.fill.solid()
        shape.line.color.rgb = line_color
        shape.line.width = line_width or Pt(1)
    return shape


def add_rounded_rect(slide, left, top, width, height, fill_color=None):
    """Add a rounded rectangle shape."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=14,
                 font_color=TEXT_PRIMARY, bold=False, italic=False,
                 alignment=PP_ALIGN.LEFT, font_name='Calibri'):
    """Add a text box with a single run of text."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.color.rgb = font_color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font_name
    return txBox


def add_tag(slide, left, top, text, fg_color, bg_color):
    """Add a colored tag/pill label."""
    tag_w = Inches(max(2.5, len(text) * 0.13))
    tag_h = Inches(0.32)
    shape = add_rounded_rect(slide, left, top, tag_w, tag_h, bg_color)
    shape.text_frame.word_wrap = False
    p = shape.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text.upper()
    run.font.size = Pt(8)
    run.font.color.rgb = fg_color
    run.font.bold = True
    run.font.name = 'Calibri'
    shape.text_frame.paragraphs[0].space_before = Pt(0)
    shape.text_frame.paragraphs[0].space_after = Pt(0)
    return shape


def add_section_tabs(slide, active_section):
    """Add the colored notebook tabs on the right edge of the paper."""
    sections = [
        ("Intro", TAB_INTRO),
        ("Data", TAB_DATA),
        ("Model", TAB_MODEL),
        ("Results", TAB_RESULTS),
        ("End", TAB_END),
    ]
    tab_x = Inches(11.5)
    tab_start_y = Inches(2.2)
    tab_w_active = Inches(0.45)
    tab_w_inactive = Inches(0.32)
    tab_heights = [Inches(0.7), Inches(0.6), Inches(0.75), Inches(0.8), Inches(0.65)]

    y = tab_start_y
    for i, (name, color) in enumerate(sections):
        is_active = name.lower() == active_section.lower()
        w = tab_w_active if is_active else tab_w_inactive
        h = tab_heights[i]
        shape = add_rounded_rect(slide, tab_x, y, w, h, color)
        # Make inactive tabs semi-transparent by blending with bg
        if not is_active:
            r, g, b = color[0], color[1], color[2]
            blended = RGBColor(
                min(255, r + (0x2D - r) // 2),
                min(255, g + (0x2D - g) // 2),
                min(255, b + (0x2D - b) // 2),
            )
            shape.fill.fore_color.rgb = blended
        y += h + Inches(0.04)


def add_slide_number(slide, num, total=13):
    """Add the slide number in bottom-right."""
    add_text_box(slide, Inches(10), Inches(6.8), Inches(1.3), Inches(0.35),
                 f"{num:02d} / {total}", font_size=9, font_color=TEXT_MUTED,
                 alignment=PP_ALIGN.RIGHT, font_name='Consolas')


def add_accent_line(slide, left, top, width=Inches(0.7), color=ACCENT_GREEN):
    """Add a short horizontal accent line/rule."""
    shape = add_shape(slide, left, top, width, Pt(2.5), fill_color=color)
    return shape


def add_card(slide, left, top, width, height, label="", label_color=ACCENT_GREEN,
             value="", value_size=28, detail=""):
    """Add a card with label, big value, and detail text."""
    card = add_rounded_rect(slide, left, top, width, height, BG_PAGE_ALT)
    card.line.fill.solid()
    card.line.color.rgb = RGBColor(0xE8, 0xE5, 0xDE)
    card.line.width = Pt(0.75)

    y_offset = top + Inches(0.15)
    if label:
        add_text_box(slide, left + Inches(0.15), y_offset, width - Inches(0.3), Inches(0.22),
                     label.upper(), font_size=7, font_color=label_color, bold=True)
        y_offset += Inches(0.22)
    if value:
        add_text_box(slide, left + Inches(0.15), y_offset, width - Inches(0.3), Inches(0.4),
                     value, font_size=value_size, font_color=TEXT_PRIMARY, bold=True,
                     font_name='Georgia')
        y_offset += Inches(0.38)
    if detail:
        add_text_box(slide, left + Inches(0.15), y_offset, width - Inches(0.3), Inches(0.6),
                     detail, font_size=9, font_color=TEXT_MUTED)
    return card


def add_bar_chart_row(slide, left, top, label, value_text, pct, bar_color, label_width=Inches(1.4)):
    """Add a single horizontal bar row: label | bar track | value."""
    row_h = Inches(0.3)
    track_w = Inches(5.5)

    # Label
    add_text_box(slide, left, top, label_width, row_h,
                 label, font_size=10, font_color=TEXT_SECONDARY,
                 alignment=PP_ALIGN.RIGHT)

    # Track background
    track_left = left + label_width + Inches(0.15)
    add_rounded_rect(slide, track_left, top + Inches(0.02), track_w, row_h - Inches(0.04),
                     RGBColor(0xEE, 0xEC, 0xE7))

    # Filled bar
    fill_w = int(track_w * pct)
    if fill_w > 0:
        bar = add_rounded_rect(slide, track_left, top + Inches(0.02),
                               fill_w, row_h - Inches(0.04), bar_color)

    # Value text
    add_text_box(slide, track_left + fill_w + Inches(0.1), top, Inches(0.6), row_h,
                 value_text, font_size=9, font_color=TEXT_SECONDARY, bold=True,
                 font_name='Consolas')


def add_insight_box(slide, left, top, width, text, bold_prefix=""):
    """Add an insight/callout box with amber left border."""
    # Background
    box = add_shape(slide, left, top, width, Inches(0.55),
                    fill_color=RGBColor(0xFB, 0xF5, 0xE6))
    # Left border accent
    add_shape(slide, left, top, Pt(3), Inches(0.55), fill_color=ACCENT_AMBER)

    txBox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.08),
                                     width - Inches(0.3), Inches(0.42))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    if bold_prefix:
        r1 = p.add_run()
        r1.text = bold_prefix + " "
        r1.font.size = Pt(9)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_PRIMARY
        r1.font.name = 'Calibri'
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(9)
    r2.font.color.rgb = TEXT_PRIMARY
    r2.font.name = 'Calibri'


def add_table(slide, left, top, data, col_widths, header_color=ACCENT_GREEN):
    """Add a table with styled header row."""
    rows = len(data)
    cols = len(data[0])
    table_shape = slide.shapes.add_table(rows, cols, left, top,
                                         sum(col_widths), Inches(0.32 * rows))
    table = table_shape.table

    for j, w in enumerate(col_widths):
        table.columns[j].width = w

    for i, row_data in enumerate(data):
        for j, cell_text in enumerate(row_data):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(cell_text)

            if i == 0:  # Header
                run.font.size = Pt(8)
                run.font.bold = True
                run.font.color.rgb = header_color
                run.font.name = 'Calibri'
                cell.fill.solid()
                cell.fill.fore_color.rgb = BG_PAGE
            else:
                run.font.size = Pt(10)
                run.font.color.rgb = TEXT_SECONDARY
                run.font.name = 'Calibri'
                cell.fill.solid()
                cell.fill.fore_color.rgb = BG_PAGE

    return table_shape


def add_feature_list(slide, left, top, items, item_height=Inches(0.28)):
    """Add a bulleted feature list."""
    for i, item in enumerate(items):
        y = top + i * item_height
        # Bullet
        add_text_box(slide, left, y, Inches(0.2), item_height,
                     "\u25B8", font_size=10, font_color=ACCENT_GREEN, bold=True)
        # Text
        add_text_box(slide, left + Inches(0.25), y, Inches(4), item_height,
                     item, font_size=11, font_color=TEXT_SECONDARY)


def create_base_slide(prs, section, slide_num):
    """Create a slide with standard background, paper shape, tabs, and number."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    set_slide_bg(slide, BG_OUTER)

    # Paper card
    paper_left = Inches(0.8)
    paper_top = Inches(0.4)
    paper_w = Inches(10.5)
    paper_h = Inches(6.5)
    paper = add_rounded_rect(slide, paper_left, paper_top, paper_w, paper_h, BG_PAGE)

    # Section tabs
    add_section_tabs(slide, section)

    # Slide number
    add_slide_number(slide, slide_num)

    return slide


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def slide_00_title(prs):
    """Slide 0: Title slide."""
    slide = create_base_slide(prs, "intro", 1)
    x, y = Inches(1.5), Inches(1.2)

    add_tag(slide, x, y, "Deep Learning Systems \u2014 NYU Courant", TAG_INTRO_FG, TAG_INTRO_BG)

    add_text_box(slide, x, y + Inches(0.6), Inches(8), Inches(1.2),
                 "Multi-Organ Segmentation\nfor Head & Neck Cancer",
                 font_size=36, font_color=TEXT_PRIMARY, bold=True, font_name='Georgia')

    add_accent_line(slide, x, y + Inches(1.9))

    add_text_box(slide, x, y + Inches(2.2), Inches(7), Inches(0.8),
                 "A systematic study of training strategies for 3D medical image "
                 "segmentation on CT scans with 9 anatomical structures.",
                 font_size=13, font_color=TEXT_SECONDARY)

    add_text_box(slide, x, y + Inches(3.3), Inches(6), Inches(0.3),
                 "PDDCA15  \u00B7  MONAI  \u00B7  PyTorch",
                 font_size=9, font_color=TEXT_MUTED)


def slide_01_problem(prs):
    """Slide 1: The Problem."""
    slide = create_base_slide(prs, "intro", 2)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Motivation", TAG_INTRO_FG, TAG_INTRO_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "The Problem", font_size=28, bold=True, font_name='Georgia')

    add_text_box(slide, x, y + Inches(1.1), Inches(8), Inches(0.5),
                 "Radiation therapy for head & neck cancer requires precise delineation "
                 "of organs-at-risk. Manual segmentation is slow, costly, and inconsistent.",
                 font_size=12, font_color=TEXT_SECONDARY)

    # Three challenge cards
    cards = [
        ("Challenge 1", ACCENT_GREEN, "Class Imbalance",
         "OARs occupy <5% of volume. Naive models predict only background."),
        ("Challenge 2", ACCENT_LAV, "Memory Limits",
         "A single 3D volume + UNet can exceed 30 GB, forcing batch = 1."),
        ("Challenge 3", ACCENT_AMBER, "Limited Data",
         "Only 33 training volumes \u2014 high risk of overfitting."),
    ]

    card_w = Inches(2.8)
    card_gap = Inches(0.25)
    for i, (label, color, value, detail) in enumerate(cards):
        cx = x + i * (card_w + card_gap)
        add_card(slide, cx, y + Inches(1.9), card_w, Inches(1.6),
                 label=label, label_color=color, value=value, value_size=16, detail=detail)


def slide_02_dataset(prs):
    """Slide 2: Dataset."""
    slide = create_base_slide(prs, "data", 3)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Dataset", TAG_DATA_FG, TAG_DATA_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(8), Inches(0.5),
                 "PDDCA15 \u2014 9 Organs at Risk", font_size=28, bold=True, font_name='Georgia')

    # Left column: organ list
    organs = ["Brain Stem", "Chiasm", "Mandible", "Optic Nerve (Left & Right)",
              "Parotid Gland (Left & Right)", "Submandibular (Left & Right)"]
    add_feature_list(slide, x, y + Inches(1.3), organs)

    # Right column: stat cards
    rx = Inches(6.2)
    add_card(slide, rx, y + Inches(1.2), Inches(3.8), Inches(0.85),
             label="Training", label_color=ACCENT_GREEN,
             value="33 CT volumes", value_size=20, detail="PDDCA15 + Cetuximab + PET-CT")
    add_card(slide, rx, y + Inches(2.2), Inches(3.8), Inches(0.7),
             label="Testing", label_color=ACCENT_LAV,
             value="5 CT volumes", value_size=20)
    add_card(slide, rx, y + Inches(3.1), Inches(3.8), Inches(0.7),
             label="Avg. Volume", label_color=ACCENT_AMBER,
             value="78 \u00D7 206 \u00D7 164", value_size=16)


def slide_03_architectures(prs):
    """Slide 3: Model Architectures."""
    slide = create_base_slide(prs, "model", 4)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Methods", TAG_MODEL_FG, TAG_MODEL_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(8), Inches(0.5),
                 "Model Architectures", font_size=28, bold=True, font_name='Georgia')

    add_text_box(slide, x, y + Inches(1.1), Inches(8), Inches(0.4),
                 "Three 3D architectures from MONAI, all with 10-channel output (background + 9 OARs).",
                 font_size=12, font_color=TEXT_SECONDARY)

    models = [
        ("Baseline", ACCENT_SKY, "UNet", "Features: (32, 64, 128, 256)\n3 downsampling levels", "0.682", ACCENT_SKY),
        ("Best", ACCENT_GREEN, "Deeper UNet", "Features: (32, 64, 128, 256, 512, 32)\n5 downsampling levels", "0.755", ACCENT_GREEN),
        ("Alternative", ACCENT_LAV, "SegResNet", "Residual blocks, deconv upsampling\n1.19M parameters", "0.660", ACCENT_LAV),
    ]

    card_w = Inches(2.8)
    for i, (label, lcolor, name, detail, dice, vcolor) in enumerate(models):
        cx = x + i * (card_w + Inches(0.25))
        cy = y + Inches(1.7)
        add_card(slide, cx, cy, card_w, Inches(1.8),
                 label=label, label_color=lcolor, value=name, value_size=16, detail=detail)
        # Dice score below detail
        add_text_box(slide, cx + Inches(0.15), cy + Inches(1.35), Inches(1), Inches(0.35),
                     dice, font_size=20, font_color=vcolor, bold=True, font_name='Georgia')

    # Insight
    add_insight_box(slide, x, y + Inches(3.8), Inches(8.5),
                    "Model depth is critical. Small structures (chiasm, optic nerves) get zero Dice with shallow networks.",
                    bold_prefix="Key finding:")


def slide_04_loss(prs):
    """Slide 4: Loss Function Comparison."""
    slide = create_base_slide(prs, "results", 5)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Results", TAG_RESULTS_FG, TAG_RESULTS_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "Loss Function Comparison", font_size=28, bold=True, font_name='Georgia')

    bars = [
        ("Dice-CE Loss", "0.737", 0.92, BAR_GREEN),
        ("Dice Loss", "0.701", 0.876, BAR_SKY),
        ("Dice-Focal", "0.695", 0.869, BAR_SKY),
        ("Masked Dice", "0.680", 0.85, BAR_LAV),
        ("Tversky", "0.634", 0.793, BAR_LAV),
        ("Focal", "0.632", 0.79, BAR_AMBER),
        ("Gen. Dice", "0.250", 0.313, BAR_RED),
    ]

    bar_y = y + Inches(1.2)
    for i, (label, val, pct, color) in enumerate(bars):
        add_bar_chart_row(slide, x, bar_y + i * Inches(0.36), label, val, pct, color)

    add_insight_box(slide, x, y + Inches(4.0), Inches(8.5),
                    "CE provides gradients for large structures; Dice focuses on small organs.",
                    bold_prefix="+3.6% over Dice alone.")


def slide_05_augmentation(prs):
    """Slide 5: Data Augmentation."""
    slide = create_base_slide(prs, "results", 6)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Results", TAG_RESULTS_FG, TAG_RESULTS_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "Data Augmentation", font_size=28, bold=True, font_name='Georgia')

    # Left: Standard (epoch 1)
    add_text_box(slide, x, y + Inches(1.2), Inches(4), Inches(0.3),
                 "STANDARD (EPOCH 1)", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    std_bars = [
        ("Elastic", "0.710", 0.888, BAR_GREEN),
        ("Affine", "0.708", 0.885, BAR_SKY),
        ("Zoom", "0.701", 0.877, BAR_SKY),
        ("Sp. Crop", "0.685", 0.857, BAR_LAV),
        ("No Aug.", "0.684", 0.855, BAR_AMBER),
    ]
    for i, (label, val, pct, color) in enumerate(std_bars):
        add_bar_chart_row(slide, x, y + Inches(1.6) + i * Inches(0.34),
                          label, val, pct, color, label_width=Inches(1.0))

    # Right: Delayed (epoch 40)
    rx = Inches(5.8)
    add_text_box(slide, rx, y + Inches(1.2), Inches(4), Inches(0.3),
                 "DELAYED (EPOCH 40)", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    del_bars = [
        ("Elastic", "0.728", 0.911, BAR_GREEN),
        ("Affine", "0.705", 0.881, BAR_SKY),
        ("Zoom", "0.696", 0.87, BAR_SKY),
        ("No Aug.", "0.684", 0.855, BAR_AMBER),
        ("Sp. Crop", "0.669", 0.836, BAR_RED),
    ]
    for i, (label, val, pct, color) in enumerate(del_bars):
        add_bar_chart_row(slide, rx, y + Inches(1.6) + i * Inches(0.34),
                          label, val, pct, color, label_width=Inches(1.0))

    add_insight_box(slide, x, y + Inches(3.6), Inches(8.5),
                    "Learn basics first, augment later.",
                    bold_prefix="Delayed elastic deformation is best (+4.4% over baseline).")


def slide_06_batch_size(prs):
    """Slide 6: Effective Batch Size."""
    slide = create_base_slide(prs, "results", 7)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Results", TAG_RESULTS_FG, TAG_RESULTS_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "Effective Batch Size", font_size=28, bold=True, font_name='Georgia')

    add_text_box(slide, x, y + Inches(1.1), Inches(8), Inches(0.4),
                 "Gradient accumulation simulates larger batches despite memory constraints (physical batch = 1).",
                 font_size=12, font_color=TEXT_SECONDARY)

    # Left table: With LR Scaling
    add_text_box(slide, x, y + Inches(1.7), Inches(4), Inches(0.25),
                 "WITH LR SCALING", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    data_lr = [
        ["BSZ", "Dice", "Epoch"],
        ["2", "0.688", "130"],
        ["4", "0.661", "80"],
        ["16", "0.647", "100"],
        ["8", "0.645", "110"],
    ]
    add_table(slide, x, y + Inches(2.1), data_lr,
              [Inches(0.8), Inches(1.2), Inches(1.0)])

    # Right table: Without LR Scaling
    rx = Inches(5.8)
    add_text_box(slide, rx, y + Inches(1.7), Inches(4), Inches(0.25),
                 "WITHOUT LR SCALING", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    data_nolr = [
        ["BSZ", "Dice", "Epoch"],
        ["4", "0.692", "70"],
        ["8", "0.679", "340"],
        ["16", "0.678", "190"],
        ["2", "0.666", "140"],
    ]
    add_table(slide, rx, y + Inches(2.1), data_nolr,
              [Inches(0.8), Inches(1.2), Inches(1.0)])

    add_insight_box(slide, x, y + Inches(4.1), Inches(8.5),
                    "for 3D segmentation with variable-sized inputs. Moderate BSZ (2\u20134) works best.",
                    bold_prefix="Linear LR scaling does not hold")


def slide_07_parallelism(prs):
    """Slide 7: Data Parallelism & Input Resolution."""
    slide = create_base_slide(prs, "results", 8)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Results", TAG_RESULTS_FG, TAG_RESULTS_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(8), Inches(0.5),
                 "Data Parallelism & Input Resolution", font_size=28, bold=True, font_name='Georgia')

    # Left: Multi-GPU
    add_text_box(slide, x, y + Inches(1.3), Inches(4), Inches(0.25),
                 "MULTI-GPU TRAINING", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    # GPU comparison cards in a row
    gpus = [("4 GPUs", ACCENT_GREEN, "0.668"), ("2 GPUs", ACCENT_SKY, "0.651"), ("1 GPU", ACCENT_LAV, "0.647")]
    for i, (lbl, clr, val) in enumerate(gpus):
        cx = x + i * Inches(1.5)
        add_card(slide, cx, y + Inches(1.7), Inches(1.35), Inches(0.9),
                 label=lbl, label_color=clr, value=val, value_size=20)

    add_text_box(slide, x, y + Inches(2.8), Inches(4.2), Inches(0.3),
                 "More GPUs converge faster per wall-clock time", font_size=9, font_color=TEXT_MUTED)

    add_insight_box(slide, x, y + Inches(3.2), Inches(4.2),
                    "Requires resizing all volumes to the same dimensions for batching.", bold_prefix="")

    # Right: Input Resolution
    rx = Inches(5.8)
    add_text_box(slide, rx, y + Inches(1.3), Inches(4), Inches(0.25),
                 "INPUT RESOLUTION", font_size=9, font_color=TEXT_SECONDARY, bold=True)

    res_bars = [
        ("1.0x (base)", "0.684", 0.855, BAR_GREEN),
        ("1.2x", "0.647", 0.808, BAR_SKY),
        ("0.8x", "0.584", 0.729, BAR_AMBER),
        ("1.4x", "0.562", 0.703, BAR_RED),
    ]
    for i, (label, val, pct, color) in enumerate(res_bars):
        add_bar_chart_row(slide, rx, y + Inches(1.7) + i * Inches(0.36),
                          label, val, pct, color, label_width=Inches(1.2))

    add_insight_box(slide, rx, y + Inches(3.4), Inches(4.2),
                    "larger inputs exceed the receptive field.",
                    bold_prefix="Non-monotonic:")


def slide_08_pretraining(prs):
    """Slide 8: Self-Supervised Pretraining."""
    slide = create_base_slide(prs, "results", 9)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Results", TAG_RESULTS_FG, TAG_RESULTS_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(8), Inches(0.5),
                 "Self-Supervised Pretraining", font_size=28, bold=True, font_name='Georgia')

    add_text_box(slide, x, y + Inches(1.2), Inches(7), Inches(0.5),
                 "Initialized encoder with Models Genesis weights (pretrained on chest CT "
                 "via self-supervised proxy tasks).",
                 font_size=12, font_color=TEXT_SECONDARY)

    # Two comparison cards
    add_card(slide, x, y + Inches(2.0), Inches(3.5), Inches(1.1),
             label="With Pretraining", label_color=ACCENT_GREEN,
             value="0.675", value_size=28, detail="Best at epoch 60")

    add_card(slide, x + Inches(3.8), y + Inches(2.0), Inches(3.5), Inches(1.1),
             label="Without Pretraining", label_color=TEXT_MUTED,
             value="0.672", value_size=28, detail="Best at epoch 80")

    add_insight_box(slide, x, y + Inches(3.5), Inches(7.5),
                    "Pretraining accelerates early convergence but the gap closes "
                    "with longer training. Domain shift (chest \u2192 head/neck) limits transfer.",
                    bold_prefix="Modest benefit (+0.3%).")


def slide_09_summary(prs):
    """Slide 9: Best Configuration Summary."""
    slide = create_base_slide(prs, "end", 10)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Summary", TAG_END_FG, TAG_END_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(8), Inches(0.5),
                 "Best Configuration Per Category", font_size=28, bold=True, font_name='Georgia')

    data = [
        ["Experiment", "Best Config", "Mean Dice"],
        ["Model Architecture", "Deeper UNet", "0.755"],
        ["Loss Function", "Dice-CE", "0.737"],
        ["Delayed Augmentation", "Random Elastic", "0.728"],
        ["Standard Augmentation", "Random Elastic", "0.710"],
        ["Eff. BSZ (No LR Scale)", "Batch Size 4", "0.692"],
        ["Eff. BSZ (LR Scale)", "Batch Size 2", "0.688"],
        ["Input Resolution", "1.0x (base)", "0.684"],
        ["SSL Pretraining", "With Pretraining", "0.675"],
        ["Data Parallelism", "4 GPUs", "0.668"],
    ]
    add_table(slide, x, y + Inches(1.2), data,
              [Inches(3.0), Inches(2.5), Inches(1.5)])


def slide_10_insights(prs):
    """Slide 10: Key Insights."""
    slide = create_base_slide(prs, "end", 11)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Discussion", TAG_END_FG, TAG_END_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "Key Insights", font_size=28, bold=True, font_name='Georgia')

    insights = [
        ("1. Model Depth Matters Most", ACCENT_GREEN,
         "Deeper UNet: 0.755. Shallow networks produce zero Dice for small structures like chiasm and optic nerves."),
        ("2. Combine Loss Functions", ACCENT_SKY,
         "Dice-CE improves over Dice alone by +3.6%. CE covers large structures, Dice focuses on small organs."),
        ("3. Augment After Warm-up", ACCENT_AMBER,
         "Delayed elastic deformation: +4.4%. The model learns basic features before seeing augmented data."),
        ("4. Batch Size & LR Interact", ACCENT_LAV,
         "Linear LR scaling fails for variable-sized 3D volumes. Moderate batch sizes (2\u20134) without scaling work best."),
    ]

    card_w = Inches(4.1)
    for i, (title, color, desc) in enumerate(insights):
        row = i // 2
        col = i % 2
        cx = x + col * (card_w + Inches(0.25))
        cy = y + Inches(1.3) + row * Inches(1.5)

        card = add_rounded_rect(slide, cx, cy, card_w, Inches(1.3), BG_PAGE_ALT)
        card.line.fill.solid()
        card.line.color.rgb = RGBColor(0xE8, 0xE5, 0xDE)
        card.line.width = Pt(0.75)

        add_text_box(slide, cx + Inches(0.15), cy + Inches(0.12), card_w - Inches(0.3), Inches(0.25),
                     title.upper(), font_size=8, font_color=color, bold=True)
        add_text_box(slide, cx + Inches(0.15), cy + Inches(0.45), card_w - Inches(0.3), Inches(0.7),
                     desc, font_size=10, font_color=TEXT_SECONDARY)


def slide_11_limitations(prs):
    """Slide 11: Limitations & Future Work."""
    slide = create_base_slide(prs, "end", 12)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, x, y, "Limitations & Future Work", TAG_END_FG, TAG_END_BG)
    add_text_box(slide, x, y + Inches(0.5), Inches(6), Inches(0.5),
                 "What's Next?", font_size=28, bold=True, font_name='Georgia')

    # Left: Limitations
    add_text_box(slide, x, y + Inches(1.3), Inches(4), Inches(0.25),
                 "LIMITATIONS", font_size=9, font_color=TEXT_SECONDARY, bold=True)
    limitations = [
        "Fixed train/test split, no cross-validation",
        "Only Dice metric \u2014 no Hausdorff distance",
        "Small test set (5 patients)",
        "No ensemble methods explored",
    ]
    add_feature_list(slide, x, y + Inches(1.7), limitations)

    # Right: Future Directions
    rx = Inches(5.8)
    add_text_box(slide, rx, y + Inches(1.3), Inches(4), Inches(0.25),
                 "FUTURE DIRECTIONS", font_size=9, font_color=TEXT_SECONDARY, bold=True)
    future = [
        "K-fold cross-validation with confidence intervals",
        "Hausdorff distance & surface DSC metrics",
        "Attention mechanisms (Swin UNETR)",
        "nnU-Net self-configuring pipeline",
    ]
    add_feature_list(slide, rx, y + Inches(1.7), future)


def slide_12_conclusion(prs):
    """Slide 12: Conclusion."""
    slide = create_base_slide(prs, "end", 13)
    x, y = Inches(1.5), Inches(1.0)

    add_tag(slide, Inches(5.2), y + Inches(0.5), "Conclusion", TAG_END_FG, TAG_END_BG)

    # Center-aligned title
    add_text_box(slide, Inches(1.5), y + Inches(1.3), Inches(9), Inches(1.0),
                 "Deeper models + hybrid loss +\ndelayed augmentation = 0.755 Dice",
                 font_size=30, font_color=TEXT_PRIMARY, bold=True,
                 alignment=PP_ALIGN.CENTER, font_name='Georgia')

    add_accent_line(slide, Inches(5.5), y + Inches(2.5), Inches(0.8))

    add_text_box(slide, Inches(2), y + Inches(2.9), Inches(8), Inches(0.8),
                 "Across 30+ experiments in 8 categories, model depth, loss design, "
                 "and smart augmentation are the three most impactful training strategies "
                 "for 3D medical image segmentation.",
                 font_size=13, font_color=TEXT_SECONDARY, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, Inches(2), y + Inches(4.0), Inches(8), Inches(0.3),
                 "NYU Courant  \u00B7  Deep Learning Systems  \u00B7  PDDCA15  \u00B7  MONAI  \u00B7  PyTorch",
                 font_size=9, font_color=TEXT_MUTED, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_00_title(prs)
    slide_01_problem(prs)
    slide_02_dataset(prs)
    slide_03_architectures(prs)
    slide_04_loss(prs)
    slide_05_augmentation(prs)
    slide_06_batch_size(prs)
    slide_07_parallelism(prs)
    slide_08_pretraining(prs)
    slide_09_summary(prs)
    slide_10_insights(prs)
    slide_11_limitations(prs)
    slide_12_conclusion(prs)

    output_path = os.path.join(os.path.dirname(__file__), 'presentation.pptx')
    prs.save(output_path)
    print(f"PPTX saved to: {output_path}")
    print(f"Total slides: {len(prs.slides)}")


if __name__ == '__main__':
    main()
