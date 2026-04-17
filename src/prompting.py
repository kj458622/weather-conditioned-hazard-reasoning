"""Prompt builders for weather-conditioned hazard reasoning."""

from __future__ import annotations

import json
from typing import Dict


def build_reasoning_system_prompt() -> str:
    """System prompt for structured weather-conditioned hazard reasoning."""
    return (
        "You are an autonomous-driving hazard reasoning assistant. "
        "Use both the image and the provided weather conditions. "
        "Do not only describe objects. Explain why the scene is risky "
        "under the given adverse-weather condition. "
        "Return structured JSON only with keys: "
        "hazard_object, risk_level, reason, explanation."
    )


def build_reasoning_user_prompt(weather_token: Dict[str, str]) -> str:
    """User prompt that injects weather metadata alongside the image."""
    payload = {
        "image": "<image>",
        "weather_type": weather_token.get("weather_type", "clear"),
        "visibility": weather_token.get("visibility", "medium"),
        "illumination": weather_token.get("illumination", "day"),
        "road_condition": weather_token.get("road_condition", "clear"),
        "instruction": (
            "Analyze the scene and explain why it is risky for autonomous driving "
            "under these conditions. Keep the reason concise and provide a Korean explanation."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_weather_system_prompt() -> str:
    """Optional prompt for weather token estimation from an image."""
    return (
        "You estimate adverse-weather driving conditions from a front-view road image. "
        "Return JSON only with keys: weather_type, visibility, illumination, road_condition."
    )


def build_weather_user_prompt() -> str:
    """Prompt payload for weather token estimation."""
    payload = {
        "image": "<image>",
        "instruction": (
            "Estimate the weather condition for driving. "
            "Use coarse categories only, such as clear/rain/fog/snow/night. "
            "Return JSON only."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

