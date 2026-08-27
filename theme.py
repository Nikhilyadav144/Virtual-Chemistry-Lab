"""
utils/theme.py
──────────────────────────────────────────────────────────────────
Central design token file.  Import this everywhere to keep the
entire application visually consistent.
"""

# ──────────────────────────────────────────────
#  COLOUR PALETTE  (dark-lab / sci-fi educational)
# ──────────────────────────────────────────────
BG_PRIMARY     = "#0A0E1A"   # near-black navy
BG_SECONDARY   = "#111827"   # dark card bg
BG_CARD        = "#1A2235"   # elevated card
BG_HOVER       = "#1E2D47"   # card hover
BORDER_COLOR   = "#1E3A5F"   # subtle borders
BORDER_ACCENT  = "#00B4D8"   # focused border

TEXT_PRIMARY   = "#F0F4FF"   # near-white
TEXT_SECONDARY = "#8A9BBF"   # muted
TEXT_MUTED     = "#4A5568"   # very muted

ACCENT_CYAN    = "#00D4FF"   # primary accent
ACCENT_TEAL    = "#00F5C4"   # secondary / success
ACCENT_ORANGE  = "#FF7043"   # warning / fire
ACCENT_PINK    = "#F472B6"   # class 12 tint
ACCENT_YELLOW  = "#FFD60A"   # class 10 tint
ACCENT_PURPLE  = "#A78BFA"   # class 11 tint
ACCENT_GREEN   = "#4ADE80"   # class 9 tint
ACCENT_BLUE    = "#60A5FA"   # class 8 tint

# Per-class accent colours
CLASS_COLORS = {
    8:  ACCENT_BLUE,
    9:  ACCENT_GREEN,
    10: ACCENT_YELLOW,
    11: ACCENT_PURPLE,
    12: ACCENT_PINK,
}

# ──────────────────────────────────────────────
#  TYPOGRAPHY
# ──────────────────────────────────────────────
FONT_FAMILY_HEADING = "Georgia"           # serif — feels academic
FONT_FAMILY_BODY    = "Segoe UI"          # clean system UI font
FONT_FAMILY_CODE    = "Consolas"          # monospace hints

FONT_SIZE_HERO   = 42
FONT_SIZE_H1     = 28
FONT_SIZE_H2     = 22
FONT_SIZE_H3     = 17
FONT_SIZE_BODY   = 14
FONT_SIZE_SMALL  = 12
FONT_SIZE_TINY   = 10

# ──────────────────────────────────────────────
#  SPACING
# ──────────────────────────────────────────────
PAD_XS  =  4
PAD_SM  =  8
PAD_MD  = 16
PAD_LG  = 24
PAD_XL  = 40
PAD_XXL = 64

# ──────────────────────────────────────────────
#  COMPONENT GEOMETRY
# ──────────────────────────────────────────────
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 16
RADIUS_XL = 24

BTN_HEIGHT_SM = 34
BTN_HEIGHT_MD = 44
BTN_HEIGHT_LG = 54

# ──────────────────────────────────────────────
#  QSS SNIPPETS  (reusable PyQt5 style strings)
# ──────────────────────────────────────────────
SCROLLBAR_STYLE = f"""
QScrollBar:vertical {{
    background: {BG_SECONDARY};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_COLOR};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_CYAN};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

TOOLTIP_STYLE = f"""
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_ACCENT};
    border-radius: {RADIUS_SM}px;
    padding: 6px 10px;
    font-family: "{FONT_FAMILY_BODY}";
    font-size: {FONT_SIZE_SMALL}pt;
}}
"""
