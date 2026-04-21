# ============================================================
# Cell 1: git pull
# ============================================================
import subprocess
subprocess.run(["git", "-C", "/content/new_research", "pull"], check=True)

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
print("Model loaded.")
print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# ============================================================
# Cell 3: grounding v2 실험 실행  (단순화된 프롬프트)
# ============================================================
import subprocess
result = subprocess.run([
    "python3", "/content/new_research/src/run_grounding.py",
    "--image_dir",  "/content/new_research/icros_workspace/icros_workspace/data/images",
    "--output_dir", "/content/new_research/outputs/grounding_v2",
    "--model_name", MODEL_NAME,
], capture_output=True, text=True)
print(result.stdout[-4000:])   # tail to avoid Colab output truncation
print(result.stderr[-2000:])

# ============================================================
# Cell 4: v2 결과 시각화
# ============================================================
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

grounding_dir = Path("/content/new_research/outputs/grounding_v2")

dirs = sorted(grounding_dir.iterdir()) if grounding_dir.exists() else []
if not dirs:
    print("No results found in", grounding_dir)
for sample_dir in dirs:
    comp = sample_dir / "comparison.png"
    if comp.exists():
        img = Image.open(comp)
        plt.figure(figsize=(16, 5))
        plt.imshow(img)
        plt.axis("off")
        plt.title(sample_dir.name)
        plt.tight_layout()
        plt.show()
    else:
        print(f"[skip] no comparison.png in {sample_dir.name}")

# ============================================================
# Cell 5: raw 출력 확인 (포맷 디버깅용)
# ============================================================
import json
for sample_dir in sorted(grounding_dir.iterdir()):
    raw_path = sample_dir / "raw.json"
    if raw_path.exists():
        data = json.loads(raw_path.read_text())
        print(f"\n=== {sample_dir.name} ===")
        print("no_token :", data.get("no_token_raw", "")[:200])
        print("with_token:", data.get("with_token_raw", "")[:200])
