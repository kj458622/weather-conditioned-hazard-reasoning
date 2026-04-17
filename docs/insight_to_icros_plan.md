# InSIGHT 분석 및 ICROS 구현/논문 계획

## 1. 목적

이 문서는 `InSIGHT.pdf` 논문이 **Qwen 계열 VLM을 어떤 방식으로 수정해 위험 지역과 위험 이유를 다루었는지**를 정리하고, 이를 바탕으로 현재 진행 중인 **악천후 조건 반영 hazard reasoning 연구**를 ICROS용으로 어떻게 단순화·구현·문서화할지 제안한다.

현재 목표는 저널급 완성형 시스템이 아니라 **ICROS 포스터 발표용 최소 기능 프로토타입**이다. 따라서 InSIGHT의 핵심 아이디어는 참고하되, 지금 단계에서 실제로 필요한 수정만 선택한다.

---

## 2. InSIGHT가 한 일

## 2.1 문제 정의

InSIGHT는 자율주행 장면에서

- 어디를 가장 주의해야 하는지
- 왜 그 지점이 위험한지

를 VLM으로 다루려는 논문이다.

기본 질문은 다음과 같이 매우 직접적이다.

> "In current autonomous driving scenario, which area should we pay more attention on?"

즉, InSIGHT는 **위험 객체 설명**보다 더 구체적으로, **위험 지역 좌표를 직접 예측하는 문제**로 설정했다.

---

## 2.2 베이스 모델

논문은 **Qwen2-VL**을 기반으로 사용했다. 핵심은 backbone을 완전히 새로 설계한 것이 아니라, **기존 Qwen2-VL 위에 supervised fine-tuning과 공간 grounding head를 추가**한 것이다.

논문 본문 기준 핵심 구성은 다음과 같다.

- Qwen2-VL backbone 사용
- image-conditioned prompt 입력
- LoRA 기반 파라미터 효율 학습
- 4-bit quantization
- gradient checkpointing

즉, 거대한 모델 구조 변경보다는 **기존 VLM에 task-specific supervision을 얹는 방식**이다.

---

## 2.3 Qwen 모델을 어떻게 수정했는가

InSIGHT의 수정은 크게 3가지다.

### 1) 텍스트 생성만 하던 Qwen2-VL을 멀티태스크 모델로 변경

기본 Qwen2-VL은 이미지와 프롬프트를 받아 텍스트만 생성한다. InSIGHT는 여기에

- 텍스트 생성 loss
- 좌표 회귀 loss

를 동시에 학습하는 **multi-task objective**를 넣었다.

논문 수식:

```text
L_total = lambda_text * L_text + lambda_coord * L_coord
```

여기서

- `L_text`: 언어 생성 cross-entropy
- `L_coord`: hazard point 좌표 회귀 MSE

다.

즉, 단순 설명 생성 모델이 아니라 **설명 + 위험 위치 예측 모델**로 바꿨다.

### 2) 경량 2D heatmap head 추가

논문은 backbone feature 위에 **lightweight 2D heatmap head**를 붙였다.

구조는 다음과 같다.

- joint vision-language representation을 mean pooling
- 2-layer MLP로 `H x W` heatmap logits 생성
- softmax로 spatial probability map 생성
- differentiable soft-argmax로 continuous `(x_hat, y_hat)` 계산

이 부분이 핵심이다. 단순 attention map을 해석하는 게 아니라, **학습 가능한 명시적 spatial head**를 붙였다.

### 3) supervision 방식 변경

InSIGHT는 이미지마다

- hazard point 1개
- 해당 장면의 natural language rationale

를 함께 annotation했다.

즉, supervision 자체를

- 한 점 클릭 기반의 위험 위치
- 그 이유를 설명하는 문장

으로 구성했다.

이 덕분에 Qwen이 "무엇을 봐야 하는지"와 "왜 위험한지"를 동시에 배우도록 만들었다.

---

## 2.4 데이터셋 구성

InSIGHT는 BDD100K 일부를 사용해 약 1,000장의 hazard-awareness subset을 만들었다.

각 샘플은 다음을 가진다.

- RGB 이미지
- 단일 hazard point
- 자연어 rationale

annotation 특징:

- 사람 annotator가 5초 내 가장 위험한 영역을 선택
- bounding box 중심을 hazard point로 저장
- 이미지당 하나의 primary hazard만 부여

이 설계는 annotation 비용을 낮추면서도 grounding supervision을 넣기 위한 절충안이다.

---

## 2.5 InSIGHT의 장점과 한계

### 장점

- 기존 Qwen2-VL을 크게 뜯지 않고도 grounding 능력을 강화함
- 위험 지점을 좌표로 명시해 해석성이 높음
- rationale과 localization을 같이 다룸
- LoRA 기반이라 학습 비용이 상대적으로 낮음

### 한계

- 핵심 출력이 "어디를 볼 것인가" 중심이라, **악천후 조건이 위험 설명을 어떻게 바꾸는지**에는 직접 대응하지 않음
- 날씨 정보를 구조적으로 넣지 않음
- image당 hazard point 1개는 설명력을 단순화하지만 scene complexity를 충분히 담지 못할 수 있음
- ICROS 최소 데모 관점에서는 SFT + heatmap head + dataset 재구축이 과함

---

## 3. 나는 어떻게 수정할 것인가

## 3.1 InSIGHT를 그대로 따라가면 안 되는 이유

현재 연구 목표는 다음이다.

- 위험 객체
- 위험 이유
- 악천후 조건

을 함께 사용해 **왜 위험한지 설명**하는 것이다.

즉, 우리의 핵심은 **spatial grounding**보다 **weather-conditioned reasoning**이다.

InSIGHT처럼 heatmap head와 coordinate regression을 붙이는 것은 연구적으로 의미는 있지만, 현재 단계에서는 아래 이유로 우선순위가 낮다.

- 발표까지 필요한 최소 기능이 아님
- annotation 비용이 증가함
- 날씨 조건 반영이라는 핵심 contribution이 흐려질 수 있음

따라서 현재 단계에서는 InSIGHT의 아이디어 중 **"Qwen을 task-specific structured reasoning model로 바꾼다"**는 방향만 가져오고, **좌표 head는 보류**하는 것이 맞다.

---

## 3.2 현재 프로젝트에서 적용할 수정 방향

현재는 Qwen2.5-VL을 다음 방식으로 수정하는 것이 적절하다.

### 수정 1) 입력 구조를 image-only에서 image + weather token으로 변경

기존 VLM 입력:

- 이미지
- 일반 질문

우리 입력:

- 이미지
- structured weather token
- hazard reasoning instruction

예:

```json
{
  "image": "<image>",
  "weather_type": "snow",
  "visibility": "low",
  "illumination": "day",
  "road_condition": "unclear"
}
```

즉, backbone 구조를 크게 바꾸지 않고 **프롬프트 조건부 reasoning 구조**로 바꾼다.

### 수정 2) 출력 구조를 자유문장 중심에서 structured JSON 중심으로 변경

InSIGHT는 좌표 문장을 출력했다.
우리는 아래 JSON을 우선 출력하게 한다.

```json
{
  "hazard_object": "...",
  "risk_level": "...",
  "reason": "...",
  "explanation": "..."
}
```

이렇게 해야

- 평가가 쉬워지고
- 후처리가 쉬워지고
- 포스터에서 비교 시연이 쉬워진다.

### 수정 3) weather module과 reasoning module을 분리

InSIGHT는 weather module이 없다.
우리는 장기적으로 end-to-end weather-aware VLM으로 확장할 계획이므로 지금부터

- `weather_preprocess.py`
- `run_inference.py`
- `prompting.py`

처럼 모듈 분리를 유지해야 한다.

### 수정 4) 현 단계에서는 학습보다 prompt-first

InSIGHT는 SFT를 했다.  
우리는 ICROS 1차 프로토타입에서는 아래 순서가 맞다.

1. prompt-only baseline
2. manual weather token 주입
3. structured JSON 안정화
4. small-scale qualitative evaluation
5. 이후 필요 시 LoRA/SFT

즉, **지금 당장 Qwen을 구조적으로 크게 수정하지 않는다.**

---

## 3.3 중기 단계에서의 수정 방향

프로토타입 이후에는 InSIGHT와 더 가까운 방향으로 확장 가능하다.

### Phase 2

- weather token을 사람이 주입하지 않고 모델이 직접 추론
- weather-aware SFT / LoRA 수행
- target에 explanation을 직접 학습

### Phase 3

- 선택적으로 region grounding 추가
- hazard object 또는 위험 영역 박스 supervision 추가
- 필요하면 InSIGHT식 heatmap head 실험

즉, InSIGHT에서 배울 점은 **"VLM을 구조화된 자율주행 hazard task로 맞춤화한다"**는 철학이지, 현 단계에서 그 전체 구조를 그대로 재현하는 것은 아니다.

---

## 4. ICROS용 구현 전략

## 4.1 ICROS 목표 재정의

ICROS에서는 다음 메시지가 명확해야 한다.

> 동일 장면이라도 악천후 조건이 바뀌면 위험 설명이 달라진다.

따라서 구현 목표는 다음 4가지면 충분하다.

- 이미지 1장 입력
- weather token 주입
- structured hazard reasoning 생성
- 한글 설명 저장 및 시각화

---

## 4.2 구현 범위

### 반드시 구현

- manual weather token 기반 inference
- structured JSON 출력
- free-text 한국어 설명 생성
- output 저장
- 간단 평가

### optional

- prompt-based weather token estimation
- 같은 이미지에 weather token만 바꿔 comparative reasoning 실험

### 제외

- heatmap head 학습
- full SFT
- region annotation dataset 구축
- real-time system

---

## 4.3 실험 시나리오

ICROS에서는 복잡한 수치보다 **직관적 비교**가 더 중요하다.

추천 실험은 다음과 같다.

### 실험 A: 기본 추론

- 이미지 1장
- weather token 1개
- structured result + 한국어 설명 출력

### 실험 B: weather-conditioned comparison

- 동일 이미지
- `clear` vs `fog`
- `day` vs `night`
- `clear road` vs `slippery`

출력 비교:

- 위험 객체는 같을 수 있음
- 위험 이유와 설명은 달라져야 함

이 비교가 포스터 핵심 그림이 된다.

### 실험 C: 소규모 정량

- JSON parsing success rate
- ROUGE-L
- hazard_object accuracy
- risk_level accuracy

---

## 4.4 현재 저장소 기준 구현 상태

이미 구현된 항목:

- `src/run_inference.py`
- `src/weather_preprocess.py`
- `src/prompting.py`
- `src/utils.py`
- `src/evaluate.py`
- `src/build_dataset_template.py`
- sample annotations
- sample outputs

즉, 현재는 **manual weather token 기반 최소 파이프라인은 이미 있는 상태**다.

앞으로 필요한 것은 "새 구조 개발"보다 "실제 발표용 데이터와 비교 예시 정리" 쪽이다.

---

## 5. ICROS 논문은 어떤 방식으로 쓸 것인가

## 5.1 논문 메시지

논문 메시지는 InSIGHT와 달라야 한다.

InSIGHT의 메시지:

- VLM에 grounding head를 붙여 hazard localization과 reasoning을 강화했다

우리 논문 메시지:

- VLM이 단순 hazard object 설명을 넘어서
- **adverse weather condition을 반영한 hazard reasoning**
- 을 생성하도록 만들었다

즉 contribution 중심을 아래처럼 잡는 게 맞다.

### Contribution 1

Weather-conditioned hazard reasoning 문제를 camera-only setting으로 정의

### Contribution 2

image + structured weather token 기반 최소 VLM 파이프라인 제안

### Contribution 3

악천후 조건 변화에 따라 explanation이 달라지는 qualitative evidence 제시

### Contribution 4

ICROS용 소규모 prototype benchmark와 annotation format 제안

---

## 5.2 논문 구성 초안

### 1. Introduction

- 기존 hazard reasoning 한계
- 악천후는 위험 해석 자체를 바꾼다는 문제 제기
- 기존 연구는 "what is risky" 중심이고 "why risky under weather"가 약함
- 우리의 문제 정의와 핵심 기여 제시

### 2. Related Work

- hazard reasoning in autonomous driving
- VLM for driving scene understanding
- adverse weather perception
- explanation / reasoning / grounding 계열
- InSIGHT는 grounding 강화 사례로 인용하되, weather reasoning과의 차이 명확화

### 3. Problem Formulation

- 입력: image + weather token
- 출력: hazard object, risk level, reason, explanation
- structured output 정의

### 4. Method

- overall pipeline
- weather preprocessing module
- prompting strategy
- structured JSON generation
- optional prompt-based weather estimator

### 5. Experimental Setup

- sample dataset construction
- weather categories
- implementation details
- model: Qwen2.5-VL-3B, optional 7B

### 6. Results

- format validity
- text overlap
- structured accuracy
- qualitative comparison
- clear vs fog / day vs night 사례

### 7. Discussion

- 장점: 빠른 프로토타입, 해석성, modularity
- 한계: weather token manual, dataset small, no fine-tuning
- future work: LoRA, end-to-end weather reasoning, LiDAR

### 8. Conclusion

- 악천후 조건을 반영한 hazard explanation 가능성 제시

---

## 5.3 ICROS에서 강조해야 할 그림과 표

### 그림

- 전체 파이프라인 다이어그램
- 같은 이미지에 서로 다른 weather token을 넣었을 때 설명이 달라지는 비교 그림
- optional overlay 예시

### 표

- annotation format 예시
- metrics summary
- weather condition별 예시 출력 비교표

---

## 5.4 논문 톤

이번 단계는 과도한 claim을 하면 안 된다.

피해야 할 표현:

- robustly solves
- state-of-the-art
- comprehensive weather reasoning

권장 표현:

- preliminary prototype
- proof-of-concept
- weather-conditioned explanation demo
- modular baseline for future weather-aware VLM research

즉, ICROS용으로는 **작지만 명확한 문제정의와 데모 가능성**이 더 중요하다.

---

## 6. 결론

InSIGHT는 Qwen2-VL에

- LoRA 기반 SFT
- multi-task loss
- 2D heatmap head
- soft-argmax coordinate regression

을 붙여 **위험 위치와 이유를 함께 학습**한 연구다.

반면 현재 우리의 ICROS 연구는

- heatmap grounding보다
- weather-conditioned reasoning이 핵심이고
- prompt-first, structured JSON-first, manual weather token-first

전략이 더 적절하다.

따라서 현재 단계에서의 정답은 InSIGHT를 그대로 복제하는 것이 아니라,

> Qwen 기반 hazard reasoning 프레임을 weather-conditioned explanation 문제로 재구성하는 것

이다.

장기적으로는 이 구조 위에 LoRA, weather-aware SFT, region grounding, LiDAR 확장을 얹는 방식이 가장 자연스럽다.

