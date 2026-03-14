"""
KiCad PCB analysis MCP tools.

Exposes tools that let Claude read and analyse .kicad_pcb files,
extracting board dimensions, mounting holes, component placements,
layer stack-ups, and track/via information.

Also provides a create_pcb_enclosure tool that generates a generic
enclosure in Fusion 360 directly from KiCad-extracted board data.
"""

import json
import os

from .parser import parse_kicad_pcb, get_board_dimensions


def register_kicad_tools(mcp, _call=None):
    """Register KiCad PCB tools with the MCP server."""

    @mcp.tool()
    def parse_kicad_pcb_file(file_path: str) -> str:
        """
        Parse a KiCad PCB file (.kicad_pcb) and return a full structured summary.

        Extracts board outline and dimensions, layer stack-up, mounting holes,
        component footprints and positions, nets, track widths, and via sizes.

        Args:
            file_path: Absolute path to a .kicad_pcb file on disk.
        """
        if not os.path.isfile(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        if not file_path.lower().endswith(".kicad_pcb"):
            return json.dumps({"error": "File must have a .kicad_pcb extension"})

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return json.dumps({"error": f"Cannot read file: {exc}"})

        try:
            result = parse_kicad_pcb(content)
        except Exception as exc:
            return json.dumps({"error": f"Parse error: {exc}"})

        # Drop the heavy per-footprint pad details from the default view
        # to keep the response manageable for the LLM.
        light = dict(result)
        light.pop("footprint_details", None)
        return json.dumps(light, indent=2)

    @mcp.tool()
    def get_kicad_board_dimensions(file_path: str) -> str:
        """
        Get key board dimensions from a KiCad PCB file.

        Returns a compact summary: board width, height, thickness, copper layer
        count, mounting hole positions, component count, and net count.

        Args:
            file_path: Absolute path to a .kicad_pcb file on disk.
        """
        if not os.path.isfile(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        if not file_path.lower().endswith(".kicad_pcb"):
            return json.dumps({"error": "File must have a .kicad_pcb extension"})

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return json.dumps({"error": f"Cannot read file: {exc}"})

        try:
            parsed = parse_kicad_pcb(content)
            dims = get_board_dimensions(parsed)
        except Exception as exc:
            return json.dumps({"error": f"Parse error: {exc}"})

        return json.dumps(dims, indent=2)

    @mcp.tool()
    def get_kicad_footprint_details(file_path: str, reference: str = "") -> str:
        """
        Get detailed footprint/component information from a KiCad PCB file.

        Lists all footprints with their positions, pad counts, and pad details.
        Optionally filter to a single component by its reference designator
        (e.g. 'U1', 'J1', 'SW1').

        Args:
            file_path: Absolute path to a .kicad_pcb file on disk.
            reference: Optional reference designator to filter (e.g. 'U1').
                       Leave empty to list all components.
        """
        if not os.path.isfile(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        if not file_path.lower().endswith(".kicad_pcb"):
            return json.dumps({"error": "File must have a .kicad_pcb extension"})

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return json.dumps({"error": f"Cannot read file: {exc}"})

        try:
            parsed = parse_kicad_pcb(content)
        except Exception as exc:
            return json.dumps({"error": f"Parse error: {exc}"})

        details = parsed["footprint_details"]
        if reference:
            details = [fp for fp in details if fp["reference"] == reference]
            if not details:
                return json.dumps({"error": f"No footprint with reference '{reference}' found"})

        return json.dumps(details, indent=2)

    @mcp.tool()
    def get_kicad_mounting_holes(file_path: str) -> str:
        """
        Get mounting hole positions and sizes from a KiCad PCB file.

        Identifies footprints that are mounting holes (by name pattern or
        NPTH pad type) and returns their positions and drill sizes.

        Args:
            file_path: Absolute path to a .kicad_pcb file on disk.
        """
        if not os.path.isfile(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        if not file_path.lower().endswith(".kicad_pcb"):
            return json.dumps({"error": "File must have a .kicad_pcb extension"})

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return json.dumps({"error": f"Cannot read file: {exc}"})

        try:
            parsed = parse_kicad_pcb(content)
        except Exception as exc:
            return json.dumps({"error": f"Parse error: {exc}"})

        return json.dumps(parsed["mounting_holes"], indent=2)

    @mcp.tool()
    def get_kicad_net_info(file_path: str) -> str:
        """
        Get net (electrical connection) information from a KiCad PCB file.

        Returns net count, net names, track segment counts, track widths,
        via counts, and via sizes.

        Args:
            file_path: Absolute path to a .kicad_pcb file on disk.
        """
        if not os.path.isfile(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        if not file_path.lower().endswith(".kicad_pcb"):
            return json.dumps({"error": "File must have a .kicad_pcb extension"})

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return json.dumps({"error": f"Cannot read file: {exc}"})

        try:
            parsed = parse_kicad_pcb(content)
        except Exception as exc:
            return json.dumps({"error": f"Parse error: {exc}"})

        return json.dumps({
            "nets": parsed["nets"],
            "tracks": parsed["tracks"],
            "vias": parsed["vias"],
        }, indent=2)

    if _call is None:
        return

    @mcp.tool()
    def create_pcb_enclosure(
        file_path: str = "",
        board_width_mm: float = 0,
        board_height_mm: float = 0,
        board_thickness_mm: float = 1.6,
        mounting_holes_mm: list = [],
        wall_thickness_mm: float = 2.0,
        bottom_thickness_mm: float = 2.0,
        clearance_mm: float = 10.0,
        bezel_mm: float = 2.0,
        corner_radius_mm: float = 2.0,
        standoff_height_mm: float = 5.0,
        screw_size: str = "M3",
        include_lid: bool = False,
        color: str = "",
    ) -> str:
        """
        Create a generic PCB enclosure in Fusion 360.

        Builds a simple box enclosure sized to fit a PCB, with standoffs at
        mounting hole positions. Works with any PCB, not just keyboards.

        Dimensions can be provided directly, or extracted automatically from
        a KiCad PCB file.

        Args:
            file_path: Path to a .kicad_pcb file. If provided, board dimensions
                       and mounting holes are extracted automatically (overrides
                       manual board_width_mm, board_height_mm, mounting_holes_mm).
            board_width_mm: Board width in mm (ignored if file_path is provided).
            board_height_mm: Board height in mm (ignored if file_path is provided).
            board_thickness_mm: Board thickness in mm (default 1.6mm).
            mounting_holes_mm: Mounting hole positions as list of {x_mm, y_mm}
                               dicts in mm from board origin. Ignored if file_path
                               is provided.
            wall_thickness_mm: Enclosure wall thickness in mm.
            bottom_thickness_mm: Enclosure bottom plate thickness in mm.
            clearance_mm: Height clearance above the PCB for components in mm.
            bezel_mm: Gap between board edge and inner wall in mm.
            corner_radius_mm: Outer corner radius in mm.
            standoff_height_mm: Height of standoffs above the case floor in mm.
            screw_size: Screw size for standoffs: 'M2', 'M2.5', or 'M3'.
            include_lid: Create a matching lid piece.
            color: Optional color name for the enclosure.
        """
        # Resolve board dimensions from KiCad file or manual input
        holes = []
        if file_path:
            if not os.path.isfile(file_path):
                return json.dumps({"error": f"File not found: {file_path}"})
            if not file_path.lower().endswith(".kicad_pcb"):
                return json.dumps({"error": "File must have a .kicad_pcb extension"})
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                parsed = parse_kicad_pcb(content)
                dims = get_board_dimensions(parsed)
            except Exception as exc:
                return json.dumps({"error": f"Parse error: {exc}"})

            board_width_mm = dims["board_width_mm"] or board_width_mm
            board_height_mm = dims["board_height_mm"] or board_height_mm
            board_thickness_mm = dims.get("board_thickness_mm", board_thickness_mm)
            holes = [{"x_mm": h["x_mm"], "y_mm": h["y_mm"]} for h in parsed["mounting_holes"]]
        else:
            holes = mounting_holes_mm

        if board_width_mm <= 0 or board_height_mm <= 0:
            return json.dumps({"error": "Board dimensions must be positive. Provide file_path or board_width_mm/board_height_mm."})

        # Convert to cm (Fusion 360 internal units)
        def mm2cm(v):
            return v / 10.0

        bw = mm2cm(board_width_mm)
        bh = mm2cm(board_height_mm)
        wall = mm2cm(wall_thickness_mm)
        bottom = mm2cm(bottom_thickness_mm)
        clearance = mm2cm(clearance_mm)
        bezel = mm2cm(bezel_mm)
        cr = mm2cm(corner_radius_mm)
        sh = mm2cm(standoff_height_mm)

        # Enclosure outer dimensions
        outer_w = bw + 2 * (bezel + wall)
        outer_h = bh + 2 * (bezel + wall)
        inner_height = sh + mm2cm(board_thickness_mm) + clearance
        total_height = inner_height + bottom

        # Import rounded rect helper
        import sys
        parent_dir = os.path.join(os.path.dirname(__file__), "..")
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from keyboard.case_tools import _rounded_rect_ops
        from keyboard.constants import SCREW_SIZES_CM

        screw_key = screw_size.upper()
        if screw_key not in SCREW_SIZES_CM:
            return json.dumps({"error": f"Unknown screw size '{screw_size}'. Use: M2, M2.5, M3"})
        screw = SCREW_SIZES_CM[screw_key]

        ops = []

        # Step 1: Create component
        ops.append({
            "command": "create_component",
            "params": {"name": "PCB Enclosure"}
        })

        # Step 2: Sketch outer profile
        ops.append({
            "command": "create_sketch",
            "params": {"plane": "XY", "name": "Enclosure Profile"}
        })

        if cr > 0.01:
            ops.extend(_rounded_rect_ops(0, 0, outer_w, outer_h, cr))
        else:
            ops.append({
                "command": "draw_rectangle",
                "params": {"x1": 0, "y1": 0, "x2": outer_w, "y2": outer_h}
            })

        # Step 3: Extrude case body
        ops.append({
            "command": "extrude",
            "params": {
                "distance": total_height,
                "operation": "new_body",
                "profile_index": 0,
            }
        })

        # Step 4: Shell (remove top face)
        ops.append({
            "command": "shell",
            "params": {
                "body": "0",
                "thickness": wall,
                "face_indices": [0],
            }
        })

        # Step 5: Mounting standoffs (if holes provided)
        if holes:
            for i, hole in enumerate(holes):
                hx = mm2cm(hole["x_mm"]) + wall + bezel
                hy = mm2cm(hole["y_mm"]) + wall + bezel

                ops.append({
                    "command": "create_sketch",
                    "params": {"plane": "XY", "name": f"Standoff {i}"}
                })
                ops.append({
                    "command": "draw_circle",
                    "params": {"cx": round(hx, 4), "cy": round(hy, 4),
                               "radius": screw["standoff_outer"] / 2}
                })
                ops.append({
                    "command": "extrude",
                    "params": {
                        "distance": bottom + sh,
                        "operation": "join",
                        "profile_index": 0,
                    }
                })
                # Screw hole
                ops.append({
                    "command": "create_sketch",
                    "params": {"plane": "XY", "name": f"Screw Hole {i}"}
                })
                ops.append({
                    "command": "draw_circle",
                    "params": {"cx": round(hx, 4), "cy": round(hy, 4),
                               "radius": screw["hole_diameter"] / 2}
                })
                ops.append({
                    "command": "extrude",
                    "params": {
                        "distance": bottom + sh + 0.05,
                        "operation": "cut",
                        "profile_index": 0,
                    }
                })

        # Step 6: Top fillet
        ops.append({
            "command": "fillet",
            "params": {
                "body": "0",
                "radius": min(cr, 0.1) if cr > 0.01 else 0.05,
                "edge_indices": [0, 1, 2, 3],
            }
        })

        # Step 7: Color
        if color:
            ops.append({
                "command": "apply_appearance",
                "params": {"body": "0", "appearance": color}
            })

        # Step 8: Optional lid
        lid_ops = []
        if include_lid:
            lid_ops.append({
                "command": "create_component",
                "params": {"name": "PCB Enclosure Lid"}
            })
            lid_ops.append({
                "command": "create_sketch",
                "params": {"plane": "XY", "name": "Lid Profile"}
            })
            lid_thickness = wall
            lip = 0.05  # 0.5mm lip inset
            if cr > 0.01:
                lid_ops.extend(_rounded_rect_ops(0, 0, outer_w, outer_h, cr))
            else:
                lid_ops.append({
                    "command": "draw_rectangle",
                    "params": {"x1": 0, "y1": 0, "x2": outer_w, "y2": outer_h}
                })
            lid_ops.append({
                "command": "extrude",
                "params": {
                    "distance": lid_thickness,
                    "operation": "new_body",
                    "profile_index": 0,
                }
            })
            # Lip that nests inside the enclosure
            lid_ops.append({
                "command": "create_sketch",
                "params": {"plane": "XY", "name": "Lid Lip"}
            })
            lid_ops.append({
                "command": "draw_rectangle",
                "params": {
                    "x1": wall + lip, "y1": wall + lip,
                    "x2": outer_w - wall - lip, "y2": outer_h - wall - lip,
                }
            })
            lid_ops.append({
                "command": "extrude",
                "params": {
                    "distance": -wall * 0.5,
                    "operation": "join",
                    "profile_index": 0,
                }
            })
            if color:
                lid_ops.append({
                    "command": "apply_appearance",
                    "params": {"body": "1", "appearance": color}
                })

        all_ops = ops + lid_ops

        # Execute
        result = _call("execute_operations_batch", {"operations": all_ops})
        if "error" in result and "Unknown command" in result:
            for op in all_ops:
                _call(op["command"], op["params"])
            return json.dumps({
                "status": "created",
                "enclosure": {
                    "outer_width_mm": round(outer_w * 10, 1),
                    "outer_height_mm": round(outer_h * 10, 1),
                    "outer_depth_mm": round(total_height * 10, 1),
                    "board_mm": {
                        "width": board_width_mm,
                        "height": board_height_mm,
                    },
                    "standoffs": len(holes),
                    "screw_size": screw_size,
                    "include_lid": include_lid,
                },
            }, indent=2)
        return result
