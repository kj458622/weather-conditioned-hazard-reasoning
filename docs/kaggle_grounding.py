# ============================================================
# Cell 1: repo clone + 의존성 설치
# ============================================================
import subprocess

subprocess.run(["git", "clone",
    "https://github.com/kj458622/weather-conditioned-hazard-reasoning",
    "/kaggle/working/new_research"], check=True)

subprocess.run(["pip", "install", "-q",
    "bitsandbytes>=0.46.1", "accelerate", "qwen-vl-utils"], check=True)

print("Setup done.")

# ============================================================
# Cell 2: 모델 로드
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

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

run_grounding   = rg.run_grounding
make_comparison = rg.make_comparison
WEATHER_TOKENS  = rg.WEATHER_TOKENS
print("Module loaded. Images:", len(WEATHER_TOKENS), "weather tokens defined.")

# ============================================================
# Cell 4: 실험 실행 (grounding_v5)
# ============================================================
from pathlib import Path
import json

image_dir  = Path("/kaggle/working/new_research/data/images")
output_dir = Path("/kaggle/working/outputs/grounding_v5")
output_dir.mkdir(parents=True, exist_ok=True)

for img_path in sorted(image_dir.glob("*.png")):
    parts = img_path.stem.split("_")
    img_id = parts[0] + "_" + parts[1]
    weather = WEATHER_TOKENS.get(img_id)
    if not weather:
        continue

    print(f"\n[{img_id}] {weather['weather_type']}...")
    sample_dir = output_dir / img_id
    sample_dir.mkdir(exist_ok=True)

    r_no = run_grounding(model, processor, "cuda", str(img_path), None, no_weather=True)
    r_wt = run_grounding(model, processor, "cuda", str(img_path), weather, no_weather=False)

    make_comparison(img_path, r_no, r_wt, weather, sample_dir / "comparison.png")

    # raw + result 저장
    json.dump({"no_token": r_no["prediction"], "with_token": r_wt["prediction"],
               "weather": weather, "bbox_no": r_no["bbox"], "bbox_wt": r_wt["bbox"]},
              open(sample_dir / "result.json", "w"), indent=2)
    json.dump({"no_token_raw": r_no["raw"], "with_token_raw": r_wt["raw"]},
              open(sample_dir / "raw.json", "w"), indent=2, ensure_ascii=False)

    print(f"  no_token  : bbox={r_no['bbox']}  hazard={r_no['prediction'].get('hazard_object','?')}")
    print(f"  with_token: bbox={r_wt['bbox']}  hazard={r_wt['prediction'].get('hazard_object','?')}")

print("\nDone.")

# ============================================================
# Cell 5: 결과 시각화
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

for sample_dir in sorted(output_dir.iterdir()):
    comp = sample_dir / "comparison.png"
    if comp.exists():
        img = Image.open(comp)
        plt.figure(figsize=(16, 5))
        plt.imshow(img)
        plt.axis("off")
        plt.title(sample_dir.name)
        plt.tight_layout()
        plt.show()

# ============================================================
# Cell 6: raw 출력 확인 (포맷 디버깅)
# ============================================================
for sample_dir in sorted(output_dir.iterdir()):
    raw_path = sample_dir / "raw.json"
    if raw_path.exists():
        data = json.loads(raw_path.read_text())
        print(f"\n=== {sample_dir.name} ===")
        print("no_token :", data.get("no_token_raw", "")[:200])
        print("with_token:", data.get("with_token_raw", "")[:200])
