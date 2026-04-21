"""
Weather-conditioned hazard grounding experiment.
Qwen2.5-VL로 위험 객체의 bounding box를 추출하고 시각화.

실행:
  python run_grounding.py --image_dir ../data/images --output_dir ../outputs/grounding
"""

from __future__ import annotations

import json
import re
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

from PIL import Image, ImageDraw, ImageFont


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

WEATHER_TOKENS = {
    "img_0001": {"weather_type": "snow",  "visibility": "low",    "illumination": "day",   "road_condition": "slippery"},
    "img_0002": {"weather_type": "snow",  "visibility": "low",    "illumination": "day",   "road_condition": "slippery"},
    "img_0003": {"weather_type": "snow",  "visibility": "medium", "illumination": "day",   "road_condition": "slippery"},
    "img_0004": {"weather_type": "rain",  "visibility": "low",    "illumination": "day",   "road_condition": "wet"},
    "img_0005": {"weather_type": "rain",  "visibility": "medium", "illumination": "day",   "road_condition": "wet"},
    "img_0006": {"weather_type": "rain",  "visibility": "low",    "illumination": "day",   "road_condition": "wet"},
    "img_0007": {"weather_type": "fog",   "visibility": "low",    "illumination": "day",   "road_condition": "clear"},
    "img_0008": {"weather_type": "fog",   "visibility": "medium", "illumination": "day",   "road_condition": "clear"},
    "img_0009": {"weather_type": "night", "visibility": "low",    "illumination": "night", "road_condition": "clear"},
    "img_0010": {"weather_type": "night", "visibility": "low",    "illumination": "night", "road_condition": "clear"},
    "img_0011": {"weather_type": "fog",   "visibility": "low",    "illumination": "day",   "road_condition": "clear"},
    "img_0012": {"weather_type": "fog",   "visibility": "low",    "illumination": "day",   "road_condition": "clear"},
    "img_0013": {"weather_type": "fog",   "visibility": "low",    "illumination": "day",   "road_condition": "clear"},
    "img_0014": {"weather_type": "fog",   "visibility": "low",    "illumination": "day",   "road_condition": "clear"},
}


def load_font(size=20):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def parse_bbox(text: str, img_w: int, img_h: int):
    """
    Qwen2.5-VL grounding 출력에서 bounding box 파싱.
    형식: <|box_start|>(x1,y1),(x2,y2)<|box_end|>  또는 [x1,y1,x2,y2] (0~1000 normalized)
    """
    # Qwen normalized format: (x1,y1),(x2,y2) in 0-1000 range
    pattern = r'\((\d+),(\d+)\),\((\d+),(\d+)\)'
    matches = re.findall(pattern, text)
    if matches:
        x1, y1, x2, y2 = [int(v) for v in matches[0]]
        return (
            int(x1 / 1000 * img_w),
            int(y1 / 1000 * img_h),
            int(x2 / 1000 * img_w),
            int(y2 / 1000 * img_h),
        )

    # fallback: JSON array [x1,y1,x2,y2]
    pattern2 = r'\[(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*)\]'
    matches2 = re.findall(pattern2, text)
    if matches2:
        x1, y1, x2, y2 = [float(v) for v in matches2[0]]
        if max(x1, y1, x2, y2) <= 1.0:
            return int(x1*img_w), int(y1*img_h), int(x2*img_w), int(y2*img_h)
        return int(x1), int(y1), int(x2), int(y2)

    return None


def draw_result(image_path: str, bbox, label: str, risk: str,
                explanation: str, out_path: Path, condition: str,
                badge_color: tuple):
    img = Image.open(image_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    font_label = load_font(22)
    font_small = load_font(18)

    # bounding box
    if bbox:
        x1, y1, x2, y2 = bbox
        color = (255, 80, 80) if "no" in condition.lower() else (80, 220, 80)
        for t in range(4):
            draw.rectangle([x1-t, y1-t, x2+t, y2+t], outline=color)
        # label above box
        draw.rectangle([x1, y1-30, x1+len(label)*13+10, y1], fill=color)
        draw.text((x1+5, y1-28), label, fill=(0,0,0), font=font_label)

    # bottom panel
    panel_h = 110
    panel_y = H - panel_h
    draw.rectangle([0, panel_y, W, H], fill=(20, 20, 20))

    # condition badge
    draw.rectangle([0, panel_y, W, panel_y+34], fill=badge_color)
    draw.text((10, panel_y+6), condition, fill=(255,255,255), font=font_label)

    # explanation (wrap)
    words = explanation.split()
    line, lines = [], []
    for w in words:
        test = " ".join(line + [w])
        if font_small.getlength(test) > W - 20:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))

    y = panel_y + 38
    for ln in lines[:3]:
        draw.text((10, y), ln, fill=(220, 220, 220), font=font_small)
        y += 22

    img.save(out_path, dpi=(300,300))


def run_grounding(model, processor, device, image_path: str,
                  weather_token: Optional[Dict], no_weather: bool = False) -> Dict[str, Any]:
    """Qwen2.5-VL grounding 추론."""
    import torch
    from PIL import Image as PILImage

    img = PILImage.open(image_path).convert("RGB")
    MAX_SIZE = 640
    if max(img.size) > MAX_SIZE:
        ratio = MAX_SIZE / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)))
    W, H = img.size

    if no_weather:
        user_text = (
            "Identify the single most dangerous object for the ego vehicle in this driving scene.\n"
            "Reply ONLY in this format:\n"
            "HAZARD: <object name>\n"
            "RISK: <high or medium or low>\n"
            "BOX: <x1>,<y1>,<x2>,<y2> in pixel coordinates\n"
            "EXPLANATION: <why this object is dangerous in this scene>"
        )
    else:
        wt = weather_token
        user_text = (
            f"Weather: {wt.get('weather_type','?')}, visibility: {wt.get('visibility','?')}, road: {wt.get('road_condition','?')}.\n"
            "Identify the single most dangerous object for the ego vehicle given the weather condition.\n"
            "Reply ONLY in this format:\n"
            "HAZARD: <object name>\n"
            "RISK: <high or medium or low>\n"
            "BOX: <x1>,<y1>,<x2>,<y2> in pixel coordinates\n"
            "EXPLANATION: <why this object is dangerous AND how the weather makes it more dangerous>"
        )

    messages = [
        {"role": "user", "content": [
            {"type": "image", "image": img},
            {"type": "text",  "text": user_text},
        ]},
    ]

    chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(
        text=[chat_text], images=[img],
        return_tensors="pt",
        max_pixels=640*640,
    )
    inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

    with torch.no_grad():
        generated = model.generate(**inputs, max_new_tokens=150, do_sample=False)

    trimmed = generated[:, inputs["input_ids"].shape[-1]:]
    decoded = processor.batch_decode(trimmed, skip_special_tokens=True,
                                     clean_up_tokenization_spaces=True)
    raw = decoded[0] if decoded else ""

    # 파싱: HAZARD/RISK/BOX/EXPLANATION 형식
    hazard = "unknown"
    risk   = "unknown"
    bbox   = None
    explanation = raw[:200]

    m = re.search(r'HAZARD:\s*(.+)', raw)
    if m: hazard = m.group(1).strip()

    m = re.search(r'RISK:\s*(.+)', raw)
    if m: risk = m.group(1).strip().lower()

    m = re.search(r'BOX:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', raw)
    if m:
        x1, y1, x2, y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        # padding 20% to make bbox more visible
        pad_x = int((x2 - x1) * 0.2)
        pad_y = int((y2 - y1) * 0.2)
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(W, x2 + pad_x)
        y2 = min(H, y2 + pad_y)
        if x2 > x1 and y2 > y1:
            bbox = (x1, y1, x2, y2)

    m = re.search(r'EXPLANATION:\s*(.+)', raw, re.DOTALL)
    if m: explanation = m.group(1).strip()[:300]

    result = {"hazard_object": hazard, "risk_level": risk, "explanation": explanation}
    return {"bbox": bbox, "prediction": result, "raw": raw}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir",  default="../data/images")
    parser.add_argument("--output_dir", default="../outputs/grounding")
    parser.add_argument("--model_name", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--device",     default=None)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    from transformers import BitsAndBytesConfig

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    processor = AutoProcessor.from_pretrained(args.model_name, trust_remote_code=True)
    model = AutoModelForImageTextToText.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        quantization_config=bnb,
        attn_implementation="eager",
        device_map="auto",
    )
    model.eval()
    print("Model loaded.")

    image_dir  = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(image_dir.glob("*.png"))
    print(f"Found {len(images)} images.")

    for img_path in images:
        img_id = img_path.stem.split("_")[0] + "_" + img_path.stem.split("_")[1]
        weather = WEATHER_TOKENS.get(img_id)
        if not weather:
            print(f"  [{img_id}] No weather token, skip.")
            continue

        print(f"\n[{img_id}] Processing...")
        sample_dir = output_dir / img_id
        sample_dir.mkdir(exist_ok=True)

        # no token
        print(f"  no token...")
        r_no = run_grounding(model, processor, device, str(img_path),
                             weather_token=None, no_weather=True)
        draw_result(
            str(img_path), r_no["bbox"],
            label=r_no["prediction"].get("hazard_object", "?"),
            risk=r_no["prediction"].get("risk_level", "?"),
            explanation=r_no["prediction"].get("explanation", ""),
            out_path=sample_dir / "no_token.png",
            condition="Without Weather Token",
            badge_color=(80, 80, 160),
        )

        # with token
        print(f"  with token ({weather['weather_type']})...")
        r_wt = run_grounding(model, processor, device, str(img_path),
                             weather_token=weather, no_weather=False)
        draw_result(
            str(img_path), r_wt["bbox"],
            label=r_wt["prediction"].get("hazard_object", "?"),
            risk=r_wt["prediction"].get("risk_level", "?"),
            explanation=r_wt["prediction"].get("explanation", ""),
            out_path=sample_dir / "with_token.png",
            condition=f"With Weather Token  ({weather['weather_type']} · {weather['visibility']} vis · {weather['road_condition']} road)",
            badge_color=(50, 140, 60),
        )

        # side-by-side comparison figure
        make_comparison(img_path, r_no, r_wt, weather, sample_dir / "comparison.png")

        # save JSON
        json.dump({"no_token": r_no["prediction"], "with_token": r_wt["prediction"],
                   "weather": weather,
                   "bbox_no": r_no["bbox"], "bbox_wt": r_wt["bbox"]},
                  open(sample_dir / "result.json", "w"), indent=2)
        # save raw outputs for debugging
        json.dump({"no_token_raw": r_no["raw"], "with_token_raw": r_wt["raw"]},
                  open(sample_dir / "raw.json", "w"), indent=2, ensure_ascii=False)
        print(f"  Saved to {sample_dir}")

    print("\nDone.")


def make_comparison(img_path: Path, r_no: dict, r_wt: dict,
                    weather: dict, out_path: Path):
    """No token / With token 나란히 비교 figure."""
    from PIL import Image as PILImage, ImageDraw, ImageFont

    img = PILImage.open(img_path).convert("RGB")
    W, H = img.size
    TARGET_W = 700
    scale = TARGET_W / W
    TARGET_H = int(H * scale)
    img = img.resize((TARGET_W, TARGET_H))

    font_badge   = load_font(22)
    font_body    = load_font(18)
    font_title   = load_font(24)

    PANEL_H = 180
    TITLE_H = 50
    GAP = 12
    TOTAL_W = TARGET_W * 2 + GAP * 3
    TOTAL_H = TITLE_H + TARGET_H + PANEL_H + GAP * 2

    canvas = PILImage.new("RGB", (TOTAL_W, TOTAL_H), (240, 240, 240))
    draw   = ImageDraw.Draw(canvas)

    # title bar
    draw.rectangle([0, 0, TOTAL_W, TITLE_H], fill=(30, 30, 30))
    draw.text((GAP, 12), f"Grounding Comparison  |  {img_path.stem}  |  weather: {weather['weather_type']}",
              fill=(255,255,255), font=font_title)

    def draw_panel(x_off, img_pil, bbox, pred, condition, badge_color):
        canvas.paste(img_pil, (x_off, TITLE_H + GAP))
        # bbox on img
        if bbox:
            x1,y1,x2,y2 = [int(v*scale) for v in bbox] if max(bbox) > TARGET_W else bbox
            tmp = img_pil.copy()
            d2 = ImageDraw.Draw(tmp)
            color = (255, 60, 60) if "no" in condition.lower() else (60, 220, 60)
            for t in range(4):
                d2.rectangle([x1-t, y1-t, x2+t, y2+t], outline=color)
            hazard_label = pred.get("hazard_object","?")
            d2.rectangle([x1, max(0,y1-30), x1+len(hazard_label)*12+10, y1], fill=color)
            d2.text((x1+4, max(0,y1-28)), hazard_label, fill=(0,0,0), font=font_badge)
            canvas.paste(tmp, (x_off, TITLE_H + GAP))

        # panel
        py = TITLE_H + GAP + TARGET_H
        draw.rectangle([x_off, py, x_off+TARGET_W, py+PANEL_H], fill=(20,20,20))
        draw.rectangle([x_off, py, x_off+TARGET_W, py+36], fill=badge_color)
        draw.text((x_off+8, py+7), condition, fill=(255,255,255), font=font_badge)

        expl = pred.get("explanation","")[:400]
        words = expl.split()
        line, lines = [], []
        for w in words:
            test = " ".join(line+[w])
            if font_body.getlength(test) > TARGET_W - 16:
                lines.append(" ".join(line)); line=[w]
            else:
                line.append(w)
        if line: lines.append(" ".join(line))
        y = py + 42
        max_lines = (PANEL_H - 48) // 22
        for ln in lines[:max_lines]:
            draw.text((x_off+8, y), ln, fill=(210,210,210), font=font_body)
            y += 22

    # no token
    draw_panel(GAP, img.copy(), r_no["bbox"], r_no["prediction"],
               "Without Weather Token", (80, 80, 170))
    # with token
    wt_label = f"With Token  ({weather['weather_type']} · {weather['road_condition']})"
    draw_panel(GAP*2 + TARGET_W, img.copy(), r_wt["bbox"], r_wt["prediction"],
               wt_label, (50, 140, 60))

    canvas.save(out_path, dpi=(300,300))


if __name__ == "__main__":
    main()
