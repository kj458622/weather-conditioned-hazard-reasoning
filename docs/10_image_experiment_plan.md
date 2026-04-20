# 10장 기준 ICROS 실험 플랜

## 1. 실험 목표

이번 실험의 목적은 성능 경쟁이 아니라, 아래 질문에 답하는 것이다.

- image + weather token을 함께 넣었을 때 설명이 실제로 달라지는가
- 그 변화가 악천후 조건을 반영한 방향으로 나타나는가
- structured JSON 출력이 안정적으로 생성되는가

즉, 이번 10장 실험은 **weather-conditioned hazard reasoning이 가능한지 보여주는 정성 중심 proof-of-concept** 실험이다.

---

## 2. 10장 구성 원칙

10장은 아래처럼 나누는 것이 가장 좋다.

- 보행자 장면: 4장
- 전방 차량 장면: 3장
- 차선/곡선/교차로 장면: 3장

날씨는 아래 4개를 반드시 섞는다.

- fog
- rain
- snow
- night

핵심은 **같은 유형의 hazard가 날씨에 따라 다르게 설명될 수 있는 장면**을 고르는 것이다.

---

## 3. 추천 10장 구성

### A. 보행자 장면 4장

1. pedestrian + snow + day
- 보행자가 차로 또는 횡단보도 근처에 있는 장면
- 포인트: 강설, 저가시성, 제동 여유 감소

2. pedestrian + night
- 야간에 보행자가 조명이 약한 구역에 있는 장면
- 포인트: 저조도, 늦은 식별 가능성

3. pedestrian + rain
- 비 오는 환경에서 보행자가 노면 가장자리 또는 차로 근처에 있는 장면
- 포인트: 젖은 노면, 시야 저하

4. pedestrian + fog
- 안개 속 보행자 장면
- 포인트: 저가시성, 조기 대응 곤란

### B. 전방 차량 장면 3장

5. front vehicle + fog
- 전방 차량이 가까운 거리에서 보이는 장면
- 포인트: 속도 변화 파악 어려움, 안전거리 필요

6. front vehicle + rain
- 젖은 노면 위 전방 차량 장면
- 포인트: 제동거리 증가, 추돌 위험 설명

7. queued vehicles + snow
- 정체 또는 저속 차량열이 보이는 장면
- 포인트: 눈, 노면 상태, 대응 여유 감소

### C. 도로 구조 장면 3장

8. lane ambiguity + rain night
- 비 오는 야간에 차선이 흐린 장면
- 포인트: 차선 경계 불명확

9. curve road + fog
- 안개 낀 곡선 도로
- 포인트: 시계 제한, 곡률 인지 어려움

10. intersection/merge + night or fog
- 교차로 또는 합류 구간 장면
- 포인트: 복합 위험, 전방 파악 제한

---

## 4. 이미지 1장당 annotation 항목

각 이미지에는 아래만 있으면 된다.

### 필수 메타데이터

- `id`
- `image_path`
- `weather.weather_type`
- `weather.visibility`
- `weather.illumination`
- `weather.road_condition`

### 필수 target

- `hazard_object`
- `risk_level`
- `reason`
- `explanation_ko`

예시:

```json
{
  "id": "img_0001",
  "image_path": "data/images/img_0001.jpg",
  "weather": {
    "weather_type": "fog",
    "visibility": "low",
    "illumination": "day",
    "road_condition": "clear"
  },
  "target": {
    "hazard_object": "front_vehicle",
    "risk_level": "high",
    "reason": "front vehicle ahead under low visibility",
    "explanation_ko": "전방 차량이 가까운 거리에 위치해 있으며 안개로 인해 전방 상황 파악이 제한되어 안전거리 확보가 더 필요함"
  }
}
```

---

## 5. 추론 실험은 어떻게 할 것인가

이번 10장 실험은 아래 3단계로 돌리는 것이 가장 좋다.

### 실험 1. 기본 추론

목적:
- 현재 파이프라인이 안정적으로 도는지 확인

입력:
- 이미지
- 정답 weather token

출력:
- structured JSON
- free-text explanation
- overlay 이미지

확인할 것:
- JSON 파싱 성공 여부
- explanation이 너무 일반적인지 여부
- 한국어 문장이 자연스러운지 여부

### 실험 2. weather-conditioned 변화 확인

목적:
- 같은 유형 장면에서 weather token이 설명을 실제로 바꾸는지 확인

방법:
- 같은 장면 또는 유사 장면에 대해 weather token을 바꿔 넣어본다

예:
- `clear` vs `fog`
- `day` vs `night`
- `clear road` vs `slippery/unclear road`

확인할 것:
- explanation에 visibility, illumination, road condition 영향이 반영되는가
- risk level이 합리적으로 달라지는가

### 실험 3. 정성 사례 선별

목적:
- 포스터/논문에 넣을 대표 예시 확보

기준:
- explanation 차이가 명확한 샘플
- JSON 구조가 깔끔한 샘플
- 사람이 읽어도 납득되는 샘플

최종적으로 3~5장만 포스터에 넣으면 충분하다.

---

## 6. 실제 추론 명령

기본 실행:

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations_draft.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir outputs_icros \
  --save_overlay
```

Colab에서는 출력 경로만 Drive로 바꾸면 된다.

```bash
python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations_draft.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir /content/drive/MyDrive/icros_outputs \
  --save_overlay
```

---

## 7. 결과를 어떻게 볼 것인가

각 이미지별로 아래를 같이 확인한다.

- 원본 이미지
- weather token
- generated JSON
- generated explanation
- target explanation
- overlay 결과

좋은 결과의 기준은 아래와 같다.

- 위험 객체가 타당하다
- 위험 수준이 과도하지 않다
- explanation에 weather 영향이 들어간다
- 한국어 문장이 자연스럽다
- 같은 장면 조건 변경 시 설명이 의미 있게 달라진다

---

## 8. 10장 실험에서 꼭 보고할 것

정량:

- JSON parsing success rate
- hazard object accuracy
- risk level accuracy
- ROUGE-L

정성:

- clear vs fog 비교 1개
- day vs night 비교 1개
- pedestrian 사례 1개
- front vehicle 사례 1개
- lane/intersection 사례 1개

즉 정량은 보조이고, **정성 비교 예시가 핵심 결과**다.

---

## 9. 실험 후 바로 해야 하는 일

1. 가장 잘 나온 3~5장을 추린다
2. explanation 문구를 논문 표현과 맞춘다
3. 포스터용 그림 구성을 만든다
4. 논문에 qualitative results 문단을 넣는다
5. 부족한 장면 유형이 있으면 5장 정도 추가한다

---

## 10. 한 줄 정리

이번 10장 실험은

> **적은 수의 대표 장면에서 image + weather token이 실제로 위험 설명을 바꾸는지 확인하는 정성 중심 실험**

으로 이해하면 된다.
