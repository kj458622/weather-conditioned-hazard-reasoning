# data/images 사용 규칙

이 폴더에는 ICROS 발표용 실제 입력 이미지를 넣는다.

권장 규칙:

- 파일명은 장면 특성이 드러나게 작성
- 예: `img_0101_ped_snow_crosswalk.jpg`
- 확장자는 `jpg`, `jpeg`, `png`만 사용

권장 최소 구성:

- 보행자 위험 장면 3장 이상
- 전방 차량 감속/정체 장면 3장 이상
- 차선/교차로/가시성 저하 장면 4장 이상

annotation 작성 절차:

1. 실제 이미지를 이 폴더에 넣는다.
2. `data/metadata/icros_annotations_draft.json`에서 `image_path`를 실제 파일명으로 수정한다.
3. `weather`와 `target`을 장면에 맞게 보정한다.
4. GPU 서버에서 `src/run_inference.py`로 실행한다.

