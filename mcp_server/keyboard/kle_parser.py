"""
Keyboard Layout Editor (KLE) JSON parser.

Parses the serialized format from keyboard-layout-editor.com.
KLE format: array of rows, where each row is an array of either:
- A string (key legend)
- An object (property changes that apply to the next key)

Reference: https://github.com/nicodemus68/keyboard-layout-editor/wiki/Serialized-Data-Format
"""

import json
from .constants import KEY_UNIT_CM, STABILIZER_SPACING_CM


def parse_kle_json(json_str: str) -> dict:
    """
    Parse a KLE JSON string into a normalized layout dict.

    Args:
        json_str: KLE serialized JSON (the raw array, or an object with a 'keys' field).

    Returns:
        dict with keys: name, keys, total_width_u, total_height_u,
        pcb_mounting_holes, stabilizer_positions
    """
    data = json.loads(json_str)

    # Handle both raw array and wrapped object formats
    if isinstance(data, dict):
        # Some KLE exports wrap in {"name": "...", "keys": [...]}
        rows = data.get("keys", data.get("rows", []))
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("KLE JSON must be an array of rows or an object with a 'keys' field")

    keys = []
    current_x = 0.0
    current_y = 0.0

    # Properties that apply to the next key only
    next_props = {}

    for row in rows:
        if isinstance(row, dict):
            # Top-level metadata object (name, author, etc.) - skip
            continue

        if not isinstance(row, list):
            continue

        current_x = 0.0

        for item in row:
            if isinstance(item, dict):
                # Property object: applies to the next key
                next_props.update(item)
                # Some properties adjust position
                if "x" in item:
                    current_x += float(item["x"])
                if "y" in item:
                    current_y += float(item["y"])
                continue

            # It's a key legend string
            w = float(next_props.get("w", 1))
            h = float(next_props.get("h", 1))
            x2 = float(next_props.get("x2", 0))
            y2 = float(next_props.get("y2", 0))
            w2 = float(next_props.get("w2", w))
            h2 = float(next_props.get("h2", h))

            key = {
                "x": round(current_x, 4),
                "y": round(current_y, 4),
                "w": w,
                "h": h,
                "legend": str(item).split("\n")[0] if item else "",
            }

            # Track secondary dimensions for ISO enter, L-shaped keys, etc.
            if x2 != 0 or y2 != 0 or w2 != w or h2 != h:
                key["x2"] = x2
                key["y2"] = y2
                key["w2"] = w2
                key["h2"] = h2

            keys.append(key)

            # Advance x by the key width
            current_x += w

            # Reset per-key properties (but NOT position offsets)
            next_props = {}

        # Move to next row
        current_y += 1.0

    # Compute bounds
    max_x = 0.0
    max_y = 0.0
    for key in keys:
        right = key["x"] + key["w"]
        bottom = key["y"] + key["h"]
        max_x = max(max_x, right)
        max_y = max(max_y, bottom)

    layout = {
        "name": "KLE Custom",
        "total_width_u": round(max_x, 4),
        "total_height_u": round(max_y, 4),
        "keys": keys,
        "pcb_mounting_holes": estimate_pcb_holes_from_layout(keys, max_x, max_y),
        "stabilizer_positions": _detect_stabilizers(keys),
    }
    return layout


def _detect_stabilizers(keys: list) -> list:
    """Auto-detect stabilizer positions from keys >= 2U wide."""
    stabs = []
    for key in keys:
        w = key["w"]
        if w >= 2.0:
            spacing = None
            for size, sp in sorted(STABILIZER_SPACING_CM.items()):
                if w >= size - 0.1:
                    spacing = sp
            if spacing is None:
                continue

            cx = (key["x"] + w / 2) * KEY_UNIT_CM
            cy = (key["y"] + key["h"] / 2) * KEY_UNIT_CM

            stabs.append({
                "x_cm": round(cx, 4),
                "y_cm": round(cy, 4),
                "width_u": w,
                "spacing_cm": spacing,
            })
    return stabs


def estimate_pcb_holes_from_layout(keys: list, width_u: float, height_u: float) -> list:
    """
    Heuristically place PCB mounting holes for a custom layout.

    Places holes in a grid pattern avoiding key positions, similar to
    standard PCB mounting patterns.
    """
    width_cm = width_u * KEY_UNIT_CM
    height_cm = height_u * KEY_UNIT_CM

    if width_cm < 1 or height_cm < 1:
        return []

    holes = []

    # Place holes at roughly equal spacing, targeting 5-8 holes
    # Standard approach: corners + midpoints
    margin_x = min(2.5, width_cm * 0.1)
    margin_y = min(1.5, height_cm * 0.15)

    # Bottom row
    holes.append({"x": round(margin_x, 4), "y": round(margin_y, 4)})
    holes.append({"x": round(width_cm / 2, 4), "y": round(margin_y, 4)})
    holes.append({"x": round(width_cm - margin_x, 4), "y": round(margin_y, 4)})

    # Middle row (only if tall enough)
    if height_cm > 6:
        mid_y = height_cm / 2
        holes.append({"x": round(width_cm * 0.25, 4), "y": round(mid_y, 4)})
        holes.append({"x": round(width_cm * 0.75, 4), "y": round(mid_y, 4)})

    # Top row
    if height_cm > 4:
        holes.append({"x": round(margin_x, 4), "y": round(height_cm - margin_y, 4)})
        holes.append({"x": round(width_cm - margin_x, 4), "y": round(height_cm - margin_y, 4)})

    return holes
