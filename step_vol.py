'''
import sys
import os
import FreeCAD
import Part

def calculate_metrics(step_path):
    if not step_path.lower().endswith(('.step', '.stp')):
        raise ValueError("No file extension or invalid format")

    FreeCAD.newDocument()
    Part.insert(step_path, "MyDocument")

    shape = FreeCAD.ActiveDocument.ActiveObject.Shape
    if shape.isNull():
        raise ValueError("Invalid shape")
    if shape.Volume < 0.0001:
        raise ValueError("Shape is not solid or volume too small")
    
    volume = shape.Volume
    surface_area = shape.Area
    face_count = len(shape.Faces)

    return volume, surface_area, face_count

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Missing file path argument", file=sys.stderr)
        sys.exit(1)
    
    step_file = sys.argv[1]

    if not os.path.isfile(step_file):
        print(f"ERROR: File not found - {step_file}", file=sys.stderr)
        sys.exit(1)

    try:
        volume, area, face_count = calculate_metrics(step_file)
        print(f"{volume:.2f},{area:.2f},{face_count}")
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
'''

# step_volume_metrics.py

import sys
import os
import cadquery as cq
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
from OCP.GProp import GProp_GProps
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
from cadquery.occ_impl.importers import read_step_file

def calculate_metrics(step_path):
    if not os.path.isfile(step_path) or not step_path.lower().endswith(('.step', '.stp')):
        raise ValueError("Invalid STEP file path")

    shape: TopoDS_Shape = read_step_file(step_path)

    # Check for a valid shape
    if shape.IsNull():
        raise ValueError("Invalid or empty STEP file")

    # Calculate volume
    volume_props = GProp_GProps()
    brepgprop_VolumeProperties(shape, volume_props)
    volume = volume_props.Mass()

    # Calculate surface area
    area_props = GProp_GProps()
    brepgprop_SurfaceProperties(shape, area_props)
    surface_area = area_props.Mass()

    # Count faces
    faces = list(cq.Shape(shape).faces())
    face_count = len(faces)

    return volume, surface_area, face_count


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Missing STEP file path", file=sys.stderr)
        sys.exit(1)

    step_file = sys.argv[1]

    try:
        volume, surface_area, face_count = calculate_metrics(step_file)
        print(f"{volume:.2f},{surface_area:.2f},{face_count}")
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
