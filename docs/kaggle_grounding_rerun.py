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

# img_0015/0016 git에 없으면 수동 복사 (Kaggle Dataset으로 업로드한 경우)
import shutil
from pathlib import Path
img_dir = Path(REPO_DIR) / "data/images"
for fname in ["img_0015_fog_car.png", "img_0016_fog_car.png"]:
    dst = img_dir / fname
    if not dst.exists():
        # Kaggle Dataset 업로드 경로에 맞게 수정
        src = Path("/kaggle/input") / fname
        if src.exists():
            shutil.copy(src, dst)
            print(f"Copied {fname}")
        else:
            print(f"WARNING: {fname} not found — upload it via Kaggle Dataset")

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

TARGET = {
    # snow
    "img_0001": {"weather_type": "snow", "visibility": "low",  "illumination": "day", "road_condition": "slippery"},
    # fog
    "img_0011": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
    "img_0012": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
    "img_0013": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
    "img_0014": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
    "img_0015": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
    "img_0016": {"weather_type": "fog",  "visibility": "low",  "illumination": "day", "road_condition": "clear"},
}

print(f"Module loaded. Targets: {list(TARGET.keys())}  |  N_SAMPLES={N_SAMPLES}")


# ============================================================
# Cell 3: 공통 실험 함수
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

def run_experiment(model_name, output_dir):
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    print(f"\n{'='*60}")
    print(f"Loading {model_name} ...")
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

        print(f"\n[{img_id}] {weather['weather_type']}  —  {N_SAMPLES} samples × 2 modes")
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
    output_dir="/kaggle/working/outputs/grounding_rerun_3B",
)

# ============================================================
# Cell 5: 7B 실험
# ============================================================
run_experiment(
    model_name="Qwen/Qwen2.5-VL-7B-Instruct",
    output_dir="/kaggle/working/outputs/grounding_rerun_7B",
)

# ============================================================
# Cell 6: 결과 요약 출력
# ============================================================
print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_rerun_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_rerun_7B")]:
    print(f"\n[{label}]")
    for img_id in TARGET:
        summary = Path(out_base) / img_id / "summary.json"
        if summary.exists():
            d = json.loads(summary.read_text())
            no = d["no_weather"]
            wt = d["with_token"]
            print(f"  {img_id}  no_weather: hazard={no['prediction'].get('hazard_object','?')[:20]:20s} bbox={no['bbox']}")
            print(f"  {img_id}  with_token: hazard={wt['prediction'].get('hazard_object','?')[:20]:20s} bbox={wt['bbox']}")

# ============================================================
# Cell 7: 결과 시각화
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_rerun_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_rerun_7B")]:
    for img_id in TARGET:
        comp = Path(out_base) / img_id / "comparison_best.png"
        if comp.exists():
            img = Image.open(comp)
            plt.figure(figsize=(16, 5))
            plt.imshow(img)
            plt.axis("off")
            plt.title(f"{img_id} — {label}")
            plt.tight_layout()
            plt.show()

# ============================================================
# Cell 8: zip 압축
# ============================================================
import zipfile, datetime

timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_rerun_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_rerun_7B")]:
    zip_path = Path(f"/kaggle/working/grounding_rerun_{label}_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in Path(out_base).rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(Path(out_base).parent))
    print(f"Saved: {zip_path}  ({zip_path.stat().st_size/1e6:.1f} MB)")
