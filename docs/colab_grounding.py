# ============================================================
# Cell 1: git pull + 의존성 설치
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
# Cell 3: grounding 실험 실행
# ============================================================
import sys
sys.path.append("/content/new_research/src")

import subprocess
result = subprocess.run([
    "python3", "/content/new_research/src/run_grounding.py",
    "--image_dir",  "/content/new_research/icros_workspace/icros_workspace/data/images",
    "--output_dir", "/content/new_research/outputs/grounding",
    "--model_name", MODEL_NAME,
], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# ============================================================
# Cell 4: 결과 시각화 (comparison figure 표시)
# ============================================================
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

grounding_dir = Path("/content/new_research/outputs/grounding")

for sample_dir in sorted(grounding_dir.iterdir()):
    comp = sample_dir / "comparison.png"
    if comp.exists():
        img = Image.open(comp)
        plt.figure(figsize=(16, 5))
        plt.imshow(img)
        plt.axis("off")
        plt.title(sample_dir.name)
        plt.tight_layout()
        plt.show()
