"""
Multi-sample grounding experiment for selected images.
각 이미지를 N번 샘플링해서 가장 좋은 bbox 결과를 고른다.
"""

from __future__ import annotations
import json, re, argparse
from pathlib import Path
from typing import Optional, Dict, Any

WEATHER_TOKENS = {
    "img_0001": {"weather_type": "snow",  "visibility": "low",    "illumination": "day", "road_condition": "slippery"},
    "img_0005": {"weather_type": "rain",  "visibility": "low",    "illumination": "day", "road_condition": "wet"},
    "img_0006": {"weather_type": "rain",  "visibility": "low",    "illumination": "day", "road_condition": "wet"},
    "img_0014": {"weather_type": "fog",   "visibility": "low",    "illumination": "day", "road_condition": "clear"},
    "img_0015": {"weather_type": "fog",   "visibility": "low",    "illumination": "day", "road_condition": "clear"},
    "img_0016": {"weather_type": "fog",   "visibility": "low",    "illumination": "day", "road_condition": "clear"},
}

TARGET_MODE = {
    "img_0001": "no_weather",   # snow  - no token
    "img_0005": "with_token",   # rain  - scooter rider
    "img_0006": "with_token",   # rain  - cyclist
    "img_0014": "with_token",   # fog   - car
    "img_0015": "with_token",   # fog   - car
    "img_0016": "with_token",   # fog   - car
}

IMAGE_DIR = Path("/content/drive/MyDrive/icros_workspace/weather-conditioned-hazard-reasoning/data/images")
OUTPUT_DIR = Path("/content/drive/MyDrive/icros_workspace/outputs/grounding_sample")
N_SAMPLES = 5


def load_font(size=20):
    from PIL import ImageFont
    from pathlib import Path
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size=size)
            except: continue
    return ImageFont.load_default()


def parse_result(raw: str, W: int, H: int) -> Dict[str, Any]:
    hazard, risk, bbox, explanation = "unknown", "unknown", None, raw[:300]

    m = re.search(r'HAZARD:\s*(.+)', raw)
    if m: hazard = m.group(1).strip()

    m = re.search(r'RISK:\s*(.+)', raw)
    if m: risk = m.group(1).strip().lower()

    m = re.search(r'BOX:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', raw)
    if m:
        x1,y1,x2,y2 = int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
        pad_x = int((x2-x1)*0.2)
        pad_y = int((y2-y1)*0.2)
        x1,y1 = max(0,x1-pad_x), max(0,y1-pad_y)
        x2,y2 = min(W,x2+pad_x), min(H,y2+pad_y)
        if x2>x1 and y2>y1 and not (x1==0 and y1==0 and x2>=W-5 and y2>=H-5):
            bbox = (x1,y1,x2,y2)

    m = re.search(r'EXPLANATION:\s*(.+)', raw, re.DOTALL)
    if m: explanation = m.group(1).strip()[:400]

    return {"hazard_object": hazard, "risk_level": risk,
            "bbox": bbox, "explanation": explanation, "raw": raw}


def run_once(model, processor, device, img_pil, user_text, temperature=0.7):
    import torch
    W, H = img_pil.size
    messages = [{"role": "user", "content": [
        {"type": "image", "image": img_pil},
        {"type": "text",  "text": user_text},
    ]}]
    chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[chat_text], images=[img_pil], return_tensors="pt", max_pixels=640*640)
    inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

    with torch.no_grad():
        generated = model.generate(
            **inputs, max_new_tokens=150,
            do_sample=True, temperature=temperature, top_p=0.9
        )
    trimmed = generated[:, inputs["input_ids"].shape[-1]:]
    raw = processor.batch_decode(trimmed, skip_special_tokens=True)[0]
    return parse_result(raw, W, H)


def draw_result(img_pil, result, out_path, condition, badge_color):
    from PIL import Image, ImageDraw
    img = img_pil.copy()
    W, H = img.size
    draw = ImageDraw.Draw(img)
    font_l = load_font(22)
    font_s = load_font(18)

    bbox = result["bbox"]
    if bbox:
        x1,y1,x2,y2 = bbox
        color = (60, 220, 60)
        for t in range(4):
            draw.rectangle([x1-t,y1-t,x2+t,y2+t], outline=color)
        label = result["hazard_object"]
        lw = len(label)*12+10
        draw.rectangle([x1, max(0,y1-30), x1+lw, y1], fill=color)
        draw.text((x1+4, max(0,y1-28)), label, fill=(0,0,0), font=font_l)

    PANEL_H = 180
    py = H - PANEL_H
    draw.rectangle([0, py, W, H], fill=(20,20,20))
    draw.rectangle([0, py, W, py+36], fill=badge_color)
    draw.text((10, py+7), condition, fill=(255,255,255), font=font_l)

    expl = result["explanation"][:400]
    words = expl.split()
    line, lines = [], []
    for w in words:
        test = " ".join(line+[w])
        if font_s.getlength(test) > W-20:
            lines.append(" ".join(line)); line=[w]
        else:
            line.append(w)
    if line: lines.append(" ".join(line))
    y = py+42
    for ln in lines[:6]:
        draw.text((10, y), ln, fill=(210,210,210), font=font_s)
        y += 22

    img.save(out_path, dpi=(300,300))


def main():
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig
    from PIL import Image as PILImage

    MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_NAME, trust_remote_code=True,
        quantization_config=bnb, attn_implementation="eager", device_map="auto"
    )
    model.eval()
    print(f"Model loaded. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for img_id, weather in WEATHER_TOKENS.items():
        mode = TARGET_MODE[img_id]
        no_weather = (mode == "no_weather")

        # find image file
        matches = list(IMAGE_DIR.glob(f"{img_id}_*.png"))
        if not matches:
            print(f"[{img_id}] image not found, skip.")
            continue
        img_path = matches[0]

        img = PILImage.open(img_path).convert("RGB")
        MAX_SIZE = 640
        if max(img.size) > MAX_SIZE:
            ratio = MAX_SIZE / max(img.size)
            img = img.resize((int(img.width*ratio), int(img.height*ratio)))

        if no_weather:
            user_text = (
                "Identify the single most dangerous object for the ego vehicle in this driving scene.\n"
                "Reply ONLY in this format:\n"
                "HAZARD: <object name>\n"
                "RISK: <high or medium or low>\n"
                "BOX: <x1>,<y1>,<x2>,<y2> in pixel coordinates\n"
                "EXPLANATION: <why this object is dangerous in this scene>"
            )
            badge_color = (80, 80, 170)
            condition = "Without Weather Token"
        else:
            user_text = (
                f"Weather: {weather['weather_type']}, visibility: {weather['visibility']}, road: {weather['road_condition']}.\n"
                "Identify the single most dangerous object for the ego vehicle given the weather condition.\n"
                "Reply ONLY in this format:\n"
                "HAZARD: <object name>\n"
                "RISK: <high or medium or low>\n"
                "BOX: <x1>,<y1>,<x2>,<y2> in pixel coordinates\n"
                "EXPLANATION: <why this object is dangerous AND how the weather makes it more dangerous>"
            )
            badge_color = (50, 140, 60)
            condition = f"With Weather Token  ({weather['weather_type']} · {weather['road_condition']})"

        sample_dir = OUTPUT_DIR / img_id
        sample_dir.mkdir(exist_ok=True)

        print(f"\n[{img_id}] {weather['weather_type']} | mode={mode} | {N_SAMPLES} samples...")
        results = []
        for i in range(N_SAMPLES):
            r = run_once(model, processor, "cuda", img, user_text, temperature=0.7)
            bbox_ok = r["bbox"] is not None
            print(f"  sample {i+1}: bbox={r['bbox']}  hazard={r['hazard_object']}  {'✓' if bbox_ok else '✗'}")
            r["sample_idx"] = i
            results.append(r)
            draw_result(img, r, sample_dir / f"sample_{i+1}.png", condition, badge_color)

        # bbox 있는 것 중 best 선택 (bbox 크기 가장 적당한 것)
        valid = [r for r in results if r["bbox"] is not None]
        if valid:
            best = max(valid, key=lambda r: (r["bbox"][2]-r["bbox"][0])*(r["bbox"][3]-r["bbox"][1]))
        else:
            best = results[0]

        draw_result(img, best, sample_dir / "best.png", condition, badge_color)
        json.dump({"best": {k:v for k,v in best.items() if k!="raw"},
                   "all_raws": [r["raw"] for r in results]},
                  open(sample_dir / "results.json", "w"), indent=2, ensure_ascii=False)
        print(f"  Best: bbox={best['bbox']}  hazard={best['hazard_object']}")

    print("\nDone.")


if __name__ == "__main__":
    main()
