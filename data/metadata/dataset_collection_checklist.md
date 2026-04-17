# BDD100K / ACDC 수집 체크리스트

## 1. 목적

이 문서는 ICROS 발표용 악천후 hazard reasoning 프로토타입을 위해

- 어떤 데이터셋에서
- 어떤 장면을
- 어떤 기준으로

고르면 좋은지 정리한 체크리스트다.

목표는 대규모 학습셋이 아니라 **발표용 10~30장 소규모 실사용 세트**를 빠르게 만드는 것이다.

---

## 2. 데이터셋별 역할

## 2.1 BDD100K

BDD100K는 기본 도로 장면 다양성이 좋다.

적합한 용도:

- 보행자 장면
- 교차로 장면
- 전방 차량 감속 장면
- 차선, 도로 구조, 일반 주행 장면

장점:

- 도시/교외/고속도로 장면이 다양함
- 객체와 주행 맥락이 비교적 명확함
- baseline scene 확보에 좋음

주의:

- 악천후 밀도가 아주 높지는 않을 수 있음
- weather-conditioned contrast를 만들려면 악천후 장면 선별이 필요함

---

## 2.2 ACDC

ACDC는 adverse weather와 저조도 장면에 강하다.

적합한 용도:

- fog
- rain
- night
- snow

장점:

- 현재 연구 주제와 직접적으로 맞음
- 악천후 영향이 시각적으로 분명함
- "왜 더 위험한가" 설명이 자연스럽게 붙음

주의:

- 모든 장면이 hazard reasoning에 적합하지는 않음
- 악천후는 강하지만 primary hazard가 약한 샘플은 제외하는 편이 좋음

---

## 3. 추천 수집 전략

가장 좋은 전략은 아래 조합이다.

### 전략 A

- BDD100K에서 기본 hazard scene 확보
- ACDC에서 adverse weather scene 보강

추천 이유:

- 장면 다양성과 weather contrast를 동시에 확보 가능

### 전략 B

- ACDC만으로 10장 먼저 선정

추천 이유:

- 빠르게 포스터 메시지를 만들 수 있음
- weather-conditioned reasoning이 가장 잘 드러남

---

## 4. 1차 수집 목표

처음에는 아래 목표만 채우면 충분하다.

- 총 10장
- pedestrian 4장
- front vehicle 3장
- lane/curve/intersection 3장

weather 분포:

- fog 3장
- rain 3장
- night 2장
- snow 2장

---

## 5. 이미지 고를 때 체크리스트

각 이미지를 볼 때 아래를 체크한다.

### 공통 체크

- hazard object 또는 hazard region이 비교적 명확한가
- weather condition이 사람이 봐도 분명한가
- explanation을 한 문장으로 만들기 쉬운가
- image resolution이 충분한가
- 너무 복잡해서 primary hazard를 정하기 어려운가

### 보행자 장면 체크

- 보행자가 차로에 가깝나
- 횡단보도/차로 진입 맥락이 있나
- 야간/비/눈에서 보행자 인지가 어려운가

### 전방 차량 장면 체크

- 앞 차량과의 거리 관계가 보이나
- 감속/정체/합류 같은 맥락이 있나
- 안개/비/눈이 stopping distance 설명으로 이어지나

### 차선/도로형상 장면 체크

- 차선 또는 곡선 형상이 보이나
- 날씨 때문에 도로 단서가 흐려졌나
- "차로 유지", "진행 방향 파악", "교차로 판단" 설명이 가능한가

---

## 6. 바로 고르면 좋은 장면 예시

## BDD100K에서 먼저 찾을 것

- 횡단보도 앞 보행자
- 정류장 주변 보행자
- 전방 차량 브레이크등 점등 장면
- 교차로 회전 차량
- 곡선 도로 진입 장면

## ACDC에서 먼저 찾을 것

- fog + front vehicle
- rain + lane boundary
- night + pedestrian
- snow + queued vehicle
- fog + curve / intersection

---

## 7. 제외 기준

다음 장면은 우선 제외한다.

- hazard가 너무 작게 보이는 장면
- 날씨가 뚜렷하지 않은 장면
- 설명이 "복잡하다" 말고는 안 나오는 장면
- 차량 내부 반사나 대시보드가 너무 큰 비중을 차지하는 장면
- static parked car만 있고 위험 맥락이 약한 장면

---

## 8. 수집 후 바로 할 일

이미지를 고른 뒤 바로 아래 순서로 진행한다.

1. `data/images/`에 저장
2. 파일명을 장면 의미가 드러나게 변경
3. `data/metadata/icros_annotations_draft.json`에 경로 반영
4. weather token 수동 입력
5. target explanation 초안 작성
6. 5장만 먼저 실행해 결과 확인
7. 품질 괜찮으면 10~30장으로 확장

---

## 9. 추천 파일명 예시

```text
img_0201_acdc_ped_night_crosswalk.jpg
img_0202_acdc_front_vehicle_fog.jpg
img_0203_bdd_lane_rain_night.jpg
img_0204_bdd_intersection_turning_vehicle.jpg
img_0205_acdc_snow_queue_vehicle.jpg
```

---

## 10. 최종 목표

최종적으로 확보해야 하는 것은 데이터셋 자체가 아니라 아래 3가지다.

- weather-conditioned reasoning이 잘 드러나는 대표 사례 3~5장
- clear vs adverse-weather 비교 사례 1~2세트
- 포스터에 바로 넣을 수 있는 overlay 및 structured output

