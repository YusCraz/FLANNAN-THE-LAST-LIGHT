"""Build transparent Rive fog and a separate lighthouse-image preview."""

import math
import shutil
import struct
from pathlib import Path
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent

IMAGE = (
    PROJECT
    / "src/flannan/web/flannan-scene-pack/assets/scenes/lighthouse_exterior.png"
)

WIDTH, HEIGHT = 1920, 1080


def element(parent, tag, **attributes):
    """Create an XML element and safely format its attributes."""
    return ET.SubElement(
        parent,
        tag,
        {key: str(value) for key, value in attributes.items()},
    )


def make_scene(image_size=None):
    """Create six independently moving groups of soft mist."""
    root = ET.Element("Rive", version="1", kind="fragment")

    board = element(
        root,
        "Artboard",
        name="Flannan Fog",
        id="0:2",
        width=WIDTH,
        height=HEIGHT,
        styleId="0:5",
        defaultStateMachineId="0:7",
    )

    element(
        board,
        "LayoutComponentStyle",
        name="Artboard Style",
        id="0:5",
    )

    # x, y, travel distance, duration in frames, density, vertical scale.
    groups = [
        (220, 900, 330, 720, 0.42, 1.0),
        (1050, 965, -390, 900, 0.38, 0.85),
        (1770, 830, -350, 1080, 0.35, 0.8),
        (430, 720, 300, 1200, 0.27, 0.65),
        (1320, 645, -270, 1440, 0.22, 0.55),
        (850, 520, 220, 1800, 0.16, 0.45),
    ]

    # Overlapping, offset shapes make each wisp uneven.
    puffs = [
        (-280, 12, 2.0, 0.23),
        (-85, -28, 1.65, 0.38),
        (120, 8, 2.15, 0.24),
        (310, -12, 1.25, 0.3),
    ]

    machine = element(
        board,
        "StateMachine",
        name="Atmosphere",
        id="0:7",
    )

    for index, settings in enumerate(groups):
        x, y, travel, duration, density, height = settings

        group_id = f"0:{100 + index}"
        animation_id = f"0:{200 + index}"
        state_id = f"0:{300 + index}"

        group = element(
            board,
            "Node",
            id=group_id,
            name=f"Mist {index + 1}",
            x=x,
            y=y,
            opacity=density,
            scaleY=height,
        )

        # Build four soft shapes for this moving group.
        for dx, dy, sx, sy in puffs:
            shape = element(
                group,
                "Shape",
                x=dx,
                y=dy,
                scaleX=sx,
                scaleY=sy,
            )

            element(shape, "Ellipse", width=420, height=420)

            fill = element(shape, "Fill")

            gradient = element(
                fill,
                "RadialGradient",
                startX=0,
                startY=0,
                endX=210,
                endY=0,
            )

            # Fade gradually from the centre to a transparent edge.
            stops = [
                (0, "90ABB4BE"),
                (0.25, "68ABB4BE"),
                (0.65, "25ABB4BE"),
                (1, "00ABB4BE"),
            ]

            for position, color in stops:
                element(
                    gradient,
                    "GradientStop",
                    position=position,
                    colorValue=color,
                )

        # Each group gets its own loop length.
        layer = element(
            machine,
            "StateMachineLayer",
            name=f"Mist layer {index + 1}",
        )

        element(layer, "AnyState", x=200, y=-120)
        element(layer, "ExitState", x=400, y=-120)

        entry = element(layer, "EntryState")
        element(entry, "StateTransition", stateToId=state_id)

        element(
            layer,
            "AnimationState",
            id=state_id,
            animationId=animation_id,
            x=200,
        )

        animation = element(
            board,
            "LinearAnimation",
            id=animation_id,
            name=f"Drift {index + 1}",
            fps=60,
            duration=duration,
            loopValue="loop",
        )

        keyed = element(
            animation,
            "KeyedObject",
            objectId=group_id,
        )

        # Rive keys: horizontal=13, vertical=14, width scale=16, opacity=18.
        for key in (13, 14, 16, 18):
            prop = element(
                keyed,
                "KeyedProperty",
                propertyKey=key,
            )

            # Sample smooth cycles, including matching start/end values.
            for step in range(17):
                angle = step / 16 * math.tau
                phase = index * 0.9

                values = {
                    13: x + travel * math.sin(angle),
                    14: y + 24 * math.sin(angle * 2 + phase),
                    16: 1 + 0.12 * math.sin(angle + phase),
                    18: density * (
                        0.78 + 0.22 * math.cos(angle + phase)
                    ),
                }

                element(
                    prop,
                    "KeyFrameDouble",
                    frame=round(duration * step / 16),
                    value=round(values[key], 5),
                    interpolationType="linear",
                )

    if image_size:
        # Fit the existing illustration without stretching its proportions.
        image_width, image_height = image_size
        scale = max(
            WIDTH / image_width,
            HEIGHT / image_height,
        )

        # Rive draws earlier siblings on top, so the image goes last.
        element(
            board,
            "Image",
            name="Lighthouse backdrop",
            assetId="0:500",
            x=WIDTH / 2,
            y=HEIGHT / 2,
            originX=0.5,
            originY=0.5,
            scaleX=scale,
            scaleY=scale,
        )

        element(
            root,
            "ImageAsset",
            id="0:500",
            name="Lighthouse",
            file="background.png",
        )

    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="unicode") + "\n"


def main():
    """Generate the overlay and preview using the existing scene artwork."""

    # Read the PNG dimensions without installing extra Python packages.
    with IMAGE.open("rb") as source:
        header = source.read(24)

    if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) != 24:
        raise ValueError(f"Not a valid PNG: {IMAGE}")

    image_size = struct.unpack(">II", header[16:24])

    if not all(image_size):
        raise ValueError("The image has invalid dimensions.")

    # Preserve the previous animation before replacing it.
    scene = HERE / "scene.rml"
    backup = HERE / "scene.rml.bak"

    if scene.exists() and not backup.exists():
        shutil.copy2(scene, backup)

    # This version stays transparent for later website integration.
    scene.write_text(
        make_scene(),
        encoding="utf-8",
    )

    # Use a separate sibling project for the preview with the background.
    preview = HERE.parent / "lighthouse-preview"
    preview.mkdir(exist_ok=True)

    shutil.copy2(
        IMAGE,
        preview / "background.png",
    )

    (preview / "rive.yaml").write_text(
        "name: lighthouse-preview\n",
        encoding="utf-8",
    )

    (preview / "scene.rml").write_text(
        make_scene(image_size),
        encoding="utf-8",
    )

    print(f"Updated transparent fog: {scene}")
    print(f"Created image preview: {preview}")


if __name__ == "__main__":
    main()