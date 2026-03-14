"""
Keyboard accessory MCP tools.

Provides tools for common keyboard case accessories:
- add_usb_cutout: USB connector opening
- add_mounting_posts: PCB mounting standoffs
- add_weight_pocket: Brass/steel weight pocket
- add_case_feet: Bumpon recesses or screw-in feet
- add_gasket_channels: Gasket strip channels
"""

import json
from .constants import (
    KEY_UNIT_CM, USB_OPENINGS_CM, DAUGHTERBOARD_HOLES_CM,
    SCREW_SIZES_CM, DEFAULT_STANDOFF_HEIGHT_CM,
    BUMPON_RECESS_CM, GASKET_CHANNEL_CM,
    GASKET_TAB_LENGTH_CM, GASKET_TAB_GAP_CM,
    mm_to_cm,
)
from .layouts import get_layout, get_layout_bounds_cm


def register_accessory_tools(mcp, _call):
    """Register keyboard accessory tools with the MCP server."""

    @mcp.tool()
    def add_usb_cutout(
        body: str = "0",
        connector_type: str = "usb_c",
        position_x_mm: float = -1,
        position_z_mm: float = -1,
        include_daughterboard_holes: bool = False,
        wall_face_index: int = -1,
    ) -> str:
        """
        Cut a USB connector opening in a keyboard case body.

        By default, centers the cutout on the back wall of the case.

        Args:
            body: Body name or index of the case to cut into.
            connector_type: 'usb_c' (9.2x3.4mm), 'usb_mini' (7.8x3.6mm), or 'usb_micro' (7.8x2.6mm).
            position_x_mm: X position in mm from left edge. -1 for auto-center.
            position_z_mm: Z position in mm from bottom. -1 for auto (40% up internal wall).
            include_daughterboard_holes: Add mounting holes for ai03 Unified Daughterboard.
            wall_face_index: Face index of the back wall. -1 to auto-detect.
        """
        usb_type = connector_type.lower()
        if usb_type not in USB_OPENINGS_CM:
            return json.dumps({"error": f"Unknown connector type '{connector_type}'. Use: usb_c, usb_mini, usb_micro"})

        usb = USB_OPENINGS_CM[usb_type]

        # Get body info to determine dimensions
        body_info = _call("measure_body", {"body": body})
        try:
            info = json.loads(body_info)
            body_w = info.get("size_cm", {}).get("x", 30)
            body_h = info.get("size_cm", {}).get("z", 1.5)
        except (json.JSONDecodeError, AttributeError):
            body_w = 30
            body_h = 1.5

        # Position
        if position_x_mm < 0:
            px = body_w / 2
        else:
            px = mm_to_cm(position_x_mm)

        if position_z_mm < 0:
            pz = body_h * 0.4
        else:
            pz = mm_to_cm(position_z_mm)

        ops = []

        # USB opening
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XZ", "name": "USB Cutout"}
        })
        ops.append({
            "command": "draw_center_rectangle",
            "params": {
                "cx": round(px, 4),
                "cy": round(pz, 4),
                "width": usb["width"],
                "height": usb["height"],
            }
        })
        ops.append({
            "command": "extrude",
            "params": {
                "distance": 0.5,  # Cut through wall
                "operation": "cut",
                "profile_index": 0,
            }
        })

        # Daughterboard holes
        if include_daughterboard_holes:
            ops.append({
                "command": "create_sketch",
                "params": {"plane": "XZ", "name": "Daughterboard Holes"}
            })
            for dh in DAUGHTERBOARD_HOLES_CM:
                ops.append({
                    "command": "draw_circle",
                    "params": {
                        "cx": round(px + dh["x"], 4),
                        "cy": round(pz + dh["y"], 4),
                        "radius": dh["diameter"] / 2,
                    }
                })
            ops.append({
                "command": "extrude",
                "params": {
                    "distance": 0.5,
                    "operation": "cut",
                    "profile_index": 0,
                }
            })

        # Execute
        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            for op in ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "cutout": connector_type,
                "position_cm": {"x": round(px, 2), "z": round(pz, 2)},
                "size_mm": {
                    "width": round(usb["width"] * 10, 1),
                    "height": round(usb["height"] * 10, 1),
                },
            }, indent=2)
        return result

    @mcp.tool()
    def add_mounting_posts(
        body: str = "0",
        layout: str = "60%",
        kle_json: str = "",
        custom_holes_mm: list = [],
        screw_size: str = "M2",
        standoff_height_mm: float = 5.0,
        use_heat_set_inserts: bool = False,
        bezel_left_mm: float = 5.0,
        bezel_front_mm: float = 4.0,
    ) -> str:
        """
        Add screw mounting posts/standoffs matching a PCB hole pattern.

        Creates cylindrical standoffs on the case floor with screw holes.
        Posts join to the existing case body.

        Args:
            body: Body name or index of the case.
            layout: Standard layout for PCB hole positions (ignored if custom_holes_mm is provided).
            kle_json: Optional KLE JSON (uses heuristic hole placement).
            custom_holes_mm: Custom hole positions as list of {x_mm, y_mm} dicts (e.g. from KiCad).
                             Coordinates are in mm from the board origin. When provided, layout
                             and kle_json are ignored. Bezel offsets are still applied.
            screw_size: 'M2', 'M2.5', or 'M3'.
            standoff_height_mm: Standoff height above case floor in mm.
            use_heat_set_inserts: Use heat-set insert diameter instead of tap diameter.
            bezel_left_mm: Left bezel to offset hole positions in mm.
            bezel_front_mm: Front bezel to offset hole positions in mm.
        """
        if custom_holes_mm:
            # Convert custom holes from mm to cm (same format as layout holes)
            holes = [{"x": mm_to_cm(h["x_mm"]), "y": mm_to_cm(h["y_mm"])} for h in custom_holes_mm]
        elif kle_json:
            from .kle_parser import parse_kle_json
            layout_data = parse_kle_json(kle_json)
            holes = layout_data.get("pcb_mounting_holes", [])
        else:
            layout_data = get_layout(layout)
            holes = layout_data.get("pcb_mounting_holes", [])

        if not holes:
            return json.dumps({"error": "No mounting holes found. Provide custom_holes_mm, a layout, or KLE JSON."})

        screw_key = screw_size.upper()
        if screw_key not in SCREW_SIZES_CM:
            return json.dumps({"error": f"Unknown screw size '{screw_size}'. Use: M2, M2.5, M3"})

        screw = SCREW_SIZES_CM[screw_key]
        sh = mm_to_cm(standoff_height_mm)
        bl = mm_to_cm(bezel_left_mm)
        bf = mm_to_cm(bezel_front_mm)

        hole_d = screw["insert_diameter"] if use_heat_set_inserts else screw["hole_diameter"]

        # Build batch circles for standoffs
        standoff_circles = []
        hole_circles = []
        for h in holes:
            hx = h["x"] + bl
            hy = h["y"] + bf
            standoff_circles.append({"cx": round(hx, 4), "cy": round(hy, 4), "radius": screw["standoff_outer"] / 2})
            hole_circles.append({"cx": round(hx, 4), "cy": round(hy, 4), "radius": hole_d / 2})

        ops = []

        # Draw and extrude standoffs
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Mounting Standoffs"}
        })

        batch_result = _call("batch_sketch_circles", {
            "circles": standoff_circles,
            "sketch": "Mounting Standoffs",
        })
        if "error" in batch_result and "Unknown command" in batch_result:
            for c in standoff_circles:
                ops.append({"command": "draw_circle", "params": c})

        ops.append({
            "command": "extrude",
            "params": {
                "distance": sh,
                "operation": "join",
                "profile_index": 0,
            }
        })

        # Screw holes
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Screw Holes"}
        })

        batch_result2 = _call("batch_sketch_circles", {
            "circles": hole_circles,
            "sketch": "Screw Holes",
        })
        if "error" in batch_result2 and "Unknown command" in batch_result2:
            for c in hole_circles:
                ops.append({"command": "draw_circle", "params": c})

        ops.append({
            "command": "extrude",
            "params": {
                "distance": sh + 0.1,
                "operation": "cut",
                "profile_index": 0,
            }
        })

        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            for op in ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "mounting_posts": len(holes),
                "screw_size": screw_size,
                "standoff_height_mm": standoff_height_mm,
            }, indent=2)
        return result

    @mcp.tool()
    def add_weight_pocket(
        body: str = "0",
        width_mm: float = 80.0,
        depth_mm: float = 30.0,
        pocket_depth_mm: float = 3.0,
        corner_radius_mm: float = 2.0,
        center_x_mm: float = -1,
        center_y_mm: float = -1,
        screw_holes: bool = True,
        screw_size: str = "M3",
    ) -> str:
        """
        Cut a pocket in the case bottom for a brass or stainless steel weight.

        The pocket is cut from the underside of the case. Add matching screw
        holes for securing the weight.

        Args:
            body: Body name or index.
            width_mm: Weight pocket width in mm.
            depth_mm: Weight pocket depth in mm.
            pocket_depth_mm: How deep to cut in mm (leave enough bottom material).
            corner_radius_mm: Pocket corner radius in mm.
            center_x_mm: X center in mm from left edge. -1 for auto-center.
            center_y_mm: Y center in mm from front edge. -1 for auto-center.
            screw_holes: Add screw holes in the corners.
            screw_size: 'M2', 'M2.5', or 'M3' for weight screws.
        """
        w = mm_to_cm(width_mm)
        d = mm_to_cm(depth_mm)
        pd = mm_to_cm(pocket_depth_mm)
        cr = mm_to_cm(corner_radius_mm)

        # Get body dimensions
        body_info = _call("measure_body", {"body": body})
        try:
            info = json.loads(body_info)
            bw = info.get("size_cm", {}).get("x", 30)
            bh = info.get("size_cm", {}).get("y", 10)
        except (json.JSONDecodeError, AttributeError):
            bw, bh = 30, 10

        cx = bw / 2 if center_x_mm < 0 else mm_to_cm(center_x_mm)
        cy = bh / 2 if center_y_mm < 0 else mm_to_cm(center_y_mm)

        ops = []

        # Pocket sketch (on bottom face, so we use XY plane)
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Weight Pocket"}
        })

        if cr > 0.01:
            from .case_tools import _rounded_rect_ops
            ops.extend(_rounded_rect_ops(cx - w/2, cy - d/2, cx + w/2, cy + d/2, cr))
        else:
            ops.append({
                "command": "draw_center_rectangle",
                "params": {"cx": round(cx, 4), "cy": round(cy, 4), "width": w, "height": d}
            })

        ops.append({
            "command": "extrude",
            "params": {
                "distance": pd,
                "operation": "cut",
                "profile_index": 0,
            }
        })

        # Screw holes in corners
        if screw_holes:
            screw_key = screw_size.upper()
            screw = SCREW_SIZES_CM.get(screw_key, SCREW_SIZES_CM["M3"])
            inset = max(cr, 0.3)

            ops.append({
                "command": "create_sketch",
                "params": {"plane": "XY", "name": "Weight Screw Holes"}
            })
            corners = [
                (cx - w/2 + inset, cy - d/2 + inset),
                (cx + w/2 - inset, cy - d/2 + inset),
                (cx - w/2 + inset, cy + d/2 - inset),
                (cx + w/2 - inset, cy + d/2 - inset),
            ]
            for hx, hy in corners:
                ops.append({
                    "command": "draw_circle",
                    "params": {"cx": round(hx, 4), "cy": round(hy, 4), "radius": screw["hole_diameter"] / 2}
                })
            ops.append({
                "command": "extrude",
                "params": {
                    "distance": pd + 0.5,  # Through pocket floor
                    "operation": "cut",
                    "profile_index": 0,
                }
            })

        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            for op in ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "weight_pocket": {
                    "width_mm": width_mm,
                    "depth_mm": depth_mm,
                    "pocket_depth_mm": pocket_depth_mm,
                    "center_cm": {"x": round(cx, 2), "y": round(cy, 2)},
                },
            }, indent=2)
        return result

    @mcp.tool()
    def add_case_feet(
        body: str = "0",
        bumpon_size: str = "medium",
        positions: list = [],
        auto_place: bool = True,
        screw_in_feet: bool = False,
    ) -> str:
        """
        Add bumpon recesses or screw-in foot holes to the case bottom.

        Args:
            body: Body name or index.
            bumpon_size: 'small' (8mm), 'medium' (12mm), or 'large' (16mm).
            positions: Manual positions as list of [x_mm, y_mm] pairs. Overrides auto_place.
            auto_place: Automatically place 4-6 feet based on case dimensions.
            screw_in_feet: Use threaded holes for screw-in feet instead of bumpon recesses.
        """
        bumpon_key = bumpon_size.lower()
        if bumpon_key not in BUMPON_RECESS_CM:
            return json.dumps({"error": f"Unknown bumpon size '{bumpon_size}'. Use: small, medium, large"})

        bumpon = BUMPON_RECESS_CM[bumpon_key]

        # Get body dimensions
        body_info = _call("measure_body", {"body": body})
        try:
            info = json.loads(body_info)
            bw = info.get("size_cm", {}).get("x", 30)
            bh = info.get("size_cm", {}).get("y", 10)
        except (json.JSONDecodeError, AttributeError):
            bw, bh = 30, 10

        # Determine positions
        if positions:
            foot_positions = [{"x": mm_to_cm(p[0]), "y": mm_to_cm(p[1])} for p in positions]
        elif auto_place:
            inset_x = max(bumpon["diameter"], bw * 0.08)
            inset_y = max(bumpon["diameter"], bh * 0.12)
            foot_positions = [
                {"x": inset_x, "y": inset_y},
                {"x": bw - inset_x, "y": inset_y},
                {"x": inset_x, "y": bh - inset_y},
                {"x": bw - inset_x, "y": bh - inset_y},
            ]
            # Add center pair for wider keyboards
            if bw > 25:
                foot_positions.extend([
                    {"x": bw / 2, "y": inset_y},
                    {"x": bw / 2, "y": bh - inset_y},
                ])
        else:
            return json.dumps({"error": "Provide positions or set auto_place=True"})

        ops = []

        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Case Feet"}
        })

        circles = []
        for fp in foot_positions:
            circles.append({
                "cx": round(fp["x"], 4),
                "cy": round(fp["y"], 4),
                "radius": bumpon["diameter"] / 2,
            })

        batch_result = _call("batch_sketch_circles", {
            "circles": circles,
            "sketch": "Case Feet",
        })
        if "error" in batch_result and "Unknown command" in batch_result:
            for c in circles:
                ops.append({"command": "draw_circle", "params": c})

        depth = bumpon["depth"] if not screw_in_feet else 0.5  # 5mm deep for screw holes
        ops.append({
            "command": "extrude",
            "params": {
                "distance": depth,
                "operation": "cut",
                "profile_index": 0,
            }
        })

        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            for op in ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "feet": len(foot_positions),
                "type": "screw_in" if screw_in_feet else f"bumpon_{bumpon_size}",
                "positions_cm": foot_positions,
            }, indent=2)
        return result

    @mcp.tool()
    def add_gasket_channels(
        body: str = "0",
        channel_width_mm: float = 2.5,
        channel_depth_mm: float = 1.5,
        segmented: bool = False,
        segment_length_mm: float = 10.0,
        segment_gap_mm: float = 5.0,
        wall_offset_fraction: float = 0.3,
    ) -> str:
        """
        Cut gasket strip channels into the inner walls of a keyboard case.

        Gasket channels run along the inner long sides (left/right walls)
        at approximately the plate seating height.

        Args:
            body: Body name or index of the case.
            channel_width_mm: Width of the gasket channel in mm.
            channel_depth_mm: Depth of the channel cut in mm.
            segmented: Use segmented (tabbed) channels instead of continuous.
            segment_length_mm: Length of each gasket segment in mm (if segmented).
            segment_gap_mm: Gap between segments in mm (if segmented).
            wall_offset_fraction: How far from inner wall surface to start the cut (0-1).
        """
        cw = mm_to_cm(channel_width_mm)
        cd = mm_to_cm(channel_depth_mm)

        body_info = _call("measure_body", {"body": body})
        try:
            info = json.loads(body_info)
            bw = info.get("size_cm", {}).get("x", 30)
            bh = info.get("size_cm", {}).get("y", 10)
            bz = info.get("size_cm", {}).get("z", 1.5)
        except (json.JSONDecodeError, AttributeError):
            bw, bh, bz = 30, 10, 1.5

        # Channel z-position (midway up the case wall)
        channel_z = bz * 0.5

        ops = []

        if not segmented:
            # Continuous channels on left and right inner walls
            for side_name, sketch_x in [("Left", 0.15), ("Right", bw - 0.15 - cd)]:
                ops.append({
                    "command": "create_sketch",
                    "params": {"plane": "YZ", "name": f"Gasket {side_name}"}
                })
                ops.append({
                    "command": "draw_rectangle",
                    "params": {
                        "x1": round(sketch_x, 4),
                        "y1": round(channel_z - cw / 2, 4),
                        "x2": round(sketch_x + cd, 4),
                        "y2": round(channel_z + cw / 2, 4),
                    }
                })
                ops.append({
                    "command": "extrude",
                    "params": {
                        "distance": bh * 0.8,
                        "operation": "cut",
                        "profile_index": 0,
                    }
                })
        else:
            seg_len = mm_to_cm(segment_length_mm)
            seg_gap = mm_to_cm(segment_gap_mm)
            usable_length = bh * 0.8
            y_start = bh * 0.1

            for side_name, sketch_x in [("Left", 0.15), ("Right", bw - 0.15 - cd)]:
                y_pos = y_start
                seg_idx = 0
                while y_pos + seg_len <= y_start + usable_length:
                    ops.append({
                        "command": "create_sketch",
                        "params": {"plane": "YZ", "name": f"Gasket {side_name} Seg{seg_idx}"}
                    })
                    ops.append({
                        "command": "draw_rectangle",
                        "params": {
                            "x1": round(sketch_x, 4),
                            "y1": round(channel_z - cw / 2, 4),
                            "x2": round(sketch_x + cd, 4),
                            "y2": round(channel_z + cw / 2, 4),
                        }
                    })
                    ops.append({
                        "command": "extrude",
                        "params": {
                            "distance": seg_len,
                            "operation": "cut",
                            "profile_index": 0,
                        }
                    })
                    y_pos += seg_len + seg_gap
                    seg_idx += 1

        result = _call("execute_operations_batch", {"operations": ops})
        if "error" in result and "Unknown command" in result:
            for op in ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "gasket_channels": "segmented" if segmented else "continuous",
                "channel_mm": {"width": channel_width_mm, "depth": channel_depth_mm},
            }, indent=2)
        return result
