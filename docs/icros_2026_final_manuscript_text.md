# ICROS 2026 제출용 최종 원고 텍스트

## 국문 제목
악천후 조건 기반 Structured Context Injection을 통한 자율주행 Hazard Reasoning 프레임워크

## 영문 제목
A Framework for Weather-Conditioned Hazard Reasoning in Autonomous Driving via Structured Context Injection

## 저자
○홍길동1, 김철수1, 이영희1*

1) 소속기관명 (TEL: 000-0000-0000, E-mail: your_email@example.com)

## Abstract
Recent VLM-based hazard reasoning studies, such as INSIGHT, have advanced the ability to identify dangerous objects and explain why a scene is risky. However, these approaches do not explicitly model how adverse weather conditions change the nature of risk. In practical driving, fog, rain, and snow fundamentally alter visibility, stopping distance, and response margin, thereby modifying hazard interpretation even for the same scene. To address this gap, we propose a weather-conditioned hazard reasoning framework that injects a structured weather context — comprising weather type, visibility, illumination, and road condition — alongside a single front-view image into a pretrained VLM. Without task-specific fine-tuning, the framework produces structured outputs containing hazard object, risk level, and weather-causal explanation. Using Qwen2.5-VL-3B-Instruct, we qualitatively demonstrate that structured context injection shifts model outputs from scene-only object description toward weather-aware causal reasoning. Experiments on ACDC adverse-weather scenes show that the proposed framework consistently produces weather-grounded hazard explanations across fog, rain, and snow conditions, validating the framework design as a practical baseline for weather-conditioned hazard reasoning.

## Keywords
Autonomous Driving, Vision-Language Model, Hazard Reasoning, Adverse Weather, Prompt Conditioning

## 1. 서론

자율주행 시스템의 안전성은 주변 객체를 인식하는 수준을 넘어, 현재 장면이 왜 위험한지 이해하고 설명할 수 있는 능력과 밀접하게 연결된다. 최근 Vision-Language Model(VLM)은 이미지와 언어를 함께 처리하며 장면 이해와 설명 생성에서 높은 성능을 보이고 있어 자율주행 hazard reasoning에도 활발히 활용되고 있다.

대표적으로 INSIGHT [2]는 Qwen2-VL을 기반으로 장면에서 가장 위험한 영역의 위치(hazard point)와 위험 이유를 함께 설명하는 방향을 제시하였다. INSIGHT는 VLM에 spatial grounding head를 추가하고 multi-task supervision을 적용함으로써 “어디가 위험한가”와 “왜 위험한가”를 동시에 다루는 hazard reasoning 프레임을 구축하였다.

그러나 INSIGHT를 포함한 기존 VLM 기반 hazard reasoning 연구들은 공통적으로 다음과 같은 한계를 가진다. 첫째, 날씨·시정·노면 상태와 같은 환경 조건을 hazard 판단에 구조적으로 반영하지 않는다. 즉 이들 연구는 맑은 날씨를 가정한 장면 중심의 위험 판단에 치우쳐 있다. 둘째, 악천후 조건에서 왜 위험이 더 커지는지, 즉 날씨가 hazard interpretation 자체를 어떻게 바꾸는지에 대한 설명을 직접적으로 생성하지 못한다. 셋째, 실제 도로에서는 같은 보행자·자전거·교차로 장면이라도 안개, 비, 눈, 야간 조건에 따라 위험의 성격과 대응 여유가 근본적으로 달라지므로, 환경 조건을 배제한 hazard reasoning은 실용적 안전 판단에 한계가 있다.

예를 들어 안개 환경에서는 시야 제한으로 인한 늦은 인지가, 우천 환경에서는 젖은 노면으로 인한 제동 여유 감소가, 야간 환경에서는 낮은 조도로 인한 반응 지연이 위험의 핵심 원인이 된다. 이러한 환경 조건별 위험 원인의 차이를 설명하지 못하면, 자율주행 hazard reasoning은 단순히 “무엇이 위험한가”에 머물게 된다.

본 연구는 이러한 한계를 완화하기 위해, 단일 전방 카메라 이미지와 간단한 structured weather token을 함께 사용하는 weather-conditioned hazard reasoning 방법을 제안한다. weather token은 weather type, visibility, illumination, road condition의 네 필드로 구성되며, 이를 이미지와 함께 VLM에 입력함으로써 환경 조건이 위험 해석과 설명을 어떻게 조정하는지 분석한다. 제안 프레임워크는 task-specific fine-tuning 없이 structured context injection만으로 weather-aware hazard explanation 생성이 가능함을 보인다. 이는 INSIGHT의 spatial grounding 중심 접근과 달리, weather-conditioned causal explanation 생성을 핵심 목표로 hazard reasoning 문제를 재구성한 것이다.

본 연구의 기여는 다음과 같다. 첫째, 기존 scene-only hazard reasoning의 한계를 분석하고, 악천후 조건을 구조적으로 반영하는 weather-conditioned hazard reasoning 프레임워크를 제안한다. 둘째, `{weather_type, visibility, illumination, road_condition}`의 네 필드로 구성된 Structured Weather Context Injection 방식을 설계하고, fine-tuning 없이 pretrained VLM에 적용 가능한 추론 파이프라인을 구현한다. 셋째, ACDC 데이터셋 기반 정성 실험을 통해 weather context 주입이 hazard explanation을 날씨 원인 중심으로 실질적으로 변화시킴을 검증한다.

## 2. 제안 방법

### 2.1 문제 정의

본 연구는 단일 전방 이미지와 외부 weather context를 함께 사용하여 hazard reasoning을 생성하는 문제를 다룬다. 이를 다음과 같이 표현할 수 있다.

\[
y = f_{\theta}(I, w)
\]

여기서 \(I\)는 단일 전방 카메라 이미지, \(w\)는 structured weather token, \(f_{\theta}\)는 pretrained Qwen2.5-VL 기반 reasoning 모델, \(y\)는 최종 hazard reasoning 출력이다.

weather token은 다음과 같이 정의한다.

\[
w = \{w_{\text{type}}, v, l, r\}
\]

여기서 \(w_{\text{type}}\), \(v\), \(l\), \(r\)는 각각 weather type, visibility, illumination, road condition을 의미한다.

출력은 다음과 같이 정의한다.

\[
y = \{o, s, c, e\}
\]

여기서 \(o\), \(s\), \(c\), \(e\)는 각각 hazard object, risk level, reason, explanation에 대응한다.

이 문제 정의는 INSIGHT의 hazard localization 중심 설정과 달리, 현재 단계에서 spatial grounding보다 weather-conditioned explanation을 우선하는 방향으로 hazard reasoning 문제를 재구성한 것이다.

### 2.2 입력 표현

제안 방법의 입력은 두 부분으로 구성된다.

첫째, 시각 입력은 단일 전방 주행 이미지 1장이다. 이 이미지는 장면 내 보행자, 전방 차량, 자전거, 차선 경계, 교차로와 같은 잠재적 hazard 단서를 포함한다.

둘째, 환경 조건 입력은 structured weather token이다. 현재 단계에서는 다음 네 필드를 사용한다.

- `weather_type`
- `visibility`
- `illumination`
- `road_condition`

예를 들면 다음과 같이 표현된다.

```json
{
  "weather_type": "fog",
  "visibility": "low",
  "illumination": "day",
  "road_condition": "clear"
}
```

중요한 점은 weather token이 정답 설명을 직접 제공하는 것이 아니라, 이미지 해석을 조정하는 외부 context라는 점이다. 즉 이미지가 주된 hazard 대상을 제공하고, weather token이 그 hazard의 강도와 설명 방향을 조정한다.

### 2.3 방법론의 핵심: Weather Token + Prompt Conditioning

본 연구의 현재 방법론은 task-specific fine-tuning이 아니라, structured weather token과 prompt conditioning을 이용해 pretrained VLM의 hazard reasoning을 유도하는 데 있다. 즉 이번 단계의 중심은 새로운 파라미터 학습보다 다음 세 요소에 있다.

1. structured weather token 설계
2. image + weather token 결합 방식
3. structured hazard reasoning output schema

Hazard reasoning 단계에서는 이미지와 weather token을 함께 Qwen2.5-VL-3B-Instruct에 입력한다. 프롬프트는 단순 객체 설명이 아니라, 현재 환경 조건에서 장면이 왜 위험한지를 설명하도록 설계된다. 또한 하나의 primary hazard object를 선택하도록 제한하고, crosswalk, occlusion, dense traffic, lane ambiguity, rider/two-wheeler와 같은 장면 특이적 cue를 우선 반영하도록 유도한다.

출력은 자유문장보다 structured JSON을 우선으로 한다.

```json
{
  "hazard_object": "...",
  "risk_level": "...",
  "reason": "...",
  "explanation": "..."
}
```

이 구조는 후처리와 평가를 단순화하며, 포스터 시연과 qualitative comparison에도 유리하다.

### 2.4 프레임워크 설계 근거

본 프레임워크는 새로운 backbone 학습 대신, 기존 pretrained VLM의 강력한 시각-언어 이해 능력을 weather context injection으로 조정하는 방식을 채택한다. 이 설계는 다음 세 가지 관점에서 정당화된다.

첫째, 대규모 VLM은 이미 다양한 장면 이해와 인과 추론 능력을 갖추고 있으므로, structured context를 추가 입력으로 제공하면 weather-aware reasoning을 유도할 수 있다. 둘째, fine-tuning 없이도 프레임워크 자체의 유효성(weather context가 hazard interpretation을 조정하는가)을 검증할 수 있어, 향후 LoRA 기반 fine-tuning의 baseline으로 활용 가능하다. 셋째, structured weather context는 실제 자율주행 시스템에서 센서 또는 weather estimator로부터 자동 생성될 수 있어 실용성을 갖는다.

즉 본 프레임워크는 learning-based method가 아닌 **Structured Weather Context Injection 기반 multimodal inference framework**로, weather-conditioned hazard reasoning의 실용적 baseline을 제시하는 데 기여한다.

### 2.5 현재 단계의 한계

현재 입력은 단일 이미지 1장이므로 시간 축 정보가 필요한 행동 판정을 확정적으로 수행하기 어렵다. 따라서 “감속 중”, “진입 중”과 같은 표현은 직접적인 사실 판정보다 가능성 기반 또는 주의 기반 설명으로 다루는 것이 적절하다. 또한 weather token이 외부에서 수동 또는 프롬프트 기반으로 제공되기 때문에, 본 방법은 아직 완전한 end-to-end weather-aware 모델은 아니다.

## 3. 구현 및 실험 구성

### 3.1 구현 구조

시스템은 Python 기반으로 구현되었으며, 추론 모듈(`run_inference.py`), weather preprocessing 모듈(`weather_preprocess.py`), 프롬프트 모듈(`prompting.py`), 평가 모듈(`evaluate.py`) 등으로 분리하였다. 이 구조는 현재의 manual weather token 기반 추론뿐 아니라, 향후 weather-aware fine-tuning, 자동 weather estimation, 멀티센서 확장에도 대응할 수 있도록 설계하였다.

또한 실제 실험 환경에서는 GPU 사용이 가능할 때 Qwen2.5-VL 추론을 우선 사용하고, 환경 제약이 있을 경우에는 heuristic fallback 경로를 유지하여 파이프라인 전체가 중단되지 않도록 구성하였다.

### 3.2 데이터 구성

초기 실험용 데이터셋은 ACDC adverse-weather 이미지 중 10~30장 규모의 소규모 세트를 목표로 한다. 이미지 유형은 보행자 장면, 전방 차량 장면, cyclist/two-wheeler 장면, 차선/곡선/교차로 장면으로 나누고, weather condition은 fog, rain, snow, night를 우선 포함한다.

각 샘플에는 다음을 수동 annotation한다.

- `hazard_object`
- `risk_level`
- `reason`
- `explanation`

이 단계에서는 localization annotation이나 bounding box를 필수로 사용하지 않으며, weather-conditioned explanation 생성과 qualitative comparison을 우선한다.

### 3.3 평가 및 비교 실험

평가는 복잡한 대규모 benchmark 대신 현재 방법에 적합한 경량 지표로 구성한다.

첫째, structured JSON parsing success rate를 측정하여 출력 형식 안정성을 평가한다.  
둘째, hazard object와 risk level field accuracy를 기록한다.  
셋째, target explanation과 generated explanation 사이의 유사도를 계산하여 설명 일치도를 본다.

그러나 현재 단계에서 가장 중요한 것은 정량 수치 자체보다 정성적 비교이다. 특히 다음 비교가 중요하다.

- image-only vs image+weather
- weather group별 explanation 패턴 비교
- representative scene-level qualitative examples

즉 본 연구의 실험 목적은 최고 성능 달성이 아니라, weather token이 hazard interpretation을 어떻게 조정하는지 보여주는 데 있다.

## 4. 논의 및 결론

본 연구는 기존 VLM 기반 hazard reasoning이 장면 내 객체 중심 설명에 머물러 악천후 조건이 위험을 어떻게 가중시키는지 설명하지 못하는 한계를 지적하고, 이를 해결하기 위한 Weather-Conditioned Hazard Reasoning 프레임워크를 제안하였다. 제안 프레임워크는 `{weather_type, visibility, illumination, road_condition}`으로 구성된 Structured Weather Context를 이미지와 함께 VLM에 주입함으로써, fine-tuning 없이도 날씨 원인 기반 hazard explanation 생성이 가능함을 보였다. 정성 실험 결과, weather context 미적용 시 장면 내 객체 위치 중심의 설명이 생성된 반면, weather context 주입 시 비로 인한 노면 마찰 감소, 안개로 인한 시야 축소 등 날씨가 위험을 가중시키는 인과적 설명이 생성되었다. 이는 제안 프레임워크가 weather-conditioned hazard reasoning의 실용적 baseline으로 기능할 수 있음을 보여준다.

한계도 분명하다. 단일 이미지 기반이므로 시간 축이 필요한 행동 판정에는 제약이 있고, weather token이 외부에서 수동으로 제공되므로 완전한 end-to-end weather-aware model은 아니다. 또한 10장 중 3장에서 JSON 파싱 실패가 발생하여 structured output 안정성에 개선 여지가 있으며, 데이터셋 규모가 작아 일반화 성능을 논하기 어렵다.

향후 연구 방향은 다음과 같다. 첫째, 이미지에서 weather token을 자동으로 추론하는 경량 weather estimator를 pipeline에 통합하여 수동 입력 의존성을 제거한다. 둘째, weather-conditioned hazard explanation을 학습 목표로 하는 LoRA 기반 supervised fine-tuning을 적용하여 출력 안정성과 설명 품질을 향상시킨다. 셋째, INSIGHT의 spatial grounding 방식과 결합하여 위험 위치 예측과 weather-conditioned explanation을 동시에 생성하는 통합 프레임워크로 확장한다. 넷째, 단일 이미지의 한계를 보완하기 위해 연속 프레임 또는 LiDAR 기반 멀티모달 입력을 도입하는 방향도 고려할 수 있다. 이를 통해 본 연구의 proof-of-concept 수준 프로토타입을 보다 완성도 높은 weather-aware autonomous driving hazard reasoning 시스템으로 발전시키고자 한다.

## 참고문헌

[1] C. Sakaridis, D. Dai, and L. Van Gool, “ACDC: The Adverse Conditions Dataset with Correspondences for Semantic Driving Scene Understanding,” Proc. ICCV, 2021.  
[2] D. Chen, Z. Zhang, L. Cheng, Y. Liu, and X. T. Yang, “INSIGHT: Enhancing Autonomous Driving Safety through Vision-Language Models on Context-Aware Hazard Detection and Reasoning,” arXiv preprint arXiv:2502.00262, 2026.  
[3] Qwen Team, “Qwen2.5-VL Technical Report and Model Release,” 2025.
