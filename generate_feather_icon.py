# -*- coding: utf-8 -*-
"""
Generate a magnificent Feather (ريشة كتابة) icon for 'فصيح'.
Combines the elegance of a classic quill feather with modern UI styling.
"""

import math
from PIL import Image, ImageDraw, ImageFilter

def create_feather_icon():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))

    # 1. Background Squircle with modern Deep Blue / Indigo Gradient
    gradient = Image.new("RGBA", size, (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)

    c1 = (30, 58, 138)   # Deep Blue #1E3A8A
    c2 = (15, 23, 42)    # Slate/Navy #0F172A

    for y in range(size[1]):
        ratio = y / size[1]
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        grad_draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))

    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([20, 20, 492, 492], radius=110, fill=255)
    img.paste(gradient, (0, 0), mask)

    # Outer border ring with subtle glow
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([20, 20, 492, 492], radius=110, outline=(56, 189, 248, 80), width=6)

    # 2. Draw the Feather (الريشة)
    # A graceful, sweeping quill feather angled from bottom-left (130, 410) to top-right (390, 95)
    feather_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(feather_layer)

    # Curve points for the central quill shaft (rachis / ساق الريشة)
    start_point = (135, 415)
    mid_point = (250, 260)
    end_point = (395, 95)

    # Draw feather vanes (شعيرات الريشة)
    # Left vane and right vane using a series of smooth curved lines / polygons
    steps = 90
    for i in range(steps):
        t = i / steps
        # Quadratic bezier for the central stem
        x = (1 - t)**2 * start_point[0] + 2 * (1 - t) * t * (mid_point[0] + 20) + t**2 * end_point[0]
        y = (1 - t)**2 * start_point[1] + 2 * (1 - t) * t * (mid_point[1] - 20) + t**2 * end_point[1]

        # Normal vector perpendicular to the curve
        dx = 2 * (1 - t) * ((mid_point[0] + 20) - start_point[0]) + 2 * t * (end_point[0] - (mid_point[0] + 20))
        dy = 2 * (1 - t) * ((mid_point[1] - 20) - start_point[1]) + 2 * t * (end_point[1] - (mid_point[1] - 20))
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            continue
        nx = -dy / length
        ny = dx / length

        # Vane width profile: tapered at bottom, wide in middle, tapered at tip
        vane_width = math.sin(t * math.pi) * 85.0

        # Colors: vibrant cyan / teal to luminous gold / emerald
        # Left vane (upper/fluffy)
        col_r = int(56 + (245 - 56) * t)
        col_g = int(189 + (215 - 189) * (1 - t))
        col_b = int(248 * (1 - t * 0.7))

        # Left side barbs
        lx = x + nx * vane_width * 0.95
        ly = y + ny * vane_width * 0.95
        f_draw.line([(x, y), (lx, ly)], fill=(col_r, col_g, col_b, 220), width=4)

        # Right side barbs
        rx = x - nx * vane_width * 0.65
        ry = y - ny * vane_width * 0.65
        f_draw.line([(x, y), (rx, ry)], fill=(col_r - 20, col_g - 20, col_b, 190), width=4)

    # Central Shaft / Rachis (ساق الريشة الشفافة اللامعة)
    shaft_points = []
    for i in range(100):
        t = i / 100
        x = (1 - t)**2 * start_point[0] + 2 * (1 - t) * t * (mid_point[0] + 20) + t**2 * end_point[0]
        y = (1 - t)**2 * start_point[1] + 2 * (1 - t) * t * (mid_point[1] - 20) + t**2 * end_point[1]
        shaft_points.append((x, y))

    # Glow shadow under shaft
    f_draw.line(shaft_points, fill=(15, 23, 42, 180), width=8)
    # Bright quill shaft
    f_draw.line(shaft_points, fill=(255, 255, 255, 255), width=5)
    f_draw.line(shaft_points, fill=(254, 240, 138, 230), width=2) # Golden highlight

    # Nib tip at the bottom
    nib_tip = (120, 430)
    f_draw.polygon([shaft_points[0], (shaft_points[0][0] + 4, shaft_points[0][1] - 4), nib_tip, (shaft_points[0][0] - 4, shaft_points[0][1] + 4)], fill=(250, 204, 21, 255))

    # Subtle glowing sparkle near the tip
    sp_x, sp_y = 395, 95
    f_draw.line([(sp_x - 12, sp_y), (sp_x + 12, sp_y)], fill=(255, 255, 255, 240), width=3)
    f_draw.line([(sp_x, sp_y - 12), (sp_x, sp_y + 12)], fill=(255, 255, 255, 240), width=3)

    # Composite feather onto image
    img = Image.alpha_composite(img, feather_layer)

    # Downscale smoothly to 256x256 for crisp anti-aliasing
    final_img = img.resize((256, 256), Image.Resampling.LANCZOS)

    out_png = r"C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\app_icon.png"
    out_ico = r"C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\app_icon.ico"

    final_img.save(out_png, "PNG")

    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    final_img.save(out_ico, format="ICO", sizes=sizes)

    # Also copy to brain folder so we can show user
    artifact_png = r"C:\Users\nnoub\.gemini\antigravity\brain\0c5e4997-74dc-49dc-85a3-e41e64daf1d3\app_icon.png"
    final_img.save(artifact_png, "PNG")

    print(f"Feather Icon generated successfully at: {out_ico}")

if __name__ == '__main__':
    create_feather_icon()
