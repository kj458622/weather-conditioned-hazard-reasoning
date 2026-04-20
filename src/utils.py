"""Utility helpers for the weather-conditioned hazard reasoning prototype."""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_WEATHER_TOKEN = {
    "weather_type": "clear",
    "visibility": "medium",
    "illumination": "day",
    "road_condition": "clear",
}
DEFAULT_REASONING_OUTPUT = {
    "hazard_object": "unknown",
    "risk_level": "medium",
    "reason": "scene requires caution under the provided weather condition",
    "explanation": "주어진 날씨 조건에서 주의가 필요한 장면입니다.",
}

WEATHER_LABELS_KO = {
    "clear": "맑은 날씨",
    "snow": "눈",
    "fog": "안개",
    "rain": "비",
    "night": "야간",
}

VISIBILITY_LABELS_KO = {
    "low": "낮은",
    "medium": "보통",
    "high": "높은",
}

ROAD_CONDITION_LABELS_KO = {
    "clear": "양호한",
    "wet": "젖은",
    "unclear": "불명확한",
    "slippery": "미끄러운",
}

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def ensure_dir(path: os.PathLike[str] | str) -> Path:
    """Create a directory if missing and return it as Path."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def load_json(path: os.PathLike[str] | str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(data: Any, path: os.PathLike[str] | str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def iter_image_files(image_dir: os.PathLike[str] | str) -> List[Path]:
    """Return sorted supported image paths from a directory."""
    image_dir = Path(image_dir)
    if not image_dir.exists():
        raise FileNotFoundError(f"Image directory does not exist: {image_dir}")
    if not image_dir.is_dir():
        raise NotADirectoryError(f"Expected an image directory, got: {image_dir}")

    image_paths = [
        path
        for path in sorted(image_dir.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    return image_paths


def normalize_record(record: Dict[str, Any], image_dir: Optional[os.PathLike[str] | str] = None) -> Dict[str, Any]:
    """Normalize annotation items into a unified internal format."""
    normalized = dict(record)
    image_path = normalized.get("image_path")
    if image_path and image_dir and not Path(image_path).is_absolute():
        candidate = Path(image_dir) / Path(image_path).name
        if candidate.exists():
            normalized["image_path"] = str(candidate)
    if "weather" not in normalized or not isinstance(normalized["weather"], dict):
        normalized["weather"] = dict(DEFAULT_WEATHER_TOKEN)
    return normalized


def load_annotations(
    annotation_file: Optional[os.PathLike[str] | str],
    image_dir: os.PathLike[str] | str,
) -> List[Dict[str, Any]]:
    """Load annotations from JSON or CSV, or build records directly from image directory."""
    image_dir = Path(image_dir)
    if annotation_file is None:
        return [
            {
                "id": image_path.stem,
                "image_path": str(image_path),
                "weather": dict(DEFAULT_WEATHER_TOKEN),
            }
            for image_path in iter_image_files(image_dir)
        ]

    annotation_path = Path(annotation_file)
    if not annotation_path.exists():
        raise FileNotFoundError(f"Annotation file does not exist: {annotation_path}")

    if annotation_path.suffix.lower() == ".json":
        data = load_json(annotation_path)
        if isinstance(data, dict) and "samples" in data:
            data = data["samples"]
        if not isinstance(data, list):
            raise ValueError("JSON annotation file must contain a list or a {'samples': [...]} object.")
        return [normalize_record(item, image_dir=image_dir) for item in data]

    if annotation_path.suffix.lower() == ".csv":
        rows: List[Dict[str, Any]] = []
        with open(annotation_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                weather = {
                    "weather_type": row.get("weather_type", DEFAULT_WEATHER_TOKEN["weather_type"]),
                    "visibility": row.get("visibility", DEFAULT_WEATHER_TOKEN["visibility"]),
                    "illumination": row.get("illumination", DEFAULT_WEATHER_TOKEN["illumination"]),
                    "road_condition": row.get("road_condition", DEFAULT_WEATHER_TOKEN["road_condition"]),
                }
                target = {
                    "hazard_object": row.get("target_hazard_object", ""),
                    "risk_level": row.get("target_risk_level", ""),
                    "reason": row.get("target_reason", ""),
                    "explanation_ko": row.get("target_explanation_ko", ""),
                }
                rows.append(
                    normalize_record(
                        {
                            "id": row.get("id") or Path(row.get("image_path", "")).stem,
                            "image_path": row.get("image_path"),
                            "weather": weather,
                            "target": target,
                        },
                        image_dir=image_dir,
                    )
                )
        return rows

    raise ValueError("Unsupported annotation format. Use JSON or CSV.")


def safe_json_loads(text: str) -> Dict[str, Any]:
    """Attempt to recover a JSON object from noisy model output."""
    text = text.strip()
    if not text:
        raise ValueError("Empty text cannot be parsed as JSON.")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")

    candidate = match.group(0)
    candidate = candidate.replace("\n", " ").replace("\t", " ")
    candidate = re.sub(r",\s*}", "}", candidate)
    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("Recovered JSON is not a dictionary.")
    return parsed


def normalize_reasoning_output(output: Dict[str, Any]) -> Dict[str, str]:
    """Ensure required hazard reasoning fields exist and are strings."""
    normalized = dict(DEFAULT_REASONING_OUTPUT)
    for key in DEFAULT_REASONING_OUTPUT:
        value = output.get(key, normalized[key])
        normalized[key] = str(value).strip() if value is not None else normalized[key]
    return normalized


def weather_token_to_text(weather_token: Dict[str, str]) -> str:
    """Create a stable plain-text representation for prompts and saved outputs."""
    weather = {**DEFAULT_WEATHER_TOKEN, **(weather_token or {})}
    return (
        f"weather_type={weather['weather_type']}, "
        f"visibility={weather['visibility']}, "
        f"illumination={weather['illumination']}, "
        f"road_condition={weather['road_condition']}"
    )


def save_text(text: str, path: os.PathLike[str] | str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


def make_free_text(structured_output: Dict[str, str]) -> str:
    """Return a Korean explanation sentence from structured reasoning output."""
    explanation = structured_output.get("explanation", "").strip()
    if explanation:
        return explanation
    hazard_object = structured_output.get("hazard_object", "객체")
    risk_level = structured_output.get("risk_level", "중간")
    reason = structured_output.get("reason", "추가 주의가 필요합니다")
    return f"{hazard_object}와 관련해 {reason}. 위험도는 {risk_level} 수준입니다."


def weather_label_ko(value: str) -> str:
    return WEATHER_LABELS_KO.get(value, value)


def visibility_label_ko(value: str) -> str:
    return VISIBILITY_LABELS_KO.get(value, value)


def road_condition_label_ko(value: str) -> str:
    return ROAD_CONDITION_LABELS_KO.get(value, value)


def infer_image_size(image_path: os.PathLike[str] | str) -> Tuple[int, int]:
    with Image.open(image_path) as image:
        return image.size


def save_overlay_visualization(
    image_path: os.PathLike[str] | str,
    overlay_text: str,
    output_path: os.PathLike[str] | str,
) -> None:
    """Overlay reasoning text on top of an input image for qualitative demos."""
    with Image.open(image_path).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        width, height = image.size
        margin = 16
        font = _load_overlay_font(max(20, width // 45))
        line_spacing = max(8, font.size // 3)
        max_text_width = width - (margin * 2)
        wrapped_lines = _wrap_overlay_text(draw, overlay_text, font, max_text_width)
        line_height = _measure_text_height(draw, "가A", font) + line_spacing
        panel_height = max(110, min(height // 2, margin * 2 + (line_height * max(1, len(wrapped_lines)))))
        panel_top = height - panel_height

        draw.rectangle([(0, panel_top), (width, height)], fill=(0, 0, 0))

        y = panel_top + margin
        for line in wrapped_lines:
            draw.text((margin, y), line, fill=(255, 255, 255), font=font)
            y += line_height

        image.save(output_path)


def _load_overlay_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _measure_text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return max(0, bbox[2] - bbox[0])


def _measure_text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return max(0, bbox[3] - bbox[1])


def _wrap_overlay_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> List[str]:
    paragraphs = [segment.strip() for segment in text.splitlines() if segment.strip()]
    if not paragraphs:
        return [text.strip()] if text.strip() else [""]

    lines: List[str] = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if len(words) > 1:
            current = words[0]
            for word in words[1:]:
                trial = f"{current} {word}"
                if _measure_text_width(draw, trial, font) <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
            continue

        current = ""
        for char in paragraph:
            trial = f"{current}{char}"
            if current and _measure_text_width(draw, trial, font) > max_width:
                lines.append(current)
                current = char
            else:
                current = trial
        if current:
            lines.append(current)
    return lines[:6]


def compute_lcs_length(a_tokens: List[str], b_tokens: List[str]) -> int:
    """Compute longest common subsequence length for ROUGE-L style scoring."""
    if not a_tokens or not b_tokens:
        return 0
    rows = len(a_tokens) + 1
    cols = len(b_tokens) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            if a_tokens[i - 1] == b_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l_f1(reference: str, prediction: str) -> float:
    """Simple ROUGE-L F1 approximation based on whitespace tokenization."""
    ref_tokens = reference.split()
    pred_tokens = prediction.split()
    if not ref_tokens or not pred_tokens:
        return 0.0
    lcs = compute_lcs_length(ref_tokens, pred_tokens)
    precision = lcs / len(pred_tokens)
    recall = lcs / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
