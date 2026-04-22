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
sys.path.insert(0, f"{REPO_DIR}/src")
import run_grounding as rg
importlib.reload(rg)

make_comparison      = rg.make_comparison
run_grounding_sample = rg.run_grounding_sample

from pathlib import Path
import json

image_dir = Path(REPO_DIR) / "data/images"

TARGET = {
    "img_0017": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0018": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0019": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
    "img_0020": {"weather_type": "snow", "visibility": "low", "illumination": "day", "road_condition": "slippery"},
}

print("Module loaded.")

# ============================================================
# Cell 3: A) 기존 결과 색 버그 수정 재렌더링 (실험 없음)
# zip 안에 있는 결과를 /kaggle/working/outputs/ 에 먼저 풀어야 함
# ============================================================
import shutil

# 기존 결과 경로 (zip 풀어놓은 위치에 맞게 수정)
EXISTING = {
    "3B": Path("/kaggle/working/outputs/grounding_snow_3B/grounding_snow_3B"),
    "7B": Path("/kaggle/working/outputs/grounding_snow_7B/grounding_snow_7B"),
}

for label, base in EXISTING.items():
    if not base.exists():
        print(f"[{label}] 경로 없음, skip: {base}")
        continue
    print(f"\n[{label}] 재렌더링 중...")
    for img_id, weather in TARGET.items():
        summary_f = base / img_id / "summary.json"
        if not summary_f.exists():
            print(f"  [{img_id}] summary.json 없음, skip.")
            continue
        d = json.loads(summary_f.read_text())

        img_path = sorted(image_dir.glob(f"{img_id}_*.png"))
        if not img_path:
            print(f"  [{img_id}] image not found, skip.")
            continue

        r_no = {"bbox": d["no_weather"]["bbox"], "prediction": d["no_weather"]["prediction"]}
        r_wt = {"bbox": d["with_token"]["bbox"], "prediction": d["with_token"]["prediction"]}

        make_comparison(img_path[0], r_no, r_wt, weather,
                        base / img_id / "comparison_best.png")
        print(f"  [{img_id}] rerendered → comparison_best.png")

print("\nRerender done.")

# ============================================================
# Cell 4: B) img_0017 / img_0018 재실험 (N=10, 3B + 7B)
# ============================================================
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

RERUN_TARGET = {
    "img_0017": TARGET["img_0017"],
    "img_0018": TARGET["img_0018"],
}
N_RERUN = 10

def run_experiment(model_name, output_dir, n_samples):
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

    for img_id, weather in RERUN_TARGET.items():
        matches = sorted(image_dir.glob(f"{img_id}_*.png"))
        if not matches:
            print(f"[{img_id}] image not found, skip.")
            continue
        img_path = str(matches[0])

        print(f"\n[{img_id}] snow — {n_samples} samples × 2 modes")
        out_dir = output_dir / img_id

        best_no = run_grounding_sample(model, processor, "cuda", img_path,
                                       weather, use_weather=False, out_dir=out_dir,
                                       n_samples=n_samples)
        best_wt = run_grounding_sample(model, processor, "cuda", img_path,
                                       weather, use_weather=True, out_dir=out_dir,
                                       n_samples=n_samples)

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


run_experiment("Qwen/Qwen2.5-VL-3B-Instruct",
               "/kaggle/working/outputs/grounding_snow_rerun_3B", N_RERUN)

run_experiment("Qwen/Qwen2.5-VL-7B-Instruct",
               "/kaggle/working/outputs/grounding_snow_rerun_7B", N_RERUN)

# ============================================================
# Cell 5: 결과 요약
# ============================================================
print("\n" + "="*60)
print("RERUN RESULTS  (N=10)")
print("="*60)

for label, out_base in [("3B", "/kaggle/working/outputs/grounding_snow_rerun_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_snow_rerun_7B")]:
    print(f"\n[{label}]")
    for img_id in RERUN_TARGET:
        s = Path(out_base) / img_id / "summary.json"
        if s.exists():
            d = json.loads(s.read_text())
            no = d["no_weather"]; wt = d["with_token"]
            print(f"  {img_id} no_weather: hazard={no['prediction'].get('hazard_object','?')[:25]:25s} bbox={no['bbox']}")
            print(f"  {img_id} with_token: hazard={wt['prediction'].get('hazard_object','?')[:25]:25s} bbox={wt['bbox']}")

# ============================================================
# Cell 6: 시각화 (재렌더링 + 재실험 모두)
# ============================================================
from PIL import Image
import matplotlib.pyplot as plt

# A) 재렌더링 결과
for label, base in EXISTING.items():
    for img_id in TARGET:
        comp = base / img_id / "comparison_best.png"
        if comp.exists():
            plt.figure(figsize=(16, 5))
            plt.imshow(Image.open(comp))
            plt.axis("off")
            plt.title(f"[Rerendered] {img_id} — {label}")
            plt.tight_layout()
            plt.show()

# B) 재실험 결과
for label, out_base in [("3B", "/kaggle/working/outputs/grounding_snow_rerun_3B"),
                         ("7B", "/kaggle/working/outputs/grounding_snow_rerun_7B")]:
    for img_id in RERUN_TARGET:
        comp = Path(out_base) / img_id / "comparison_best.png"
        if comp.exists():
            plt.figure(figsize=(16, 5))
            plt.imshow(Image.open(comp))
            plt.axis("off")
            plt.title(f"[Rerun N=10] {img_id} — {label}")
            plt.tight_layout()
            plt.show()

# ============================================================
# Cell 7: zip 압축
# ============================================================
import zipfile, datetime

timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

zip_targets = [
    ("rerender_3B", EXISTING["3B"]),
    ("rerender_7B", EXISTING["7B"]),
    ("rerun_3B",    Path("/kaggle/working/outputs/grounding_snow_rerun_3B")),
    ("rerun_7B",    Path("/kaggle/working/outputs/grounding_snow_rerun_7B")),
]

from IPython.display import FileLink, display

for name, src_dir in zip_targets:
    if not src_dir.exists():
        continue
    zip_path = Path(f"/kaggle/working/snow_{name}_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in src_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(src_dir.parent))
    print(f"Saved: {zip_path}  ({zip_path.stat().st_size/1e6:.1f} MB)")
    display(FileLink(str(zip_path).replace("/kaggle/working/", "")))
