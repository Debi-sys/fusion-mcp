"""
KiCad PCB file parser.

Parses .kicad_pcb files (S-expression format) and extracts key mechanical
dimensions, component positions, mounting holes, and board outline geometry.

KiCad PCB files use a Lisp-like S-expression syntax:
  (kicad_pcb (version 20221018) (generator pcbnew)
    (general (thickness 1.6))
    (layers (0 "F.Cu" signal) ...)
    (footprint "Package:Name" (at x y) ...)
    (gr_line (start x y) (end x y) (layer "Edge.Cuts") ...)
    ...
  )

Reference: https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/
"""

import json
import math
import re


# ---------------------------------------------------------------------------
# S-expression tokenizer / parser
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Tokenize an S-expression string into a flat list of tokens."""
    tokens: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        if ch in (" ", "\t", "\r", "\n"):
            i += 1
        elif ch == "(":
            tokens.append("(")
            i += 1
        elif ch == ")":
            tokens.append(")")
            i += 1
        elif ch == '"':
            # Quoted string
            j = i + 1
            while j < length:
                if text[j] == "\\" and j + 1 < length:
                    j += 2
                elif text[j] == '"':
                    break
                else:
                    j += 1
            tokens.append(text[i + 1 : j])  # strip quotes
            i = j + 1
        else:
            # Unquoted atom
            j = i
            while j < length and text[j] not in (" ", "\t", "\r", "\n", "(", ")"):
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def _parse_tokens(tokens: list[str], pos: int) -> tuple:
    """Recursively parse tokens into nested lists starting at *pos*.

    Returns (parsed_node, next_pos).
    """
    if tokens[pos] == "(":
        lst: list = []
        pos += 1  # skip '('
        while pos < len(tokens) and tokens[pos] != ")":
            node, pos = _parse_tokens(tokens, pos)
            lst.append(node)
        pos += 1  # skip ')'
        return lst, pos
    else:
        return tokens[pos], pos + 1


def parse_sexpr(text: str):
    """Parse a full S-expression string into a nested Python list structure."""
    tokens = _tokenize(text)
    if not tokens:
        return []
    node, _ = _parse_tokens(tokens, 0)
    return node


# ---------------------------------------------------------------------------
# Helper look-ups inside parsed S-expression trees
# ---------------------------------------------------------------------------

def _find(node: list, tag: str):
    """Return the first child list whose first element equals *tag*, or None."""
    if not isinstance(node, list):
        return None
    for child in node:
        if isinstance(child, list) and len(child) > 0 and child[0] == tag:
            return child
    return None


def _find_all(node: list, tag: str) -> list:
    """Return all child lists whose first element equals *tag*."""
    results = []
    if not isinstance(node, list):
        return results
    for child in node:
        if isinstance(child, list) and len(child) > 0 and child[0] == tag:
            results.append(child)
    return results


def _find_value(node: list, tag: str, default=None):
    """Return the second element of the first child matching *tag*."""
    child = _find(node, tag)
    if child and len(child) > 1:
        return child[1]
    return default


def _to_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Board outline extraction from Edge.Cuts layer
# ---------------------------------------------------------------------------

def _extract_outline_segments(tree: list) -> list[dict]:
    """Extract graphic primitives on the Edge.Cuts layer.

    Returns a list of dicts with type and coordinates (all in mm).
    """
    segments: list[dict] = []

    for child in tree:
        if not isinstance(child, list) or len(child) < 1:
            continue
        kind = child[0]
        if kind not in ("gr_line", "gr_arc", "gr_circle", "gr_rect", "gr_poly"):
            continue

        layer = _find_value(child, "layer")
        if layer != "Edge.Cuts":
            continue

        if kind == "gr_line":
            start = _find(child, "start")
            end = _find(child, "end")
            if start and end:
                segments.append({
                    "type": "line",
                    "start": [_to_float(start[1]), _to_float(start[2])],
                    "end": [_to_float(end[1]), _to_float(end[2])],
                })

        elif kind == "gr_arc":
            start = _find(child, "start")
            mid = _find(child, "mid")
            end = _find(child, "end")
            center = _find(child, "center")
            if start and end:
                seg = {
                    "type": "arc",
                    "start": [_to_float(start[1]), _to_float(start[2])],
                    "end": [_to_float(end[1]), _to_float(end[2])],
                }
                if mid:
                    seg["mid"] = [_to_float(mid[1]), _to_float(mid[2])]
                if center:
                    seg["center"] = [_to_float(center[1]), _to_float(center[2])]
                segments.append(seg)

        elif kind == "gr_circle":
            center = _find(child, "center")
            end = _find(child, "end")
            if center and end:
                cx, cy = _to_float(center[1]), _to_float(center[2])
                ex, ey = _to_float(end[1]), _to_float(end[2])
                radius = math.sqrt((ex - cx) ** 2 + (ey - cy) ** 2)
                segments.append({
                    "type": "circle",
                    "center": [cx, cy],
                    "radius": round(radius, 4),
                })

        elif kind == "gr_rect":
            start = _find(child, "start")
            end = _find(child, "end")
            if start and end:
                x1, y1 = _to_float(start[1]), _to_float(start[2])
                x2, y2 = _to_float(end[1]), _to_float(end[2])
                segments.append({
                    "type": "rect",
                    "start": [min(x1, x2), min(y1, y2)],
                    "end": [max(x1, x2), max(y1, y2)],
                })

        elif kind == "gr_poly":
            pts_node = _find(child, "pts")
            if pts_node:
                pts = []
                for xy in _find_all(pts_node, "xy"):
                    if len(xy) >= 3:
                        pts.append([_to_float(xy[1]), _to_float(xy[2])])
                if pts:
                    segments.append({"type": "polygon", "points": pts})

    return segments


def _bounding_box_from_outline(segments: list[dict]) -> dict | None:
    """Compute the axis-aligned bounding box from outline segments."""
    xs: list[float] = []
    ys: list[float] = []

    for seg in segments:
        stype = seg["type"]
        if stype == "line":
            xs.extend([seg["start"][0], seg["end"][0]])
            ys.extend([seg["start"][1], seg["end"][1]])
        elif stype == "arc":
            xs.extend([seg["start"][0], seg["end"][0]])
            ys.extend([seg["start"][1], seg["end"][1]])
            if "mid" in seg:
                xs.append(seg["mid"][0])
                ys.append(seg["mid"][1])
        elif stype == "circle":
            cx, cy = seg["center"]
            r = seg["radius"]
            xs.extend([cx - r, cx + r])
            ys.extend([cy - r, cy + r])
        elif stype == "rect":
            xs.extend([seg["start"][0], seg["end"][0]])
            ys.extend([seg["start"][1], seg["end"][1]])
        elif stype == "polygon":
            for pt in seg["points"]:
                xs.append(pt[0])
                ys.append(pt[1])

    if not xs:
        return None

    return {
        "min_x_mm": round(min(xs), 4),
        "min_y_mm": round(min(ys), 4),
        "max_x_mm": round(max(xs), 4),
        "max_y_mm": round(max(ys), 4),
        "width_mm": round(max(xs) - min(xs), 4),
        "height_mm": round(max(ys) - min(ys), 4),
    }


# ---------------------------------------------------------------------------
# Footprint / component extraction
# ---------------------------------------------------------------------------

def _extract_footprints(tree: list) -> list[dict]:
    """Extract footprint (component) information from the PCB tree."""
    footprints = []
    for child in _find_all(tree, "footprint"):
        fp_name = child[1] if len(child) > 1 and isinstance(child[1], str) else ""
        at_node = _find(child, "at")
        x = _to_float(at_node[1]) if at_node and len(at_node) > 1 else 0.0
        y = _to_float(at_node[2]) if at_node and len(at_node) > 2 else 0.0
        rotation = _to_float(at_node[3]) if at_node and len(at_node) > 3 else 0.0

        layer = _find_value(child, "layer", "")
        ref = ""
        value = ""
        for fp_text in _find_all(child, "fp_text"):
            if len(fp_text) >= 3:
                if fp_text[1] == "reference":
                    ref = fp_text[2]
                elif fp_text[1] == "value":
                    value = fp_text[2]
        # KiCad 8+ uses `property` nodes instead of `fp_text`
        for prop in _find_all(child, "property"):
            if len(prop) >= 3:
                if prop[1] == "Reference":
                    ref = prop[2]
                elif prop[1] == "Value":
                    value = prop[2]

        pads = []
        for pad_node in _find_all(child, "pad"):
            pad_info: dict = {}
            if len(pad_node) > 1:
                pad_info["number"] = pad_node[1]
            if len(pad_node) > 2:
                pad_info["type"] = pad_node[2]  # thru_hole, smd, etc.
            if len(pad_node) > 3:
                pad_info["shape"] = pad_node[3]  # circle, rect, oval, etc.
            pad_at = _find(pad_node, "at")
            if pad_at and len(pad_at) > 2:
                pad_info["x_mm"] = _to_float(pad_at[1])
                pad_info["y_mm"] = _to_float(pad_at[2])
            pad_size = _find(pad_node, "size")
            if pad_size and len(pad_size) > 2:
                pad_info["size_x_mm"] = _to_float(pad_size[1])
                pad_info["size_y_mm"] = _to_float(pad_size[2])
            drill = _find(pad_node, "drill")
            if drill and len(drill) > 1:
                pad_info["drill_mm"] = _to_float(drill[1])
            pads.append(pad_info)

        footprints.append({
            "footprint": fp_name,
            "reference": ref,
            "value": value,
            "x_mm": round(x, 4),
            "y_mm": round(y, 4),
            "rotation": round(rotation, 2),
            "layer": layer,
            "pad_count": len(pads),
            "pads": pads,
        })

    return footprints


# ---------------------------------------------------------------------------
# Mounting hole detection
# ---------------------------------------------------------------------------

_MOUNTING_HOLE_RE = re.compile(
    r"(mounting.?hole|mount.?hole|m[0-9]|standoff)", re.IGNORECASE
)


def _extract_mounting_holes(footprints: list[dict]) -> list[dict]:
    """Identify mounting holes from the footprint list."""
    holes = []
    for fp in footprints:
        name = fp["footprint"]
        ref = fp["reference"]
        is_hole = bool(_MOUNTING_HOLE_RE.search(name))
        # Also treat single-pad NPTH footprints as mounting holes
        if not is_hole and fp["pad_count"] == 1:
            for pad in fp["pads"]:
                if pad.get("type") == "np_thru_hole":
                    is_hole = True
                    break
        if is_hole:
            drill = 0.0
            for pad in fp["pads"]:
                drill = max(drill, pad.get("drill_mm", 0.0))
            holes.append({
                "reference": ref,
                "footprint": name,
                "x_mm": fp["x_mm"],
                "y_mm": fp["y_mm"],
                "drill_mm": round(drill, 4),
            })
    return holes


# ---------------------------------------------------------------------------
# Net / track / via summary
# ---------------------------------------------------------------------------

def _extract_net_info(tree: list) -> dict:
    """Summarise net information."""
    nets = _find_all(tree, "net")
    net_names = []
    for n in nets:
        if len(n) >= 3 and isinstance(n[2], str):
            net_names.append(n[2])
        elif len(n) >= 2 and isinstance(n[1], str):
            net_names.append(n[1])
    return {
        "net_count": len(nets),
        "net_names": net_names,
    }


def _extract_track_info(tree: list) -> dict:
    """Summarise track (segment) widths and count."""
    segments = _find_all(tree, "segment")
    widths: set[float] = set()
    for seg in segments:
        w = _find_value(seg, "width")
        if w is not None:
            widths.add(_to_float(w))
    return {
        "segment_count": len(segments),
        "track_widths_mm": sorted(widths),
    }


def _extract_via_info(tree: list) -> dict:
    """Summarise via sizes and count."""
    vias = _find_all(tree, "via")
    sizes: set[float] = set()
    drills: set[float] = set()
    for v in vias:
        s = _find_value(v, "size")
        d = _find_value(v, "drill")
        if s is not None:
            sizes.add(_to_float(s))
        if d is not None:
            drills.add(_to_float(d))
    return {
        "via_count": len(vias),
        "via_sizes_mm": sorted(sizes),
        "via_drills_mm": sorted(drills),
    }


# ---------------------------------------------------------------------------
# Layer summary
# ---------------------------------------------------------------------------

def _extract_layers(tree: list) -> list[dict]:
    """Extract the board layer stack-up."""
    layers_node = _find(tree, "layers")
    if not layers_node:
        return []
    result = []
    for child in layers_node[1:]:
        if isinstance(child, list) and len(child) >= 3:
            result.append({
                "id": child[0],
                "name": child[1],
                "type": child[2],
            })
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_kicad_pcb(file_content: str) -> dict:
    """Parse a .kicad_pcb file and return a structured summary.

    Args:
        file_content: The full text content of a .kicad_pcb file.

    Returns:
        A dict containing board dimensions, outline geometry, mounting holes,
        footprints, layers, net/track/via summaries, and general info.
    """
    tree = parse_sexpr(file_content)
    if not isinstance(tree, list) or not tree or tree[0] != "kicad_pcb":
        raise ValueError("Not a valid kicad_pcb file: expected top-level (kicad_pcb ...)")

    # General info
    general = _find(tree, "general")
    thickness = _to_float(_find_value(general, "thickness")) if general else 1.6

    # Version
    version = _find_value(tree, "version", "unknown")

    # Layers
    layers = _extract_layers(tree)
    copper_layers = [l for l in layers if l["type"] in ("signal", "power")]

    # Outline
    outline_segments = _extract_outline_segments(tree)
    bbox = _bounding_box_from_outline(outline_segments)

    # Footprints / components
    footprints = _extract_footprints(tree)
    mounting_holes = _extract_mounting_holes(footprints)

    # Nets, tracks, vias
    net_info = _extract_net_info(tree)
    track_info = _extract_track_info(tree)
    via_info = _extract_via_info(tree)

    return {
        "format_version": str(version),
        "board_thickness_mm": round(thickness, 4),
        "layer_count": len(copper_layers),
        "layers": layers,
        "board_outline": {
            "segment_count": len(outline_segments),
            "segments": outline_segments,
            "bounding_box": bbox,
        },
        "mounting_holes": mounting_holes,
        "footprints": _summarize_footprints(footprints),
        "footprint_details": footprints,
        "nets": net_info,
        "tracks": track_info,
        "vias": via_info,
    }


def _summarize_footprints(footprints: list[dict]) -> dict:
    """Produce a high-level footprint summary."""
    total = len(footprints)
    by_type: dict[str, int] = {}
    for fp in footprints:
        lib = fp["footprint"].split(":")[0] if ":" in fp["footprint"] else fp["footprint"]
        by_type[lib] = by_type.get(lib, 0) + 1
    return {
        "total_count": total,
        "by_library": by_type,
    }


def get_board_dimensions(parsed: dict) -> dict:
    """Extract just the key board dimensions from a parsed PCB dict.

    Returns a compact dict with board width, height, thickness, layer count,
    mounting holes, and component count.
    """
    bbox = parsed["board_outline"]["bounding_box"]
    return {
        "board_width_mm": bbox["width_mm"] if bbox else None,
        "board_height_mm": bbox["height_mm"] if bbox else None,
        "board_thickness_mm": parsed["board_thickness_mm"],
        "copper_layer_count": parsed["layer_count"],
        "mounting_holes": parsed["mounting_holes"],
        "component_count": parsed["footprints"]["total_count"],
        "net_count": parsed["nets"]["net_count"],
    }
