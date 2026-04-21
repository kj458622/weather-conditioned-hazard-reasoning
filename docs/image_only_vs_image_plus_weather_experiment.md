# Image-Only vs Image+Weather 실험 결과 정리 (v4)

## 실험 개요

- **목표:** weather token이 hazard explanation을 실제로 바꾸는지 확인
- **모델:** Qwen2.5-VL-3B-Instruct (prompt-conditioned inference, fine-tuning 없음)
- **데이터:** ACDC adverse-weather 이미지 10장 (fog, rain, snow, night)
- **실험 버전:** v4 (dtype=bfloat16 + attn_implementation=eager + device_map=auto)

---

## 실험 설정

| 항목 | image_only | image_weather |
|------|-----------|---------------|
| 입력 | 이미지 + unknown weather token | 이미지 + true weather token |
| weather_type | unknown | snow / rain / fog / night |
| visibility | unknown | low / medium |
| illumination | unknown | day / night |
| road_condition | unknown | slippery / clear |

---

## Metrics 비교

| metric | image_weather | image_only |
|--------|:------------:|:---------:|
| json_parse_success_rate | 0.7 | 0.7 |
| hazard_object_accuracy | 0.1 | 0.1 |
| risk_level_accuracy | 0.6 | 0.6 |
| rouge_l_f1 | 0.0 | 0.0 |

> **rouge_l_f1 = 0.0인 이유:** annotation의 `explanation_ko`가 한국어이고 모델 출력은 영어라서 토큰이 전혀 겹치지 않음. 실제 explanation 품질과 무관한 수치.

---

## Per-Sample 비교

### img_0001 | snow | parse=True | explanation_changed=**True**

**weather token:** snow / visibility=medium / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The presence of pedestrians crossing the street in snowy conditions increases the risk for autonomous driving due to reduced visibility and slippery surfaces, which can lead to accidents if the vehicle fails to detect or respond appropriately to the pedestrians' movements. |
| **image_weather** | The heavy snowfall reduces visibility, making it difficult for pedestrians to see approaching vehicles clearly. This increases the risk of accidents as drivers may not notice the pedestrians until it's too late. |

**분석:** image_weather는 "heavy snowfall reduces visibility"를 weather token 기반으로 명시. 원인 중심의 설명으로 재구성됨.

---

### img_0002 | snow | parse=**False** | explanation_changed=False

**weather token:** snow / visibility=low / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The scene requires caution under the provided weather condition. |
| **image_weather** | The scene requires caution under the provided weather condition. |

**분석:** parse 실패 → fallback 출력. 모델이 structured JSON 생성 실패.

---

### img_0003 | snow | parse=**False** | explanation_changed=False

**weather token:** snow / visibility=medium / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The scene requires caution under the provided weather condition. |
| **image_weather** | The scene requires caution under the provided weather condition. |

**분석:** parse 실패 → fallback 출력.

---

### img_0004 | rain | parse=True | explanation_changed=**True**

**weather token:** rain / visibility=low / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The presence of pedestrians crossing the street in the rain increases the risk due to reduced visibility and slippery surfaces, which can lead to accidents if drivers fail to react quickly enough. |
| **image_weather** | The presence of pedestrians crossing the street at a red light increases the risk for autonomous driving due to reduced visibility and potential sudden movements from the pedestrians. The wet road conditions further reduce traction, making it challenging for the vehicle to stop quickly if necessary. |

**분석:** image_weather는 "wet road conditions further reduce traction"을 추가 언급. weather token의 road_condition=slippery가 반영됨.

---

### img_0005 | rain | parse=True | explanation_changed=**True**

**weather token:** rain / visibility=low / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The presence of a skateboarder on the sidewalk, combined with the rainy weather, reduces visibility and increases the risk of accidents. The wet pavement makes it slippery, and the skateboarder's movement could obstruct the view for oncoming vehicles. |
| **image_weather** | The skateboarder is navigating through the wet street, which increases the risk of slipping and losing control. The rain reduces traction, making it difficult to maintain balance and speed, especially near the tram tracks where the road surface is likely to be slippery. |

**분석:** image_weather는 tram tracks + wet surface의 구체적 위험 조합을 설명. 장면 세부사항과 weather token이 결합된 설명.

---

### img_0006 | rain | parse=True | explanation_changed=**True**

**weather token:** rain / visibility=low / illumination=day / road=slippery

| | explanation |
|--|-------------|
| **image_only** | The cyclist is riding on the sidewalk, which is not designated for cyclists. This increases the risk of accidents due to the slippery pavement and reduced visibility caused by the rain. |
| **image_weather** | The cyclist is riding on the right side of the road, which is against the traffic rules. This increases the risk of collision with oncoming vehicles, especially since the road appears wet due to recent rain, reducing traction and visibility. Additionally, the cyclist's presence in the lane where the tram tracks run adds complexity to the driving scenario. |

**분석:** image_weather는 wet road + tram tracks 복합 위험을 명시. 더 구체적인 장면 분석.

---

### img_0007 | fog | parse=True | explanation_changed=**True**

**weather token:** fog / visibility=low / illumination=day / road=clear

| | explanation |
|--|-------------|
| **image_only** | The dense fog significantly reduces visibility, making it difficult for the autonomous vehicle to detect pedestrians at the crossing. This lack of clear sight increases the risk of accidents, especially if the pedestrian is not visible due to the fog's opacity. |
| **image_weather** | The low visibility due to fog significantly reduces the driver's ability to see pedestrians clearly, increasing the risk of accidents. Pedestrians may not be easily identifiable, making it difficult for the autonomous vehicle to detect them in time to avoid collisions. |

**분석:** image_weather는 "low visibility due to fog"를 weather token 기반으로 명시적으로 프레이밍.

---

### img_0008 | fog | parse=True | explanation_changed=**True**

**weather token:** fog / visibility=low / illumination=day / road=clear

| | explanation |
|--|-------------|
| **image_only** | The foggy conditions significantly reduce visibility, making it difficult to see other vehicles and pedestrians clearly. This increases the risk of collisions due to reduced reaction time and difficulty in maintaining safe distances from other road users. |
| **image_weather** | The fog reduces visibility, making it difficult to see other vehicles and pedestrians clearly. This increases the risk of collisions due to reduced reaction time and difficulty in maintaining safe distances. |

**분석:** 두 설명 모두 fog를 언급하나 image_only가 더 verbose. image_weather가 weather token 기반으로 간결하게 fog 효과를 표현.

---

### img_0009 | night | parse=True | explanation_changed=**True**

**weather token:** night / visibility=low / illumination=night / road=clear

| | explanation |
|--|-------------|
| **image_only** | The road appears to be curved, and the darkness makes it difficult to see the edges and markings clearly. This can lead to difficulty in maintaining lane discipline and potentially causing accidents if the driver cannot see the road ahead properly. |
| **image_weather** | The low visibility due to night conditions makes it difficult for the autonomous vehicle to clearly see the curve ahead, increasing the risk of a collision if the vehicle cannot adjust its speed or direction accordingly. |

**분석:** image_only는 "darkness"라는 일반 표현, image_weather는 "night conditions" + curve 위험을 weather token과 연결하여 구체화.

---

### img_0010 | night | parse=**False** | explanation_changed=False

**weather token:** night / visibility=low / illumination=night / road=clear

| | explanation |
|--|-------------|
| **image_only** | The scene requires caution under the provided weather condition. |
| **image_weather** | The scene requires caution under the provided weather condition. |

**분석:** parse 실패 → fallback 출력.

---

## 종합 요약

| 항목 | 결과 |
|------|------|
| 실제 모델 추론 성공 (parse_ok=True) | 10장 중 **7장** |
| explanation 변화 발생 | parse 성공 7장 중 **7장 전부** |
| parse 실패 (fallback) | 3장 (img_0002, 0003, 0010) |

### Weather token 효과 확인된 사례

| weather | 샘플 | 핵심 변화 |
|---------|------|----------|
| snow | img_0001 | "heavy snowfall reduces visibility" 명시 |
| rain | img_0004 | "wet road conditions further reduce traction" 추가 |
| rain | img_0005 | tram tracks + wet surface 복합 위험 설명 |
| fog | img_0007 | "low visibility due to fog" 프레이밍 |
| night | img_0009 | "night conditions" + curve 위험 연결 |

### 한계

- 10장 중 3장 parse 실패 (JSON 생성 불안정)
- fine-tuning 없이 prompt-conditioned inference만 사용
- weather token이 외부 제공이라 end-to-end weather-aware 모델은 아님
- rouge_l_f1은 한국어 annotation과 영어 출력 비교로 의미없는 수치

### 논문 활용 방향

- 정성적 비교 대표 사례: img_0001(snow), img_0004(rain), img_0009(night)
- 핵심 주장 근거: parse 성공 7/7장에서 explanation 변화 → weather token이 실제로 explanation을 바꿈
- parse 실패 3장은 현재 단계의 한계로 논문에 명시
