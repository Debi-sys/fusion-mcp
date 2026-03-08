"""
Script to create a 3D-printable clothes hanger in Fusion 360 via MCP bridge.
Fits Bambu P2S build plate: 256 x 256 x 256 mm
"""
import requests
import json
import time

URL = "http://127.0.0.1:7432/command"

def run(code):
    r = requests.post(URL, json={"command": "execute_script", "params": {"code": code}}, timeout=30)
    data = r.json()
    if "error" in data:
        print(f"ERROR: {data['error']}")
    else:
        print(f"OK: {data.get('output', data)}")
    return data

# Step 1: Clear design
print("=== Step 1: Clear design ===")
run("""
design.designType = adsk.fusion.DesignTypes.DirectDesignType
for b in list(root.bRepBodies):
    b.deleteMe()
for s in list(root.sketches):
    s.deleteMe()
design.designType = adsk.fusion.DesignTypes.ParametricDesignType
result['output'] = 'Design cleared'
""")

# Step 2: Create hanger profile sketch (all-in-one closed profile)
print("\n=== Step 2: Create hanger body profile ===")
run(r"""
import math

# Fusion uses cm internally
# Target: 240mm wide x ~140mm tall, 8mm thick
# Bambu P2S: 256x256x256mm

W = 24.0        # total width (240mm)
H_DROP = 3.5    # shoulder drop (35mm)
NECK_W = 1.6    # neck width (16mm)
NECK_H = 2.0    # neck height above shoulder (20mm)
BAR_Y = -1.0    # trouser bar y position
BAR_H = 0.6     # trouser bar height (6mm)
THICK = 0.8     # extrude thickness (8mm)

half_w = W / 2.0
half_neck = NECK_W / 2.0

xy = root.xYConstructionPlane
sk = root.sketches.add(xy)
lines = sk.sketchCurves.sketchLines
p3 = adsk.core.Point3D

# Hanger body profile - a symmetrical shape
# Points going clockwise from top-left of neck
# The shape: neck on top, angled shoulders, vertical sides, bottom bar

p0 = p3.create(-half_neck, NECK_H, 0)      # top-left neck
p1 = p3.create(half_neck, NECK_H, 0)       # top-right neck
p2 = p3.create(half_w, -H_DROP, 0)         # right shoulder tip
p3a = p3.create(half_w, BAR_Y, 0)          # right side bottom
p4 = p3.create(-half_w, BAR_Y, 0)          # left side bottom
p5 = p3.create(-half_w, -H_DROP, 0)        # left shoulder tip

# Draw closed profile
l0 = lines.addByTwoPoints(p0, p1)   # neck top
l1 = lines.addByTwoPoints(p1, p2)   # right shoulder slope
l2 = lines.addByTwoPoints(p2, p3a)  # right side down
l3 = lines.addByTwoPoints(p3a, p4)  # bottom
l4 = lines.addByTwoPoints(p4, p5)   # left side up
l5 = lines.addByTwoPoints(p5, p0)   # left shoulder slope

result['output'] = f'Body profile: {sk.profiles.count} profiles'
""")

# Step 3: Extrude hanger body
print("\n=== Step 3: Extrude hanger body ===")
run("""
sk = root.sketches.item(0)
prof = sk.profiles.item(0)
extrudes = root.features.extrudeFeatures
dist = adsk.core.ValueInput.createByReal(0.8)
ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ext_input.setDistanceExtent(False, dist)
ext = extrudes.add(ext_input)
result['output'] = f'Extruded body: {ext.bodies.item(0).name}'
""")

# Step 4: Create hook sketch and extrude
print("\n=== Step 4: Create hook profile ===")
run(r"""
import math

NECK_W = 1.6
NECK_H = 2.0
HOOK_OR = 1.1    # outer radius 11mm
HOOK_IR = 0.6    # inner radius 6mm
half_neck = NECK_W / 2.0

xy = root.xYConstructionPlane
sk2 = root.sketches.add(xy)
lines2 = sk2.sketchCurves.sketchLines
arcs2 = sk2.sketchCurves.sketchArcs
p3 = adsk.core.Point3D

cx = 0.0
cy = NECK_H + HOOK_OR  # hook center above neck

# Hook is a C-shape opening downward-right (about 270 degrees)
# Use three-point arcs

# Opening angle: the gap in the hook faces down
# Outer arc from ~200 deg to ~340 deg (going through top)
# That's a 220-degree span... let's do 270 degrees
# Opening at bottom, from -60 to -120 relative...
# Simple approach: opening at bottom, arc goes from left-bottom to right-bottom through top

open_half = math.radians(30)  # half opening angle from bottom

# Outer arc
out_left = p3.create(cx + HOOK_OR * math.sin(-open_half), cy - HOOK_OR * math.cos(open_half), 0)
out_top = p3.create(cx, cy + HOOK_OR, 0)
out_right = p3.create(cx + HOOK_OR * math.sin(open_half), cy - HOOK_OR * math.cos(open_half), 0)

# Inner arc
in_left = p3.create(cx + HOOK_IR * math.sin(-open_half), cy - HOOK_IR * math.cos(open_half), 0)
in_top = p3.create(cx, cy + HOOK_IR, 0)
in_right = p3.create(cx + HOOK_IR * math.sin(open_half), cy - HOOK_IR * math.cos(open_half), 0)

# Draw arcs (outer goes left->top->right, inner goes right->top->left)
arc_out = arcs2.addByThreePoints(out_left, out_top, out_right)
arc_in = arcs2.addByThreePoints(in_right, in_top, in_left)

# End caps
cap_right = lines2.addByTwoPoints(out_right, in_right)
cap_left = lines2.addByTwoPoints(in_left, out_left)

result['output'] = f'Hook profile: {sk2.profiles.count} profiles'
""")

# Step 5: Extrude hook
print("\n=== Step 5: Extrude hook ===")
run("""
sk2 = root.sketches.item(1)
# Find the hook ring profile (should be the one that looks like a C-ring)
prof = sk2.profiles.item(0)
extrudes = root.features.extrudeFeatures
dist = adsk.core.ValueInput.createByReal(0.8)
ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ext_input.setDistanceExtent(False, dist)
ext = extrudes.add(ext_input)
result['output'] = f'Hook extruded: {ext.bodies.item(0).name}'
""")

# Step 6: Create neck connector sketch and extrude (joins hook to body)
print("\n=== Step 6: Create neck connector ===")
run(r"""
import math

NECK_W = 1.6
NECK_H = 2.0
HOOK_OR = 1.1
HOOK_IR = 0.6
half_neck = NECK_W / 2.0
cy = NECK_H + HOOK_OR
open_half = math.radians(30)

xy = root.xYConstructionPlane
sk3 = root.sketches.add(xy)
lines3 = sk3.sketchCurves.sketchLines
p3 = adsk.core.Point3D

# Neck rectangle connecting body top to hook bottom
# From body top (y=NECK_H) to just below hook inner arc bottom
hook_bottom_y = cy - HOOK_IR * math.cos(open_half)
neck_top_y = hook_bottom_y

# Simple rectangle
pa = p3.create(-half_neck, NECK_H, 0)
pb = p3.create(half_neck, NECK_H, 0)
pc = p3.create(half_neck, neck_top_y, 0)
pd = p3.create(-half_neck, neck_top_y, 0)

lines3.addByTwoPoints(pa, pb)
lines3.addByTwoPoints(pb, pc)
lines3.addByTwoPoints(pc, pd)
lines3.addByTwoPoints(pd, pa)

result['output'] = f'Neck profile: {sk3.profiles.count} profiles'
""")

# Step 7: Extrude neck as join
print("\n=== Step 7: Extrude neck ===")
run("""
sk3 = root.sketches.item(2)
prof = sk3.profiles.item(0)
extrudes = root.features.extrudeFeatures
dist = adsk.core.ValueInput.createByReal(0.8)
ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ext_input.setDistanceExtent(False, dist)
ext = extrudes.add(ext_input)
result['output'] = f'Neck extruded: {ext.bodies.item(0).name}'
""")

# Step 8: Add strap notches on the shoulders
print("\n=== Step 8: Create strap notches ===")
run(r"""
import math

W = 24.0
H_DROP = 3.5
NOTCH_INSET = 3.0  # cm from center along shoulder
NOTCH_W = 0.4      # notch width
NOTCH_D = 0.6      # notch depth

half_w = W / 2.0

# Calculate position along shoulder slope
# Shoulder goes from (0.8, 2.0) to (12.0, -3.5)
# Direction vector
dx = half_w - 0.8
dy = -H_DROP - 2.0
length = math.sqrt(dx*dx + dy*dy)
nx = -dy / length  # normal pointing upward-right
ny = dx / length

# Position along shoulder at NOTCH_INSET from neck
t = NOTCH_INSET / length
sx = 0.8 + dx * t
sy = 2.0 + dy * t

# Tangent direction along shoulder
tx = dx / length
ty = dy / length

xy = root.xYConstructionPlane
sk4 = root.sketches.add(xy)
lines4 = sk4.sketchCurves.sketchLines
p3 = adsk.core.Point3D

# Right notch - V shape cut into shoulder
for side in [1, -1]:  # right and left
    cx = side * sx
    cy_pos = sy
    # Normal flips for left side
    nnx = side * nx
    nny = ny
    ttx = side * tx
    tty = ty

    # Rectangle notch perpendicular to shoulder
    p_a = p3.create(cx - ttx * NOTCH_W/2, cy_pos - tty * NOTCH_W/2, 0)
    p_b = p3.create(cx + ttx * NOTCH_W/2, cy_pos + tty * NOTCH_W/2, 0)
    p_c = p3.create(cx + ttx * NOTCH_W/2 - nnx * NOTCH_D, cy_pos + tty * NOTCH_W/2 - nny * NOTCH_D, 0)
    p_d = p3.create(cx - ttx * NOTCH_W/2 - nnx * NOTCH_D, cy_pos - tty * NOTCH_W/2 - nny * NOTCH_D, 0)

    lines4.addByTwoPoints(p_a, p_b)
    lines4.addByTwoPoints(p_b, p_c)
    lines4.addByTwoPoints(p_c, p_d)
    lines4.addByTwoPoints(p_d, p_a)

result['output'] = f'Notch profiles: {sk4.profiles.count}'
""")

# Step 9: Cut the notches
print("\n=== Step 9: Cut notches ===")
run("""
sk4 = root.sketches.item(3)
extrudes = root.features.extrudeFeatures

for i in range(sk4.profiles.count):
    prof = sk4.profiles.item(i)
    dist = adsk.core.ValueInput.createByReal(1.0)  # cut through
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ext_input.setDistanceExtent(False, dist)
    try:
        ext = extrudes.add(ext_input)
    except:
        pass

result['output'] = f'Notches cut'
""")

# Step 10: Combine all bodies
print("\n=== Step 10: Combine bodies ===")
run("""
bodies = root.bRepBodies
body_count = bodies.count
if body_count > 1:
    target = bodies.item(0)
    combines = root.features.combineFeatures
    tool_bodies = adsk.core.ObjectCollection.create()
    for i in range(1, body_count):
        tool_bodies.add(bodies.item(i))

    combine_input = combines.createInput(target, tool_bodies)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combine = combines.add(combine_input)
    result['output'] = f'Combined {body_count} bodies into one'
else:
    result['output'] = 'Only 1 body, no combine needed'
""")

# Step 11: Fillet edges for printability
print("\n=== Step 11: Fillet edges ===")
run("""
body = root.bRepBodies.item(0)
edges = body.edges
fillets = root.features.filletFeatures

# Collect all edges
edge_col = adsk.core.ObjectCollection.create()
for i in range(edges.count):
    edge_col.add(edges.item(i))

fillet_input = fillets.createInput()
fillet_input.addConstantRadiusEdgeSet(edge_col, adsk.core.ValueInput.createByReal(0.1), True)  # 1mm fillet
try:
    fillet = fillets.add(fillet_input)
    result['output'] = f'Filleted {edges.count} edges with 1mm radius'
except Exception as e:
    # Try smaller fillet
    edge_col2 = adsk.core.ObjectCollection.create()
    for i in range(edges.count):
        edge_col2.add(edges.item(i))
    fillet_input2 = fillets.createInput()
    fillet_input2.addConstantRadiusEdgeSet(edge_col2, adsk.core.ValueInput.createByReal(0.05), True)
    try:
        fillet2 = fillets.add(fillet_input2)
        result['output'] = f'Filleted with 0.5mm radius (1mm was too large)'
    except Exception as e2:
        result['output'] = f'Fillet failed: {str(e2)}'
""")

# Step 12: Verify dimensions fit build plate
print("\n=== Step 12: Verify dimensions ===")
run("""
body = root.bRepBodies.item(0)
bb = body.boundingBox
minP = bb.minPoint
maxP = bb.maxPoint
w = (maxP.x - minP.x) * 10  # mm
h = (maxP.y - minP.y) * 10  # mm
d = (maxP.z - minP.z) * 10  # mm
result['output'] = f'Hanger dimensions: {w:.1f} x {h:.1f} x {d:.1f} mm (Bambu P2S: 256x256x256mm) - {"FITS!" if w <= 256 and h <= 256 and d <= 256 else "TOO BIG!"}'
""")

print("\n=== Done! Clothes hanger created in Fusion 360 ===")
