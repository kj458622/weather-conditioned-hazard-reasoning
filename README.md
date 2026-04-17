# Weather-Conditioned Hazard Reasoning Prototype

## 1. 프로젝트 개요

이 프로젝트의 목표는 자율주행 장면에서 단순히 "무엇이 위험한가"를 설명하는 수준을 넘어서, **악천후 조건 때문에 왜 더 위험한지**를 설명하는 Vision-Language 기반 프로토타입을 구현하는 것이다.

이번 단계는 논문 완성형 시스템이 아니라 **ICROS 포스터 발표용 1차 프로토타입**을 목표로 한다. 따라서 복잡한 학습 파이프라인이나 멀티센서 융합보다는, **camera-only 입력과 weather-conditioned reasoning**이 실제로 동작하는 최소 기능 데모를 우선 구현한다.

핵심 메시지는 다음과 같다.

> 단순한 hazard 설명이 아니라, 환경 조건에 따라 달라지는 위험 설명을 만드는 모델

---

## 2. 연구 목표

기존 hazard reasoning 연구는 일반적으로 위험 객체와 일반적 위험 요인을 설명하는 데 집중해 왔다. 그러나 실제 도로 환경에서는 눈, 안개, 비, 저조도와 같은 악천후 조건이 위험 판단의 강도와 이유를 직접 바꾼다.

본 프로젝트의 목표는 전방 카메라 이미지 1장과 weather token을 함께 입력으로 사용하여 다음 정보를 통합적으로 생성하는 것이다.

- 위험 객체
- 위험 이유
- 악천후 조건
- 악천후가 위험도에 미치는 영향이 반영된 설명

예시 출력:

- 보행자가 차로에 진입 중이며, 눈으로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음
- 앞 차량이 감속 중이며 안개로 인해 시야가 제한되어 안전거리가 더 필요함

---

## 3. 이번 단계의 구현 범위

### 포함 범위

- 단일 전방 카메라 이미지 입력
- 악천후 상태 전처리 모듈
- image + weather token 기반 hazard reasoning
- structured JSON 결과 생성
- 사람이 읽을 수 있는 한글 설명 생성
- 결과 저장 및 간단한 시각화
- 간단 평가 기능

### 제외 범위

- LiDAR 입력
- end-to-end fine-tuning
- 대규모 데이터셋 구축
- 센서 신뢰도 추정
- 복잡한 웹 UI
- 분산 학습
- 실시간 주행 시스템

---

## 4. 모델 기본 방향

베이스 모델은 **Qwen2.5-VL 계열**을 사용한다.

- 기본 모델: `Qwen/Qwen2.5-VL-3B-Instruct`
- 확장 가능 모델: `Qwen/Qwen2.5-VL-7B-Instruct`

3B 모델을 기본값으로 두는 이유는 최소 기능 프로토타입을 현실적으로 구현하기에 적절하기 때문이다. 다만 코드 구조는 향후 7B 또는 다른 VLM으로 쉽게 교체할 수 있도록 **모델 로딩과 추론 로직을 추상화**해야 한다.

---

## 5. 시스템 파이프라인

전체 시스템은 다음 순서로 동작한다.

1. 이미지 파일 입력
2. weather preprocessing 수행
3. 이미지와 weather token을 함께 VLM에 입력
4. structured hazard reasoning 생성
5. 한글 free-text 설명 생성
6. 결과 JSON 및 시각화 저장

이 구조는 현재 단계에서는 weather token을 외부에서 주입하지만, 이후 단계에서는 모델이 직접 weather를 추론하는 end-to-end 구조로 확장할 수 있도록 설계한다.

---

## 6. 입력 데이터 포맷

입력은 이미지 파일 경로 리스트 또는 annotation 파일 기반으로 처리한다.

지원 이미지 형식:

- `jpg`
- `jpeg`
- `png`

예시 폴더 구조:

```text
data/
  images/
    img_0001.jpg
    img_0002.jpg
  metadata/
    labels.csv
```

---

## 7. Weather Preprocessing 모듈 설계

weather preprocessing 모듈은 이미지에 대응하는 날씨 정보를 structured token으로 반환한다.

예시:

```json
{
  "weather_type": "snow",
  "visibility": "low",
  "illumination": "day",
  "road_condition": "unclear"
}
```

### 지원 모드

#### 1) Manual / Rule-Based Mode

- CSV 또는 JSON에 미리 정의된 weather token 사용
- 이번 단계의 기본 모드
- 모델 추론 실패 여부와 무관하게 전체 파이프라인이 항상 동작하도록 보장

#### 2) Model-Prompt Mode

- 같은 Qwen2.5-VL 또는 별도 간단한 프롬프트를 사용해 weather token 추론
- optional 기능
- 실패 시 manual mode 또는 기본값으로 fallback

이 모듈은 reasoning 모듈과 분리하여, 향후 weather preprocessing 제거 또는 end-to-end 모델 통합이 가능하도록 구성한다.

---

## 8. Hazard Reasoning 모듈 설계

reasoning 모듈은 이미지와 weather token을 함께 입력으로 받아 위험 객체, 위험 수준, 위험 이유, 자연어 설명을 생성한다.

### 입력

- 이미지
- weather token

### 출력 1: Structured JSON

```json
{
  "hazard_object": "pedestrian",
  "risk_level": "high",
  "reason": "pedestrian entering ego lane under low visibility",
  "explanation": "보행자가 차로에 진입 중이며, 눈으로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음"
}
```

### 출력 2: Free-Text Output

- 사람이 바로 읽을 수 있는 한글 설명문
- 필요하면 structured JSON 결과를 바탕으로 후처리 생성

이번 단계에서는 **structured output을 우선**으로 두고, free-text는 그 결과를 정리하는 방식으로 구현한다.

---

## 9. 프롬프트 설계 원칙

프롬프트는 단순 장면 설명이 아니라 **악천후가 위험 판단에 어떤 영향을 주는지**를 반드시 반영해야 한다.

핵심 원칙:

- 객체 나열이 아니라 위험 이유 설명
- weather condition 반영
- 짧고 명확한 설명
- JSON 우선 출력

예시 시스템 프롬프트:

```text
You are an autonomous-driving hazard reasoning assistant.
Use both the image and the provided weather conditions.
Explain why the scene is risky under the given adverse-weather condition.
Return structured JSON only.
```

예시 입력:

```json
{
  "image": "<image>",
  "weather_type": "snow",
  "visibility": "low",
  "illumination": "day",
  "road_condition": "unclear"
}
```

---

## 10. 최소 데이터셋 포맷

초기 프로토타입은 10~30개 정도의 소규모 샘플셋으로도 실행 가능해야 한다.

샘플 annotation 형식:

```json
{
  "id": "img_0001",
  "image_path": "data/images/img_0001.jpg",
  "weather": {
    "weather_type": "snow",
    "visibility": "low",
    "illumination": "day",
    "road_condition": "unclear"
  },
  "target": {
    "hazard_object": "pedestrian",
    "risk_level": "high",
    "reason": "pedestrian entering ego lane under low visibility",
    "explanation_ko": "보행자가 차로에 진입 중이며, 눈으로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음"
  }
}
```

초기 샘플셋은 다음 유형을 포함하는 것이 바람직하다.

- 보행자 차로 진입
- 전방 차량 감속
- 차선 식별 불명확
- 교차로 접근
- 안개, 눈, 비, 저조도 조합

---

## 11. 구현 파일 구성

### 필수 파일

- `README.md`
- `requirements.txt`
- `src/run_inference.py`
- `src/weather_preprocess.py`
- `src/prompting.py`
- `src/utils.py`
- `examples/sample_annotations.json`
- `examples/sample_outputs/`

### 옵션 파일

- `src/evaluate.py`
- `src/build_dataset_template.py`

---

## 12. 실행 기능 요구사항

`run_inference.py`는 아래 인자를 지원해야 한다.

### 입력

- 이미지 폴더 경로
- annotation JSON 또는 CSV 경로
- 출력 폴더 경로
- 모델명 인자

### 출력

- 이미지별 structured JSON 결과
- 이미지별 free-text 결과
- optional overlay 시각화 이미지

예시 실행:

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file examples/sample_annotations.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs
```

---

## 13. 평가 계획

이번 최소 구현에서는 복잡한 정량 평가 대신 아래 항목부터 구현한다.

### 1) Format Validity

- JSON 파싱 성공률

### 2) Simple Text Overlap

- target explanation과 생성 explanation 간 BLEU 또는 ROUGE-L

### 3) Structured Field Accuracy

- `hazard_object` accuracy
- `risk_level` accuracy

이 평가는 논문 수준 성능 검증이 아니라, 프로토타입의 동작 안정성과 발표용 데모 품질을 확인하기 위한 기준이다.

---

## 14. 코드 설계 원칙

코드는 다음 조건을 만족해야 한다.

- 모듈 구조를 명확히 분리
- weather module과 reasoning module 분리
- 상세 주석 포함
- 함수 단위 책임 분리
- 실패 시 친절한 에러 메시지 제공
- GPU가 없을 때 CPU fallback 지원
- 모델 교체가 쉽도록 추상화
- manual weather token만으로 전체 시스템 동작 가능

핵심은 **지금 당장 돌아가는 최소 기능**과 **향후 확장 가능성**을 동시에 확보하는 것이다.

---

## 15. 단계별 우선순위

구현 우선순위는 다음과 같다.

1. manual weather token 기반 end-to-end inference
2. structured JSON 출력
3. free-text 설명 생성
4. 간단 평가
5. optional weather preprocessor prompt mode

애매한 부분은 더 단순한 구현을 선택하고, 그 판단은 README 또는 코드 주석에 명시한다.

---

## 16. 개발 일정 제안

### 1단계: 골격 구현

- 폴더 구조 생성
- annotation 포맷 정의
- manual weather token 로딩 구현
- CLI 인터페이스 구성

### 2단계: VLM reasoning 연결

- Qwen2.5-VL 모델 로딩
- image + weather token prompt 구성
- JSON 출력 안정화
- 한글 설명 생성

### 3단계: 결과 저장 및 평가

- 출력 JSON 저장
- 시각화 이미지 저장
- BLEU/ROUGE-L 구현
- structured accuracy 계산

### 4단계: 데모 정리

- 대표 예시 샘플 구성
- weather token 변화에 따른 설명 차이 비교
- 포스터용 qualitative 사례 정리

---

## 17. 기대 시연 결과

최종적으로 다음 흐름을 실제로 보여줄 수 있어야 한다.

1. 이미지 1장 입력
2. weather token 주입
3. structured hazard reasoning 생성
4. 한글 설명 생성
5. 결과 저장

ICROS 포스터에서는 특히 같은 장면에 대해 weather token을 다르게 주입했을 때 reasoning 문장이 어떻게 달라지는지를 보여주는 것이 중요하다.

---

## 18. 한계 및 리스크

이번 단계의 예상 한계는 다음과 같다.

- 소규모 데이터셋으로 인해 일반화 성능이 제한적
- 프롬프트 기반 JSON 출력이 불안정할 수 있음
- weather token 품질이 reasoning 품질에 직접 영향
- 실제 안전성 검증 수준까지는 도달하지 않음

대응 방안:

- JSON 우선 출력 강제
- 파싱 실패 시 fallback 처리
- manual mode를 기본 경로로 유지
- README에 구현 한계 명시

---

## 19. 향후 연구 확장 계획

### Phase 1. Weather-Conditioned Hazard Reasoning

- image + weather token -> reasoning
- camera-only
- manual label 기반
- prompt-based 또는 lightweight tuning 가능성 탐색

### Phase 2. End-to-End Weather-Aware VLM

- weather preprocessing 제거
- 모델이 직접 weather 추론
- Qwen2.5-VL 기반 SFT / LoRA 적용
- larger dataset 구축

### Phase 3. Multi-Modal Sensor-Aware Reasoning

- image + LiDAR 확장
- sensor degradation modeling
- object-level uncertainty 반영
- perception -> reasoning 구조 강화

### Phase 4. Uncertainty-Aware Explanation

- 왜 위험한지뿐 아니라 얼마나 불확실한지 설명
- 예: 가시성이 낮아 객체 인식이 불완전하여 위험도가 증가함

### Phase 5. Decision-Level Integration

- reasoning과 planning 연계
- risk-aware decision model로 확장

---

## 20. 결론

본 프로젝트는 악천후 환경을 반영하여 자율주행 장면의 위험 이유를 설명하는 Vision-Language 기반 hazard reasoning 프로토타입을 만드는 것을 목표로 한다.

현재 단계의 핵심은 다음 세 가지다.

- image + weather token 기반 end-to-end 동작
- structured JSON 결과 생성
- 발표에서 바로 시연 가능한 예시 저장

즉, 이번 구현은 완성형 연구보다 **실제로 보여줄 수 있는 최소 기능 데모**에 집중한다. 이후 이 구조를 바탕으로 end-to-end weather-aware VLM, 멀티모달 reasoning, uncertainty-aware explanation으로 확장할 수 있다.

---

## 21. 현재 구현 상태

현재 저장소에는 아래 기능이 구현되어 있다.

- `manual` weather token 기반 end-to-end inference
- optional `prompt` weather mode 인터페이스
- Qwen2.5-VL 로딩 경로
- 모델 로딩 실패 시 heuristic fallback
- structured JSON 결과 저장
- 한글 free-text 저장
- overlay 이미지 저장
- JSON validity / ROUGE-L / structured accuracy 평가
- 샘플 annotation과 synthetic demo 이미지

즉, **모델 가중치를 받지 못하는 환경에서도 데모 전체는 실행 가능**하며, 실제 Qwen2.5-VL이 준비되면 같은 CLI로 교체 실행할 수 있다.

---

## 22. 프로젝트 구조

```text
src/
  run_inference.py
  weather_preprocess.py
  prompting.py
  utils.py
  evaluate.py
  build_dataset_template.py
examples/
  sample_annotations.json
  sample_images/
  sample_outputs/
```

---

## 23. 실행 방법

### 1) 의존성 설치

CPU 환경 권장 설치 순서:

```bash
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

주의:

- 현재 환경에서는 `python`과 `pip`가 서로 다른 인터프리터를 가리킬 수 있다.
- 반드시 `python -m pip` 형식으로 설치하는 것이 안전하다.
- CPU-only 환경에서는 먼저 CPU wheel로 `torch`, `torchvision`을 설치하는 편이 안전하다.
- GPU 환경이면 시스템 드라이버와 CUDA 호환성을 먼저 확인한 뒤 별도 wheel을 선택하는 것이 낫다.

설치 확인:

```bash
python - <<'PY'
import torch, transformers
from transformers import AutoProcessor
print(torch.__version__)
print(transformers.__version__)
print(torch.cuda.is_available())
print(hasattr(__import__('transformers'), 'AutoModelForImageTextToText'))
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", trust_remote_code=True)
print(processor.__class__.__name__)
PY
```

### 2) 샘플 추론 실행

```bash
python src/run_inference.py \
  --image_dir examples/sample_images \
  --annotation_file examples/sample_annotations.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs \
  --save_overlay
```

### 3) 출력 확인

- `outputs/all_results.json`
- `outputs/metrics.json`
- `outputs/<sample_id>/result.json`
- `outputs/<sample_id>/free_text.txt`
- `outputs/<sample_id>/overlay.png`

---

## 24. 구현 메모

- 기본 실행은 annotation에 들어 있는 weather token을 그대로 사용한다.
- `--weather_mode prompt`를 주면 weather를 먼저 추론하려 시도한다.
- Qwen2.5-VL이 로드되지 않으면 자동으로 heuristic backend로 fallback한다.
- 발표용 데모에서는 같은 이미지에 weather token만 바꿔 reasoning 변화를 비교하는 방식이 가장 단순하고 효과적이다.

---

## 25. ICROS 실데이터 시작점

실제 발표용 작업은 아래 파일에서 시작하면 된다.

- 초안 annotation: `data/metadata/icros_annotations_draft.json`
- 이미지 폴더 규칙: `data/images/README.md`
- 이미지 선정 가이드: `data/metadata/image_selection_guide.md`
- 데이터셋 수집 체크리스트: `data/metadata/dataset_collection_checklist.md`
- annotation 작업 규칙: `data/metadata/annotation_workflow.md`
- annotation 체크리스트: `data/metadata/annotation_checklist.md`

권장 순서:

1. 실제 이미지 10~30장을 `data/images/`에 넣는다.
2. `data/metadata/icros_annotations_draft.json`의 `image_path`를 실제 파일명으로 맞춘다.
3. 각 샘플의 `weather`와 `target`을 장면에 맞게 보정한다.
4. GPU 서버에서 아래 명령으로 실행한다.

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations_draft.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs_icros \
  --save_overlay
```

비교 실험 권장:

- 같은 이미지에 대해 `clear`와 `fog`
- 같은 이미지에 대해 `day`와 `night`
- 같은 이미지에 대해 `clear road`와 `slippery`

이 세 가지 비교 중 2세트만 확보해도 포스터 메시지는 충분히 전달된다.
