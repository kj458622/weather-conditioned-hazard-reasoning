# ICROS 2026 2페이지 압축 원고

## 국문 제목
악천후 조건을 반영한 자율주행 Hazard Reasoning 프로토타입

## 영문 제목
Weather-Conditioned Hazard Reasoning Prototype for Autonomous Driving

## 저자
○홍길동1, 김철수1, 이영희1*

1) 소속기관명 (TEL: 000-0000-0000, E-mail: your_email@example.com)

## Abstract
This paper presents a weather-conditioned hazard reasoning prototype for autonomous driving scenes using a vision-language model. Existing hazard reasoning studies mainly explain what is risky in a scene, but they often do not explicitly describe how adverse weather changes the risk explanation. To address this gap, we use a single front-view camera image together with a structured weather token that includes weather type, visibility, illumination, and road condition. The proposed pipeline takes the image and weather token as input and generates structured JSON outputs containing hazard object, risk level, reason, and a Korean explanation. Qwen2.5-VL-3B-Instruct is used as the base model, while manual weather tokens are employed in the current stage for stable end-to-end inference. The system also provides simple result saving, visualization, and lightweight evaluation. The main objective of this prototype is to demonstrate that risk explanations can change according to weather conditions even for similar driving scenes.

## Keywords
Autonomous Driving, Vision-Language Model, Hazard Reasoning, Adverse Weather, Explanation Generation

## 1. 서론

자율주행 장면 이해에서 중요한 것은 단순히 위험 객체를 인식하는 것을 넘어, 현재 장면이 왜 위험한지 설명하는 능력이다. 특히 실제 도로에서는 안개, 비, 눈, 야간과 같은 악천후 조건이 위험 판단의 강도와 이유를 직접 바꾼다. 그러나 기존 hazard reasoning 연구는 주로 무엇이 위험한가를 설명하는 데 초점을 맞추며, 환경 조건을 함께 반영한 설명은 상대적으로 부족하다.

본 연구의 목적은 ICROS 포스터 발표용 최소 기능 프로토타입으로서, 단일 전방 카메라 이미지와 weather token을 함께 사용하여 위험 객체와 위험 이유를 구조화된 형태로 생성하는 것이다. 핵심은 같은 장면이라도 weather condition이 달라지면 설명이 달라지도록 만드는 것이다.

## 2. 제안 방법

제안 시스템은 입력 이미지, weather preprocessing, hazard reasoning 모듈로 구성된다. 입력은 단일 전방 카메라 이미지이며, weather preprocessing 단계에서는 `{weather_type, visibility, illumination, road_condition}` 구조의 weather token을 사용한다. 현재 단계에서는 manual mode를 기본으로 채택하여 안정적인 실험이 가능하도록 하였다.

Hazard reasoning 단계에서는 이미지와 weather token을 함께 Qwen2.5-VL-3B-Instruct에 입력한다. 출력은 `hazard_object`, `risk_level`, `reason`, `explanation`을 포함하는 structured JSON을 우선 생성하며, 한국어 설명문은 포스터 시연에 활용한다. 프롬프트는 단순 객체 설명이 아니라, 악천후가 위험 판단에 미치는 영향을 반드시 반영하도록 설계하였다.

## 3. 구현 및 평가

프로토타입은 Python 기반으로 구현되었으며 추론, weather preprocessing, prompting, evaluation 모듈로 분리하였다. 또한 GPU가 없는 환경에서도 개발을 계속할 수 있도록 CPU fallback과 heuristic fallback 경로를 함께 제공하였다. 초기 데이터는 10~30장 규모의 소규모 세트를 목표로 하며, 보행자, 전방 차량, 차선/곡선/교차로 장면에 fog, rain, snow, night 조건을 포함하도록 설계하였다.

평가는 경량 지표를 사용한다. 첫째, structured JSON parsing success rate를 측정한다. 둘째, 생성 explanation과 target explanation 간 ROUGE-L을 계산한다. 셋째, hazard object와 risk level field accuracy를 함께 확인한다. ICROS 단계에서는 정량 지표보다 동일 장면에서 날씨 조건 변화에 따라 설명이 달라지는 정성 사례가 더 중요하다.

## 4. 결론

본 논문에서는 악천후 조건을 반영한 자율주행 hazard reasoning 프로토타입을 제안하였다. 제안 방식은 단일 이미지와 structured weather token을 입력으로 받아 위험 객체, 위험도, 위험 이유 및 한국어 설명을 생성한다. 본 프로토타입은 악천후가 위험 설명을 어떻게 바꾸는지 직관적으로 보여줄 수 있으며, 향후 weather-aware fine-tuning, end-to-end weather estimation, region grounding 및 멀티센서 확장으로 발전시킬 수 있다.

## 참고문헌

[1] C. Sakaridis, D. Dai, and L. Van Gool, “ACDC: The Adverse Conditions Dataset with Correspondences for Semantic Driving Scene Understanding,” Proc. ICCV, 2021.  
[2] D. Chen, Z. Zhang, L. Cheng, Y. Liu, and X. T. Yang, “INSIGHT: Enhancing Autonomous Driving Safety through Vision-Language Models on Context-Aware Hazard Detection and Reasoning,” arXiv preprint arXiv:2502.00262, 2026.  
[3] Qwen Team, “Qwen2.5-VL Technical Report and Model Release,” 2025.

