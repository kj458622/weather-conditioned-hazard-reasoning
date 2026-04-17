# GPU 서버 실행 가이드

## 1. 목적

이 문서는 현재 프로젝트를 **GPU 서버에서 Qwen2.5-VL 기반으로 실제 실행**하기 위한 최소 설치 및 실행 절차를 정리한다.

현재 로컬 환경은 CPU-only이므로, 실사용 추론과 발표용 결과 생성은 GPU 서버에서 수행하는 것이 현실적이다.

---

## 2. 권장 환경

권장 환경은 다음과 같다.

- OS: Ubuntu 22.04 또는 유사 Linux
- Python: 3.10 ~ 3.12 권장
- CUDA: PyTorch wheel과 호환되는 버전
- GPU:
  - 최소: 24GB VRAM 권장
  - 더 안정적: 40GB 이상

모델 기준:

- `Qwen/Qwen2.5-VL-3B-Instruct`
  - 데모 및 프로토타입용 기본값
- `Qwen/Qwen2.5-VL-7B-Instruct`
  - 비교 실험용
  - 메모리 요구량 증가

---

## 3. 서버 준비

### 3.1 가상환경

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

conda를 쓸 경우:

```bash
conda create -n icros-qwen python=3.11 -y
conda activate icros-qwen
python -m pip install --upgrade pip
```

---

## 4. 패키지 설치

GPU 서버에서는 PyTorch를 먼저 CUDA 호환 wheel로 설치하는 편이 안전하다.

예시:

```bash
python -m pip install torch torchvision
python -m pip install -r requirements.txt
```

주의:

- 실제 설치 전 `nvidia-smi`와 CUDA 호환성 확인 필요
- 환경마다 PyTorch 공식 설치 가이드를 따라 wheel 소스를 조정하는 것이 안전하다
- `python -m pip`를 사용해 인터프리터 혼선을 피한다

---

## 5. Hugging Face 인증

비공개 제한은 없더라도 대형 모델 다운로드 안정성을 위해 로그인해두는 것이 좋다.

```bash
huggingface-cli login
```

또는 환경 변수:

```bash
export HF_TOKEN=your_token_here
```

---

## 6. 설치 확인

```bash
python - <<'PY'
import torch, transformers
from transformers import AutoProcessor
print('torch', torch.__version__)
print('transformers', transformers.__version__)
print('cuda_available', torch.cuda.is_available())
if torch.cuda.is_available():
    print('gpu', torch.cuda.get_device_name(0))
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", trust_remote_code=True)
print('processor', processor.__class__.__name__)
PY
```

---

## 7. 모델 로딩 확인

```bash
python - <<'PY'
import torch
from transformers import AutoModelForImageTextToText

model = AutoModelForImageTextToText.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    trust_remote_code=True,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(type(model).__name__)
print(next(model.parameters()).device)
print(next(model.parameters()).dtype)
PY
```

---

## 8. 프로젝트 실행

### 8.1 샘플 데이터 실행

```bash
python src/run_inference.py \
  --image_dir examples/sample_images \
  --annotation_file examples/sample_annotations.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs_gpu \
  --save_overlay
```

### 8.2 실제 발표 데이터 실행

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs_icros \
  --save_overlay
```

### 8.3 prompt weather mode 실험

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --weather_mode prompt \
  --output_dir outputs_icros_prompt \
  --save_overlay
```

---

## 9. GPU 서버에서 확인할 포인트

- `Model backend: transformers`가 출력되는지 확인
- JSON 파싱 실패가 없는지 확인
- 처리 속도와 GPU 메모리 사용량 기록
- same-image / different-weather 비교 결과 저장
- `outputs_icros/metrics.json` 생성 여부 확인

---

## 10. 권장 실험 순서

### 1단계

- 샘플 3장으로 서버 실행 확인
- 모델 로드 및 추론 정상 여부 확인

### 2단계

- 실제 이미지 10장으로 소규모 테스트
- JSON format 안정성 확인

### 3단계

- 발표용 10~30장 전체 실행
- 대표 qualitative 사례 선별

### 4단계

- 필요 시 7B 비교
- 속도/품질 trade-off 정리

---

## 11. 운영 메모

- 로컬 CPU 환경은 개발 및 구조 검증용으로 충분하지만, 실제 3B/7B 실행은 GPU 서버가 현실적이다.
- ICROS용 결과는 heuristic backend가 아니라 `transformers` backend 결과를 따로 저장해두는 것이 좋다.
- 향후 LoRA를 붙일 경우에도 현재 파일 구조는 그대로 유지 가능하다.

