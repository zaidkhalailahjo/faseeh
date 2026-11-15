# -*- coding: utf-8 -*-
"""
Generate a professional, high-resolution application icon (.ico and .png)
Theme: Modern Keyboard Keycap with Arabic 'ف' and translation badge
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Outer Squircle / Rounded Background with Gradient
    # Create base gradient image
    gradient = Image.new("RGBA", size, (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)

    c1 = (37, 99, 235)   # #2563EB Vibrant Blue
    c2 = (15, 23, 42)    # #0F172A Deep Slate / Navy

    for y in range(size[1]):
        ratio = y / size[1]
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        grad_draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))

    # Mask for squircle rounded rectangle
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    # Rounded box: margin 8, radius 52
    mask_draw.rounded_rectangle([10, 10, 246, 246], radius=54, fill=255)

    # Apply mask to gradient
    img.paste(gradient, (0, 0), mask)

    # Subtle inner border glow
    border_draw = ImageDraw.Draw(img)
    border_draw.rounded_rectangle([10, 10, 246, 246], radius=54, outline=(255, 255, 255, 60), width=3)

    # 2. Keycap shape in center
    # Keycap base shadow
    border_draw.rounded_rectangle([44, 48, 212, 216], radius=32, fill=(10, 15, 30, 90))
    # Keycap body
    border_draw.rounded_rectangle([44, 40, 212, 208], radius=30, fill=(255, 255, 255, 245), outline=(226, 232, 240, 255), width=2)
    # Keycap top surface highlight
    border_draw.rounded_rectangle([52, 46, 204, 196], radius=24, fill=(248, 250, 252, 255))

    # 3. Add Typography / Icon Details
    # Try finding an Arabic font or Segoe UI / Arial
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    arial_path = "C:\\Windows\\Fonts\\arial.ttf"

    font_large = None
    font_small = None
    for p in [font_bold_path, font_path, arial_path]:
        if os.path.exists(p):
            try:
                font_large = ImageFont.truetype(p, 96)
                font_small = ImageFont.truetype(p, 20)
                break
            except Exception:
                pass

    if font_large is None:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw the main Arabic Letter "ف" (or stylized emblem)
    # Using 'ف' or symbol
    text_main = "ف"
    bbox = border_draw.textbbox((0, 0), text_main, font=font_large)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Center the letter on keycap
    tx = (256 - tw) // 2
    ty = (256 - th) // 2 - 18
    # Subtle drop shadow for letter
    border_draw.text((tx, ty + 2), text_main, font=font_large, fill=(203, 213, 225, 200))
    border_draw.text((tx, ty), text_main, font=font_large, fill=(29, 78, 216, 255))

    # Bottom badge on keycap: "EN ⇄ AR"
    badge_text = "EN ⇄ AR"
    bbox_s = border_draw.textbbox((0, 0), badge_text, font=font_small)
    sw = bbox_s[2] - bbox_s[0]
    sx = (256 - sw) // 2
    sy = 168
    border_draw.rounded_rectangle([sx - 10, sy - 2, sx + sw + 10, sy + 22], radius=8, fill=(239, 246, 255, 255))
    border_draw.text((sx, sy), badge_text, font=font_small, fill=(37, 99, 235, 255))

    # Save PNG
    out_png = r"C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\app_icon.png"
    img.save(out_png, "PNG")

    # Save Multi-resolution ICO (256, 128, 64, 48, 32, 16)
    out_ico = r"C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\app_icon.ico"
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(out_ico, format="ICO", sizes=sizes)

    print(f"Generated PNG: {out_png}")
    print(f"Generated ICO: {out_ico}")

if __name__ == '__main__':
    create_app_icon()
