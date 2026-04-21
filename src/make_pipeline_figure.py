"""Pipeline diagram for ICROS paper: image + weather token -> VLM -> structured output."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

OUT_PATH = Path("/home/seong/new_research/docs/figure_pipeline.png")
SAMPLE_IMAGE = Path("/home/seong/new_research/icros_workspace/icros_workspace/data/images/img_0006_rain_cyclist.png")


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(draw, x0, y0, x1, y1, color=(80, 80, 80), width=3):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)
    # arrowhead
    draw.polygon([(x1, y1), (x1 - 10, y1 - 6), (x1 - 10, y1 + 6)], fill=color)


def make_pipeline():
    W, H = 1800, 500
    PAD = 30
    BG = (250, 250, 252)

    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    f_title  = load_font(26)
    f_label  = load_font(19)
    f_small  = load_font(18)
    f_tiny   = load_font(16)

    # ── title bar ──────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 52], fill=(40, 40, 40))
    draw.text((PAD, 13), "Fig. 1  Weather-Conditioned Hazard Reasoning Pipeline",
              fill=(255, 255, 255), font=f_title)

    TOP = 80
    BOX_H = 320

    # ── Block definitions ─────────────────────────────────────────────────
    # [Image Input] -> [Weather Token] -> [Qwen2.5-VL] -> [Structured Output]

    blocks = [
        {
            "x": 30, "w": 240,
            "title": "Input Image",
            "color": (210, 225, 245),
            "outline": (80, 110, 170),
            "lines": ["Front-view camera", "image (single frame)"],
        },
        {
            "x": 320, "w": 360,
            "title": "Structured Weather Context",
            "color": (215, 240, 220),
            "outline": (60, 140, 80),
            "lines": [
                "weather_type : rain",
                "visibility     : low",
                "illumination : day",
                "road_condition: wet",
            ],
        },
        {
            "x": 740, "w": 360,
            "title": "Qwen2.5-VL-3B",
            "color": (245, 235, 210),
            "outline": (170, 120, 40),
            "lines": [
                "Prompt-conditioned",
                "multimodal inference",
                "(no fine-tuning)",
                "image + w → JSON",
            ],
        },
        {
            "x": 1180, "w": 590,
            "title": "Structured Output  y",
            "color": (245, 215, 215),
            "outline": (170, 60, 60),
            "lines": [
                "hazard_object : cyclist",
                "bounding_box   : (507, 218, 640, 360)",
                "risk_level       : high",
                "reason            : wet road + tram tracks",
                "explanation    : rain reduces traction ...",
            ],
        },
    ]

    for b in blocks:
        x0 = b["x"]
        x1 = x0 + b["w"]
        y0 = TOP
        y1 = TOP + BOX_H
        draw_rounded_rect(draw, [x0, y0, x1, y1], radius=14,
                          fill=b["color"], outline=b["outline"], width=3)
        # title bar inside box
        draw_rounded_rect(draw, [x0 + 2, y0 + 2, x1 - 2, y0 + 44], radius=12,
                          fill=b["outline"])
        draw.text((x0 + 12, y0 + 10), b["title"], fill=(255, 255, 255), font=f_label)
        # content lines
        for i, line in enumerate(b["lines"]):
            draw.text((x0 + 14, y0 + 58 + i * 36), line,
                      fill=(40, 40, 40), font=f_small)

    # ── Arrows ────────────────────────────────────────────────────────────
    arrow_y = TOP + BOX_H // 2

    # image -> weather token  (diagonal merge arrow: both go into VLM)
    # image box right edge
    img_right = blocks[0]["x"] + blocks[0]["w"]
    wt_right  = blocks[1]["x"] + blocks[1]["w"]
    vlm_left  = blocks[2]["x"]

    # arrow: image → VLM
    draw_arrow(draw, img_right, arrow_y - 30, vlm_left - 2, arrow_y - 30,
               color=(80, 110, 170), width=3)
    # arrow: weather token → VLM
    draw_arrow(draw, wt_right, arrow_y + 30, vlm_left - 2, arrow_y + 30,
               color=(60, 140, 80), width=3)

    # merge indicator at VLM left
    draw.line([(vlm_left - 2, arrow_y - 30), (vlm_left - 2, arrow_y + 30)],
              fill=(120, 120, 120), width=3)

    # arrow: VLM → output
    vlm_right = blocks[2]["x"] + blocks[2]["w"]
    out_left  = blocks[3]["x"]
    draw_arrow(draw, vlm_right, arrow_y, out_left - 2, arrow_y,
               color=(170, 60, 60), width=3)

    # ── Sample image thumbnail ────────────────────────────────────────────
    if SAMPLE_IMAGE.exists():
        thumb = Image.open(SAMPLE_IMAGE).convert("RGB")
        thumb_w, thumb_h = 200, 160
        thumb = thumb.resize((thumb_w, thumb_h))
        tx = blocks[0]["x"] + (blocks[0]["w"] - thumb_w) // 2
        ty = TOP + 120
        canvas.paste(thumb, (tx, ty))

    # ── Bottom caption ────────────────────────────────────────────────────
    draw.text((PAD, H - 34),
              "Structured Weather Context w = {weather_type, visibility, illumination, road_condition}  |  "
              "output y = {hazard_object, bounding_box, risk_level, reason, explanation}",
              fill=(90, 90, 90), font=f_tiny)

    canvas.save(OUT_PATH, dpi=(300, 300))
    print(f"Saved: {OUT_PATH}  ({W}x{H})")


if __name__ == "__main__":
    make_pipeline()
