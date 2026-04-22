"""2x2 qualitative figure: weather-conditioned hazard reasoning results."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

IMAGE_BASE = Path("/home/seong/new_research/icros_workspace/icros_workspace/data/images")
OUT_PATH   = Path("/home/seong/new_research/docs/figure_qualitative.png")

SAMPLES = [
    {
        "image": IMAGE_BASE / "img_0001_snow_pedestrian.png",
        "weather": "Snow  |  low visibility  |  slippery road",
        "weather_color": (80, 120, 200),
        "hazard": "Pedestrian",
        "risk": "HIGH",
        "bbox": (232, 258, 487, 360),
        "explanation": (
            "Pedestrians on slippery snow roads can cause sudden movements, "
            "making it difficult to predict their actions. Snow and low visibility "
            "further reduce the driver's ability to see and react in time."
        ),
    },
    {
        "image": IMAGE_BASE / "img_0006_rain_cyclist.png",
        "weather": "Rain  |  low visibility  |  wet road",
        "weather_color": (60, 130, 180),
        "hazard": "Cyclist",
        "risk": "HIGH",
        "bbox": (476, 228, 624, 360),
        "explanation": (
            "The cyclist is riding on a wet road, reducing traction and stability. "
            "Rain reduces the cyclist's visibility to the ego vehicle, making it "
            "difficult to anticipate their movement and avoid collision."
        ),
    },
    {
        "image": IMAGE_BASE / "img_0013_fog_car.png",
        "weather": "Fog  |  low visibility  |  clear road",
        "weather_color": (110, 110, 140),
        "hazard": "Bicycle / Pedestrian",
        "risk": "HIGH",
        "bbox": (531, 260, 619, 317),
        "explanation": (
            "The presence of fog severely reduces visibility, making it difficult "
            "for the ego vehicle to detect cyclists and pedestrians ahead. "
            "Low visibility increases the risk of late detection and collision."
        ),
    },
    {
        "image": IMAGE_BASE / "img_0003_snow_cyclist.png",
        "weather": "Snow  |  medium visibility  |  slippery road",
        "weather_color": (80, 120, 200),
        "hazard": "Cyclist",
        "risk": "HIGH",
        "bbox": (470, 258, 631, 360),
        "explanation": (
            "Cyclists on snow-covered roads face significant instability due to "
            "reduced traction. Slippery conditions make sudden stops difficult, "
            "and reduced visibility increases the risk for both cyclist and driver."
        ),
    },
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width):
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if font.getlength(test) > max_width:
            if line:
                lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    return lines


def make_figure():
    CELL_W   = 760
    CELL_H   = 500
    IMG_H    = 300
    PANEL_H  = CELL_H - IMG_H
    GAP      = 16
    TITLE_H  = 60
    COLS, ROWS = 2, 2

    TOTAL_W = COLS * CELL_W + (COLS + 1) * GAP
    TOTAL_H = TITLE_H + ROWS * CELL_H + (ROWS + 1) * GAP

    f_title   = load_font(28)
    f_weather = load_font(20)
    f_field   = load_font(20)
    f_expl    = load_font(18)

    canvas = Image.new("RGB", (TOTAL_W, TOTAL_H), (245, 245, 248))
    draw   = ImageDraw.Draw(canvas)

    # title bar
    draw.rectangle([0, 0, TOTAL_W, TITLE_H], fill=(30, 30, 30))
    draw.text((GAP, 16),
              "Fig. 2  Qualitative Results: Weather-Conditioned Hazard Reasoning",
              fill=(255, 255, 255), font=f_title)

    for idx, s in enumerate(SAMPLES):
        col = idx % COLS
        row = idx // COLS
        cx  = GAP + col * (CELL_W + GAP)
        cy  = TITLE_H + GAP + row * (CELL_H + GAP)

        # cell background
        draw.rectangle([cx, cy, cx + CELL_W, cy + CELL_H], fill=(255, 255, 255))
        draw.rectangle([cx, cy, cx + CELL_W, cy + CELL_H],
                       outline=(180, 180, 180), width=2)

        # image
        img = Image.open(s["image"]).convert("RGB").resize((CELL_W, IMG_H))
        d_img = ImageDraw.Draw(img)

        # bbox on image
        if s["bbox"]:
            iw_orig, ih_orig = Image.open(s["image"]).size
            sx = CELL_W / iw_orig
            sy = IMG_H / ih_orig
            x1 = int(s["bbox"][0] * sx)
            y1 = int(s["bbox"][1] * sy)
            x2 = int(s["bbox"][2] * sx)
            y2 = int(s["bbox"][3] * sy)
            for t in range(4):
                d_img.rectangle([x1-t, y1-t, x2+t, y2+t], outline=(60, 220, 60))
            label = s["hazard"]
            lw = int(len(label) * 11 + 12)
            d_img.rectangle([x1, max(0, y1-30), x1+lw, y1], fill=(60, 220, 60))
            d_img.text((x1+5, max(0, y1-27)), label, fill=(0, 0, 0), font=f_weather)

        canvas.paste(img, (cx, cy))

        # weather badge
        py = cy + IMG_H
        draw.rectangle([cx, py, cx + CELL_W, py + 36], fill=s["weather_color"])
        draw.text((cx + 10, py + 8), s["weather"], fill=(255, 255, 255), font=f_weather)

        # hazard + risk
        y = py + 44
        draw.text((cx + 10, y),
                  f"Hazard: {s['hazard']}   |   Risk: {s['risk']}",
                  fill=(40, 40, 40), font=f_field)
        y += 30

        # explanation
        for line in wrap_text(s["explanation"], f_expl, CELL_W - 20):
            if y + 22 > cy + CELL_H:
                break
            draw.text((cx + 10, y), line, fill=(70, 70, 70), font=f_expl)
            y += 22

    canvas.save(OUT_PATH, dpi=(300, 300))
    print(f"Saved: {OUT_PATH}  ({TOTAL_W}x{TOTAL_H})")


if __name__ == "__main__":
    make_figure()
