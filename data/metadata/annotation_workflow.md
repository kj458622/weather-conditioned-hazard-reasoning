# Hazard Reasoning Annotation Workflow

## 1. 목적

이 문서는 ICROS 발표용 weather-conditioned hazard reasoning 프로토타입을 위해
이미지 1장당 어떤 방식으로 annotation을 작성해야 하는지 정리한다.

현재 단계의 annotation 목표는 다음 4가지를 만드는 것이다.

- 위험 객체
- 위험도
- 위험 이유
- 악천후가 반영된 한국어 설명

중요:

- 지금 단계에서는 bounding box가 필수가 아니다
- 지금 단계에서는 hazard point가 필수가 아니다
- 핵심은 **weather-conditioned explanation annotation**이다

---

## 2. 이미지 1장당 작성해야 하는 항목

각 이미지에 대해 아래 구조를 채운다.

```json
{
  "id": "img_0201_acdc_ped_night_crosswalk",
  "image_path": "data/images/img_0201_acdc_ped_night_crosswalk.jpg",
  "weather": {
    "weather_type": "night",
    "visibility": "medium",
    "illumination": "night",
    "road_condition": "clear"
  },
  "target": {
    "hazard_object": "pedestrian",
    "risk_level": "high",
    "reason": "pedestrian near the crosswalk is less conspicuous at night",
    "explanation_ko": "횡단보도 주변 보행자가 야간 조도에서 눈에 덜 띄어 발견이 늦어질 수 있어 충돌 위험이 높음"
  }
}
```

---

## 3. 작성 순서

이미지 1장을 볼 때 아래 순서로 적는다.

### 1) Primary hazard를 하나 정한다

먼저 이 장면에서 가장 강조하고 싶은 위험을 하나만 정한다.

예:

- pedestrian
- front vehicle
- queued vehicles
- lane boundary
- turning vehicle
- merging vehicle
- road curvature

중요:

- 여러 위험이 보여도 **하나만 대표 hazard로 선택**한다
- 포스터에서는 명확한 primary hazard가 중요하다

### 2) Weather token을 넣는다

아래 4개를 채운다.

- `weather_type`
- `visibility`
- `illumination`
- `road_condition`

권장 값:

#### weather_type

- `clear`
- `fog`
- `rain`
- `snow`

#### visibility

- `low`
- `medium`
- `high`

#### illumination

- `day`
- `night`

#### road_condition

- `clear`
- `slippery`
- `unclear`

---

## 4. 각 항목 작성 규칙

## 4.1 hazard_object

짧고 일관되게 쓴다.

좋은 예:

- `pedestrian`
- `front vehicle`
- `lane boundary`
- `turning vehicle`
- `merging vehicle`

피해야 할 예:

- `a person who might cross the road soon`
- 너무 긴 문장형 표현

---

## 4.2 risk_level

아래 3개만 쓴다.

- `low`
- `medium`
- `high`

판단 기준:

- `high`: 조기 대응 실패 시 충돌 가능성이 크고 weather 영향이 큼
- `medium`: 주의 필요하지만 즉각 충돌 직전은 아님
- `low`: 현재 프로젝트에서는 거의 쓰지 않아도 됨

실제로는 `medium`과 `high` 중심으로 가는 것이 좋다.

---

## 4.3 reason

영문 짧은 설명이다.

구조 추천:

```text
<hazard> + <behavior or scene context> + <weather impact>
```

좋은 예:

- `pedestrian is entering the ego lane under low visibility`
- `front vehicle may decelerate abruptly while fog reduces reaction time`
- `lane boundary is harder to follow because rain and night reduce lane cues`

규칙:

- 짧게
- 행동 또는 장면 맥락 포함
- 날씨 영향 포함

---

## 4.4 explanation_ko

한국어 한 문장 설명이다.

구조 추천:

```text
무엇이 위험한지 + 날씨 때문에 왜 더 위험한지 + 결과적으로 어떤 대응 문제가 생기는지
```

좋은 예:

- `보행자가 차로 쪽으로 진입하고 있으며 안개로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음`
- `앞 차량이 감속 중일 수 있으며 비로 인해 노면이 미끄러워 제동 거리 확보가 더 필요함`
- `야간과 노면 반사로 차선 경계 식별이 어려워 차로 유지 위험이 증가함`

규칙:

- 1문장 권장
- 너무 길지 않게
- 반드시 weather 영향 포함

---

## 5. 가장 쉬운 작성 공식

처음에는 아래 공식대로 적으면 된다.

### 보행자

```text
보행자가 차로 근처에 있으며 <날씨>로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음
```

### 전방 차량

```text
앞 차량이 감속 또는 정지할 수 있으며 <날씨/노면> 때문에 안전거리와 제동 여유가 더 필요함
```

### 차선/곡선

```text
<날씨/야간>으로 차선 또는 도로 형상 단서가 약해져 차로 유지 또는 진행 방향 판단이 어려워질 수 있음
```

---

## 6. 예시 3개

### 예시 1

```json
{
  "hazard_object": "pedestrian",
  "risk_level": "high",
  "reason": "pedestrian is stepping into the ego lane under low visibility",
  "explanation_ko": "보행자가 차로 쪽으로 진입하고 있으며 눈으로 인해 가시성이 낮아 조기 대응이 어려워 충돌 위험이 높음"
}
```

### 예시 2

```json
{
  "hazard_object": "front vehicle",
  "risk_level": "high",
  "reason": "front vehicle may brake abruptly while fog reduces stopping distance margin",
  "explanation_ko": "앞 차량이 급감속할 수 있으며 안개로 인해 시야가 제한되어 안전거리 확보가 더 필요함"
}
```

### 예시 3

```json
{
  "hazard_object": "lane boundary",
  "risk_level": "high",
  "reason": "lane boundary is harder to follow because rain and night reduce lane cues",
  "explanation_ko": "비 오는 야간 환경에서 차선 경계 식별이 어려워 차로 유지 위험이 증가함"
}
```

---

## 7. 피해야 할 annotation

- weather 영향이 없는 설명
- 단순 객체 나열만 있는 설명
- 너무 긴 paragraph
- 한 이미지에 hazard를 두세 개 동시에 넣는 방식
- `reason`과 `explanation_ko`가 서로 다른 의미를 가지는 경우

---

## 8. 현재 단계에서 좌표 라벨링은 필요한가

결론:

- **필수 아님**

이유:

- 현재 ICROS 목표는 hazard localization이 아니라
- weather-conditioned reasoning demonstration이기 때문

좌표 라벨링이 필요해지는 경우:

- InSIGHT 스타일 확장
- heatmap head 추가
- 위험 영역 시각 grounding 실험

지금은 하지 않아도 된다.

---

## 9. 실제 작업 루틴

추천 작업 루틴:

1. 이미지 10장을 고른다
2. 파일명을 정리한다
3. `weather`를 먼저 채운다
4. `hazard_object`를 적는다
5. `risk_level`을 적는다
6. `reason`을 적는다
7. `explanation_ko`를 적는다
8. 5장만 먼저 추론해 본다
9. 결과가 이상하면 annotation 문구를 조금 다듬는다

---

## 10. 최종 목표

최종적으로 필요한 것은 정확한 dense annotation이 아니라,

- 발표에서 바로 읽히는 대표 hazard reasoning 사례
- 악천후가 설명을 바꾸는 qualitative evidence
- structured JSON 기준의 소규모 benchmark

이다.

