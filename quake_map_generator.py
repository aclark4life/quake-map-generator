#!/usr/bin/env python3
"""
Quake .MAP File Generator
Demonstrates procedural level generation and map file manipulation
"""

import math
import os


class QuakeMapWriter:
    """Handles writing Quake .map files in proper format"""

    def __init__(self, filename):
        self.filename = filename
        self.entities = []
        self.brush_id = 0

    def create_box_brush(self, min_point, max_point, texture="__TB_empty"):
        """
        Create a simple box brush with proper plane winding
        Quake brushes are defined by planes, not vertices
        """
        x1, y1, z1 = min_point
        x2, y2, z2 = max_point

        # Each plane needs 3 points in counter-clockwise order when viewed from outside
        # Format: ( x y z ) ( x y z ) ( x y z ) TEXTURE xoff yoff rot xscale yscale

        planes = [
            # Top face (looking down, CCW)
            [(x1, y2, z2), (x2, y2, z2), (x2, y1, z2)],
            # Bottom face (looking up, CCW)
            [(x1, y1, z1), (x2, y1, z1), (x2, y2, z1)],
            # North face (+Y)
            [(x1, y2, z2), (x1, y2, z1), (x2, y2, z1)],
            # South face (-Y)
            [(x2, y1, z2), (x2, y1, z1), (x1, y1, z1)],
            # East face (+X)
            [(x2, y1, z2), (x2, y1, z1), (x2, y2, z1)],
            # West face (-X)
            [(x1, y2, z2), (x1, y2, z1), (x1, y1, z1)],
        ]

        return {"planes": planes, "texture": texture}

    def add_entity(self, classname, properties=None, brushes=None):
        """Add an entity (point entity or brush entity)"""
        entity = {
            "classname": classname,
            "properties": properties or {},
            "brushes": brushes or [],
        }
        self.entities.append(entity)

    def write(self):
        """Write the .map file"""
        with open(self.filename, "w") as f:
            # Write header comment
            f.write("// Game: Quake\n")
            f.write("// Format: Standard\n")
            f.write("// entity 0\n")
            f.write("{\n")
            f.write('"classname" "worldspawn"\n')

            # Write worldspawn brushes
            worldspawn_brushes = [
                e for e in self.entities if e["classname"] == "worldspawn"
            ]
            if worldspawn_brushes:
                for brush in worldspawn_brushes[0]["brushes"]:
                    self._write_brush(f, brush)

            f.write("}\n")

            # Write other entities
            entity_num = 1
            for entity in self.entities:
                if entity["classname"] != "worldspawn":
                    f.write(f"// entity {entity_num}\n")
                    f.write("{\n")
                    f.write(f'"classname" "{entity["classname"]}"\n')

                    for key, value in entity["properties"].items():
                        f.write(f'"{key}" "{value}"\n')

                    for brush in entity["brushes"]:
                        self._write_brush(f, brush)

                    f.write("}\n")
                    entity_num += 1

    def _write_brush(self, f, brush):
        """Write a single brush in Quake .map format"""
        f.write("{\n")

        for plane in brush["planes"]:
            # Each plane is defined by 3 points
            p1, p2, p3 = plane

            # Format: ( x1 y1 z1 ) ( x2 y2 z2 ) ( x3 y3 z3 ) TEXTURE x_offset y_offset rotation x_scale y_scale
            f.write(f"( {int(p1[0])} {int(p1[1])} {int(p1[2])} ) ")
            f.write(f"( {int(p2[0])} {int(p2[1])} {int(p2[2])} ) ")
            f.write(f"( {int(p3[0])} {int(p3[1])} {int(p3[2])} ) ")
            f.write(f"{brush['texture']} 0 0 0 1 1\n")

        f.write("}\n")


def create_hollow_room(
    writer, origin, size, thickness=16, wall_tex="__TB_empty", floor_tex="__TB_empty"
):
    """Create a hollow room with proper walls"""
    x, y, z = origin
    w, d, h = size

    brushes = []

    # Floor
    floor = writer.create_box_brush((x, y, z), (x + w, y + d, z + thickness), floor_tex)
    brushes.append(floor)

    # Ceiling
    ceiling = writer.create_box_brush(
        (x, y, z + h - thickness), (x + w, y + d, z + h), wall_tex
    )
    brushes.append(ceiling)

    # North wall (back, +Y)
    north = writer.create_box_brush(
        (x, y + d - thickness, z + thickness),
        (x + w, y + d, z + h - thickness),
        wall_tex,
    )
    brushes.append(north)

    # South wall (front, -Y)
    south = writer.create_box_brush(
        (x, y, z + thickness), (x + w, y + thickness, z + h - thickness), wall_tex
    )
    brushes.append(south)

    # West wall (left, -X)
    west = writer.create_box_brush(
        (x, y, z + thickness), (x + thickness, y + d, z + h - thickness), wall_tex
    )
    brushes.append(west)

    # East wall (right, +X)
    east = writer.create_box_brush(
        (x + w - thickness, y, z + thickness),
        (x + w, y + d, z + h - thickness),
        wall_tex,
    )
    brushes.append(east)

    return brushes


def create_spiral_staircase(
    writer, origin, radius, height, steps, texture="__TB_empty"
):
    """Generate a spiral staircase"""
    x, y, z = origin
    step_height = height / steps
    angle_per_step = 360 / steps
    step_width = 48
    step_depth = 64
    step_thickness = 8

    brushes = []

    for i in range(steps):
        angle = math.radians(i * angle_per_step)
        step_x = x + radius * math.cos(angle)
        step_y = y + radius * math.sin(angle)
        step_z = z + i * step_height

        # Create a step
        step = writer.create_box_brush(
            (step_x - step_width / 2, step_y - step_depth / 2, step_z),
            (step_x + step_width / 2, step_y + step_depth / 2, step_z + step_thickness),
            texture,
        )
        brushes.append(step)

    return brushes


def create_pillar(writer, origin, width, height, texture="__TB_empty"):
    """Create a simple pillar"""
    x, y, z = origin
    pillar = writer.create_box_brush(
        (x, y, z), (x + width, y + width, z + height), texture
    )
    return [pillar]


def create_platform(writer, origin, size, height, texture="__TB_empty"):
    """Create a raised platform"""
    x, y, z = origin
    w, d = size

    platform = writer.create_box_brush((x, y, z), (x + w, y + d, z + height), texture)
    return [platform]


# Example: Generate a complete map
def generate_example_map():
    """Generate a sample Quake map"""

    writer = QuakeMapWriter("generated_map.map")

    print("Generating map geometry...")

    # Create main room
    main_room = create_hollow_room(writer, (0, 0, 0), (512, 512, 256), thickness=16)

    # Create second room
    second_room = create_hollow_room(writer, (600, 0, 0), (512, 512, 256), thickness=16)

    # Add connecting corridor walls (simplified - just remove one wall section)
    # In practice, you'd create a proper corridor with doorway

    # Add spiral staircase in main room
    print("Adding spiral staircase...")
    staircase = create_spiral_staircase(writer, (256, 256, 16), 100, 180, 20)

    # Add some pillars
    print("Adding decorative elements...")
    pillar1 = create_pillar(writer, (100, 100, 16), 32, 128)
    pillar2 = create_pillar(writer, (400, 100, 16), 32, 128)
    pillar3 = create_pillar(writer, (100, 400, 16), 32, 128)
    pillar4 = create_pillar(writer, (400, 400, 16), 32, 128)

    # Add a raised platform in second room
    platform = create_platform(writer, (700, 200, 16), (200, 150), 64)

    # Combine all worldspawn geometry
    all_brushes = (
        main_room
        + second_room
        + staircase
        + pillar1
        + pillar2
        + pillar3
        + pillar4
        + platform
    )

    print(f"Total brushes: {len(all_brushes)}")

    writer.add_entity("worldspawn", brushes=all_brushes)

    # Add player start
    print("Adding entities...")
    writer.add_entity("info_player_start", {"origin": "256 256 32", "angle": "0"})

    # Add lights
    writer.add_entity("light", {"origin": "256 256 180", "light": "300"})

    writer.add_entity("light", {"origin": "856 256 180", "light": "300"})

    writer.add_entity("light", {"origin": "100 100 150", "light": "200"})

    writer.add_entity("light", {"origin": "400 400 150", "light": "200"})

    # Add some monsters
    writer.add_entity("monster_army", {"origin": "856 256 32", "angle": "180"})

    writer.add_entity("monster_army", {"origin": "856 400 32", "angle": "180"})

    writer.add_entity("monster_dog", {"origin": "700 300 90", "angle": "270"})

    # Add some items
    writer.add_entity("weapon_supershotgun", {"origin": "400 256 32"})

    writer.add_entity("item_health", {"origin": "256 400 32"})

    writer.add_entity("item_shells", {"origin": "800 450 32"})

    # Write the file
    print("Writing map file...")
    writer.write()
    print(f"\n✓ Map generated: generated_map.map")
    print(f"\nNext steps:")
    print(f"1. Open in TrenchBroom to view and add textures")
    print(
        f"2. Compile: qbsp generated_map.map && vis generated_map.bsp && light generated_map.bsp"
    )
    print(f"3. Copy generated_map.bsp to your Quake/id1/maps/ folder")
    print(f"4. Run Quake and type: map generated_map")


if __name__ == "__main__":
    generate_example_map()
