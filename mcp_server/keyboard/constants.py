"""
Keyboard design constants and enums.

All dimensions are in centimeters (Fusion 360's internal unit).
User-facing APIs accept millimeters and convert at the boundary.
"""

from enum import Enum


# ---- Unit Conversion ----

def mm_to_cm(mm: float) -> float:
    return mm / 10.0


def cm_to_mm(cm: float) -> float:
    return cm * 10.0


# ---- Key Units ----

# 1U = 19.05mm = 1.905cm (standard key pitch)
KEY_UNIT_CM = 1.905
KEY_UNIT_MM = 19.05


# ---- Switch Cutout Sizes (cm) ----

class SwitchCutout(str, Enum):
    CHERRY_MX = "cherry_mx"
    ALPS = "alps"
    KAILH_CHOC = "kailh_choc"


SWITCH_CUTOUT_CM = {
    SwitchCutout.CHERRY_MX: {"width": 1.4, "height": 1.4},       # 14mm x 14mm
    SwitchCutout.ALPS: {"width": 1.55, "height": 1.28},           # 15.5mm x 12.8mm
    SwitchCutout.KAILH_CHOC: {"width": 1.35, "height": 1.35},    # 13.5mm x 13.5mm
}

# Clip notches for Cherry MX (optional, for plate-mount switches)
MX_CLIP_NOTCH_CM = {
    "width": 0.1,      # 1mm wide notch on each side
    "depth": 0.08,     # 0.8mm deep
    "offset_y": 0.0,   # centered vertically
}


# ---- Stabilizer Dimensions (cm) ----
# Keyed by key width in units. Values are center-to-center distance between stems.

STABILIZER_SPACING_CM = {
    2.0:   1.176,   # 11.76mm - 2U (backspace, etc.)
    2.25:  1.176,   # 11.76mm - 2.25U (left shift)
    2.75:  1.176,   # 11.76mm - 2.75U (right shift)
    6.25:  5.0,     # 50mm - 6.25U (standard spacebar)
    7.0:   5.715,   # 57.15mm - 7U (spacebar)
}

# Cherry-style stabilizer cutout (each side)
STABILIZER_CUTOUT_CM = {
    "width": 0.675,    # 6.75mm wide
    "height": 1.2,     # 12mm tall
}

# Stabilizer wire slot
STABILIZER_WIRE_SLOT_CM = {
    "width": 0.34,     # 3.4mm wide
    "height": 0.13,    # 1.3mm tall
}


# ---- USB Connector Openings (cm) ----

USB_OPENINGS_CM = {
    "usb_c": {"width": 0.92, "height": 0.34, "corner_radius": 0.08},
    "usb_mini": {"width": 0.78, "height": 0.36, "corner_radius": 0.04},
    "usb_micro": {"width": 0.78, "height": 0.26, "corner_radius": 0.02},
}

# ai03 Unified Daughterboard mounting holes (cm from connector center)
DAUGHTERBOARD_HOLES_CM = [
    {"x": -1.455, "y": -0.425, "diameter": 0.26},   # M2.5
    {"x":  1.455, "y": -0.425, "diameter": 0.26},
]


# ---- Mount Styles ----

class MountStyle(str, Enum):
    TRAY = "tray"             # Standoffs on case bottom, PCB screws down
    TOP = "top"               # Screw tabs on upper rim, plate hangs from top
    GASKET = "gasket"         # Gasket strips between plate and case walls
    SANDWICH = "sandwich"     # Plate sandwiched between top and bottom halves
    BOTTOM = "bottom"         # Similar to tray but plate sits on ledge


# ---- Layout Sizes ----

class LayoutSize(str, Enum):
    SIXTY = "60%"
    SIXTY_FIVE = "65%"
    SEVENTY_FIVE = "75%"
    TKL = "tkl"
    FULL = "full"


# ---- Default Case Dimensions (cm) ----

DEFAULT_WALL_THICKNESS_CM = 0.4       # 4mm walls
DEFAULT_BOTTOM_THICKNESS_CM = 0.3     # 3mm bottom
DEFAULT_CASE_HEIGHT_CM = 1.5          # 15mm internal height
DEFAULT_CORNER_RADIUS_CM = 0.3        # 3mm corner radius
DEFAULT_PLATE_THICKNESS_CM = 0.15     # 1.5mm plate thickness
DEFAULT_PLATE_MARGIN_CM = 0.05        # 0.5mm margin around plate edges

DEFAULT_BEZEL_CM = {
    "front": 0.4,   # 4mm
    "back": 0.6,    # 6mm (extra room for USB)
    "left": 0.5,    # 5mm
    "right": 0.5,   # 5mm
}


# ---- Screw / Standoff Dimensions (cm) ----

SCREW_SIZES_CM = {
    "M2":   {"hole_diameter": 0.2,  "standoff_outer": 0.4,  "insert_diameter": 0.32},
    "M2.5": {"hole_diameter": 0.25, "standoff_outer": 0.5,  "insert_diameter": 0.38},
    "M3":   {"hole_diameter": 0.3,  "standoff_outer": 0.6,  "insert_diameter": 0.44},
}

DEFAULT_STANDOFF_HEIGHT_CM = 0.5     # 5mm tall standoffs


# ---- Bumpon / Feet Dimensions (cm) ----

BUMPON_RECESS_CM = {
    "small":  {"diameter": 0.8, "depth": 0.1},    # 8mm dia, 1mm deep
    "medium": {"diameter": 1.2, "depth": 0.15},   # 12mm dia, 1.5mm deep
    "large":  {"diameter": 1.6, "depth": 0.2},     # 16mm dia, 2mm deep
}


# ---- Gasket Dimensions (cm) ----

GASKET_CHANNEL_CM = {
    "width": 0.25,     # 2.5mm wide channel
    "depth": 0.15,     # 1.5mm deep channel
}

GASKET_TAB_LENGTH_CM = 1.0   # 10mm long gasket tab segments
GASKET_TAB_GAP_CM = 0.5      # 5mm gap between segments
