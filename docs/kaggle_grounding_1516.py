# ============================================================
# Cell 1: repo pull + 의존성 설치
# ============================================================
import subprocess, os

REPO_DIR = "/kaggle/working/new_research"

if not os.path.exists(REPO_DIR):
    subprocess.run([
        "git", "clone",
        "https://github.com/kj458622/weather-conditioned-hazard-reasoning",
        REPO_DIR
    ], check=True)
else:
    subprocess.run(["git", "pull"], cwd=REPO_DIR, check=True)

subprocess.run(["pip", "install", "-q",
    "bitsandbytes>=0.46.1", "accelerate", "qwen-vl-utils"], check=True)

print("Setup done.")

# ============================================================
# Cell 2: 모듈 로드
# ============================================================
import sys, importlib
sys.path.insert(0, "/kaggle/working/new_research/src")
import run_grounding as rg
importlib.reload(rg)

run_grounding_sample = rg.run_grounding_sample
make_comparison      = rg.make_comparison
N_SAMPLES            = rg.N_SAMPLES

from pathlib import Path
import json

image_dir = Path("/kaggle/working/new_research/data/images")

TARGET = {
    "img_0015": {"weather_type": "fog", "visibility": "low", "illumination": "day", "road_condition": "clear"},
    "img_0016": {"weather_type": "fog", "visibility": "low", "illumination": "day", "road_condition": "clear"},
}

print(f"Module loaded. N_SAMPLES={N_SAMPLES}")

# ============================================================
# Cell 3: 3B 실험 (grounding_v7_3B 에 0015/0016 추가)
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)

print("Loading 3B model...")
processor_3b = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", trust_remote_code=True)
model_3b = AutoModelForImageTextToText.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    trust_remote_code=True, quantization_config=bnb,
    attn_implementation="eager", device_map="auto",
)
model_3b.eval()
print(f"3B loaded. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

output_dir_3b = Path("/kaggle/working/outputs/grounding_v7_3B")
output_dir_3b.mkdir(parents=True, exist_ok=True)

for img_id, weather in TARGET.items():
    matches = sorted(image_dir.glob(f"{img_id}_*.png"))
    if not matches:
        print(f"[{img_id}] image not found, skip."); continue
    img_path = str(matches[0])

    print(f"\n[3B][{img_id}] fog — {N_SAMPLES} samples × 2 modes")
    out_dir = output_dir_3b / img_id

    best_no = run_grounding_sample(model_3b, processor_3b, "cuda", img_path,
                                   weather, use_weather=False, out_dir=out_dir)
    best_wt = run_grounding_sample(model_3b, processor_3b, "cuda", img_path,
                                   weather, use_weather=True,  out_dir=out_dir)

    make_comparison(Path(img_path), best_no, best_wt, weather,
                    out_dir / "comparison_best.png")
    json.dump({
        "img_id": img_id, "weather": weather,
        "no_weather": {"bbox": best_no["bbox"], "prediction": best_no["prediction"]},
        "with_token": {"bbox": best_wt["bbox"], "prediction": best_wt["prediction"]},
    }, open(out_dir / "summary.json", "w"), indent=2, ensure_ascii=False)

# 3B 메모리 해제
del model_3b, processor_3b
torch.cuda.empty_cache()
print("\n3B done. VRAM freed.")

# ============================================================
# Cell 4: 7B 실험 (grounding_v7_7B 에 0015/0016 추가)
# ============================================================
print("Loading 7B model...")
processor_7b = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", trust_remote_code=True)
model_7b = AutoModelForImageTextToText.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    trust_remote_code=True, quantization_config=bnb,
    attn_implementation="eager", device_map="auto",
)
model_7b.eval()
print(f"7B loaded. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

output_dir_7b = Path("/kaggle/working/outputs/grounding_v7_7B")
output_dir_7b.mkdir(parents=True, exist_ok=True)

for img_id, weather in TARGET.items():
    matches = sorted(image_dir.glob(f"{img_id}_*.png"))
    if not matches:
        print(f"[{img_id}] image not found, skip."); continue
    img_path = str(matches[0])

    print(f"\n[7B][{img_id}] fog — {N_SAMPLES} samples × 2 modes")
    out_dir = output_dir_7b / img_id

    best_no = run_grounding_sample(model_7b, processor_7b, "cuda", img_path,
                                   weather, use_weather=False, out_dir=out_dir)
    best_wt = run_grounding_sample(model_7b, processor_7b, "cuda", img_path,
                                   weather, use_weather=True,  out_dir=out_dir)

    make_comparison(Path(img_path), best_no, best_wt, weather,
                    out_dir / "comparison_best.png")
    json.dump({
        "img_id": img_id, "weather": weather,
        "no_weather": {"bbox": best_no["bbox"], "prediction": best_no["prediction"]},
        "with_token": {"bbox": best_wt["bbox"], "prediction": best_wt["prediction"]},
    }, open(out_dir / "summary.json", "w"), indent=2, ensure_ascii=False)

del model_7b, processor_7b
torch.cuda.empty_cache()
print("\n7B done.")

# ============================================================
# Cell 5: 결과 시각화 (3B / 7B 나란히)
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

for img_id in TARGET:
    fig, axes = plt.subplots(1, 2, figsize=(32, 5))
    for ax, (label, out_dir) in zip(axes, [("3B", output_dir_3b), ("7B", output_dir_7b)]):
        comp = out_dir / img_id / "comparison_best.png"
        if comp.exists():
            ax.imshow(Image.open(comp))
        ax.axis("off")
        ax.set_title(f"{img_id} — {label}")
    plt.tight_layout()
    plt.show()

# ============================================================
# Cell 6: raw 확인
# ============================================================
for label, out_dir in [("3B", output_dir_3b), ("7B", output_dir_7b)]:
    for img_id in TARGET:
        for tag in ["no_weather", "with_token"]:
            rjson = out_dir / img_id / tag / "results.json"
            if rjson.exists():
                data = json.loads(rjson.read_text())
                print(f"\n=== [{label}] {img_id} / {tag} ===")
                print("Best hazard:", data["best"].get("hazard_object", "?"),
                      " | bbox:", data["bbox"])
                if data.get("all_raws"):
                    print("Sample 1 raw:", data["all_raws"][0][:200])

# ============================================================
# Cell 7: 결과 zip 압축
# ============================================================
import zipfile, datetime

timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

for label, out_dir in [("3B", output_dir_3b), ("7B", output_dir_7b)]:
    zip_path = Path(f"/kaggle/working/grounding_1516_{label}_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for img_id in TARGET:
            img_dir = out_dir / img_id
            if img_dir.exists():
                for f in img_dir.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(out_dir.parent))
    print(f"Saved: {zip_path}  ({zip_path.stat().st_size/1e6:.1f} MB)")
