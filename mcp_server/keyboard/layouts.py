"""
Standard keyboard layout definitions.

Each layout contains:
- keys: list of {x, y, w, h} in key units
- total_width_u / total_height_u: bounding dimensions in units
- pcb_mounting_holes: list of {x, y} in cm from bottom-left of PCB
- stabilizer_positions: auto-detected from keys >= 2U wide
"""

from .constants import KEY_UNIT_CM, STABILIZER_SPACING_CM


# ---- Standard Layouts ----

# 60% (GH60-compatible, ANSI, 61 keys)
LAYOUT_60 = {
    "name": "60%",
    "total_width_u": 15,
    "total_height_u": 5,
    "keys": [
        # Row 0 (top): number row - 14 keys
        {"x": 0, "y": 0, "w": 1, "h": 1},      # Esc/~
        {"x": 1, "y": 0, "w": 1, "h": 1},       # 1
        {"x": 2, "y": 0, "w": 1, "h": 1},       # 2
        {"x": 3, "y": 0, "w": 1, "h": 1},       # 3
        {"x": 4, "y": 0, "w": 1, "h": 1},       # 4
        {"x": 5, "y": 0, "w": 1, "h": 1},       # 5
        {"x": 6, "y": 0, "w": 1, "h": 1},       # 6
        {"x": 7, "y": 0, "w": 1, "h": 1},       # 7
        {"x": 8, "y": 0, "w": 1, "h": 1},       # 8
        {"x": 9, "y": 0, "w": 1, "h": 1},       # 9
        {"x": 10, "y": 0, "w": 1, "h": 1},      # 0
        {"x": 11, "y": 0, "w": 1, "h": 1},      # -
        {"x": 12, "y": 0, "w": 1, "h": 1},      # =
        {"x": 13, "y": 0, "w": 2, "h": 1},      # Backspace (2U)
        # Row 1: QWERTY row - 14 keys
        {"x": 0, "y": 1, "w": 1.5, "h": 1},     # Tab
        {"x": 1.5, "y": 1, "w": 1, "h": 1},     # Q
        {"x": 2.5, "y": 1, "w": 1, "h": 1},     # W
        {"x": 3.5, "y": 1, "w": 1, "h": 1},     # E
        {"x": 4.5, "y": 1, "w": 1, "h": 1},     # R
        {"x": 5.5, "y": 1, "w": 1, "h": 1},     # T
        {"x": 6.5, "y": 1, "w": 1, "h": 1},     # Y
        {"x": 7.5, "y": 1, "w": 1, "h": 1},     # U
        {"x": 8.5, "y": 1, "w": 1, "h": 1},     # I
        {"x": 9.5, "y": 1, "w": 1, "h": 1},     # O
        {"x": 10.5, "y": 1, "w": 1, "h": 1},    # P
        {"x": 11.5, "y": 1, "w": 1, "h": 1},    # [
        {"x": 12.5, "y": 1, "w": 1, "h": 1},    # ]
        {"x": 13.5, "y": 1, "w": 1.5, "h": 1},  # Backslash
        # Row 2: home row - 13 keys
        {"x": 0, "y": 2, "w": 1.75, "h": 1},    # Caps Lock
        {"x": 1.75, "y": 2, "w": 1, "h": 1},    # A
        {"x": 2.75, "y": 2, "w": 1, "h": 1},    # S
        {"x": 3.75, "y": 2, "w": 1, "h": 1},    # D
        {"x": 4.75, "y": 2, "w": 1, "h": 1},    # F
        {"x": 5.75, "y": 2, "w": 1, "h": 1},    # G
        {"x": 6.75, "y": 2, "w": 1, "h": 1},    # H
        {"x": 7.75, "y": 2, "w": 1, "h": 1},    # J
        {"x": 8.75, "y": 2, "w": 1, "h": 1},    # K
        {"x": 9.75, "y": 2, "w": 1, "h": 1},    # L
        {"x": 10.75, "y": 2, "w": 1, "h": 1},   # ;
        {"x": 11.75, "y": 2, "w": 1, "h": 1},   # '
        {"x": 12.75, "y": 2, "w": 2.25, "h": 1},  # Enter (2.25U)
        # Row 3: bottom alpha row - 12 keys
        {"x": 0, "y": 3, "w": 2.25, "h": 1},    # Left Shift (2.25U)
        {"x": 2.25, "y": 3, "w": 1, "h": 1},    # Z
        {"x": 3.25, "y": 3, "w": 1, "h": 1},    # X
        {"x": 4.25, "y": 3, "w": 1, "h": 1},    # C
        {"x": 5.25, "y": 3, "w": 1, "h": 1},    # V
        {"x": 6.25, "y": 3, "w": 1, "h": 1},    # B
        {"x": 7.25, "y": 3, "w": 1, "h": 1},    # N
        {"x": 8.25, "y": 3, "w": 1, "h": 1},    # M
        {"x": 9.25, "y": 3, "w": 1, "h": 1},    # ,
        {"x": 10.25, "y": 3, "w": 1, "h": 1},   # .
        {"x": 11.25, "y": 3, "w": 1, "h": 1},   # /
        {"x": 12.25, "y": 3, "w": 2.75, "h": 1},  # Right Shift (2.75U)
        # Row 4: bottom row - 8 keys
        {"x": 0, "y": 4, "w": 1.25, "h": 1},    # Left Ctrl
        {"x": 1.25, "y": 4, "w": 1.25, "h": 1}, # Win
        {"x": 2.5, "y": 4, "w": 1.25, "h": 1},  # Left Alt
        {"x": 3.75, "y": 4, "w": 6.25, "h": 1}, # Space (6.25U)
        {"x": 10, "y": 4, "w": 1.25, "h": 1},   # Right Alt
        {"x": 11.25, "y": 4, "w": 1.25, "h": 1},  # Win
        {"x": 12.5, "y": 4, "w": 1.25, "h": 1},   # Menu
        {"x": 13.75, "y": 4, "w": 1.25, "h": 1},  # Right Ctrl
    ],
    "pcb_mounting_holes": [
        # GH60 standard mounting holes (cm from PCB bottom-left)
        {"x": 2.54, "y": 1.27},
        {"x": 13.335, "y": 1.27},
        {"x": 24.13, "y": 1.27},
        {"x": 7.62, "y": 5.08},
        {"x": 20.32, "y": 5.08},
    ],
}

# 65% (68 keys, adds arrow cluster + a few nav keys)
LAYOUT_65 = {
    "name": "65%",
    "total_width_u": 16,
    "total_height_u": 5,
    "keys": [
        # Row 0: number row + Del
        {"x": 0, "y": 0, "w": 1, "h": 1},
        {"x": 1, "y": 0, "w": 1, "h": 1},
        {"x": 2, "y": 0, "w": 1, "h": 1},
        {"x": 3, "y": 0, "w": 1, "h": 1},
        {"x": 4, "y": 0, "w": 1, "h": 1},
        {"x": 5, "y": 0, "w": 1, "h": 1},
        {"x": 6, "y": 0, "w": 1, "h": 1},
        {"x": 7, "y": 0, "w": 1, "h": 1},
        {"x": 8, "y": 0, "w": 1, "h": 1},
        {"x": 9, "y": 0, "w": 1, "h": 1},
        {"x": 10, "y": 0, "w": 1, "h": 1},
        {"x": 11, "y": 0, "w": 1, "h": 1},
        {"x": 12, "y": 0, "w": 1, "h": 1},
        {"x": 13, "y": 0, "w": 2, "h": 1},      # Backspace
        {"x": 15, "y": 0, "w": 1, "h": 1},      # Del/Home
        # Row 1: QWERTY + PgUp
        {"x": 0, "y": 1, "w": 1.5, "h": 1},
        {"x": 1.5, "y": 1, "w": 1, "h": 1},
        {"x": 2.5, "y": 1, "w": 1, "h": 1},
        {"x": 3.5, "y": 1, "w": 1, "h": 1},
        {"x": 4.5, "y": 1, "w": 1, "h": 1},
        {"x": 5.5, "y": 1, "w": 1, "h": 1},
        {"x": 6.5, "y": 1, "w": 1, "h": 1},
        {"x": 7.5, "y": 1, "w": 1, "h": 1},
        {"x": 8.5, "y": 1, "w": 1, "h": 1},
        {"x": 9.5, "y": 1, "w": 1, "h": 1},
        {"x": 10.5, "y": 1, "w": 1, "h": 1},
        {"x": 11.5, "y": 1, "w": 1, "h": 1},
        {"x": 12.5, "y": 1, "w": 1, "h": 1},
        {"x": 13.5, "y": 1, "w": 1.5, "h": 1},
        {"x": 15, "y": 1, "w": 1, "h": 1},      # PgUp
        # Row 2: Home row + PgDn
        {"x": 0, "y": 2, "w": 1.75, "h": 1},
        {"x": 1.75, "y": 2, "w": 1, "h": 1},
        {"x": 2.75, "y": 2, "w": 1, "h": 1},
        {"x": 3.75, "y": 2, "w": 1, "h": 1},
        {"x": 4.75, "y": 2, "w": 1, "h": 1},
        {"x": 5.75, "y": 2, "w": 1, "h": 1},
        {"x": 6.75, "y": 2, "w": 1, "h": 1},
        {"x": 7.75, "y": 2, "w": 1, "h": 1},
        {"x": 8.75, "y": 2, "w": 1, "h": 1},
        {"x": 9.75, "y": 2, "w": 1, "h": 1},
        {"x": 10.75, "y": 2, "w": 1, "h": 1},
        {"x": 11.75, "y": 2, "w": 1, "h": 1},
        {"x": 12.75, "y": 2, "w": 2.25, "h": 1},  # Enter
        {"x": 15, "y": 2, "w": 1, "h": 1},      # PgDn
        # Row 3: Shift row + Up + End
        {"x": 0, "y": 3, "w": 2.25, "h": 1},    # LShift
        {"x": 2.25, "y": 3, "w": 1, "h": 1},
        {"x": 3.25, "y": 3, "w": 1, "h": 1},
        {"x": 4.25, "y": 3, "w": 1, "h": 1},
        {"x": 5.25, "y": 3, "w": 1, "h": 1},
        {"x": 6.25, "y": 3, "w": 1, "h": 1},
        {"x": 7.25, "y": 3, "w": 1, "h": 1},
        {"x": 8.25, "y": 3, "w": 1, "h": 1},
        {"x": 9.25, "y": 3, "w": 1, "h": 1},
        {"x": 10.25, "y": 3, "w": 1, "h": 1},
        {"x": 11.25, "y": 3, "w": 1.75, "h": 1},  # RShift (1.75U)
        {"x": 13, "y": 3, "w": 1, "h": 1},      # Up
        {"x": 14, "y": 3, "w": 1, "h": 1},      # End (shifted due to arrows)
        # Note: 65% right shift is typically 1.75U to make room
        # Row 4: Bottom row + arrows
        {"x": 0, "y": 4, "w": 1.25, "h": 1},
        {"x": 1.25, "y": 4, "w": 1.25, "h": 1},
        {"x": 2.5, "y": 4, "w": 1.25, "h": 1},
        {"x": 3.75, "y": 4, "w": 6.25, "h": 1}, # Space
        {"x": 10, "y": 4, "w": 1.25, "h": 1},
        {"x": 11.25, "y": 4, "w": 1.25, "h": 1},
        {"x": 12.5, "y": 4, "w": 1, "h": 1},    # Left
        {"x": 13.5, "y": 4, "w": 1, "h": 1},    # Down
        {"x": 14.5, "y": 4, "w": 1, "h": 1},    # Right
    ],
    "pcb_mounting_holes": [
        {"x": 2.54, "y": 1.27},
        {"x": 15.24, "y": 1.27},
        {"x": 27.94, "y": 1.27},
        {"x": 7.62, "y": 5.08},
        {"x": 22.86, "y": 5.08},
    ],
}

# 75% (84 keys)
LAYOUT_75 = {
    "name": "75%",
    "total_width_u": 16,
    "total_height_u": 6,
    "keys": [
        # Row 0: F-row (compressed)
        {"x": 0, "y": 0, "w": 1, "h": 1},       # Esc
        {"x": 1, "y": 0, "w": 1, "h": 1},       # F1
        {"x": 2, "y": 0, "w": 1, "h": 1},       # F2
        {"x": 3, "y": 0, "w": 1, "h": 1},       # F3
        {"x": 4, "y": 0, "w": 1, "h": 1},       # F4
        {"x": 5, "y": 0, "w": 1, "h": 1},       # F5
        {"x": 6, "y": 0, "w": 1, "h": 1},       # F6
        {"x": 7, "y": 0, "w": 1, "h": 1},       # F7
        {"x": 8, "y": 0, "w": 1, "h": 1},       # F8
        {"x": 9, "y": 0, "w": 1, "h": 1},       # F9
        {"x": 10, "y": 0, "w": 1, "h": 1},      # F10
        {"x": 11, "y": 0, "w": 1, "h": 1},      # F11
        {"x": 12, "y": 0, "w": 1, "h": 1},      # F12
        {"x": 13, "y": 0, "w": 1, "h": 1},      # PrtSc
        {"x": 14, "y": 0, "w": 1, "h": 1},      # Pause
        {"x": 15, "y": 0, "w": 1, "h": 1},      # Del
        # Row 1: Number row
        {"x": 0, "y": 1, "w": 1, "h": 1},
        {"x": 1, "y": 1, "w": 1, "h": 1},
        {"x": 2, "y": 1, "w": 1, "h": 1},
        {"x": 3, "y": 1, "w": 1, "h": 1},
        {"x": 4, "y": 1, "w": 1, "h": 1},
        {"x": 5, "y": 1, "w": 1, "h": 1},
        {"x": 6, "y": 1, "w": 1, "h": 1},
        {"x": 7, "y": 1, "w": 1, "h": 1},
        {"x": 8, "y": 1, "w": 1, "h": 1},
        {"x": 9, "y": 1, "w": 1, "h": 1},
        {"x": 10, "y": 1, "w": 1, "h": 1},
        {"x": 11, "y": 1, "w": 1, "h": 1},
        {"x": 12, "y": 1, "w": 1, "h": 1},
        {"x": 13, "y": 1, "w": 2, "h": 1},      # Backspace
        {"x": 15, "y": 1, "w": 1, "h": 1},      # Home
        # Row 2: QWERTY
        {"x": 0, "y": 2, "w": 1.5, "h": 1},
        {"x": 1.5, "y": 2, "w": 1, "h": 1},
        {"x": 2.5, "y": 2, "w": 1, "h": 1},
        {"x": 3.5, "y": 2, "w": 1, "h": 1},
        {"x": 4.5, "y": 2, "w": 1, "h": 1},
        {"x": 5.5, "y": 2, "w": 1, "h": 1},
        {"x": 6.5, "y": 2, "w": 1, "h": 1},
        {"x": 7.5, "y": 2, "w": 1, "h": 1},
        {"x": 8.5, "y": 2, "w": 1, "h": 1},
        {"x": 9.5, "y": 2, "w": 1, "h": 1},
        {"x": 10.5, "y": 2, "w": 1, "h": 1},
        {"x": 11.5, "y": 2, "w": 1, "h": 1},
        {"x": 12.5, "y": 2, "w": 1, "h": 1},
        {"x": 13.5, "y": 2, "w": 1.5, "h": 1},
        {"x": 15, "y": 2, "w": 1, "h": 1},      # PgUp
        # Row 3: Home row
        {"x": 0, "y": 3, "w": 1.75, "h": 1},
        {"x": 1.75, "y": 3, "w": 1, "h": 1},
        {"x": 2.75, "y": 3, "w": 1, "h": 1},
        {"x": 3.75, "y": 3, "w": 1, "h": 1},
        {"x": 4.75, "y": 3, "w": 1, "h": 1},
        {"x": 5.75, "y": 3, "w": 1, "h": 1},
        {"x": 6.75, "y": 3, "w": 1, "h": 1},
        {"x": 7.75, "y": 3, "w": 1, "h": 1},
        {"x": 8.75, "y": 3, "w": 1, "h": 1},
        {"x": 9.75, "y": 3, "w": 1, "h": 1},
        {"x": 10.75, "y": 3, "w": 1, "h": 1},
        {"x": 11.75, "y": 3, "w": 1, "h": 1},
        {"x": 12.75, "y": 3, "w": 2.25, "h": 1},  # Enter
        {"x": 15, "y": 3, "w": 1, "h": 1},      # PgDn
        # Row 4: Shift row
        {"x": 0, "y": 4, "w": 2.25, "h": 1},    # LShift
        {"x": 2.25, "y": 4, "w": 1, "h": 1},
        {"x": 3.25, "y": 4, "w": 1, "h": 1},
        {"x": 4.25, "y": 4, "w": 1, "h": 1},
        {"x": 5.25, "y": 4, "w": 1, "h": 1},
        {"x": 6.25, "y": 4, "w": 1, "h": 1},
        {"x": 7.25, "y": 4, "w": 1, "h": 1},
        {"x": 8.25, "y": 4, "w": 1, "h": 1},
        {"x": 9.25, "y": 4, "w": 1, "h": 1},
        {"x": 10.25, "y": 4, "w": 1, "h": 1},
        {"x": 11.25, "y": 4, "w": 1.75, "h": 1},  # RShift
        {"x": 13, "y": 4, "w": 1, "h": 1},      # Up
        {"x": 14, "y": 4, "w": 1, "h": 1},      # End
        # Row 5: Bottom row
        {"x": 0, "y": 5, "w": 1.25, "h": 1},
        {"x": 1.25, "y": 5, "w": 1.25, "h": 1},
        {"x": 2.5, "y": 5, "w": 1.25, "h": 1},
        {"x": 3.75, "y": 5, "w": 6.25, "h": 1}, # Space
        {"x": 10, "y": 5, "w": 1, "h": 1},
        {"x": 11, "y": 5, "w": 1, "h": 1},
        {"x": 12, "y": 5, "w": 1, "h": 1},      # Left
        {"x": 13, "y": 5, "w": 1, "h": 1},      # Down
        {"x": 14, "y": 5, "w": 1, "h": 1},      # Right
    ],
    "pcb_mounting_holes": [
        {"x": 2.54, "y": 1.27},
        {"x": 15.24, "y": 1.27},
        {"x": 27.94, "y": 1.27},
        {"x": 7.62, "y": 5.715},
        {"x": 22.86, "y": 5.715},
        {"x": 15.24, "y": 10.16},
    ],
}

# TKL (87 keys, ANSI)
LAYOUT_TKL = {
    "name": "TKL",
    "total_width_u": 18.25,
    "total_height_u": 6.5,  # includes gap between F-row and number row
    "keys": [
        # Row 0: F-row with gaps
        {"x": 0, "y": 0, "w": 1, "h": 1},       # Esc
        {"x": 2, "y": 0, "w": 1, "h": 1},       # F1
        {"x": 3, "y": 0, "w": 1, "h": 1},       # F2
        {"x": 4, "y": 0, "w": 1, "h": 1},       # F3
        {"x": 5, "y": 0, "w": 1, "h": 1},       # F4
        {"x": 6.5, "y": 0, "w": 1, "h": 1},     # F5
        {"x": 7.5, "y": 0, "w": 1, "h": 1},     # F6
        {"x": 8.5, "y": 0, "w": 1, "h": 1},     # F7
        {"x": 9.5, "y": 0, "w": 1, "h": 1},     # F8
        {"x": 11, "y": 0, "w": 1, "h": 1},      # F9
        {"x": 12, "y": 0, "w": 1, "h": 1},      # F10
        {"x": 13, "y": 0, "w": 1, "h": 1},      # F11
        {"x": 14, "y": 0, "w": 1, "h": 1},      # F12
        {"x": 15.25, "y": 0, "w": 1, "h": 1},   # PrtSc
        {"x": 16.25, "y": 0, "w": 1, "h": 1},   # ScrLk
        {"x": 17.25, "y": 0, "w": 1, "h": 1},   # Pause
        # Row 1: Number row (y=1.5 for gap)
        {"x": 0, "y": 1.5, "w": 1, "h": 1},
        {"x": 1, "y": 1.5, "w": 1, "h": 1},
        {"x": 2, "y": 1.5, "w": 1, "h": 1},
        {"x": 3, "y": 1.5, "w": 1, "h": 1},
        {"x": 4, "y": 1.5, "w": 1, "h": 1},
        {"x": 5, "y": 1.5, "w": 1, "h": 1},
        {"x": 6, "y": 1.5, "w": 1, "h": 1},
        {"x": 7, "y": 1.5, "w": 1, "h": 1},
        {"x": 8, "y": 1.5, "w": 1, "h": 1},
        {"x": 9, "y": 1.5, "w": 1, "h": 1},
        {"x": 10, "y": 1.5, "w": 1, "h": 1},
        {"x": 11, "y": 1.5, "w": 1, "h": 1},
        {"x": 12, "y": 1.5, "w": 1, "h": 1},
        {"x": 13, "y": 1.5, "w": 2, "h": 1},    # Backspace
        {"x": 15.25, "y": 1.5, "w": 1, "h": 1}, # Ins
        {"x": 16.25, "y": 1.5, "w": 1, "h": 1}, # Home
        {"x": 17.25, "y": 1.5, "w": 1, "h": 1}, # PgUp
        # Row 2: QWERTY
        {"x": 0, "y": 2.5, "w": 1.5, "h": 1},
        {"x": 1.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 2.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 3.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 4.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 5.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 6.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 7.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 8.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 9.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 10.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 11.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 12.5, "y": 2.5, "w": 1, "h": 1},
        {"x": 13.5, "y": 2.5, "w": 1.5, "h": 1},
        {"x": 15.25, "y": 2.5, "w": 1, "h": 1}, # Del
        {"x": 16.25, "y": 2.5, "w": 1, "h": 1}, # End
        {"x": 17.25, "y": 2.5, "w": 1, "h": 1}, # PgDn
        # Row 3: Home row
        {"x": 0, "y": 3.5, "w": 1.75, "h": 1},
        {"x": 1.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 2.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 3.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 4.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 5.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 6.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 7.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 8.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 9.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 10.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 11.75, "y": 3.5, "w": 1, "h": 1},
        {"x": 12.75, "y": 3.5, "w": 2.25, "h": 1},  # Enter
        # Row 4: Shift row
        {"x": 0, "y": 4.5, "w": 2.25, "h": 1},
        {"x": 2.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 3.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 4.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 5.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 6.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 7.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 8.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 9.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 10.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 11.25, "y": 4.5, "w": 1, "h": 1},
        {"x": 12.25, "y": 4.5, "w": 2.75, "h": 1},  # RShift
        {"x": 16.25, "y": 4.5, "w": 1, "h": 1}, # Up
        # Row 5: Bottom row
        {"x": 0, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 1.25, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 2.5, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 3.75, "y": 5.5, "w": 6.25, "h": 1},  # Space
        {"x": 10, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 11.25, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 12.5, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 13.75, "y": 5.5, "w": 1.25, "h": 1},
        {"x": 15.25, "y": 5.5, "w": 1, "h": 1}, # Left
        {"x": 16.25, "y": 5.5, "w": 1, "h": 1}, # Down
        {"x": 17.25, "y": 5.5, "w": 1, "h": 1}, # Right
    ],
    "pcb_mounting_holes": [
        {"x": 2.54, "y": 1.27},
        {"x": 15.24, "y": 1.27},
        {"x": 27.94, "y": 1.27},
        {"x": 7.62, "y": 5.715},
        {"x": 22.86, "y": 5.715},
        {"x": 33.655, "y": 5.715},
        {"x": 15.24, "y": 10.16},
    ],
}

# Full-size (104 keys, ANSI) - same as TKL + numpad
LAYOUT_FULL = {
    "name": "Full",
    "total_width_u": 22.5,
    "total_height_u": 6.5,
    "keys": LAYOUT_TKL["keys"] + [
        # Numpad - Row 1 (alongside number row)
        {"x": 18.5, "y": 1.5, "w": 1, "h": 1},  # NumLk
        {"x": 19.5, "y": 1.5, "w": 1, "h": 1},  # /
        {"x": 20.5, "y": 1.5, "w": 1, "h": 1},  # *
        {"x": 21.5, "y": 1.5, "w": 1, "h": 1},  # -
        # Numpad - Row 2
        {"x": 18.5, "y": 2.5, "w": 1, "h": 1},  # 7
        {"x": 19.5, "y": 2.5, "w": 1, "h": 1},  # 8
        {"x": 20.5, "y": 2.5, "w": 1, "h": 1},  # 9
        {"x": 21.5, "y": 2.5, "w": 1, "h": 2},  # + (2U tall)
        # Numpad - Row 3
        {"x": 18.5, "y": 3.5, "w": 1, "h": 1},  # 4
        {"x": 19.5, "y": 3.5, "w": 1, "h": 1},  # 5
        {"x": 20.5, "y": 3.5, "w": 1, "h": 1},  # 6
        # Numpad - Row 4
        {"x": 18.5, "y": 4.5, "w": 1, "h": 1},  # 1
        {"x": 19.5, "y": 4.5, "w": 1, "h": 1},  # 2
        {"x": 20.5, "y": 4.5, "w": 1, "h": 1},  # 3
        {"x": 21.5, "y": 4.5, "w": 1, "h": 2},  # Enter (2U tall)
        # Numpad - Row 5
        {"x": 18.5, "y": 5.5, "w": 2, "h": 1},  # 0 (2U wide)
        {"x": 20.5, "y": 5.5, "w": 1, "h": 1},  # .
    ],
    "pcb_mounting_holes": LAYOUT_TKL["pcb_mounting_holes"] + [
        {"x": 40.64, "y": 1.27},
        {"x": 40.64, "y": 5.715},
        {"x": 40.64, "y": 10.16},
    ],
}


# ---- Layout Registry ----

LAYOUTS = {
    "60%": LAYOUT_60,
    "60": LAYOUT_60,
    "65%": LAYOUT_65,
    "65": LAYOUT_65,
    "75%": LAYOUT_75,
    "75": LAYOUT_75,
    "tkl": LAYOUT_TKL,
    "tenkeyless": LAYOUT_TKL,
    "80%": LAYOUT_TKL,
    "full": LAYOUT_FULL,
    "100%": LAYOUT_FULL,
    "104": LAYOUT_FULL,
}


def get_layout(name: str) -> dict:
    """Get a standard layout by name. Raises KeyError if not found."""
    key = name.lower().strip()
    if key not in LAYOUTS:
        available = sorted(set(l["name"] for l in LAYOUTS.values()))
        raise KeyError(f"Unknown layout '{name}'. Available: {available}")
    return LAYOUTS[key]


def get_layout_bounds_cm(layout: dict) -> dict:
    """
    Compute the bounding dimensions of a layout in cm.

    Returns: {width_cm, height_cm} representing the total key area
    (not including case bezels).
    """
    if not layout.get("keys"):
        return {"width_cm": 0, "height_cm": 0}

    max_x = 0
    max_y = 0
    for key in layout["keys"]:
        right = (key["x"] + key["w"]) * KEY_UNIT_CM
        bottom = (key["y"] + key["h"]) * KEY_UNIT_CM
        max_x = max(max_x, right)
        max_y = max(max_y, bottom)

    return {
        "width_cm": round(max_x, 4),
        "height_cm": round(max_y, 4),
    }


def get_pcb_holes(layout_name: str) -> list:
    """Get PCB mounting hole positions for a standard layout."""
    layout = get_layout(layout_name)
    return layout.get("pcb_mounting_holes", [])


def get_stabilizer_positions(layout: dict) -> list:
    """
    Auto-detect stabilizer positions from keys >= 2U wide.

    Returns list of {x_cm, y_cm, width_u, spacing_cm} for each stabilized key.
    """
    stabs = []
    for key in layout.get("keys", []):
        w = key["w"]
        if w >= 2.0:
            # Find the closest matching stabilizer spacing
            spacing = None
            for size, sp in sorted(STABILIZER_SPACING_CM.items()):
                if w >= size - 0.1:
                    spacing = sp
            if spacing is None:
                continue

            # Center of the key in cm
            cx = (key["x"] + w / 2) * KEY_UNIT_CM
            cy = (key["y"] + key["h"] / 2) * KEY_UNIT_CM

            stabs.append({
                "x_cm": round(cx, 4),
                "y_cm": round(cy, 4),
                "width_u": w,
                "spacing_cm": spacing,
            })
    return stabs
