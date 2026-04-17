# ICROS 2026 제출용 최종 원고 텍스트

## 국문 제목
악천후 조건을 반영한 자율주행 Hazard Reasoning 프로토타입

## 영문 제목
Weather-Conditioned Hazard Reasoning Prototype for Autonomous Driving

## 저자
○홍길동1, 김철수1, 이영희1*

1) 소속기관명 (TEL: 000-0000-0000, E-mail: your_email@example.com)

## Abstract
This paper presents a weather-conditioned hazard reasoning prototype for autonomous driving using a vision-language model. While existing hazard reasoning approaches mainly focus on identifying what is dangerous in a driving scene, they often do not explicitly explain how adverse weather changes the reason for risk. In real-world driving, however, fog, rain, snow, and nighttime conditions directly affect visibility, response time, and stopping margin, thereby altering the interpretation of scene risk. To address this issue, we propose a camera-only prototype that takes a single front-view image and a structured weather token as input and generates a structured hazard explanation. The weather token contains weather type, visibility, illumination, and road condition. Based on the image and token, the model outputs hazard object, risk level, reason, and a Korean explanation in structured JSON form. Qwen2.5-VL-3B-Instruct is used as the base model, and manual weather tokens are used in the current stage to ensure stable end-to-end inference. The prototype also includes simple result saving, visualization, and lightweight evaluation. The main goal of this work is not to claim full autonomous driving reasoning capability, but to provide a practical proof-of-concept showing that hazard explanations can change according to adverse weather conditions.

## Keywords
Autonomous Driving, Vision-Language Model, Hazard Reasoning, Adverse Weather, Structured Explanation

## 1. 서론

자율주행 시스템의 안전성은 주변 객체를 인식하는 수준을 넘어, 현재 장면이 왜 위험한지 이해하고 설명할 수 있는 능력과 밀접하게 연결된다. 최근 Vision-Language Model(VLM)은 이미지와 언어를 함께 처리하며 장면 이해와 설명 생성에서 높은 성능을 보이고 있어 자율주행 장면 reasoning에도 활용 가능성이 크다. 그러나 기존 hazard reasoning 연구는 대체로 위험 객체 또는 위험 위치를 설명하는 데 초점을 맞추며, 환경 조건에 따라 위험 설명이 어떻게 달라지는지에 대한 관점은 상대적으로 제한적이다.

실제 도로에서는 같은 장면이라도 날씨와 조명 조건에 따라 위험의 의미가 달라진다. 예를 들어 보행자가 횡단보도 근처에 있는 장면은 맑은 낮보다 야간이나 눈 오는 환경에서 더 늦게 인지될 수 있으며, 전방 차량은 안개나 비 환경에서 더 큰 안전거리를 요구한다. 따라서 자율주행 hazard reasoning은 단순히 “무엇이 위험한가”를 넘어서 “환경 조건 때문에 왜 더 위험한가”를 설명할 필요가 있다.

본 연구에서는 ICROS 포스터 발표용 1차 프로토타입으로서, 단일 전방 카메라 이미지와 weather token을 함께 사용하는 weather-conditioned hazard reasoning 파이프라인을 제안한다. 본 시스템은 이미지와 악천후 정보를 입력받아 위험 객체, 위험도, 위험 이유, 한국어 설명문을 구조화된 형태로 생성한다. 본 연구의 기여는 다음과 같다. 첫째, camera-only setting에서 weather-conditioned hazard reasoning 문제를 정의한다. 둘째, image와 structured weather token을 함께 사용하는 최소 기능 VLM 파이프라인을 제안한다. 셋째, 악천후 조건에 따라 설명이 달라질 수 있음을 보여주는 정성 시연 중심의 프로토타입을 구현한다.

## 2. 제안 방법

제안 시스템은 입력 데이터 처리, weather preprocessing, hazard reasoning의 세 단계로 구성된다. 입력은 단일 전방 카메라 이미지이며, weather preprocessing 단계에서는 이미지에 대응하는 날씨 조건을 구조화된 token으로 표현한다. token은 `weather_type`, `visibility`, `illumination`, `road_condition` 네 필드로 이루어지며, 예를 들어 fog-low-day-clear 또는 rain-medium-night-slippery와 같은 형태로 사용된다. 현재 단계에서는 manual mode를 우선 적용하여 전체 파이프라인의 안정성을 확보하였고, 추후 prompt-based weather estimation 또는 end-to-end weather-aware 모델로 확장 가능하도록 모듈을 분리하였다.

본 연구의 weather-conditioned hazard reasoning 문제는 다음과 같이 정의할 수 있다.

\[
y = f_{\theta}(I, w)
\]

여기서 \(I\)는 전방 카메라 이미지, \(w\)는 구조화된 weather token, \(f_{\theta}\)는 Qwen2.5-VL 기반 reasoning 모델, \(y\)는 최종 hazard reasoning 출력이다. 본 연구에서는 weather token과 출력을 각각 다음과 같이 정의한다.

\[
w = \{w_{\text{type}}, v, l, r\}, \quad
y = \{o, s, c, e\}
\]

여기서 \(w_{\text{type}}\), \(v\), \(l\), \(r\)는 각각 weather type, visibility, illumination, road condition을 의미하며, \(o\), \(s\), \(c\), \(e\)는 hazard object, risk level, reason, explanation에 대응한다. 이 정의는 weather 정보를 별도의 구조화 입력으로 유지하면서, 추론 결과 또한 후처리와 평가가 쉬운 structured form으로 유지하기 위한 것이다.

Hazard reasoning 단계에서는 이미지와 weather token을 함께 Qwen2.5-VL-3B-Instruct에 입력한다. 프롬프트는 단순한 장면 설명이 아니라, 주어진 날씨 조건 하에서 장면이 왜 위험한지 설명하도록 구성된다. 출력은 structured JSON을 우선으로 하며, `hazard_object`, `risk_level`, `reason`, `explanation` 네 필드를 포함한다. 예를 들어 보행자 장면에서는 “보행자가 차로 근처에 있으며 안개로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음”과 같은 설명이 생성될 수 있다.

현재 단계는 단일 이미지 입력을 사용하므로 시간 축 정보가 필요한 행동 판정을 확정적으로 수행하는 것은 어렵다. 따라서 “감속 중”, “진입 중”과 같은 표현은 직접적인 사실 판정보다 가능성 기반 또는 주의 기반 표현으로 다루는 것이 적절하다. 이에 따라 본 연구의 출력은 행동 인식 시스템이 아니라, 장면과 환경 조건을 함께 고려한 risk-aware explanation 생성에 초점을 둔다.

## 3. 구현 및 실험 구성

프로토타입은 Python 기반으로 구현되었으며, 추론 모듈(`run_inference.py`), weather preprocessing 모듈(`weather_preprocess.py`), 프롬프트 모듈(`prompting.py`), 평가 모듈(`evaluate.py`) 등으로 분리하였다. 이 구조는 현재의 manual weather token 기반 프로토타입뿐 아니라, 향후 weather-aware fine-tuning이나 멀티센서 확장에도 대응할 수 있도록 설계하였다. 또한 모델 로딩 실패 또는 GPU 미사용 환경에서도 개발을 지속할 수 있도록 CPU fallback과 heuristic fallback 경로를 포함하였다.

초기 실험용 데이터셋은 10~30장 규모의 소규모 세트를 목표로 한다. 이미지 유형은 보행자 장면, 전방 차량 장면, 차선/곡선/교차로 장면으로 나누고, weather condition은 fog, rain, snow, night를 우선 포함한다. 각 샘플에는 weather token과 함께 `hazard_object`, `risk_level`, `reason`, `explanation_ko`를 수동 annotation한다. 본 단계에서는 localization annotation이나 bounding box는 필수로 사용하지 않으며, weather-conditioned explanation annotation을 우선시한다.

평가는 복잡한 대규모 벤치마크 대신 프로토타입에 적합한 경량 지표로 구성한다. 첫째, structured JSON parsing success rate를 측정하여 출력 안정성을 평가한다. 둘째, target explanation과 generated explanation 사이의 ROUGE-L을 계산하여 설명 유사도를 본다. 셋째, hazard object와 risk level field accuracy를 함께 기록한다. 그러나 ICROS 단계에서 가장 중요한 것은 동일하거나 유사한 장면에서 weather condition을 다르게 주었을 때 생성 설명이 의미 있게 달라지는지를 보여주는 정성 사례이다.

## 4. 논의 및 결론

본 연구는 완성형 자율주행 reasoning 시스템이 아니라, weather-conditioned hazard explanation이라는 문제를 직관적으로 보여주기 위한 ICROS용 proof-of-concept이다. 제안 방식은 단일 이미지와 structured weather token만으로도 환경 조건을 반영한 위험 설명을 생성할 수 있다는 가능성을 보여준다. 또한 structured JSON 출력 방식을 사용함으로써 후처리, 평가, 시각화, 포스터 구성 측면에서 실용성을 확보하였다.

한편 한계도 분명하다. 첫째, 단일 이미지 기반이므로 시간 축이 필요한 행동 판정에는 제약이 있다. 둘째, weather token이 수동 또는 프롬프트 기반으로 주어지므로 완전한 end-to-end 모델은 아니다. 셋째, 데이터셋 규모가 작아 일반화 성능을 논하기 어렵다. 그럼에도 불구하고 본 프로토타입은 “악천후가 reasoning을 어떻게 바꾸는가”를 직접 시연할 수 있는 최소 기능 시스템으로서 의미가 있다.

향후에는 첫째, weather token 자동 추론을 포함하는 end-to-end weather-aware VLM으로 확장하고, 둘째, LoRA 기반 supervised fine-tuning을 적용하며, 셋째, region grounding 또는 멀티센서 입력을 포함하는 보다 정교한 autonomous driving reasoning 프레임워크로 발전시키고자 한다.

## 참고문헌

[1] C. Sakaridis, D. Dai, and L. Van Gool, “ACDC: The Adverse Conditions Dataset with Correspondences for Semantic Driving Scene Understanding,” Proc. ICCV, 2021.  
[2] D. Chen, Z. Zhang, L. Cheng, Y. Liu, and X. T. Yang, “INSIGHT: Enhancing Autonomous Driving Safety through Vision-Language Models on Context-Aware Hazard Detection and Reasoning,” arXiv preprint arXiv:2502.00262, 2026.  
[3] Qwen Team, “Qwen2.5-VL Technical Report and Model Release,” 2025.
