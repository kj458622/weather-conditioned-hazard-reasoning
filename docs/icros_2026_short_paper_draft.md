# 악천후 조건을 반영한 자율주행 Hazard Reasoning 프로토타입

홍길동1, OpenAI Codex2  
1 소속기관명  
2 연구협업 초안 지원  
E-mail: your_email@example.com

## 국문요약

기존 자율주행 hazard reasoning 연구는 주로 장면 내에서 무엇이 위험한지를 설명하는 데 초점을 맞추어 왔다. 그러나 실제 도로 환경에서는 안개, 비, 눈, 야간과 같은 악천후 조건이 위험의 정도와 이유를 직접 바꾼다. 본 연구에서는 전방 카메라 이미지와 악천후 정보를 함께 사용하는 weather-conditioned hazard reasoning 프로토타입을 제안한다. 제안 방식은 단일 이미지와 구조화된 weather token을 Vision-Language Model에 입력하여 위험 객체, 위험도, 위험 이유 및 한국어 설명문을 생성한다. 베이스 모델로는 Qwen2.5-VL-3B-Instruct를 사용하고, weather preprocessing 모듈과 reasoning 모듈을 분리하여 추후 end-to-end weather-aware VLM으로 확장 가능하도록 설계하였다. 또한 manual weather token 기반 추론, structured JSON 출력, 간단한 결과 저장 및 평가 파이프라인을 포함하는 최소 기능 데모를 구현하였다. 본 프로토타입은 ICROS 포스터 단계에서 동일 장면에 대해 날씨 조건을 바꾸었을 때 위험 설명이 어떻게 달라지는지를 정성적으로 제시하는 것을 목표로 한다.

핵심어: 자율주행, 비전-언어모델, 위험 추론, 악천후, 설명 생성

## 1. 서론

자율주행 시스템의 안전성은 주변 객체를 인식하는 수준을 넘어, 현재 장면이 왜 위험한지 이해하고 설명할 수 있는 능력과 밀접하게 연결된다. 최근 Vision-Language Model(VLM)은 이미지와 언어를 함께 처리하며 장면 이해와 자연어 설명에서 강점을 보이고 있어 자율주행 hazard reasoning에도 적용 가능성이 커지고 있다. 그러나 기존 연구는 대체로 위험 객체나 위험 위치를 설명하는 데 집중되어 있으며, 악천후 조건이 위험 판단을 어떻게 바꾸는지에 대한 설명은 상대적으로 부족하다.

실제 주행에서는 동일한 장면이라도 안개, 비, 눈, 야간 조건에 따라 대응 난이도와 위험도가 달라진다. 예를 들어 보행자가 횡단보도 근처에 있는 장면은 맑은 낮보다 야간이나 적설 환경에서 훨씬 높은 주의가 필요하다. 따라서 hazard reasoning은 단순한 객체 설명이 아니라, 환경 조건을 함께 고려한 위험 이유 설명으로 확장될 필요가 있다.

본 연구의 목표는 논문 완성형 시스템이 아니라 ICROS 포스터 발표용 1차 프로토타입을 구현하는 것이다. 이를 위해 본 논문에서는 단일 전방 카메라 이미지와 weather token을 함께 입력받아 구조화된 위험 설명을 생성하는 weather-conditioned hazard reasoning 파이프라인을 제안한다.

## 2. 제안 방법

제안 시스템은 입력 이미지, weather preprocessing, hazard reasoning의 세 모듈로 구성된다. 입력은 단일 전방 카메라 이미지이며, weather preprocessing 단계에서 장면에 대응하는 구조화된 weather token을 생성하거나 불러온다. 본 단계에서는 manual mode를 기본값으로 사용하며, token은 `weather_type`, `visibility`, `illumination`, `road_condition` 네 필드로 구성된다. 예를 들어 안개 환경은 `{fog, low, day, clear}`, 비 오는 야간 환경은 `{rain, medium, night, slippery}`로 표현된다.

Hazard reasoning 단계에서는 이미지와 weather token을 함께 Qwen2.5-VL-3B-Instruct에 입력한다. 모델은 위험 객체, 위험도, 위험 이유, 한국어 설명문을 포함하는 structured JSON을 우선 생성하도록 설계하였다. 출력 예시는 다음과 같다. `{"hazard_object": "pedestrian", "risk_level": "high", "reason": "pedestrian near ego path under low visibility", "explanation": "보행자가 차로 근처에 있으며 안개로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음"}`. 이와 같은 structured output은 후처리, 저장, 평가 및 포스터 시각화에 유리하다.

프롬프트 설계에서는 단순한 객체 나열이 아니라 “왜 위험한가”와 “날씨가 위험 판단에 어떤 영향을 주는가”를 반드시 반영하도록 지시하였다. 또한 현재 단계는 단일 이미지 기반이므로 “감속 중” 또는 “진입 중”과 같은 행동을 단정하기보다, “감속 가능성”, “차로 근처에 위치”, “조기 대응이 어려움”과 같이 보수적인 표현을 사용하도록 설계하였다.

## 3. 구현 및 실험 구성

프로토타입은 Python 기반으로 구현되었으며, `run_inference.py`, `weather_preprocess.py`, `prompting.py`, `evaluate.py` 등으로 모듈화하였다. manual weather token만으로도 전체 추론이 가능하도록 구성하여 GPU가 없거나 모델 다운로드가 제한된 환경에서도 개발을 진행할 수 있도록 하였다. 또한 Qwen 모델 로딩 실패 시 heuristic fallback을 제공하여 파이프라인 전체가 중단되지 않도록 하였다.

초기 데이터셋은 10~30장 규모의 소규모 정성 평가 세트를 목표로 한다. 이미지 유형은 보행자 장면, 전방 차량 장면, 차선/곡선/교차로 장면으로 나누고, 날씨 조건은 fog, rain, snow, night를 우선 포함한다. 각 샘플에는 weather token과 함께 `hazard_object`, `risk_level`, `reason`, `explanation_ko`를 수동 라벨링한다.

평가는 복잡한 정량 실험 대신 프로토타입에 적합한 경량 지표를 사용한다. 첫째, JSON parsing success rate를 통해 structured output 안정성을 확인한다. 둘째, target explanation과 생성 explanation 간 ROUGE-L을 계산하여 설명 유사도를 확인한다. 셋째, `hazard_object`와 `risk_level`에 대한 field accuracy를 함께 측정한다. ICROS 단계에서는 정량 지표 자체보다, 동일 이미지에 대해 날씨 조건을 바꾸었을 때 설명이 의미 있게 달라지는지 보여주는 정성 결과가 더 중요하다.

## 4. 기대 결과 및 논의

본 연구를 통해 기대하는 결과는 다음과 같다. 첫째, 단일 이미지와 weather token만으로도 위험 객체와 위험 이유를 함께 설명하는 최소 기능 데모를 구축할 수 있다. 둘째, 동일 장면이라도 `clear`, `fog`, `rain`, `night` 조건에 따라 설명문이 다르게 생성됨을 확인할 수 있다. 셋째, weather preprocessing과 reasoning 모듈을 분리함으로써 향후 end-to-end weather-aware VLM, LoRA 기반 미세조정, LiDAR 확장 등으로 자연스럽게 이어질 수 있다.

한계도 분명하다. 현재 시스템은 단일 이미지 기반이므로 시간 축 정보가 필요한 행동 판정에는 제약이 있다. 또한 weather token이 수동 또는 프롬프트 기반으로 주어지므로, 실제 운영 수준의 자동화와는 차이가 있다. 데이터셋 규모 역시 작기 때문에 일반화 성능을 주장하기는 어렵다. 그럼에도 불구하고 본 연구는 악천후 조건을 반영한 hazard explanation이라는 문제를 명확히 정의하고, 이를 시연 가능한 형태로 구현했다는 점에서 의의가 있다.

## 5. 결론

본 논문에서는 자율주행 장면에서 악천후 조건을 함께 고려하여 위험 이유를 설명하는 weather-conditioned hazard reasoning 프로토타입을 제안하였다. 제안 방식은 단일 전방 카메라 이미지와 structured weather token을 입력으로 사용하고, Qwen2.5-VL 기반으로 위험 객체, 위험도, 위험 이유 및 한국어 설명문을 생성한다. 구현 결과는 ICROS 포스터 단계에서 악천후가 reasoning을 어떻게 바꾸는지 직관적으로 보여주는 데 활용될 수 있다. 향후에는 weather token 자동 추론, LoRA 기반 fine-tuning, region grounding 및 멀티센서 확장을 통해 보다 정교한 weather-aware autonomous driving reasoning 연구로 발전시킬 계획이다.

## 참고문헌

[1] C. Sakaridis, D. Dai, and L. Van Gool, “ACDC: The Adverse Conditions Dataset with Correspondences for Semantic Driving Scene Understanding,” in Proc. ICCV, 2021.  
[2] D. Chen, Z. Zhang, L. Cheng, Y. Liu, and X. T. Yang, “INSIGHT: Enhancing Autonomous Driving Safety through Vision-Language Models on Context-Aware Hazard Detection and Reasoning,” arXiv preprint arXiv:2502.00262, 2026.  
[3] Qwen Team, “Qwen2.5-VL Technical Report and Model Release,” 2025.
