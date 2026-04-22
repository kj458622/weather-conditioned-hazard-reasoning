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
# Cell 2: 모델 로드 (7B)
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    quantization_config=bnb,
    attn_implementation="eager",
    device_map="auto",
)
model.eval()
print(f"Model loaded. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# ============================================================
# Cell 3: 모듈 로드
# ============================================================
import sys, importlib
sys.path.insert(0, "/kaggle/working/new_research/src")
import run_grounding as rg
importlib.reload(rg)

run_grounding_sample = rg.run_grounding_sample
make_comparison      = rg.make_comparison
N_SAMPLES            = rg.N_SAMPLES

print(f"Module loaded. N_SAMPLES={N_SAMPLES}")

# ============================================================
# Cell 4: img_0015 / img_0016 실험 (7B, grounding_v7_7B에 추가)
# ============================================================
from pathlib import Path
import json

image_dir  = Path("/kaggle/working/new_research/data/images")
output_dir = Path("/kaggle/working/outputs/grounding_v7_7B")
output_dir.mkdir(parents=True, exist_ok=True)

TARGET = {
    "img_0015": {"weather_type": "fog", "visibility": "low", "illumination": "day", "road_condition": "clear"},
    "img_0016": {"weather_type": "fog", "visibility": "low", "illumination": "day", "road_condition": "clear"},
}

for img_id, weather in TARGET.items():
    matches = sorted(image_dir.glob(f"{img_id}_*.png"))
    if not matches:
        print(f"[{img_id}] image not found, skip.")
        continue
    img_path = str(matches[0])

    print(f"\n[{img_id}] fog  —  {N_SAMPLES} samples × 2 modes")
    out_dir = output_dir / img_id

    best_no = run_grounding_sample(model, processor, "cuda", img_path,
                                   weather, use_weather=False, out_dir=out_dir)
    best_wt = run_grounding_sample(model, processor, "cuda", img_path,
                                   weather, use_weather=True,  out_dir=out_dir)

    make_comparison(Path(img_path), best_no, best_wt, weather,
                    out_dir / "comparison_best.png")

    json.dump({
        "img_id": img_id, "weather": weather,
        "no_weather": {"bbox": best_no["bbox"], "prediction": best_no["prediction"]},
        "with_token": {"bbox": best_wt["bbox"], "prediction": best_wt["prediction"]},
    }, open(out_dir / "summary.json", "w"), indent=2, ensure_ascii=False)

print("\nDone.")

# ============================================================
# Cell 5: 결과 시각화
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

for img_id in TARGET:
    comp = output_dir / img_id / "comparison_best.png"
    if comp.exists():
        img = Image.open(comp)
        plt.figure(figsize=(16, 5))
        plt.imshow(img)
        plt.axis("off")
        plt.title(img_id)
        plt.tight_layout()
        plt.show()

# ============================================================
# Cell 6: raw 확인
# ============================================================
for img_id in TARGET:
    for tag in ["no_weather", "with_token"]:
        rjson = output_dir / img_id / tag / "results.json"
        if rjson.exists():
            data = json.loads(rjson.read_text())
            print(f"\n=== {img_id} / {tag} ===")
            print("Best hazard:", data["best"].get("hazard_object", "?"),
                  " | bbox:", data["bbox"])
            if data.get("all_raws"):
                print("Sample 1 raw:", data["all_raws"][0][:200])
