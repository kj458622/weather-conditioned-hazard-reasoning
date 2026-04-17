# Annotation Checklist

이미지 1장을 annotation하기 전에 아래를 체크한다.

## 기본 체크

- primary hazard를 하나만 정했는가
- weather_type을 넣었는가
- visibility를 넣었는가
- illumination을 넣었는가
- road_condition을 넣었는가
- hazard_object가 짧고 일관적인가
- risk_level이 `low/medium/high` 중 하나인가
- reason에 weather 영향이 들어갔는가
- explanation_ko에 weather 영향이 들어갔는가
- explanation_ko가 한 문장으로 읽히는가

## 품질 체크

- 단순 객체 설명으로 끝나지 않는가
- 왜 위험한지가 드러나는가
- 날씨가 없으면 설명이 달라져야 하는가
- 포스터에 넣어도 한눈에 이해되는가

## 현재 단계 체크

- bounding box를 안 넣어도 괜찮다
- hazard point를 안 넣어도 괜찮다
- 지금은 reasoning annotation이 우선이다

