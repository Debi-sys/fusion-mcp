"""
KiCad PCB analysis MCP tools.

Exposes tools that let Claude read and analyse .kicad_pcb files,
extracting board dimensions, mounting holes, component placements,
layer stack-ups, and track/via information.
"""

import json
import os

from .parser import parse_kicad_pcb, get_board_dimensions


def register_kicad_tools(mcp):
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
