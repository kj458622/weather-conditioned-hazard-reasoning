"""Run weather-conditioned hazard reasoning on road scene images."""

from __future__ import annotations

import argparse
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from evaluate import evaluate_predictions
from prompting import (
    build_reasoning_system_prompt,
    build_reasoning_user_prompt,
    build_weather_system_prompt,
    build_weather_user_prompt,
)
from utils import (
    DEFAULT_REASONING_OUTPUT,
    dump_json,
    ensure_dir,
    load_annotations,
    make_free_text,
    normalize_reasoning_output,
    road_condition_label_ko,
    safe_json_loads,
    save_overlay_visualization,
    save_text,
    visibility_label_ko,
    weather_label_ko,
    weather_token_to_text,
)
from weather_preprocess import WeatherPreprocessConfig, WeatherPreprocessor


class ModelRunner:
    """Abstract model runner with transformer-based path and heuristic fallback."""

    def __init__(self, model_name: str, device: Optional[str] = None) -> None:
        self.model_name = model_name
        self.device = device
        self.backend = "heuristic"
        self.model = None
        self.processor = None
        self._load_backend()

    def _load_backend(self) -> None:
        """Load Qwen2.5-VL if possible; otherwise keep heuristic fallback active."""
        try:
            import torch
            from transformers import AutoModelForImageTextToText, AutoProcessor

            resolved_device = self.device
            if resolved_device is None:
                resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
            self.device = resolved_device

            dtype = torch.float16 if self.device == "cuda" else torch.float32
            self.processor = AutoProcessor.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=dtype,
            )
            self.model.to(self.device)
            self.model.eval()
            self.backend = "transformers"
        except Exception:
            self.backend = "heuristic"

    def infer_weather(self, image_path: str) -> Dict[str, str]:
        """Infer weather token from image; fallback remains deterministic."""
        if self.backend == "transformers":
            prompt = build_weather_user_prompt()
            raw_text = self._run_multimodal_generation(
                image_path=image_path,
                system_prompt=build_weather_system_prompt(),
                user_prompt=prompt,
                max_new_tokens=128,
            )
            parsed = safe_json_loads(raw_text)
            return {
                "weather_type": str(parsed.get("weather_type", "clear")),
                "visibility": str(parsed.get("visibility", "medium")),
                "illumination": str(parsed.get("illumination", "day")),
                "road_condition": str(parsed.get("road_condition", "clear")),
            }
        return self._heuristic_weather(image_path)

    def infer_hazard(self, image_path: str, weather_token: Dict[str, str]) -> Dict[str, Any]:
        """Generate weather-conditioned hazard reasoning."""
        if self.backend == "transformers":
            raw_text = self._run_multimodal_generation(
                image_path=image_path,
                system_prompt=build_reasoning_system_prompt(),
                user_prompt=build_reasoning_user_prompt(weather_token),
                max_new_tokens=256,
            )
            parsed = safe_json_loads(raw_text)
            return normalize_reasoning_output(parsed)
        return self._heuristic_hazard(weather_token, image_path)

    def _run_multimodal_generation(
        self,
        image_path: str,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int,
    ) -> str:
        """Run Hugging Face multimodal generation using the Qwen chat template."""
        import torch
        from PIL import Image

        if self.model is None or self.processor is None:
            raise RuntimeError("Model backend is not initialized.")

        image = Image.open(image_path).convert("RGB")
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": user_prompt},
                ],
            },
        ]

        chat_text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[chat_text], images=[image], return_tensors="pt")
        inputs = {key: value.to(self.device) if hasattr(value, "to") else value for key, value in inputs.items()}

        with torch.no_grad():
            generated = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)

        trimmed = generated[:, inputs["input_ids"].shape[-1] :]
        decoded = self.processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return decoded[0] if decoded else ""

    def _heuristic_weather(self, image_path: str) -> Dict[str, str]:
        """Simple filename-based fallback weather estimation for demo continuity."""
        name = Path(image_path).stem.lower()
        weather_type = "clear"
        visibility = "medium"
        illumination = "day"
        road_condition = "clear"

        if any(token in name for token in ["snow", "blizzard"]):
            weather_type = "snow"
            visibility = "low"
            road_condition = "unclear"
        elif "fog" in name or "mist" in name:
            weather_type = "fog"
            visibility = "low"
            road_condition = "clear"
        elif "rain" in name or "wet" in name:
            weather_type = "rain"
            visibility = "medium"
            road_condition = "slippery"

        if "night" in name or "dark" in name:
            illumination = "night"
            visibility = "low" if visibility == "medium" else visibility

        return {
            "weather_type": weather_type,
            "visibility": visibility,
            "illumination": illumination,
            "road_condition": road_condition,
        }

    def _heuristic_hazard(self, weather_token: Dict[str, str], image_path: str) -> Dict[str, str]:
        """Deterministic fallback reasoning so the demo runs without model weights."""
        name = Path(image_path).stem.lower()
        weather_type = weather_token.get("weather_type", "clear")
        visibility = weather_token.get("visibility", "medium")
        illumination = weather_token.get("illumination", "day")
        road_condition = weather_token.get("road_condition", "clear")
        weather_type_ko = weather_label_ko(weather_type)
        visibility_ko = visibility_label_ko(visibility)
        road_condition_ko = road_condition_label_ko(road_condition)

        hazard_object = "vehicle"
        risk_level = "medium"
        reason = "front vehicle requires caution under current conditions"
        explanation = "전방 상황에 주의가 필요합니다."

        if "ped" in name or "walk" in name or "cross" in name:
            hazard_object = "pedestrian"
            risk_level = "high"
            reason = f"pedestrian entering or near ego lane under {visibility} visibility"
            explanation = (
                f"보행자가 주행 경로 근처에 있으며, {weather_type_ko} 상태로 인해 가시성이 {visibility_ko} 수준이라 "
                "조기 대응이 어려워 충돌 위험이 높습니다."
            )
        elif "car" in name or "vehicle" in name or "brake" in name:
            hazard_object = "front vehicle"
            risk_level = "high" if visibility == "low" or road_condition == "slippery" else "medium"
            reason = f"front vehicle may slow down abruptly with {weather_type} and {road_condition} road surface"
            explanation = (
                f"앞 차량의 속도 변화 가능성이 있으며, {weather_type_ko} 환경과 {road_condition_ko} 노면으로 인해 "
                "제동 거리 확보가 더 필요합니다."
            )
        elif "lane" in name or "curve" in name:
            hazard_object = "lane boundary"
            risk_level = "medium"
            reason = f"lane boundary is less reliable under {weather_type} weather"
            explanation = (
                f"차선 경계가 {weather_type_ko} 환경에서 불명확해질 수 있어 차로 유지 판단이 어려워질 수 있습니다."
            )

        if illumination == "night":
            risk_level = "high" if risk_level == "medium" else risk_level
            explanation += " 야간 조도로 인해 추가적인 시야 제약이 있습니다."

        return normalize_reasoning_output(
            {
                "hazard_object": hazard_object,
                "risk_level": risk_level,
                "reason": reason,
                "explanation": explanation,
            }
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weather-conditioned hazard reasoning prototype.")
    parser.add_argument("--image_dir", required=True, help="Directory that contains input images.")
    parser.add_argument("--annotation_file", default=None, help="Path to annotation JSON or CSV.")
    parser.add_argument(
        "--model_name",
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Hugging Face model name. Swap to 7B later without changing the pipeline.",
    )
    parser.add_argument("--output_dir", default="outputs", help="Directory to save results.")
    parser.add_argument(
        "--weather_mode",
        choices=["manual", "prompt"],
        default="manual",
        help="Use manual weather tokens or prompt-based weather estimation.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Optional device override, for example 'cuda' or 'cpu'.",
    )
    parser.add_argument(
        "--save_overlay",
        action="store_true",
        help="Save images with reasoning text overlaid for qualitative demos.",
    )
    return parser.parse_args()


def process_record(
    record: Dict[str, Any],
    weather_preprocessor: WeatherPreprocessor,
    model_runner: ModelRunner,
    output_dir: Path,
    save_overlay: bool,
) -> Dict[str, Any]:
    """Run preprocessing, reasoning, and persistence for one sample."""
    image_path = record.get("image_path")
    if not image_path:
        raise ValueError(f"Record is missing image_path: {record}")

    image_path = str(image_path)
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image path does not exist: {image_path}")

    weather_token = weather_preprocessor.get_weather_token(
        image_path=image_path,
        record=record,
        model_runner=model_runner if weather_preprocessor.config.mode == "prompt" else None,
    )

    parse_ok = True
    raw_model_output = None
    try:
        prediction = model_runner.infer_hazard(image_path=image_path, weather_token=weather_token)
    except Exception as error:
        parse_ok = False
        raw_model_output = f"runtime_error: {error}"
        prediction = dict(DEFAULT_REASONING_OUTPUT)

    prediction = normalize_reasoning_output(prediction)
    prediction["_parse_ok"] = parse_ok

    free_text = make_free_text(prediction)
    sample_id = record.get("id") or Path(image_path).stem
    sample_dir = ensure_dir(output_dir / sample_id)

    saved_record = {
        "id": sample_id,
        "image_path": image_path,
        "weather": weather_token,
        "prediction": prediction,
        "free_text": free_text,
        "target": record.get("target", {}),
    }
    if raw_model_output:
        saved_record["raw_model_output"] = raw_model_output

    dump_json(saved_record, sample_dir / "result.json")
    save_text(free_text, sample_dir / "free_text.txt")
    save_text(weather_token_to_text(weather_token), sample_dir / "weather_token.txt")

    if save_overlay:
        overlay_text = f"[{prediction['risk_level']}] {free_text}"
        save_overlay_visualization(image_path, overlay_text, sample_dir / "overlay.png")

    return saved_record


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    annotations = load_annotations(args.annotation_file, args.image_dir)
    weather_preprocessor = WeatherPreprocessor(
        WeatherPreprocessConfig(mode=args.weather_mode, allow_model_fallback=True)
    )
    model_runner = ModelRunner(model_name=args.model_name, device=args.device)

    print(f"Loaded {len(annotations)} samples")
    print(f"Model backend: {model_runner.backend}")

    results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for record in tqdm(annotations, desc="Running inference"):
        try:
            saved_record = process_record(
                record=record,
                weather_preprocessor=weather_preprocessor,
                model_runner=model_runner,
                output_dir=output_dir,
                save_overlay=args.save_overlay,
            )
            results.append(saved_record)
        except Exception as error:
            failures.append(
                {
                    "id": str(record.get("id", "unknown")),
                    "image_path": str(record.get("image_path", "")),
                    "error": str(error),
                    "traceback": traceback.format_exc(),
                }
            )

    dump_json(results, output_dir / "all_results.json")
    if failures:
        dump_json(failures, output_dir / "failures.json")

    has_targets = any(record.get("target") for record in results)
    if has_targets:
        metrics = evaluate_predictions(results)
        dump_json(metrics, output_dir / "metrics.json")
        print("Saved evaluation metrics.")

    print(f"Saved outputs to {output_dir}")
    if failures:
        print(f"Encountered {len(failures)} failures. Check failures.json for details.")


if __name__ == "__main__":
    main()
