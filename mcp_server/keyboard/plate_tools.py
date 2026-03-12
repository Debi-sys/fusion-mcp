"""
Switch plate generation MCP tools.

Provides tools for creating keyboard switch plates in Fusion 360:
- create_switch_plate: Full plate with switch cutouts and stabilizer cutouts
- create_plate_from_kle: Convenience wrapper for KLE JSON input
"""

import json
from .constants import (
    KEY_UNIT_CM, SwitchCutout, SWITCH_CUTOUT_CM,
    STABILIZER_CUTOUT_CM, STABILIZER_SPACING_CM, STABILIZER_WIRE_SLOT_CM,
    DEFAULT_PLATE_THICKNESS_CM, DEFAULT_PLATE_MARGIN_CM,
    mm_to_cm,
)
from .layouts import get_layout, get_layout_bounds_cm, get_stabilizer_positions


def register_plate_tools(mcp, _call):
    """Register keyboard plate tools with the MCP server."""

    @mcp.tool()
    def create_switch_plate(
        layout: str = "60%",
        kle_json: str = "",
        thickness_mm: float = 1.5,
        cutout_type: str = "cherry_mx",
        include_stabilizer_cutouts: bool = True,
        corner_radius_mm: float = 2.0,
        plate_margin_mm: float = 0.5,
        flex_cuts: bool = False,
        material_appearance: str = "",
    ) -> str:
        """
        Create a keyboard switch plate with cutouts for all keys.

        The plate is a flat sheet with precisely-sized holes for each switch.
        Standard plates are 1.5mm thick for Cherry MX switches.

        Args:
            layout: Standard layout: '60%', '65%', '75%', 'tkl', or 'full'.
            kle_json: Optional KLE JSON for custom layouts (overrides layout param).
            thickness_mm: Plate thickness in mm (1.5mm standard for MX, 1.2mm for Choc).
            cutout_type: Switch type: 'cherry_mx' (14mm), 'alps' (15.5x12.8mm), 'kailh_choc' (13.5mm).
            include_stabilizer_cutouts: Add cutouts for stabilizers on wide keys.
            corner_radius_mm: Plate outer corner radius in mm.
            plate_margin_mm: Extra margin around the key area on each side in mm.
            flex_cuts: Add flex cuts between rows for a softer typing feel.
            material_appearance: Optional appearance (e.g., 'Aluminum', 'Steel', 'Brass').
        """
        # Resolve layout
        if kle_json:
            from .kle_parser import parse_kle_json
            layout_data = parse_kle_json(kle_json)
        else:
            layout_data = get_layout(layout)

        bounds = get_layout_bounds_cm(layout_data)
        key_width = bounds["width_cm"]
        key_height = bounds["height_cm"]

        thickness = mm_to_cm(thickness_mm)
        cr = mm_to_cm(corner_radius_mm)
        margin = mm_to_cm(plate_margin_mm)

        plate_w = key_width + margin * 2
        plate_h = key_height + margin * 2

        # Get cutout dimensions
        try:
            cutout_enum = SwitchCutout(cutout_type.lower())
        except ValueError:
            cutout_enum = SwitchCutout.CHERRY_MX
        cutout = SWITCH_CUTOUT_CM[cutout_enum]

        keys = layout_data.get("keys", [])
        ops = []

        # Step 1: Create component
        ops.append({
            "command": "create_component",
            "params": {"name": f"Switch Plate {layout_data.get('name', 'Custom')}"}
        })

        # Step 2: Create plate sketch
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Plate Outline"}
        })

        # Step 3: Draw plate outline
        if cr > 0.01:
            from .case_tools import _rounded_rect_ops
            ops.extend(_rounded_rect_ops(0, 0, plate_w, plate_h, cr))
        else:
            ops.append({
                "command": "draw_rectangle",
                "params": {"x1": 0, "y1": 0, "x2": plate_w, "y2": plate_h}
            })

        # Step 4: Extrude plate
        ops.append({
            "command": "extrude",
            "params": {
                "distance": thickness,
                "operation": "new_body",
                "profile_index": 0,
            }
        })

        # Step 5: Batch-draw all switch cutouts
        # Try batch command first; prepare rectangles
        cutout_rects = []
        for key in keys:
            # Center of key in plate coordinates
            cx = key["x"] * KEY_UNIT_CM + (key["w"] * KEY_UNIT_CM) / 2 + margin
            cy = key["y"] * KEY_UNIT_CM + (key["h"] * KEY_UNIT_CM) / 2 + margin

            cutout_rects.append({
                "cx": round(cx, 4),
                "cy": round(cy, 4),
                "width": cutout["width"],
                "height": cutout["height"],
            })

        # Try batch sketch rectangles
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Switch Cutouts"}
        })

        batch_result = _call("batch_sketch_rectangles", {
            "rectangles": cutout_rects,
            "sketch": "Switch Cutouts",
        })

        if "error" in batch_result and "Unknown command" in batch_result:
            # Fallback: draw rectangles one by one
            for rect in cutout_rects:
                ops.append({
                    "command": "draw_center_rectangle",
                    "params": rect,
                })
        else:
            # Batch worked, just need the cut extrude
            pass

        # Step 6: Cut-extrude all cutouts through the plate
        ops.append({
            "command": "extrude",
            "params": {
                "distance": thickness + 0.05,
                "operation": "cut",
                "profile_index": -1,  # All inner profiles
            }
        })

        # Step 7: Stabilizer cutouts
        if include_stabilizer_cutouts:
            stab_rects = []
            stab_wire_slots = []

            stab_positions = get_stabilizer_positions(layout_data)
            for stab in stab_positions:
                sx = stab["x_cm"] + margin
                sy = stab["y_cm"] + margin
                spacing = stab["spacing_cm"]

                # Left stabilizer cutout
                stab_rects.append({
                    "cx": round(sx - spacing / 2, 4),
                    "cy": round(sy, 4),
                    "width": STABILIZER_CUTOUT_CM["width"],
                    "height": STABILIZER_CUTOUT_CM["height"],
                })
                # Right stabilizer cutout
                stab_rects.append({
                    "cx": round(sx + spacing / 2, 4),
                    "cy": round(sy, 4),
                    "width": STABILIZER_CUTOUT_CM["width"],
                    "height": STABILIZER_CUTOUT_CM["height"],
                })
                # Wire slot connecting the two
                stab_wire_slots.append({
                    "cx": round(sx, 4),
                    "cy": round(sy + STABILIZER_CUTOUT_CM["height"] / 2 - STABILIZER_WIRE_SLOT_CM["height"] / 2, 4),
                    "width": round(spacing + STABILIZER_CUTOUT_CM["width"], 4),
                    "height": STABILIZER_WIRE_SLOT_CM["height"],
                })

            if stab_rects:
                ops.append({
                    "command": "create_sketch",
                    "params": {"plane": "XY", "name": "Stabilizer Cutouts"}
                })
                # Try batch, fallback to individual
                batch_stab = _call("batch_sketch_rectangles", {
                    "rectangles": stab_rects + stab_wire_slots,
                    "sketch": "Stabilizer Cutouts",
                })
                if "error" in batch_stab and "Unknown command" in batch_stab:
                    for rect in stab_rects + stab_wire_slots:
                        ops.append({
                            "command": "draw_center_rectangle",
                            "params": rect,
                        })
                ops.append({
                    "command": "extrude",
                    "params": {
                        "distance": thickness + 0.05,
                        "operation": "cut",
                        "profile_index": -1,
                    }
                })

        # Step 8: Flex cuts (horizontal slots between rows)
        if flex_cuts and len(keys) > 0:
            ops.append({
                "command": "create_sketch",
                "params": {"plane": "XY", "name": "Flex Cuts"}
            })
            # Determine row y-positions
            row_ys = sorted(set(k["y"] for k in keys))
            for i in range(len(row_ys) - 1):
                # Cut between rows
                cut_y = (row_ys[i] + row_ys[i + 1]) / 2 * KEY_UNIT_CM + margin
                # Alternating flex cut pattern
                x_start = margin + 0.5
                while x_start < plate_w - margin - 1.0:
                    slot_len = min(1.5, plate_w - margin - x_start - 0.5)
                    if slot_len > 0.3:
                        ops.append({
                            "command": "draw_slot",
                            "params": {
                                "x1": round(x_start, 4),
                                "y1": round(cut_y, 4),
                                "x2": round(x_start + slot_len, 4),
                                "y2": round(cut_y, 4),
                                "width": 0.08,  # 0.8mm wide flex cuts
                            }
                        })
                    x_start += 2.5  # 25mm spacing

            ops.append({
                "command": "extrude",
                "params": {
                    "distance": thickness + 0.05,
                    "operation": "cut",
                    "profile_index": -1,
                }
            })

        # Step 9: Material appearance
        if material_appearance:
            ops.append({
                "command": "apply_appearance",
                "params": {"body": "0", "appearance": material_appearance}
            })

        # Execute all operations
        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            results = []
            for op in ops:
                r = _call(op["command"], op["params"])
                results.append(r)
            return json.dumps({
                "status": "created",
                "plate": layout_data.get("name", "Custom"),
                "dimensions_cm": {
                    "width": round(plate_w, 2),
                    "depth": round(plate_h, 2),
                    "thickness": thickness,
                },
                "switch_cutouts": len(cutout_rects),
                "stabilizer_cutouts": len(stab_rects) if include_stabilizer_cutouts else 0,
                "operations": len(ops),
            }, indent=2)

        return result

    @mcp.tool()
    def create_plate_from_kle(
        kle_json: str = "",
        thickness_mm: float = 1.5,
        cutout_type: str = "cherry_mx",
        include_stabilizer_cutouts: bool = True,
        material_appearance: str = "",
    ) -> str:
        """
        Create a switch plate from a Keyboard Layout Editor JSON string.

        Paste the raw JSON from keyboard-layout-editor.com to generate
        a custom plate with switch cutouts matching your exact layout.

        Args:
            kle_json: KLE JSON string (the raw array format from keyboard-layout-editor.com).
            thickness_mm: Plate thickness in mm.
            cutout_type: 'cherry_mx', 'alps', or 'kailh_choc'.
            include_stabilizer_cutouts: Auto-detect and cut stabilizer openings.
            material_appearance: Optional appearance (e.g., 'Aluminum', 'Brass').
        """
        if not kle_json:
            return json.dumps({"error": "kle_json is required. Paste the JSON from keyboard-layout-editor.com."})

        return create_switch_plate(
            kle_json=kle_json,
            thickness_mm=thickness_mm,
            cutout_type=cutout_type,
            include_stabilizer_cutouts=include_stabilizer_cutouts,
            material_appearance=material_appearance,
        )
