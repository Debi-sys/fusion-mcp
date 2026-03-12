"""
Keyboard case generation MCP tools.

Provides tools for creating keyboard case bodies in Fusion 360:
- create_keyboard_case: Full bottom case with mount-specific features
- create_keyboard_case_top: Top bezel/frame piece
"""

import json
import math
from .constants import (
    KEY_UNIT_CM, MountStyle, SwitchCutout,
    DEFAULT_WALL_THICKNESS_CM, DEFAULT_BOTTOM_THICKNESS_CM,
    DEFAULT_CASE_HEIGHT_CM, DEFAULT_CORNER_RADIUS_CM, DEFAULT_BEZEL_CM,
    SCREW_SIZES_CM, DEFAULT_STANDOFF_HEIGHT_CM,
    GASKET_CHANNEL_CM, GASKET_TAB_LENGTH_CM, GASKET_TAB_GAP_CM,
    USB_OPENINGS_CM, mm_to_cm,
)
from .layouts import get_layout, get_layout_bounds_cm, get_stabilizer_positions


def register_case_tools(mcp, _call):
    """Register keyboard case tools with the MCP server."""

    @mcp.tool()
    def create_keyboard_case(
        layout: str = "60%",
        kle_json: str = "",
        mount_style: str = "tray",
        typing_angle_deg: float = 6.0,
        bezel_front_mm: float = 4.0,
        bezel_back_mm: float = 6.0,
        bezel_left_mm: float = 5.0,
        bezel_right_mm: float = 5.0,
        wall_thickness_mm: float = 4.0,
        bottom_thickness_mm: float = 3.0,
        case_height_mm: float = 15.0,
        corner_radius_mm: float = 3.0,
        top_fillet_mm: float = 1.0,
        color: str = "",
        include_usb_cutout: bool = True,
    ) -> str:
        """
        Create a complete keyboard case bottom in Fusion 360.

        This generates the main case body with the chosen mount style. The case
        is a hollow shell with rounded corners and optional typing angle.

        Args:
            layout: Standard layout name: '60%', '65%', '75%', 'tkl', or 'full'.
            kle_json: Optional KLE JSON string for custom layouts (overrides layout param).
            mount_style: Mount type: 'tray' (standoffs), 'top' (screw tabs on rim),
                        'gasket' (gasket channels), 'sandwich', or 'bottom' (plate ledge).
            typing_angle_deg: Typing angle in degrees (0-12). Front stays at desk level.
            bezel_front_mm: Front bezel width in mm.
            bezel_back_mm: Back bezel width in mm (extra for USB connector).
            bezel_left_mm: Left bezel width in mm.
            bezel_right_mm: Right bezel width in mm.
            wall_thickness_mm: Case wall thickness in mm.
            bottom_thickness_mm: Case bottom plate thickness in mm.
            case_height_mm: Internal cavity height in mm.
            corner_radius_mm: Outer corner radius in mm.
            top_fillet_mm: Top edge fillet radius in mm (0 for sharp edges).
            color: Optional color name to apply (e.g., 'black', 'silver', 'navy').
            include_usb_cutout: Whether to add a USB-C cutout on the back wall.
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

        # Convert mm to cm
        bf = mm_to_cm(bezel_front_mm)
        bb = mm_to_cm(bezel_back_mm)
        bl = mm_to_cm(bezel_left_mm)
        br = mm_to_cm(bezel_right_mm)
        wall = mm_to_cm(wall_thickness_mm)
        bottom = mm_to_cm(bottom_thickness_mm)
        height = mm_to_cm(case_height_mm)
        cr = mm_to_cm(corner_radius_mm)
        fillet = mm_to_cm(top_fillet_mm)

        # Outer dimensions
        outer_w = key_width + bl + br
        outer_h = key_height + bf + bb
        total_height = height + bottom

        # Build operations list
        ops = []

        # Step 1: Create component
        ops.append({
            "command": "create_component",
            "params": {"name": f"Keyboard Case {layout_data.get('name', 'Custom')}"}
        })

        # Step 2: Create sketch for outer profile on XY plane
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Case Profile"}
        })

        # Step 3: Draw rounded rectangle for case outer profile
        # Use lines and arcs for rounded corners
        if cr > 0.01:
            ops.extend(_rounded_rect_ops(0, 0, outer_w, outer_h, cr))
        else:
            ops.append({
                "command": "draw_rectangle",
                "params": {"x1": 0, "y1": 0, "x2": outer_w, "y2": outer_h}
            })

        # Step 4: Extrude the case body
        ops.append({
            "command": "extrude",
            "params": {
                "distance": total_height,
                "operation": "new_body",
                "profile_index": 0,
            }
        })

        # Step 5: Shell the body (remove top face)
        ops.append({
            "command": "shell",
            "params": {
                "body": "0",
                "thickness": wall,
                "face_indices": [0],  # Top face (usually index 0 after extrude)
            }
        })

        # Step 6: Apply typing angle (rotate around front bottom edge)
        if typing_angle_deg > 0.1:
            ops.append({
                "command": "rotate_body",
                "params": {
                    "body": "0",
                    "axis": "X",
                    "angle": -typing_angle_deg,
                    "cx": 0, "cy": 0, "cz": 0,
                }
            })

        # Step 7: Mount-specific features
        mount = mount_style.lower()
        if mount == "tray":
            ops.extend(_tray_mount_ops(layout_data, bl, bf, bottom, wall))
        elif mount == "gasket":
            ops.extend(_gasket_mount_ops(outer_w, outer_h, bottom, height, wall))
        elif mount == "top":
            ops.extend(_top_mount_ops(outer_w, outer_h, total_height, wall))

        # Step 8: USB cutout
        if include_usb_cutout:
            usb = USB_OPENINGS_CM["usb_c"]
            usb_x = outer_w / 2
            usb_z = bottom + height * 0.4  # 40% up from internal bottom
            ops.append({
                "command": "create_sketch",
                "params": {"plane": "XZ", "name": "USB Cutout"}
            })
            ops.append({
                "command": "draw_center_rectangle",
                "params": {
                    "cx": usb_x,
                    "cy": usb_z,
                    "width": usb["width"],
                    "height": usb["height"],
                }
            })
            ops.append({
                "command": "extrude",
                "params": {
                    "distance": wall + 0.1,
                    "operation": "cut",
                    "profile_index": 0,
                }
            })

        # Step 9: Top fillet
        if fillet > 0.01:
            ops.append({
                "command": "fillet",
                "params": {
                    "body": "0",
                    "radius": fillet,
                    "edge_indices": [0, 1, 2, 3],  # Top edges
                }
            })

        # Step 10: Color
        if color:
            ops.append({
                "command": "apply_appearance",
                "params": {"body": "0", "appearance": color}
            })

        # Execute via batch if available, otherwise sequential
        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            # Fallback: execute operations one by one
            results = []
            for op in ops:
                r = _call(op["command"], op["params"])
                results.append(r)
            return json.dumps({
                "status": "created",
                "case": layout_data.get("name", "Custom"),
                "mount_style": mount_style,
                "outer_dimensions_cm": {
                    "width": round(outer_w, 2),
                    "depth": round(outer_h, 2),
                    "height": round(total_height, 2),
                },
                "typing_angle": typing_angle_deg,
                "operations": len(ops),
            }, indent=2)

        return result

    @mcp.tool()
    def create_keyboard_case_top(
        layout: str = "60%",
        kle_json: str = "",
        bezel_front_mm: float = 4.0,
        bezel_back_mm: float = 6.0,
        bezel_left_mm: float = 5.0,
        bezel_right_mm: float = 5.0,
        bezel_height_mm: float = 5.0,
        lip_depth_mm: float = 2.0,
        corner_radius_mm: float = 3.0,
        typing_angle_deg: float = 6.0,
        color: str = "",
    ) -> str:
        """
        Create a keyboard case top frame/bezel that sits on the bottom case.

        The top piece has a lip that nests inside the bottom case for alignment.
        The center is open for the switch plate / keys to be accessible.

        Args:
            layout: Standard layout name: '60%', '65%', '75%', 'tkl', or 'full'.
            kle_json: Optional KLE JSON for custom layouts.
            bezel_front_mm: Front bezel width in mm.
            bezel_back_mm: Back bezel width in mm.
            bezel_left_mm: Left bezel width in mm.
            bezel_right_mm: Right bezel width in mm.
            bezel_height_mm: Height of the top frame in mm.
            lip_depth_mm: Depth of the alignment lip in mm.
            corner_radius_mm: Corner radius in mm.
            typing_angle_deg: Must match bottom case typing angle.
            color: Optional appearance name.
        """
        if kle_json:
            from .kle_parser import parse_kle_json
            layout_data = parse_kle_json(kle_json)
        else:
            layout_data = get_layout(layout)

        bounds = get_layout_bounds_cm(layout_data)
        key_width = bounds["width_cm"]
        key_height = bounds["height_cm"]

        bf = mm_to_cm(bezel_front_mm)
        bb = mm_to_cm(bezel_back_mm)
        bl = mm_to_cm(bezel_left_mm)
        br = mm_to_cm(bezel_right_mm)
        bh = mm_to_cm(bezel_height_mm)
        lip = mm_to_cm(lip_depth_mm)
        cr = mm_to_cm(corner_radius_mm)

        outer_w = key_width + bl + br
        outer_h = key_height + bf + bb

        ops = []

        # Create component
        ops.append({
            "command": "create_component",
            "params": {"name": f"Case Top {layout_data.get('name', 'Custom')}"}
        })

        # Outer profile sketch
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Top Outer Profile"}
        })

        if cr > 0.01:
            ops.extend(_rounded_rect_ops(0, 0, outer_w, outer_h, cr))
        else:
            ops.append({
                "command": "draw_rectangle",
                "params": {"x1": 0, "y1": 0, "x2": outer_w, "y2": outer_h}
            })

        # Extrude outer
        ops.append({
            "command": "extrude",
            "params": {
                "distance": bh,
                "operation": "new_body",
                "profile_index": 0,
            }
        })

        # Inner cutout sketch (the key opening)
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Top Inner Cutout"}
        })
        inner_cr = max(cr - min(bl, bf, br, bb) * 0.5, 0.05)
        if inner_cr > 0.01:
            ops.extend(_rounded_rect_ops(bl, bf, bl + key_width, bf + key_height, inner_cr))
        else:
            ops.append({
                "command": "draw_rectangle",
                "params": {"x1": bl, "y1": bf, "x2": bl + key_width, "y2": bf + key_height}
            })

        # Cut through
        ops.append({
            "command": "extrude",
            "params": {
                "distance": bh + 0.1,
                "operation": "cut",
                "profile_index": 0,
            }
        })

        # Add alignment lip (extrude downward from bottom face)
        if lip > 0.01:
            ops.append({
                "command": "create_sketch",
                "params": {"plane": "XY", "name": "Lip Profile"}
            })
            # Lip is a frame slightly inset from outer edge
            lip_inset = 0.05  # 0.5mm gap for fit
            ops.append({
                "command": "draw_rectangle",
                "params": {
                    "x1": lip_inset, "y1": lip_inset,
                    "x2": outer_w - lip_inset, "y2": outer_h - lip_inset,
                }
            })
            ops.append({
                "command": "draw_rectangle",
                "params": {
                    "x1": bl - lip_inset, "y1": bf - lip_inset,
                    "x2": bl + key_width + lip_inset, "y2": bf + key_height + lip_inset,
                }
            })
            # Extrude the frame region downward
            ops.append({
                "command": "extrude",
                "params": {
                    "distance": -lip,
                    "operation": "join",
                    "profile_index": 0,
                }
            })

        # Typing angle
        if typing_angle_deg > 0.1:
            ops.append({
                "command": "rotate_body",
                "params": {
                    "body": "0",
                    "axis": "X",
                    "angle": -typing_angle_deg,
                    "cx": 0, "cy": 0, "cz": 0,
                }
            })

        if color:
            ops.append({
                "command": "apply_appearance",
                "params": {"body": "0", "appearance": color}
            })

        # Execute
        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            results = []
            for op in ops:
                r = _call(op["command"], op["params"])
                results.append(r)
            return json.dumps({
                "status": "created",
                "piece": "case_top",
                "layout": layout_data.get("name", "Custom"),
                "outer_dimensions_cm": {
                    "width": round(outer_w, 2),
                    "depth": round(outer_h, 2),
                    "height": round(bh, 2),
                },
                "operations": len(ops),
            }, indent=2)

        return result


def _rounded_rect_ops(x1, y1, x2, y2, radius):
    """Generate draw operations for a rounded rectangle using lines and arcs."""
    r = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    ops = []
    # Four lines (sides without corners)
    # Bottom
    ops.append({"command": "draw_line", "params": {
        "x1": x1 + r, "y1": y1, "x2": x2 - r, "y2": y1}})
    # Right
    ops.append({"command": "draw_line", "params": {
        "x1": x2, "y1": y1 + r, "x2": x2, "y2": y2 - r}})
    # Top
    ops.append({"command": "draw_line", "params": {
        "x1": x2 - r, "y1": y2, "x2": x1 + r, "y2": y2}})
    # Left
    ops.append({"command": "draw_line", "params": {
        "x1": x1, "y1": y2 - r, "x2": x1, "y2": y1 + r}})
    # Four corner arcs
    # Bottom-left
    ops.append({"command": "draw_arc", "params": {
        "cx": x1 + r, "cy": y1 + r, "radius": r,
        "start_angle": 180, "sweep_angle": 90}})
    # Bottom-right
    ops.append({"command": "draw_arc", "params": {
        "cx": x2 - r, "cy": y1 + r, "radius": r,
        "start_angle": 270, "sweep_angle": 90}})
    # Top-right
    ops.append({"command": "draw_arc", "params": {
        "cx": x2 - r, "cy": y2 - r, "radius": r,
        "start_angle": 0, "sweep_angle": 90}})
    # Top-left
    ops.append({"command": "draw_arc", "params": {
        "cx": x1 + r, "cy": y2 - r, "radius": r,
        "start_angle": 90, "sweep_angle": 90}})
    return ops


def _tray_mount_ops(layout_data, bezel_left, bezel_front, bottom_thickness, wall_thickness):
    """Generate operations for tray mount standoffs."""
    ops = []
    holes = layout_data.get("pcb_mounting_holes", [])
    if not holes:
        return ops

    screw = SCREW_SIZES_CM["M2"]
    standoff_h = DEFAULT_STANDOFF_HEIGHT_CM

    for i, hole in enumerate(holes):
        # Offset hole positions by bezel amount (holes are relative to PCB origin)
        hx = hole["x"] + bezel_left
        hy = hole["y"] + bezel_front

        # Create sketch for standoff
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": f"Standoff {i}"}
        })
        # Outer circle (standoff body)
        ops.append({
            "command": "draw_circle",
            "params": {"cx": hx, "cy": hy, "radius": screw["standoff_outer"] / 2}
        })
        # Extrude standoff upward from bottom
        ops.append({
            "command": "extrude",
            "params": {
                "distance": bottom_thickness + standoff_h,
                "operation": "join",
                "profile_index": 0,
            }
        })
        # Create sketch for screw hole
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": f"Screw Hole {i}"}
        })
        ops.append({
            "command": "draw_circle",
            "params": {"cx": hx, "cy": hy, "radius": screw["hole_diameter"] / 2}
        })
        # Cut the screw hole
        ops.append({
            "command": "extrude",
            "params": {
                "distance": bottom_thickness + standoff_h + 0.05,
                "operation": "cut",
                "profile_index": 0,
            }
        })

    return ops


def _gasket_mount_ops(outer_w, outer_h, bottom_thickness, cavity_height, wall_thickness):
    """Generate operations for gasket mount channels in the inner walls."""
    ops = []
    channel = GASKET_CHANNEL_CM
    # Channel is cut midway up the inner wall
    channel_z = bottom_thickness + cavity_height * 0.5

    # Sketch for left wall channel
    ops.append({
        "command": "create_sketch",
        "params": {"plane": "YZ", "name": "Gasket Channel Left"}
    })
    ops.append({
        "command": "draw_rectangle",
        "params": {
            "x1": wall_thickness * 0.3,
            "y1": channel_z - channel["width"] / 2,
            "x2": wall_thickness * 0.3 + channel["depth"],
            "y2": channel_z + channel["width"] / 2,
        }
    })
    ops.append({
        "command": "extrude",
        "params": {
            "distance": outer_h - wall_thickness * 2,
            "operation": "cut",
            "profile_index": 0,
        }
    })

    # Right wall channel
    ops.append({
        "command": "create_sketch",
        "params": {"plane": "YZ", "name": "Gasket Channel Right"}
    })
    ops.append({
        "command": "draw_rectangle",
        "params": {
            "x1": outer_w - wall_thickness * 0.3 - channel["depth"],
            "y1": channel_z - channel["width"] / 2,
            "x2": outer_w - wall_thickness * 0.3,
            "y2": channel_z + channel["width"] / 2,
        }
    })
    ops.append({
        "command": "extrude",
        "params": {
            "distance": outer_h - wall_thickness * 2,
            "operation": "cut",
            "profile_index": 0,
        }
    })

    # Front wall channel
    ops.append({
        "command": "create_sketch",
        "params": {"plane": "XZ", "name": "Gasket Channel Front"}
    })
    ops.append({
        "command": "draw_rectangle",
        "params": {
            "x1": wall_thickness,
            "y1": channel_z - channel["width"] / 2,
            "x2": outer_w - wall_thickness,
            "y2": channel_z + channel["width"] / 2,
        }
    })
    ops.append({
        "command": "extrude",
        "params": {
            "distance": channel["depth"],
            "operation": "cut",
            "profile_index": 0,
        }
    })

    # Back wall channel
    ops.append({
        "command": "create_sketch",
        "params": {"plane": "XZ", "name": "Gasket Channel Back"}
    })
    ops.append({
        "command": "draw_rectangle",
        "params": {
            "x1": wall_thickness,
            "y1": channel_z - channel["width"] / 2,
            "x2": outer_w - wall_thickness,
            "y2": channel_z + channel["width"] / 2,
        }
    })
    ops.append({
        "command": "extrude",
        "params": {
            "distance": channel["depth"],
            "operation": "cut",
            "profile_index": 0,
        }
    })

    return ops


def _top_mount_ops(outer_w, outer_h, total_height, wall_thickness):
    """Generate operations for top mount screw tab features."""
    ops = []
    # Add small screw tabs along the top rim
    tab_width = 0.6   # 6mm wide tabs
    tab_depth = 0.3   # 3mm deep extension inward
    screw = SCREW_SIZES_CM["M2.5"]

    # Place tabs at ~5cm intervals along each side
    positions = []
    # Left/right sides
    for y_frac in [0.25, 0.5, 0.75]:
        y_pos = outer_h * y_frac
        positions.append(("left", wall_thickness, y_pos))
        positions.append(("right", outer_w - wall_thickness, y_pos))
    # Front/back
    for x_frac in [0.25, 0.5, 0.75]:
        x_pos = outer_w * x_frac
        positions.append(("front", x_pos, wall_thickness))
        positions.append(("back", x_pos, outer_h - wall_thickness))

    for i, (side, x, y) in enumerate(positions):
        # Create a small tab sketch at the top
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": f"Mount Tab {i}"}
        })
        ops.append({
            "command": "draw_center_rectangle",
            "params": {
                "cx": x, "cy": y,
                "width": tab_width, "height": tab_width,
            }
        })
        ops.append({
            "command": "extrude",
            "params": {
                "distance": total_height,
                "operation": "join",
                "profile_index": 0,
            }
        })
        # Screw hole
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": f"Tab Hole {i}"}
        })
        ops.append({
            "command": "draw_circle",
            "params": {"cx": x, "cy": y, "radius": screw["hole_diameter"] / 2}
        })
        ops.append({
            "command": "extrude",
            "params": {
                "distance": total_height + 0.1,
                "operation": "cut",
                "profile_index": 0,
            }
        })

    return ops
