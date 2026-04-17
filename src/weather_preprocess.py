"""Weather preprocessing module for manual and prompt-based inference modes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from utils import DEFAULT_WEATHER_TOKEN


@dataclass
class WeatherPreprocessConfig:
    """Configuration for the weather preprocessor."""

    mode: str = "manual"
    allow_model_fallback: bool = True


class WeatherPreprocessor:
    """Resolve weather tokens from annotations or optional model inference."""

    def __init__(self, config: Optional[WeatherPreprocessConfig] = None) -> None:
        self.config = config or WeatherPreprocessConfig()

    def get_weather_token(
        self,
        image_path: str,
        record: Optional[Dict[str, Any]] = None,
        model_runner: Optional[Any] = None,
    ) -> Dict[str, str]:
        """Return a weather token for the given image and annotation record."""
        record = record or {}
        manual_weather = record.get("weather")

        if self.config.mode == "manual":
            return self._normalize_weather(manual_weather)

        if self.config.mode == "prompt":
            if manual_weather and self.config.allow_model_fallback:
                fallback_weather = self._normalize_weather(manual_weather)
            else:
                fallback_weather = dict(DEFAULT_WEATHER_TOKEN)

            if model_runner is None:
                return fallback_weather

            try:
                estimated = model_runner.infer_weather(str(image_path))
                return self._normalize_weather(estimated)
            except Exception:
                return fallback_weather

        raise ValueError(f"Unsupported weather preprocessing mode: {self.config.mode}")

    def _normalize_weather(self, weather_token: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Merge a possibly incomplete weather token with defaults."""
        normalized = dict(DEFAULT_WEATHER_TOKEN)
        if weather_token:
            for key, default_value in DEFAULT_WEATHER_TOKEN.items():
                value = weather_token.get(key, default_value)
                normalized[key] = str(value).strip() if value else default_value

        image_name = (
            Path(str(weather_token.get("image_path"))).name
            if isinstance(weather_token, dict) and weather_token.get("image_path")
            else ""
        )
        if "night" in image_name.lower():
            normalized["illumination"] = "night"
        return normalized
