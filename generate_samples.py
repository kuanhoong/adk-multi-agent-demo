"""
generate_samples.py — Creates synthetic manufacturing component images for demo testing.

Generates 5 sample images in sample_images/:
  1. ic_chip_clean.jpg        — Clean IC chip, no defects        → expected: PASS
  2. ic_chip_cracked.jpg      — IC chip with hairline crack       → expected: MRB
  3. pcb_solder_defect.jpg    — PCB with solder bridge defect     → expected: FAIL
  4. capacitor_clean.jpg      — Clean SMD capacitor array         → expected: PASS
  5. bga_misaligned.jpg       — BGA package with misaligned balls → expected: MRB/FAIL

Run: python generate_samples.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("sample_images")
OUT.mkdir(exist_ok=True)
SIZE = (600, 600)


def base_gradient(color_top, color_bot):
    """Create a subtle gradient background."""
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img)
    for y in range(SIZE[1]):
        t = y / SIZE[1]
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        draw.line([(0, y), (SIZE[0], y)], fill=(r, g, b))
    return img, draw


def add_label(draw, text, color=(200, 200, 200)):
    draw.rectangle([0, SIZE[1] - 36, SIZE[0], SIZE[1]], fill=(20, 20, 20))
    draw.text((10, SIZE[1] - 26), text, fill=color)


# ── 1. Clean IC chip ──────────────────────────────────────────────────────────
def make_ic_chip_clean():
    img, draw = base_gradient((28, 28, 35), (18, 18, 25))

    # PCB substrate
    draw.rectangle([60, 60, 540, 540], fill=(34, 85, 34), outline=(20, 60, 20), width=3)

    # Chip body
    draw.rectangle([130, 130, 470, 470], fill=(40, 40, 50), outline=(80, 80, 90), width=3)

    # Chip label / markings
    draw.rectangle([160, 160, 440, 260], fill=(50, 50, 65), outline=(90, 90, 100), width=1)
    draw.text((175, 175), "IC-7430-MCU", fill=(180, 180, 200))
    draw.text((175, 200), "Rev: B2  Lot: 2024-11", fill=(130, 130, 150))
    draw.text((175, 220), "ROHS COMPLIANT", fill=(100, 160, 100))

    # Pin rows — left side
    for i in range(8):
        y = 155 + i * 42
        draw.rectangle([90, y, 130, y + 28], fill=(192, 160, 80), outline=(220, 190, 100), width=1)

    # Pin rows — right side
    for i in range(8):
        y = 155 + i * 42
        draw.rectangle([470, y, 510, y + 28], fill=(192, 160, 80), outline=(220, 190, 100), width=1)

    # Pin rows — top
    for i in range(8):
        x = 155 + i * 42
        draw.rectangle([x, 90, x + 28, 130], fill=(192, 160, 80), outline=(220, 190, 100), width=1)

    # Pin rows — bottom
    for i in range(8):
        x = 155 + i * 42
        draw.rectangle([x, 470, x + 28, 510], fill=(192, 160, 80), outline=(220, 190, 100), width=1)

    # Die attach area
    draw.rectangle([280, 290, 380, 390], fill=(60, 60, 80), outline=(100, 100, 120), width=2)
    draw.ellipse([300, 310, 360, 370], fill=(70, 70, 90), outline=(110, 110, 130))

    # Corner marker (pin 1 indicator)
    draw.ellipse([135, 135, 155, 155], fill=(220, 220, 80))

    add_label(draw, "IC-7430-MCU  |  Clean component  |  Expected: PASS", color=(100, 220, 100))
    img.save(OUT / "ic_chip_clean.jpg", quality=95)
    print("  ✓  ic_chip_clean.jpg")


# ── 2. IC chip with hairline crack ────────────────────────────────────────────
def make_ic_chip_cracked():
    img, draw = base_gradient((28, 28, 35), (18, 18, 25))

    # PCB substrate
    draw.rectangle([60, 60, 540, 540], fill=(34, 85, 34), outline=(20, 60, 20), width=3)

    # Chip body
    draw.rectangle([130, 130, 470, 470], fill=(40, 40, 50), outline=(80, 80, 90), width=3)

    # Label
    draw.rectangle([160, 160, 440, 260], fill=(50, 50, 65), outline=(90, 90, 100), width=1)
    draw.text((175, 175), "IC-7430-MCU", fill=(180, 180, 200))
    draw.text((175, 200), "Rev: B2  Lot: 2024-11", fill=(130, 130, 150))

    # Pins
    for i in range(8):
        y = 155 + i * 42
        draw.rectangle([90, y, 130, y + 28], fill=(192, 160, 80), outline=(220, 190, 100), width=1)
        draw.rectangle([470, y, 510, y + 28], fill=(192, 160, 80), outline=(220, 190, 100), width=1)
    for i in range(8):
        x = 155 + i * 42
        draw.rectangle([x, 90, x + 28, 130], fill=(192, 160, 80), outline=(220, 190, 100), width=1)
        draw.rectangle([x, 470, x + 28, 510], fill=(192, 160, 80), outline=(220, 190, 100), width=1)

    # Corner marker
    draw.ellipse([135, 135, 155, 155], fill=(220, 220, 80))

    # === DEFECT: Hairline crack across top-left corner of chip body ===
    crack_color = (180, 140, 100)
    for offset in range(3):
        draw.line([(130 + offset, 130), (250 + offset, 210)], fill=crack_color, width=1)
    draw.line([(130, 130), (255, 215)], fill=(210, 170, 120), width=2)
    # Crack propagation branches
    draw.line([(190, 168), (220, 145)], fill=crack_color, width=1)
    draw.line([(215, 185), (240, 170)], fill=crack_color, width=1)

    # Crack highlight (make it visible)
    draw.line([(132, 132), (252, 212)], fill=(230, 200, 150), width=1)

    add_label(draw, "IC-7430-MCU  |  Hairline crack top-left  |  Expected: MRB", color=(255, 200, 50))
    img.save(OUT / "ic_chip_cracked.jpg", quality=95)
    print("  ✓  ic_chip_cracked.jpg")


# ── 3. PCB with solder bridge defect ─────────────────────────────────────────
def make_pcb_solder_defect():
    img, draw = base_gradient((20, 40, 20), (10, 25, 10))

    # PCB body
    draw.rectangle([30, 30, 570, 570], fill=(0, 100, 60), outline=(0, 80, 45), width=4)

    # Silk screen traces
    for i in range(5):
        y = 80 + i * 90
        draw.line([(60, y), (540, y)], fill=(180, 220, 180), width=2)
    for i in range(5):
        x = 80 + i * 110
        draw.line([(x, 60), (x, 540)], fill=(180, 220, 180), width=2)

    # SMD component pads (two rows)
    pad_color   = (200, 170, 80)
    pad_outline = (230, 200, 100)

    # Row 1 — clean pads
    for i in range(6):
        x = 80 + i * 80
        draw.rectangle([x, 140, x + 45, 170], fill=pad_color, outline=pad_outline, width=2)

    # Row 2 — solder bridge between pad 2 and pad 3
    for i in range(6):
        x = 80 + i * 80
        color = pad_color
        if i in (1, 2):
            color = (210, 180, 90)
        draw.rectangle([x, 240, x + 45, 270], fill=color, outline=pad_outline, width=2)

    # === DEFECT: Solder bridge between pad index 1 and 2 (row 2) ===
    bx1 = 80 + 1 * 80 + 45   # right edge of pad 1
    bx2 = 80 + 2 * 80         # left edge of pad 2
    bridge_y_top = 240
    bridge_y_bot = 270
    draw.polygon(
        [(bx1, bridge_y_top + 5), (bx2, bridge_y_top + 5),
         (bx2 + 5, bridge_y_top + 15), (bx2, bridge_y_bot - 5),
         (bx1, bridge_y_bot - 5), (bx1 - 5, bridge_y_top + 15)],
        fill=(230, 200, 60), outline=(255, 220, 80), width=1,
    )
    # Solder blob centre
    cx = (bx1 + bx2) // 2
    cy = (bridge_y_top + bridge_y_bot) // 2
    draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 8], fill=(245, 215, 70), outline=(255, 230, 90))

    # Row 3 — clean
    for i in range(6):
        x = 80 + i * 80
        draw.rectangle([x, 340, x + 45, 370], fill=pad_color, outline=pad_outline, width=2)

    # ICs placed on board
    draw.rectangle([220, 400, 380, 520], fill=(45, 45, 55), outline=(80, 80, 90), width=3)
    draw.text((240, 450), "U4 — MCU", fill=(160, 160, 180))

    # Annotation arrow pointing to bridge
    draw.line([(bx1 + 10, bridge_y_bot + 10), (bx1 + 10, bridge_y_bot + 50)], fill=(255, 80, 80), width=2)
    draw.polygon(
        [(bx1 + 10, bridge_y_bot + 10), (bx1 + 4, bridge_y_bot + 22), (bx1 + 16, bridge_y_bot + 22)],
        fill=(255, 80, 80),
    )
    draw.text((bx1 - 30, bridge_y_bot + 55), "SOLDER BRIDGE", fill=(255, 100, 100))

    add_label(draw, "PCB Assembly  |  Solder bridge between U3 pads  |  Expected: FAIL", color=(255, 100, 100))
    img.save(OUT / "pcb_solder_defect.jpg", quality=95)
    print("  ✓  pcb_solder_defect.jpg")


# ── 4. Clean SMD capacitor array ─────────────────────────────────────────────
def make_capacitor_clean():
    img, draw = base_gradient((25, 35, 45), (15, 22, 30))

    # PCB substrate
    draw.rectangle([40, 40, 560, 560], fill=(0, 90, 55), outline=(0, 70, 40), width=3)

    # Grid of SMD capacitors (0402 style)
    cap_body  = (80, 80, 100)
    cap_end   = (190, 160, 70)
    cap_out   = (100, 100, 120)

    positions = []
    for row in range(4):
        for col in range(4):
            cx = 120 + col * 110
            cy = 120 + row * 110
            positions.append((cx, cy))

    for (cx, cy) in positions:
        # Left terminal
        draw.rectangle([cx - 30, cy - 12, cx - 10, cy + 12], fill=cap_end, outline=(220, 190, 90))
        # Body
        draw.rectangle([cx - 10, cy - 14, cx + 30, cy + 14], fill=cap_body, outline=cap_out, width=1)
        # Right terminal
        draw.rectangle([cx + 30, cy - 12, cx + 50, cy + 12], fill=cap_end, outline=(220, 190, 90))
        # Capacitor marking
        draw.text((cx - 5, cy - 6), "C1", fill=(160, 160, 180))

    # Trace lines
    for (cx, cy) in positions:
        draw.line([(cx - 40, cy), (cx - 30, cy)], fill=(200, 170, 80), width=2)
        draw.line([(cx + 50, cy), (cx + 60, cy)], fill=(200, 170, 80), width=2)

    add_label(draw, "SMD 0402 Capacitor Array  |  No defects  |  Expected: PASS", color=(100, 220, 100))
    img.save(OUT / "capacitor_clean.jpg", quality=95)
    print("  ✓  capacitor_clean.jpg")


# ── 5. BGA package with misaligned solder balls ───────────────────────────────
def make_bga_misaligned():
    img, draw = base_gradient((30, 25, 35), (20, 15, 25))

    # PCB substrate
    draw.rectangle([40, 40, 560, 560], fill=(34, 85, 34), outline=(20, 60, 20), width=3)

    # BGA package body
    draw.rectangle([100, 100, 500, 500], fill=(55, 45, 65), outline=(90, 75, 100), width=4)
    draw.text((160, 115), "BGA-256  FPGA-XC7A35T", fill=(170, 160, 185))
    draw.text((200, 140), "Lot: 2024-Q3-B7", fill=(130, 120, 145))

    # BGA solder ball grid
    ball_r = 14
    rows   = 8
    cols   = 8
    start_x = 145
    start_y = 185
    step    = 44

    misaligned_balls = {(2, 3), (2, 4)}  # intentionally offset balls

    for r in range(rows):
        for c in range(cols):
            bx = start_x + c * step
            by = start_y + r * step

            if (r, c) in misaligned_balls:
                # Offset ball — misalignment defect
                bx_off = bx + 10
                by_off = by - 8
                # Show expected pad position (ghost)
                draw.ellipse(
                    [bx - ball_r, by - ball_r, bx + ball_r, by + ball_r],
                    outline=(255, 100, 100), width=2,
                )
                # Actual misaligned ball
                draw.ellipse(
                    [bx_off - ball_r, by_off - ball_r, bx_off + ball_r, by_off + ball_r],
                    fill=(200, 170, 60), outline=(230, 200, 80), width=1,
                )
                # Mismatch indicator
                draw.line([(bx, by), (bx_off, by_off)], fill=(255, 80, 80), width=2)
            else:
                # Normal aligned ball
                shade = 150 + (r + c) % 3 * 10
                draw.ellipse(
                    [bx - ball_r, by - ball_r, bx + ball_r, by + ball_r],
                    fill=(shade, shade - 20, 60), outline=(200, 180, 80), width=1,
                )

    # Annotation
    ax = start_x + 2 * step
    ay = start_y + 3 * step
    draw.text((ax + 20, ay + 25), "← MISALIGNED", fill=(255, 100, 100))

    add_label(draw, "BGA-256 FPGA  |  2 misaligned solder balls (r2,c3-4)  |  Expected: MRB/FAIL", color=(255, 200, 50))
    img.save(OUT / "bga_misaligned.jpg", quality=95)
    print("  ✓  bga_misaligned.jpg")


if __name__ == "__main__":
    print("Generating sample component images...")
    make_ic_chip_clean()
    make_ic_chip_cracked()
    make_pcb_solder_defect()
    make_capacitor_clean()
    make_bga_misaligned()
    print(f"\nDone — 5 images saved to ./{OUT}/")
    print("\nExpected inspection outcomes:")
    print("  ic_chip_clean.jpg       → PASS")
    print("  ic_chip_cracked.jpg     → MRB  (hairline crack)")
    print("  pcb_solder_defect.jpg   → FAIL (solder bridge)")
    print("  capacitor_clean.jpg     → PASS")
    print("  bga_misaligned.jpg      → MRB / FAIL (ball misalignment)")
