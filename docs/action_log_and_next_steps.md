# 작업 로그 및 다음 단계

## 오늘 직접 수행한 항목

- `InSIGHT.pdf` 본문을 추출해 핵심 수정 지점 확인
- 현재 Python / dependency 상태 점검
- `manual` weather mode 실행 확인
- `prompt` weather mode 실행 확인
- annotation template 자동 생성
- ICROS용 분석/논문 계획 문서 작성

---

## 오늘 확인된 환경 상태

- Python: `3.13.9`
- `PIL`, `tqdm`: 설치됨
- `torch`, `transformers`: 초기 상태에서는 미설치
- GPU 확인: `torch` 부재로 미확인
- 의존성 설치: 진행 시도함
- `python`은 `3.13`, 반면 `pip` alias는 다른 경로를 가리킬 수 있어 `python -m pip` 사용이 필요함

주의:

- 현재 `requirements.txt`의 `torch>=2.1.0`는 환경에 따라 CUDA wheel을 크게 받을 수 있다.
- 실제 배포나 서버 환경에서는 CPU 전용 wheel 또는 명시 버전 고정이 더 안전할 수 있다.
- 설치 명령은 `pip install ...`보다 `python -m pip install ...`로 통일하는 것이 안전하다.

---

## 오늘 생성한 산출물

- [docs/insight_to_icros_plan.md](/home/seong/new_research/docs/insight_to_icros_plan.md)
- [data/metadata/icros_annotation_template.json](/home/seong/new_research/data/metadata/icros_annotation_template.json)
- `outputs_prompt/` 테스트 결과

---

## 이번 주에 이어서 바로 할 일

### 데이터

- 실제 발표용 이미지 10~30장 수집
- `data/images/`에 배치
- `data/metadata/icros_annotation_template.json` 기반으로 annotation 작성

### 모델

- 실제 `Qwen/Qwen2.5-VL-3B-Instruct` 로딩 확인
- 가능하면 7B는 비교만 수행
- JSON 출력 안정성 비교

### 프롬프트

- weather condition을 반드시 reasoning에 반영하도록 system prompt 강화
- 설명문 한글 품질 개선

### 논문

- Introduction 1차 초안 작성
- Related Work에서 InSIGHT와의 차별점 명시
- 실험 그림 후보 수집

---

## 이번 주 종료 시점 목표

- 실제 샘플 10장 이상으로 추론 결과 확보
- clear vs fog / day vs night 비교 예시 2세트 확보
- 포스터에 넣을 대표 사례 3~5장 선정
- 논문 초안의 Method / Experiment 섹션 윤곽 완성
