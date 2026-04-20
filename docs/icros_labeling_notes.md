# ICROS 라벨링 메모

## 사용 방법
	첫 번째: 이 장면의 메인 hazard는 뭔가
	하나만 고른다.

	pedestrian
	front_vehicle
	lane_boundary
	curve_road
	intersection_or_merge
- 원본 ACDC에서 발표용으로 쓸 이미지를 `data/images/`에 복사한 뒤 이 문서에 메모한다.
- 한 이미지에 위험 요소가 여러 개 보여도 **대표 hazard 1개만** 기록한다.
- weather 필드는 아래 값만 사용한다.
  - `weather_type`: `clear`, `fog`, `rain`, `snow`
  - `visibility`: `high`, `medium`, `low`
  - `illumination`: `day`, `night`
  - `road_condition`: `clear`, `wet`, `slippery`, `unclear`
- 메모가 끝나면 `data/metadata/icros_annotations_final.json`에 옮긴다.

---
## example
# ICROS 라벨링 메모

## img_ex
- image_path: data/images/
- scene_category: pedestrian
- weather_type: snow
- visibility: low
- illumination: day
- road_condition: slippery
- hazard_object: pedestrian
- risk_level: high
- reason: pedestrian near ego path under low visibility
- explanation_ko: 보행자가 차로 근처에 있으며 눈으로 인해 가시성이 낮고 노면 상태가 좋지 않아 조기 대응이 어려워 충돌 위험이 높음
- note: 보행자와 차로 거리가 가깝고 적설이 뚜렷함



## img_0001
- image_path:data/images/img_0001_snow_pedestrian
- scene_category:pedestrian
- weather_type:snow
- visibility:medium
- illumination:day
- road_condition:snow
- hazard_object:pedestrian
- risk_level:medium
- reason:many pedestrians near ego path under low visibility
- explanation_ko:보행자들이 차로 근처에 있으며 눈으로 인해 가시성이 낮고 노면 상태가 좋지 않아 조기 대응이 어려워 충돌 위험이 높음
- note:보행자들과 차로 거리가 가깝고 많은 사람이 있어 변수 발생가능성이 높음

## img_0002
- image_path:data/images/img_0002_snow_pedestrian
- scene_category:pedestrian
- weather_type:snow
- visibility:low
- illumination:day
- road_condition:slippery
- hazard_object:pedestrian
- risk_level:medium
- reason:potential pedestrians occluded by parked vehicles near crosswalk under snowy low-visibility conditions
- explanation_ko:전방 횡단보도 인근에 정차된 차량들로 인해 보행자 출현 여부를 명확히 확인하기 어렵고, 눈으로 인해 가시성이 낮아 돌발 보행자에 대한 조기 인지가 어려워 충돌 위험이 높음
- note:횡단보도 앞 시야가 부분적으로 가려져 있고 노면 상태도 좋지 않아 미리 감속하며 잠재적 보행자 출현에 대비해야 함

## img_0003
- image_path:data/images/img_0003_snow_cyclist
- scene_category:cyclist
- weather_type:snow
- visibility:medium
- illumination:day
- road_condition:slippery
- hazard_object:cyclist
- risk_level:medium
- reason:nearby cyclist moving alongside ego vehicle under snowy low-visibility conditions
- explanation_ko:차량 옆에서 자전거 이용자가 주행 중이며, 눈으로 인해 가시성과 노면 상태가 저하되어 자전거의 균형 흔들림이나 예상치 못한 경로 변경이 발생할 수 있어 충돌 위험이 높음
- note:측면 간격을 충분히 확보하고 속도를 줄이며 자전거의 움직임을 지속적으로 관찰해야 함

## img_0004
- image_path:/data/images/img_0004_rain_pedestrian
- scene_category:pedestrian
- weather_type:rain
- visibility:low
- illumination:day
- road_condition:wet
- hazard_object:pedestrian,front_vehicle
- risk_level:medium
- reason:occluded pedestrian risk at crosswalk due to lane-changing vehicle under rainy low-visibility conditions
- explanation_ko:전방 차량이 차선 변경 중 두 개 차선을 동시에 점유하며 시야를 가리고 있고, 그 앞에 횡단보도가 있어 보행자 출현 여부를 확인하기 어려운 상황임. 비로 인해 가시성과 노면 상태가 저하되어 돌발 보행자에 대한 대응이 늦어질 수 있어 충돌 위험이 높음
- note:차선 변경 중인 차량으로 인해 전방 상황 예측이 불확실하며, 횡단보도와 결합되어 잠재적 보행자 위험이 증가함. 감속과 함께 전방 및 좌우 탐색을 강화할 필요가 있음

## img_0005
- image_path:/data/images/img_0005_rain_scooter rider.png
- scene_category:two_wheeler
- weather_type:rain
- visibility:medium
- illumination:day
- road_condition:wet
- hazard_object:two_wheeler
- risk_level:hard
- reason:two_wheeler emergence ahead under rainy low-visibility conditions
- explanation_ko:비가 내리는 상황에서 킥보드 이용자가 차량 전방에 갑자기 나타나 반응 시간이 매우 짧고, 노면이 미끄러워 제동 및 회피가 어려워 충돌 위험이 높음
- note:킥보드는 소형 이륜 이동체로 시각적으로 탐지가 늦어질 수 있고, 빗길에서 균형이 불안정해 급격한 경로 변화 가능성이 높아 선제적 감속과 충분한 안전거리 확보가 필요함

## img_0006
- image_path:/data/images/img_0006_rain_cyclist
- scene_category:cyclist
- weather_type:rain
- visibility:low
- illumination:day
- road_condition:wet
- hazard_object:cyclist
- risk_level:medium
- reason:cyclist traveling in adjacent lane under rainy conditions
- explanation_ko:비가 내리는 상황에서 옆차로에 자전거 이용자가 주행하고 있어, 미끄러짐이나 균형 상실, 갑작스러운 차로 쪽 접근 가능성으로 인해 충돌 위험이 존재함
- note:자전거는 빗길에서 접지력이 낮아지고 움직임이 불안정해질 수 있으므로, 충분한 측면 거리 확보와 속도 조절이 필요함

## img_0007
- image_path:/data/images/img_0007_fog_front_vehicle.png
- scene_category:front_vehicle
- weather_type:fog
- visibility:hard
- illumination:day
- road_condition:fog
- hazard_object:front_vehicle
- risk_level:medium
- reason:dense traffic ahead under foggy low-visibility conditions
- explanation_ko:개로 인해 전방 차량의 위치와 움직임을 명확히 파악하기 어려운 상태에서 교통량이 많아, 선행 차량의 급정지나 흐름 변화에 대한 대응 시간이 부족해질 수 있음
- note:저가시성 환경에서는 차량 군집의 움직임 예측이 어려워지므로, 보수적인 속도 유지와 충분한 안전거리 확보가 요구됨

## img_0008
- image_path:/data/images/img_0008_fog_front_vehicle.png
- scene_category:front_vehicle
- weather_type:fog
- visibility:medium
- illumination:day
- road_condition:fog
- hazard_object:front_vehicle
- risk_level:medium
- reason:potential path crossing from opposing vehicle making U-turn under foggy low-visibility conditions
- explanation_ko:안개로 인해 전방 시야가 제한된 상황에서 반대편 차선의 차량이 유턴을 시도하고 있어, 차량 진행 경로를 가로지를 가능성이 있으며 상대 차량의 움직임을 늦게 인지할 수 있어 충돌 위험이 높음
- note:유턴 차량은 진로가 불확실하고 회전 반경이 커 차로를 침범할 수 있으며, 안개로 인해 거리 및 속도 판단이 어려워 조기 감속과 주의가 필요함

## img_0009
- image_path:/data/images/img_0009_night_unknown_object.png
- scene_category:unknown
- weather_type:night
- visibility:hard
- illumination:night
- road_condition:night
- hazard_object:unknown_object
- risk_level:medium
- reason:unpredictable hazard emergence under nighttime low-visibility conditions
- explanation_ko:야간으로 인해 전반적인 시야 확보가 어려운 상황이며, 어두운 환경 때문에 차량·보행자·이륜 이동체 등 위험 요소가 어느 위치에서 나타날지 미리 파악하기 어려워 충돌 위험이 높음
- note:조명 범위 밖 영역과 시야 사각지대에서 돌발 상황이 발생할 가능성이 높아, 속도를 줄이고 주변 탐색을 강화하며 보수적으로 주행해야 함

## img_0010
- image_path:/data/images/img_0010_night_cyclist.png
- scene_category:cyclsit
- weather_type:night
- visibility:low
- illumination:night
- road_condition:night
- hazard_object:cyclist,pedestrian
- risk_level:medium
- reason:dense pedestrian environment with adjacent-lane bicycle under nighttime urban conditions
- explanation_ko:야간 번화가 환경에서 인도에 많은 보행자가 밀집해 있고, 옆차로에 자전거 이용자가 주행 중이어서 보행자의 차로 유입이나 자전거의 예상치 못한 움직임으로 인한 충돌 위험이 존재함
- note:보행자 밀집 지역에서는 일부 보행자가 도로로 접근할 가능성이 있으며, 자전거는 불안정한 궤적을 보일 수 있어 측면 간격 확보와 속도 조절이 필요함
