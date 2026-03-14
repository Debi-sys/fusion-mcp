"""
Tests for the KiCad PCB parser.

Validates S-expression parsing, board outline extraction, footprint parsing,
mounting hole detection, and the public parse_kicad_pcb API.
"""

import json
import os
import sys
import unittest

# Ensure the mcp_server package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))

from kicad.parser import (
    parse_sexpr,
    parse_kicad_pcb,
    get_board_dimensions,
)

SAMPLE_PCB = os.path.join(os.path.dirname(__file__), "sample.kicad_pcb")


class TestSexprParser(unittest.TestCase):
    """Test the low-level S-expression tokenizer and parser."""

    def test_simple_atom(self):
        result = parse_sexpr("(hello world)")
        self.assertEqual(result, ["hello", "world"])

    def test_nested(self):
        result = parse_sexpr("(a (b c) d)")
        self.assertEqual(result, ["a", ["b", "c"], "d"])

    def test_quoted_string(self):
        result = parse_sexpr('(layer "F.Cu" signal)')
        self.assertEqual(result, ["layer", "F.Cu", "signal"])

    def test_numeric_atoms(self):
        result = parse_sexpr("(at 10.5 20.3)")
        self.assertEqual(result, ["at", "10.5", "20.3"])

    def test_empty(self):
        result = parse_sexpr("()")
        self.assertEqual(result, [])


class TestKicadPcbParser(unittest.TestCase):
    """Test parsing a sample .kicad_pcb file."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_PCB, "r", encoding="utf-8") as fh:
            cls.parsed = parse_kicad_pcb(fh.read())

    def test_format_version(self):
        self.assertEqual(self.parsed["format_version"], "20221018")

    def test_board_thickness(self):
        self.assertAlmostEqual(self.parsed["board_thickness_mm"], 1.6)

    def test_copper_layer_count(self):
        self.assertEqual(self.parsed["layer_count"], 2)

    def test_board_outline_bounding_box(self):
        bbox = self.parsed["board_outline"]["bounding_box"]
        self.assertIsNotNone(bbox)
        self.assertAlmostEqual(bbox["width_mm"], 105.0)
        self.assertAlmostEqual(bbox["height_mm"], 60.0)

    def test_outline_segment_count(self):
        self.assertEqual(self.parsed["board_outline"]["segment_count"], 4)

    def test_mounting_holes_detected(self):
        holes = self.parsed["mounting_holes"]
        self.assertEqual(len(holes), 4)
        refs = sorted(h["reference"] for h in holes)
        self.assertEqual(refs, ["H1", "H2", "H3", "H4"])
        for h in holes:
            self.assertAlmostEqual(h["drill_mm"], 3.2)

    def test_footprint_total_count(self):
        # 4 mounting holes + U1 + J1 + SW1 = 7
        self.assertEqual(self.parsed["footprints"]["total_count"], 7)

    def test_footprint_details_present(self):
        details = self.parsed["footprint_details"]
        refs = {fp["reference"] for fp in details}
        self.assertIn("U1", refs)
        self.assertIn("J1", refs)
        self.assertIn("SW1", refs)

    def test_u1_position(self):
        u1 = [fp for fp in self.parsed["footprint_details"] if fp["reference"] == "U1"]
        self.assertEqual(len(u1), 1)
        self.assertAlmostEqual(u1[0]["x_mm"], 50.0)
        self.assertAlmostEqual(u1[0]["y_mm"], 30.0)

    def test_net_count(self):
        self.assertEqual(self.parsed["nets"]["net_count"], 5)

    def test_net_names(self):
        names = self.parsed["nets"]["net_names"]
        self.assertIn("GND", names)
        self.assertIn("VCC", names)

    def test_track_info(self):
        tracks = self.parsed["tracks"]
        self.assertEqual(tracks["segment_count"], 3)
        self.assertIn(0.25, tracks["track_widths_mm"])
        self.assertIn(0.5, tracks["track_widths_mm"])

    def test_via_info(self):
        vias = self.parsed["vias"]
        self.assertEqual(vias["via_count"], 2)
        self.assertIn(0.8, vias["via_sizes_mm"])
        self.assertIn(0.6, vias["via_sizes_mm"])


class TestGetBoardDimensions(unittest.TestCase):
    """Test the compact board dimensions helper."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_PCB, "r", encoding="utf-8") as fh:
            cls.parsed = parse_kicad_pcb(fh.read())

    def test_dimensions(self):
        dims = get_board_dimensions(self.parsed)
        self.assertAlmostEqual(dims["board_width_mm"], 105.0)
        self.assertAlmostEqual(dims["board_height_mm"], 60.0)
        self.assertAlmostEqual(dims["board_thickness_mm"], 1.6)
        self.assertEqual(dims["copper_layer_count"], 2)
        self.assertEqual(dims["component_count"], 7)
        self.assertEqual(dims["net_count"], 5)
        self.assertEqual(len(dims["mounting_holes"]), 4)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_invalid_content_raises(self):
        with self.assertRaises(ValueError):
            parse_kicad_pcb("(not_kicad_pcb)")

    def test_empty_pcb(self):
        result = parse_kicad_pcb("(kicad_pcb)")
        self.assertEqual(result["layer_count"], 0)
        self.assertEqual(result["footprints"]["total_count"], 0)

    def test_gr_rect_outline(self):
        pcb = """(kicad_pcb (version 20221018)
            (gr_rect (start 0 0) (end 50 30) (layer "Edge.Cuts"))
        )"""
        result = parse_kicad_pcb(pcb)
        bbox = result["board_outline"]["bounding_box"]
        self.assertAlmostEqual(bbox["width_mm"], 50.0)
        self.assertAlmostEqual(bbox["height_mm"], 30.0)

    def test_kicad8_property_nodes(self):
        """KiCad 8+ uses (property "Reference" "U1") instead of (fp_text reference "U1")."""
        pcb = """(kicad_pcb (version 20240108)
            (footprint "Package:Test" (layer "F.Cu") (at 10 20)
                (property "Reference" "U1")
                (property "Value" "TestChip")
            )
        )"""
        result = parse_kicad_pcb(pcb)
        fp = result["footprint_details"][0]
        self.assertEqual(fp["reference"], "U1")
        self.assertEqual(fp["value"], "TestChip")


class TestAbsolutePadPositions(unittest.TestCase):
    """Test that pad positions include board-absolute coordinates."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_PCB, "r", encoding="utf-8") as fh:
            cls.parsed = parse_kicad_pcb(fh.read())

    def test_zero_rotation_pad_abs_position(self):
        """Mounting hole at (5,5) with pad at (0,0) -> abs should be (5,5)."""
        h1 = [fp for fp in self.parsed["footprint_details"] if fp["reference"] == "H1"][0]
        pad = h1["pads"][0]
        self.assertAlmostEqual(pad["abs_x_mm"], 5.0)
        self.assertAlmostEqual(pad["abs_y_mm"], 5.0)

    def test_zero_rotation_offset_pad(self):
        """U1 at (50,30) with pad1 at (-4,-2.4) -> abs should be (46,-27.6)."""
        u1 = [fp for fp in self.parsed["footprint_details"] if fp["reference"] == "U1"][0]
        pad1 = u1["pads"][0]
        self.assertAlmostEqual(pad1["abs_x_mm"], 46.0, places=2)
        self.assertAlmostEqual(pad1["abs_y_mm"], 27.6, places=2)

    def test_rotated_footprint_pad(self):
        """J1 at (52,0) with 180 deg rotation. Pad A1 at (-3.25,4.32).
        Rotated 180: abs = (52 - (-3.25)*cos180 - 4.32*sin180, 0 + (-3.25)*sin180 + 4.32*cos180)
                    = (52 - 3.25, 0 - 4.32) = (55.25, -4.32)."""
        j1 = [fp for fp in self.parsed["footprint_details"] if fp["reference"] == "J1"][0]
        pad_a1 = [p for p in j1["pads"] if p["number"] == "A1"][0]
        self.assertAlmostEqual(pad_a1["abs_x_mm"], 55.25, places=2)
        self.assertAlmostEqual(pad_a1["abs_y_mm"], -4.32, places=2)

    def test_all_pads_have_abs_fields(self):
        """All pads with position data should have abs_x_mm and abs_y_mm."""
        for fp in self.parsed["footprint_details"]:
            for pad in fp["pads"]:
                if "x_mm" in pad:
                    self.assertIn("abs_x_mm", pad, f"Missing abs_x_mm in {fp['reference']} pad {pad.get('number')}")
                    self.assertIn("abs_y_mm", pad, f"Missing abs_y_mm in {fp['reference']} pad {pad.get('number')}")


if __name__ == "__main__":
    unittest.main()
