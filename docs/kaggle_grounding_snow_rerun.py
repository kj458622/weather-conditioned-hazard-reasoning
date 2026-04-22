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
# Cell 2: 모듈 로드 / 실험 대상 정의
# ============================================================
import sys, importlib
sys.path.insert(0, f"{REPO_DIR}/src")
import run_grounding as rg
importlib.reload(rg)

run_grounding_sample = rg.run_grounding_sample
make_comparison      = rg.make_comparison
N_SAMPLES            = rg.N_SAMPLES

from pathlib import Path
import json

image_dir = Path(REPO_DIR) / "data/images"

# snow cyclist 4장 — with_token only
TARGET = {
    "img_0017": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0018": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0019": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0020": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
}

print(f"Targets: {list(TARGET.keys())}  |  N_SAMPLES={N_SAMPLES}")

# ============================================================
# Cell 3: 공통 실험 함수
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

def run_experiment(model_name, output_dir):
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    print(f"\n{'='*60}\nLoading {model_name} ...")
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForImageTextToText.from_pretrained(
        model_name, trust_remote_code=True,
        quantization_config=bnb, attn_implementation="eager", device_map="auto",
    )
    model.eval()
    print(f"Loaded. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_id, weather in TARGET.items():
        matches = sorted(image_dir.glob(f"{img_id}_*.png"))
        if not matches:
            print(f"[{img_id}] image not found, skip.")
            continue
        img_path = str(matches[0])

        print(f"\n[{img_id}] snow — {N_SAMPLES} samples × 2 modes")
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

    del model, processor
    torch.cuda.empty_cache()
    print(f"\n{model_name} done. VRAM freed.")

# ============================================================
# Cell 4: 3B 실험
# ============================================================
run_experiment(
    model_name="Qwen/Qwen2.5-VL-3B-Instruct",
    output_dir="/kaggle/working/outputs/grounding_snow_3B",
)

# ============================================================
# Cell 5: 7B 실험
# ============================================================
run_experiment(
    model_name="Qwen/Qwen2.5-VL-7B-Instruct",
    output_dir="/kaggle/working/outputs/grounding_snow_7B",
)

# ============================================================
# Cell 6: 결과 요약
# ============================================================
print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_snow_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_snow_7B")]:
    print(f"\n[{label}]")
    for img_id in TARGET:
        summary = Path(out_base) / img_id / "summary.json"
        if summary.exists():
            d = json.loads(summary.read_text())
            no = d["no_weather"]
            wt = d["with_token"]
            print(f"  {img_id}  no_weather: hazard={no['prediction'].get('hazard_object','?')[:25]:25s} bbox={no['bbox']}")
            print(f"  {img_id}  with_token: hazard={wt['prediction'].get('hazard_object','?')[:25]:25s} bbox={wt['bbox']}")

# ============================================================
# Cell 7: 시각화
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_snow_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_snow_7B")]:
    for img_id in TARGET:
        comp = Path(out_base) / img_id / "comparison_best.png"
        if comp.exists():
            plt.figure(figsize=(16, 5))
            plt.imshow(Image.open(comp))
            plt.axis("off")
            plt.title(f"{img_id} — {label}")
            plt.tight_layout()
            plt.show()

# ============================================================
# Cell 8: zip 압축
# ============================================================
import zipfile, datetime

timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_snow_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_snow_7B")]:
    zip_path = Path(f"/kaggle/working/grounding_snow_{label}_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in Path(out_base).rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(Path(out_base).parent))
    print(f"Saved: {zip_path}  ({zip_path.stat().st_size/1e6:.1f} MB)")

from IPython.display import FileLink, display
for zip_path in sorted(Path("/kaggle/working").glob("grounding_snow_*.zip")):
    display(FileLink(str(zip_path).replace("/kaggle/working/", "")))
