"""Generate qualitative comparison figure for ICROS paper."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

SAMPLES = [
    {
        "image": "img_0001_snow_pedestrian.png",
        "label": "(a) Snow scene — pedestrian",
        "true_weather": "snow",
        "wrong_weather": "fog",
        "rows": [
            ("image+weather\n(snow token)", "heavy snowfall reduces visibility, making it\ndifficult for pedestrians to see approaching\nvehicles clearly."),
            ("image only\n(no token)", "Pedestrians crossing in snowy conditions,\nwhich can make it difficult for autonomous\nvehicles to detect them."),
            ("wrong token\n(fog token)", "low visibility caused by fog makes it\ndifficult to see pedestrians clearly,\nincreasing the risk of accidents."),
        ],
    },
    {
        "image": "img_0009_night_unknown_object.png",
        "label": "(b) Night scene — curved road",
        "true_weather": "night",
        "wrong_weather": "rain",
        "rows": [
            ("image+weather\n(night token)", "low visibility due to night conditions makes\nit difficult to clearly see the curve ahead,\nincreasing the risk of collision."),
            ("image only\n(no token)", "The road appears curved, and the darkness\nmakes it difficult to see the road ahead\nclearly, increasing risk of accidents."),
            ("wrong token\n(rain token)", "low visibility due to rain significantly\nreduces the ability to see the road ahead,\nmaking curved road navigation dangerous."),
        ],
    },
]

ROW_COLORS = [
    (220, 240, 220),  # image+weather — green tint
    (230, 230, 250),  # image only — blue tint
    (255, 230, 220),  # wrong token — red tint (highlight)
]
LABEL_COLOR = (50, 50, 50)
WRONG_HIGHLIGHT = (180, 0, 0)


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_figure(image_dir: Path, output_path: Path) -> None:
    img_w = 520
    img_h = 350
    col_label_w = 160
    col_text_w = 500
    row_h = 120
    n_rows = 3
    header_h = 44
    scene_label_h = 40
    padding = 16

    n_samples = len(SAMPLES)
    total_w = padding + n_samples * (img_w + col_label_w + col_text_w + padding)
    total_h = scene_label_h + header_h + n_rows * row_h + padding * 2

    canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    font_title = load_font(19)
    font_label = load_font(17)
    font_text  = load_font(16)
    font_scene = load_font(18)

    for si, sample in enumerate(SAMPLES):
        x0 = padding + si * (img_w + col_label_w + col_text_w + padding)
        y0 = padding

        # scene label
        draw.text((x0 + img_w // 2 - 60, y0), sample["label"], fill=(30, 30, 30), font=font_scene)
        y0 += scene_label_h

        # header row
        draw.rectangle([x0, y0, x0 + img_w, y0 + header_h], fill=(200, 200, 200))
        draw.text((x0 + 8, y0 + 8), "Input Image", fill=LABEL_COLOR, font=font_title)
        draw.rectangle([x0 + img_w, y0, x0 + img_w + col_label_w, y0 + header_h], fill=(180, 180, 180))
        draw.text((x0 + img_w + 6, y0 + 8), "Condition", fill=LABEL_COLOR, font=font_title)
        draw.rectangle([x0 + img_w + col_label_w, y0, x0 + img_w + col_label_w + col_text_w, y0 + header_h], fill=(160, 160, 160))
        draw.text((x0 + img_w + col_label_w + 8, y0 + 8), "Generated Explanation", fill=LABEL_COLOR, font=font_title)
        y0 += header_h

        # image — spans all rows
        img = Image.open(image_dir / sample["image"]).convert("RGB").resize((img_w, row_h * n_rows))
        canvas.paste(img, (x0, y0))

        # rows
        for ri, (cond_label, explanation) in enumerate(sample["rows"]):
            ry = y0 + ri * row_h
            bg = ROW_COLORS[ri]
            draw.rectangle([x0 + img_w, ry, x0 + img_w + col_label_w, ry + row_h], fill=bg)
            draw.rectangle([x0 + img_w + col_label_w, ry, x0 + img_w + col_label_w + col_text_w, ry + row_h], fill=bg)

            # condition label
            text_color = WRONG_HIGHLIGHT if ri == 2 else LABEL_COLOR
            draw.text((x0 + img_w + 6, ry + 8), cond_label, fill=text_color, font=font_label)

            # explanation text
            draw.text((x0 + img_w + col_label_w + 6, ry + 8), explanation, fill=text_color, font=font_text)

            # row border
            draw.line([(x0 + img_w, ry), (x0 + img_w + col_label_w + col_text_w, ry)], fill=(180, 180, 180), width=1)

        # outer border
        draw.rectangle(
            [x0, padding, x0 + img_w + col_label_w + col_text_w, total_h - padding],
            outline=(100, 100, 100), width=2
        )
        # column dividers
        draw.line([(x0 + img_w, y0), (x0 + img_w, y0 + n_rows * row_h)], fill=(150, 150, 150), width=1)
        draw.line([(x0 + img_w + col_label_w, y0), (x0 + img_w + col_label_w, y0 + n_rows * row_h)], fill=(150, 150, 150), width=1)

    canvas.save(output_path, dpi=(300, 300))
    print(f"Saved: {output_path}  ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    image_dir = Path("/home/seong/new_research/icros_workspace/icros_workspace/data/images")
    output_path = Path("/home/seong/new_research/docs/figure_qualitative_comparison.png")
    make_figure(image_dir, output_path)
