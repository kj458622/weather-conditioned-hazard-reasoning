# 내 연구를 이해하기 위한 정리

## 1. 이 연구를 한 줄로 말하면

이 연구는  
**“같은 주행 장면이라도 날씨와 가시성에 따라 왜 더 위험한지가 달라진다는 점을 설명하는 모델”**  
을 만드는 것이다.

조금 더 쉽게 말하면,

- 그냥 “위험하다”라고 말하는 모델이 아니라
- “왜 위험한지”
- 그리고 “날씨 때문에 왜 더 위험해졌는지”

를 함께 설명하는 모델을 만들고자 하는 것이다.

---

## 2. 기존 연구와 뭐가 다른가

기존 hazard reasoning 연구는 보통 이런 질문에 답한다.

- 무엇이 위험한가?
- 어느 위치가 위험한가?
- 위험한 이유는 무엇인가?

그런데 실제 도로에서는  
**같은 객체라도 날씨에 따라 위험의 의미가 달라진다.**

예를 들어:

- 맑은 날의 보행자
- 눈 오는 날의 보행자

는 둘 다 위험할 수 있지만, 위험한 이유는 다르다.

맑은 날에는

- 단순히 거리가 가까워서 위험할 수 있고

눈 오는 날에는

- 가시성이 낮아 발견이 늦을 수 있고
- 노면 상태가 나빠져 제동 여유가 줄어들 수 있다.

즉 이 연구는

> “무엇이 위험한가”에서 끝나는 것이 아니라  
> “왜 지금 이 날씨에서 더 위험한가”까지 설명하는 것

을 목표로 한다.

---

## 3. 내가 만들고 싶은 입력과 출력

## 입력

현재 단계에서 입력은 2개다.

1. 전방 카메라 이미지 1장
2. 날씨 정보 token

예:

```json
{
  "weather_type": "snow",
  "visibility": "low",
  "illumination": "day",
  "road_condition": "unclear"
}
```

즉 모델은 이미지뿐 아니라  
“지금 눈이 오는지”, “가시성이 낮은지”, “야간인지”, “노면이 어떤지”  
를 함께 받는다.

---

## 출력

출력은 이런 구조다.

```json
{
  "hazard_object": "pedestrian",
  "risk_level": "high",
  "reason": "pedestrian near ego path under low visibility",
  "explanation": "보행자가 차로 근처에 있으며 눈으로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음"
}
```

즉 모델이 해야 하는 일은:

1. 위험한 객체 또는 상황을 정하고
2. 위험 수준을 정하고
3. 왜 위험한지 설명하고
4. 날씨가 그 위험을 어떻게 키우는지 말하는 것

이다.

---

## 4. 이 연구에서 중요한 포인트

이 연구에서 제일 중요한 포인트는  
**날씨가 reasoning에 들어간다**는 것이다.

예를 들어 같은 이미지라도:

- `clear`
- `fog`
- `night`

를 넣었을 때 설명이 달라져야 한다.

예:

- 맑은 날:  
  `전방 보행자와의 거리가 가까워 주의가 필요함`

- 안개:  
  `전방 보행자와의 거리가 가깝고 안개로 인해 가시성이 낮아 조기 대응이 어려움`

- 야간:  
  `전방 보행자가 야간 조도에서 눈에 덜 띄어 발견이 늦어질 수 있음`

즉 이 연구는 “객체 인식”보다  
**weather-conditioned explanation**이 핵심이다.

---

## 5. 지금 단계에서 하는 것

지금은 ICROS 포스터용 1차 프로토타입 단계다.

그래서 지금 하는 것은 아래 정도다.

- 단일 이미지 사용
- weather token 수동 입력
- Qwen2.5-VL 기반 추론
- structured JSON 생성
- 한국어 설명 생성
- 결과 저장

즉 지금 목표는

> “일단 돌아가는 데모를 만드는 것”

이다.

---

## 6. 지금 단계에서 안 하는 것

지금은 아래를 하지 않는다.

- LiDAR 사용
- 대규모 데이터셋 학습
- end-to-end fine-tuning
- localization head 추가
- 실시간 시스템
- planning/control 연결

이유는 단순하다.

지금은 연구 전체를 완성하는 단계가 아니라,  
**핵심 아이디어가 성립하는지 보여주는 단계**이기 때문이다.

---

## 7. 왜 학습을 안 해도 되나

이 부분이 헷갈릴 수 있다.

“연구인데 왜 학습을 안 하지?”  
라는 생각이 들 수 있다.

하지만 지금은

- 대규모 성능 비교 논문
- 최종 완성형 모델

이 아니라,

- weather-conditioned reasoning이 가능한지 확인하는
- 초기 proof-of-concept

단계다.

Qwen2.5-VL 같은 VLM은 원래

- 이미지 이해
- 텍스트 생성
- instruction following

능력이 어느 정도 학습되어 있다.

그래서 지금은

- weather token을 잘 넣고
- prompt를 잘 구성해서
- explanation이 달라지는지 확인하는 것

만으로도 충분히 의미가 있다.

즉,

> 지금은 “학습이 필요 없는 연구”가 아니라  
> “학습 전 단계 연구”라고 보는 것이 맞다.

---

## 8. 왜 localization보다 explanation이 우선인가

INSIGHT 같은 연구는

- 위험 위치를 찍고
- 그 이유를 설명하는 방식

에 가깝다.

하지만 지금 내 연구의 핵심은

- “어디가 위험한가”보다
- “왜 지금 날씨에서 더 위험한가”

이다.

즉 현재 단계에서는

- 좌표 예측
- bounding box
- heatmap head

보다

- weather-conditioned explanation

이 더 중요하다.

그래서 localization은 지금 당장 필수가 아니라  
향후 확장 과제로 두는 것이 맞다.

---

## 9. 단일 이미지라서 조심해야 하는 점

현재 입력은 이미지 1장이다.

그래서 모델이 조심해야 하는 것도 있다.

예를 들어 이런 표현은 너무 강할 수 있다.

- `감속 중이다`
- `차로에 진입 중이다`
- `곧 충돌한다`

단일 이미지로는 시간 축 정보가 없기 때문이다.

그래서 지금 연구에서는 이런 식으로 말하는 게 더 적절하다.

- `감속 가능성이 있다`
- `차로 근처에 위치해 있다`
- `조기 대응이 어려워질 수 있다`
- `안전거리가 더 필요하다`

즉 지금 모델은

> 행동을 정확히 판정하는 모델이 아니라  
> 장면과 날씨를 바탕으로 위험 가능성을 설명하는 모델

이다.

---

## 10. 지금 내가 실제로 해야 하는 것

이 연구를 진행하기 위해 지금 해야 하는 실질적 작업은 다음과 같다.

1. ACDC 같은 데이터셋에서 이미지 고르기
2. 각 이미지에 weather token 붙이기
3. 각 이미지에 hazard reasoning annotation 작성
4. Qwen2.5-VL로 추론 돌리기
5. 결과가 날씨에 따라 달라지는지 확인하기
6. 대표 예시를 포스터와 논문에 넣기

즉 지금 가장 중요한 건  
**실험 결과를 실제로 한 번 뽑아보는 것**이다.

---

## 11. 이 연구의 전체 로드맵

## Phase 1: 지금

- image + weather token
- prompt-based reasoning
- structured JSON
- 포스터용 데모

## Phase 2: 다음

- weather token 자동 추론
- LoRA / fine-tuning
- 더 많은 데이터셋

## Phase 3: 이후

- localization 추가
- uncertainty-aware explanation
- LiDAR / multi-modal 확장

즉 지금은 전체 연구 중  
**가장 첫 번째 실험 단계**다.

---

## 12. 최종적으로 내가 이해해야 하는 핵심

이 연구는

- 객체 탐지 연구가 아니고
- 날씨 분류 연구만도 아니고
- localization 연구만도 아니다.

이 연구는

> **이미지와 날씨 조건을 함께 보고,  
> 왜 지금 이 장면이 더 위험한지를 설명하는 모델**

을 만드는 것이다.

그리고 이번 ICROS에서는 그 전체 연구 중에서

> **“weather-conditioned hazard reasoning이 실제로 가능하다”**

를 보여주는 최소 기능 프로토타입을 구현하는 것이 목표다.

---

## 13. InSIGHT를 기준으로 보면 내 연구는 무엇인가

내가 참고한 핵심 논문은 `InSIGHT.pdf`이다.

InSIGHT는 자율주행 장면에서

- 어디를 주의해야 하는지
- 왜 그 지점이 위험한지

를 Vision-Language Model로 설명하려는 연구다.

조금 더 구체적으로 보면 InSIGHT는

- Qwen2-VL을 backbone으로 사용하고
- 위험 위치를 좌표 또는 heatmap 형태로 다루며
- 위험 이유를 자연어로 설명하는 구조를 가진다.

즉 InSIGHT의 핵심은

> **hazard localization + hazard reasoning**

이다.

---

## 13.1 내가 InSIGHT에서 참고한 부분

내 연구는 InSIGHT에서 아래 문제의식을 참고한다.

### 1) 자율주행 위험을 자연어로 설명해야 한다

기존 perception 시스템은 객체를 탐지할 수는 있어도,
왜 지금 장면이 위험한지 자연어로 설명하는 데는 한계가 있다.

이 점에서 InSIGHT는 매우 중요한 참고점이다.

### 2) VLM을 자율주행 hazard reasoning에 쓸 수 있다

InSIGHT는 Qwen 기반 VLM이

- 장면을 이해하고
- 위험을 설명하며
- 사람에게 해석 가능한 출력을 만들 수 있다는 점

을 보여준다.

내 연구도 이 점을 그대로 이어받는다.

### 3) 자율주행 위험은 단순 인식이 아니라 reasoning 문제다

InSIGHT는 위험을 단순한 detection 문제가 아니라
context-aware reasoning 문제로 본다.

내 연구도 마찬가지로

- 단순 객체 인식이 아니라
- 위험 이유를 설명하는 문제

로 접근한다.

---

## 13.2 내가 InSIGHT와 다른 부분

하지만 내 연구는 InSIGHT를 그대로 따라가는 것이 아니다.

가장 중요한 차이는 다음과 같다.

### InSIGHT

- 어디가 위험한가
- 왜 위험한가
- 위험 위치 grounding

### 내 연구

- 같은 장면이라도 날씨에 따라 왜 더 위험한가
- weather-conditioned explanation
- localization보다 explanation 우선

즉 InSIGHT가

> **hazard localization을 포함한 reasoning 연구**

라면,

내 연구는

> **weather-aware hazard explanation 연구**

에 더 가깝다.

---

## 13.3 왜 InSIGHT를 그대로 복제하지 않는가

처음에는 InSIGHT처럼

- 위험 위치를 찍고
- 그 이유를 설명하는 구조

를 그대로 가져올 수도 있어 보인다.

하지만 지금 내 연구 목표는 ICROS 포스터용 1차 프로토타입이다.

그래서 InSIGHT 전체를 그대로 재현하면 다음 문제가 생긴다.

- 위치 annotation이 추가로 필요함
- heatmap head 같은 구조 확장이 필요함
- 학습 비용이 커짐
- 현재 핵심 메시지인 “악천후가 reasoning을 바꾼다”가 흐려질 수 있음

따라서 현재 단계에서는

- InSIGHT의 “hazard reasoning” 문제의식은 참고하되
- localization은 뒤로 미루고
- weather-conditioned explanation에 집중하는 것이 맞다.

---

## 13.4 지금 연구를 InSIGHT 기반으로 설명하면

내 연구는 이렇게 설명하면 가장 정확하다.

> InSIGHT가 자율주행 장면에서 위험 위치와 위험 이유를 설명하는 VLM 기반 hazard reasoning 연구라면,  
> 내 연구는 그 문제를 악천후 조건까지 확장하여, 같은 장면에서도 weather condition에 따라 위험 설명이 어떻게 달라지는지를 다루는 연구이다.

또는 더 짧게 말하면:

> **InSIGHT의 hazard reasoning 문제를 weather-conditioned explanation 문제로 확장한 연구**

라고 볼 수 있다.

---

## 13.5 논문/발표에서 어떻게 말하면 좋은가

발표나 논문에서 InSIGHT와의 관계는 아래처럼 설명하면 된다.

### 한 줄 버전

> 본 연구는 InSIGHT와 같은 hazard reasoning 계열 연구를 참고하되, 위험 위치 예측보다 악천후 조건을 반영한 위험 이유 설명에 초점을 둔다.

### 조금 더 긴 버전

> 기존 VLM 기반 hazard reasoning 연구인 InSIGHT는 위험 영역과 그 이유를 설명하는 데 초점을 두고 있으나, 날씨와 가시성 변화에 따라 위험의 성격이 어떻게 달라지는지는 직접적으로 다루지 않는다. 본 연구는 이러한 한계를 보완하기 위해 image와 structured weather token을 함께 입력하여 weather-conditioned hazard explanation을 생성하는 프로토타입을 제안한다.

---

## 14. 마지막 한 줄 정리

내 연구는  
**“악천후 조건이 위험 설명을 어떻게 바꾸는지 보여주는 자율주행 VLM 프로토타입”**  
이다.
