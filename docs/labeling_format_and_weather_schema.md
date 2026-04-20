# ACDC 라벨링 형식 및 Weather 분류 기준

## 1. 이 문서의 목적

이 문서는 이번 ICROS 프로토타입 실험에서 사용할 이미지들을

- 어떤 기준으로 분류할지
- weather 필드를 어떻게 기록할지
- 장면별 hazard reasoning annotation을 어떤 형식으로 남길지

를 정리한 실전용 라벨링 가이드다.

이번 단계의 목표는 대규모 정밀 라벨링이 아니라,
**weather-conditioned hazard reasoning 데모를 만들기 위한 소규모 정성 중심 annotation**이다.

---

## 2. 기본 원칙

이번 라벨링은 복잡하게 하지 않는다.

이미지 1장마다 아래 3가지만 명확하면 충분하다.

1. 이 장면에서 **무엇이 위험한가**
2. 이 장면에서 **왜 위험한가**
3. 날씨/가시성/조도/노면이 **그 위험을 어떻게 키우는가**

즉, 이번 라벨링은 detection annotation이 아니라
**hazard reasoning annotation**이다.

---

## 3. 전체 분류 축

이미지 1장당 아래 3축으로 기록한다.

### A. 장면 유형

- `pedestrian`
- `front_vehicle`
- `lane_boundary`
- `curve_road`
- `intersection_or_merge`

### B. Weather 필드

- `weather_type`
- `visibility`
- `illumination`
- `road_condition`

### C. 출력 목표

- `hazard_object`
- `risk_level`
- `reason`
- `explanation_ko`

---

## 4. Weather 필드 정의

### 4.1 `weather_type`

이번 단계에서는 아래 중 하나만 사용한다.

- `clear`
- `fog`
- `rain`
- `snow`

설명:
- `clear`: 악천후가 아닌 기준 조건
- `fog`: 안개/연무로 시야가 제한된 경우
- `rain`: 비가 오거나 젖은 환경이 분명한 경우
- `snow`: 눈, 적설, 강설 환경이 분명한 경우

주의:
- `night`는 `weather_type`가 아니라 `illumination`에 넣는다

### 4.2 `visibility`

아래 3단계만 사용한다.

- `high`
- `medium`
- `low`

판단 기준:
- `high`: 객체와 차선이 비교적 선명하게 보임
- `medium`: 보이긴 하지만 흐리거나 원거리 확인이 어려움
- `low`: 시야 제한이 뚜렷해 조기 인지가 어려움

### 4.3 `illumination`

아래 2개만 사용한다.

- `day`
- `night`

판단 기준:
- `day`: 주간, 주간 수준의 조도
- `night`: 야간, 터널 수준의 저조도, 야간성 강조 장면

### 4.4 `road_condition`

아래 4개만 사용한다.

- `clear`
- `wet`
- `slippery`
- `unclear`

판단 기준:
- `clear`: 노면 상태가 비교적 정상
- `wet`: 젖은 노면이 보이거나 비 환경으로 판단 가능
- `slippery`: 결빙/적설 등으로 미끄러움이 강하게 시사됨
- `unclear`: 차선 또는 노면 경계가 뚜렷하지 않음

주의:
- `unclear`는 노면 경계/차선 인지 불명확성에 가깝다
- `wet`, `slippery`는 노면 마찰/제동 여유 측면의 상태다

---

## 5. Weather 필드별 권장 분포

10장 기준으로는 아래 정도가 가장 무난하다.

### `weather_type`

- `fog`: 2~3장
- `rain`: 2장
- `snow`: 2~3장
- `clear`: 1~2장

설명:
- `clear`는 비교 기준용으로만 소수 넣는다
- 핵심은 adverse weather가 explanation을 바꾸는 장면이다

### `visibility`

- `low`: 4~5장
- `medium`: 3~4장
- `high`: 1~2장

설명:
- visibility가 explanation 차이를 가장 잘 만들기 때문에 `low` 비중을 높이는 것이 좋다

### `illumination`

- `day`: 6~7장
- `night`: 3~4장

설명:
- weather_type와 조도 조건을 분리해서 보여주기 위해 `night` 샘플도 꼭 넣는다

### `road_condition`

- `clear`: 2~3장
- `wet`: 2장
- `slippery`: 2장
- `unclear`: 3~4장

설명:
- `unclear`는 차선/노면 경계 설명에 유용하다
- `wet`, `slippery`는 비/눈 장면의 위험 설명에 유용하다

---

## 6. 장면 유형별 권장 분포

10장 기준 추천:

- `pedestrian`: 4장
- `front_vehicle`: 3장
- `lane_boundary`: 1장
- `curve_road`: 1장
- `intersection_or_merge`: 1장

설명:
- 보행자와 전방 차량이 weather-conditioned explanation 차이를 가장 만들기 쉽다
- 차선/곡선/교차로는 구조적 위험 예시로 보강한다

---

## 7. 이미지 1장당 실제 기록 형식

아래 2개를 함께 남기면 된다.

### 7.1 사람이 보는 markdown 메모 형식

```md
## img_0001

- image_path: data/images/img_0001.jpg
- scene_category: pedestrian
- weather_type: snow
- visibility: low
- illumination: day
- road_condition: slippery
- hazard_object: pedestrian
- risk_level: high
- reason: pedestrian near ego path under low visibility
- explanation_ko: 보행자가 차로 근처에 있으며 눈으로 인해 가시성이 낮고 노면 상태가 좋지 않아 조기 대응이 어려워 충돌 위험이 높음
- note: 보행자가 차로 경계와 가깝고 적설이 분명하여 weather effect 설명이 쉬운 샘플
```

### 7.2 실제 annotation JSON 형식

```json
{
  "id": "img_0001",
  "image_path": "data/images/img_0001.jpg",
  "scene_category": "pedestrian",
  "weather": {
    "weather_type": "snow",
    "visibility": "low",
    "illumination": "day",
    "road_condition": "slippery"
  },
  "target": {
    "hazard_object": "pedestrian",
    "risk_level": "high",
    "reason": "pedestrian near ego path under low visibility",
    "explanation_ko": "보행자가 차로 근처에 있으며 눈으로 인해 가시성이 낮고 노면 상태가 좋지 않아 조기 대응이 어려워 충돌 위험이 높음"
  }
}
```

---

## 8. 라벨링 절차

이미지 1장 볼 때 아래 순서로 기록한다.

### Step 1. 메인 hazard 결정

다음 중 하나만 고른다.

- `pedestrian`
- `front_vehicle`
- `lane_boundary`
- `curve_road`
- `intersection_or_merge`

주의:
- 한 장면에 위험 요소가 여러 개 있어도 **대표 hazard 1개만** 선택한다

### Step 2. weather 필드 기록

아래를 순서대로 본다.

- 날씨가 무엇인가
- 시야가 얼마나 제한되는가
- 낮/밤인가
- 노면 상태 또는 차선 경계는 어떤가

### Step 3. risk level 결정

3단계만 사용한다.

- `low`
- `medium`
- `high`

판단 기준:
- `low`: 주의는 필요하나 즉각적 위험 강조는 약함
- `medium`: 대응 필요, weather 영향이 분명함
- `high`: weather 때문에 대응 여유가 크게 줄어듦

### Step 4. reason 작성

reason은 영어 짧은 구문으로 쓴다.

예:
- `pedestrian near ego path under low visibility`
- `front vehicle ahead with limited sight distance`
- `lane boundary unclear in rainy night condition`

### Step 5. explanation_ko 작성

한국어 explanation은 아래 3요소가 들어가면 된다.

1. 무엇이 위험한가
2. 왜 위험한가
3. weather가 왜 더 불리하게 만드는가

예:
- `전방 차량이 가까운 거리에 위치해 있으며 안개로 인해 전방 상황 파악이 제한되어 안전거리 확보가 더 필요함`

---

## 9. 좋은 explanation 작성 규칙

좋은 explanation은 아래 조건을 만족한다.

- 주된 위험 대상이 명확하다
- weather 영향이 직접 들어간다
- 과도하게 단정하지 않는다
- 한 문장으로 읽기 쉽다

### 권장 표현

- `차로 근처에 위치해 있음`
- `가시성이 낮아 조기 대응이 어려움`
- `전방 상황 파악이 제한됨`
- `안전거리 확보가 더 필요함`
- `노면 상태 악화로 제동 여유가 줄어듦`

### 피할 표현

- `감속 중이다`
- `차로에 진입 중이다`
- `곧 충돌한다`

이유:
- 단일 이미지로는 시간 축 행동을 확정하기 어렵기 때문이다

---

## 10. markdown 라벨링 템플릿

아래 템플릿을 복사해서 이미지별로 채우면 된다.

```md
# ICROS 10장 라벨링 메모

## img_0001
- image_path:
- scene_category:
- weather_type:
- visibility:
- illumination:
- road_condition:
- hazard_object:
- risk_level:
- reason:
- explanation_ko:
- note:

## img_0002
- image_path:
- scene_category:
- weather_type:
- visibility:
- illumination:
- road_condition:
- hazard_object:
- risk_level:
- reason:
- explanation_ko:
- note:

## img_0003
- image_path:
- scene_category:
- weather_type:
- visibility:
- illumination:
- road_condition:
- hazard_object:
- risk_level:
- reason:
- explanation_ko:
- note:
```

---

## 11. 추천 기록 방식

실제로는 아래처럼 관리하는 것이 좋다.

### 1차 기록

`markdown` 문서에 빠르게 수동 메모

목적:
- 이미지 후보를 빠르게 걸러내기
- 장면별 reasoning 가능 여부를 확인하기

### 2차 정리

최종 선정된 10장은 `json`으로 정리

목적:
- `run_inference.py`에 바로 입력하기
- 평가 및 결과 저장과 연결하기

즉:
- **markdown = 사람이 보는 라벨링 메모**
- **json = 실제 실행용 annotation**

---

## 12. 최종 한 줄 정리

이번 라벨링은

> **장면 유형 1개 + weather 4필드 + risk 설명 4필드**

만 일관되게 기록하면 충분하다.
