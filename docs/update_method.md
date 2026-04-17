# Update Method: VSCode + GitHub + Colab

## 1. 목적

이 문서는 현재 프로젝트를 아래 워크플로우로 운영할 때의 업데이트 방법을 정리한다.

- 로컬: VSCode에서 코드/문서 수정
- 저장소: GitHub로 버전 관리
- 실행: Colab GPU에서 추론

핵심 원칙은 다음과 같다.

- 로컬에서 수정
- GitHub에 push
- Colab에서 pull

즉, Colab은 실행 환경이고, 개발의 기준점은 로컬 저장소와 GitHub이다.

---

## 2. 기본 흐름

### 로컬에서 수정 후

```bash
git add .
git commit -m "update prototype"
git push
```

### Colab에서 최신 반영

```python
!git pull
```

이것이 가장 기본적인 업데이트 방식이다.

---

## 3. 로컬 작업 방법

로컬에서 코드를 수정한 뒤 다음 순서로 반영한다.

### 1) 변경 파일 확인

```bash
git status
```

### 2) 변경 내용 추가

```bash
git add .
```

특정 파일만 올리고 싶으면:

```bash
git add src/run_inference.py README.md
```

### 3) 커밋

```bash
git commit -m "update prototype"
```

추천 커밋 메시지 예시:

- `update inference pipeline`
- `revise icros manuscript draft`
- `add annotation workflow docs`
- `fix colab runtime compatibility`

### 4) GitHub로 push

```bash
git push
```

---

## 4. Colab에서 최신 코드 반영

Colab에서는 아래 순서로 진행한다.

### 1) 저장소 위치로 이동

```python
%cd /content/weather-conditioned-hazard-reasoning
```

### 2) 최신 코드 pull

```python
!git pull
```

### 3) 필요 시 패키지 재설치

requirements가 바뀌었으면:

```python
!python -m pip install -r requirements.txt
```

---

## 5. Colab에서 최초 1회 세팅

### 1) 저장소 clone

```python
!git clone https://github.com/kj458622/weather-conditioned-hazard-reasoning.git
%cd weather-conditioned-hazard-reasoning
```

### 2) GPU 확인

```python
!nvidia-smi
```

### 3) 패키지 설치

```python
!python -m pip install --upgrade pip
!python -m pip install -r requirements.txt
```

### 4) Google Drive 연결

```python
from google.colab import drive
drive.mount('/content/drive')
```

### 5) 출력 폴더 생성

```python
!mkdir -p /content/drive/MyDrive/icros_outputs
```

---

## 6. 데이터 업데이트 방식

코드와 문서는 GitHub로 관리하고, 대용량 데이터는 Drive로 관리하는 것을 권장한다.

### GitHub에 올리는 것

- `src/`
- `docs/`
- `README.md`
- `requirements.txt`
- 소형 annotation JSON

### GitHub에 올리지 않는 것

- `data/raw/`
- 대용량 원본 데이터셋
- `outputs/`
- `outputs_prompt/`

### 이미지 데이터 사용 방법

실제 이미지가 Drive에 있을 경우:

```python
!cp -r /content/drive/MyDrive/your_images data/images
```

annotation JSON도 Drive에 둘 수 있다.

---

## 7. 실행 예시

### Colab에서 추론 실행

```python
!python src/run_inference.py \
  --image_dir data/images \
  --annotation_file data/metadata/icros_annotations_draft.json \
  --model_name Qwen/Qwen2.5-VL-3B-Instruct \
  --output_dir /content/drive/MyDrive/icros_outputs \
  --save_overlay
```

---

## 8. 자주 하는 작업

### 코드만 바뀐 경우

로컬:

```bash
git add .
git commit -m "update prototype"
git push
```

Colab:

```python
!git pull
```

### requirements가 바뀐 경우

Colab:

```python
!git pull
!python -m pip install -r requirements.txt
```

### annotation만 바뀐 경우

로컬:

```bash
git add data/metadata/icros_annotations_draft.json
git commit -m "update annotation draft"
git push
```

Colab:

```python
!git pull
```

---

## 9. 권장 운영 방식

- 코드 편집은 로컬 VSCode에서 한다
- Colab에서는 가급적 코드 직접 수정하지 않는다
- Colab에서 수정했다면 로컬과 불일치가 생기므로 장기적으로 불편해진다
- 항상 로컬이 기준이고, GitHub가 동기화 지점이 되도록 유지한다

---

## 10. 한 줄 요약

현재 프로젝트의 권장 업데이트 방식은 아래 한 줄로 정리된다.

> 로컬에서 수정하고 GitHub에 push한 뒤, Colab에서 pull하여 GPU 실행한다.

