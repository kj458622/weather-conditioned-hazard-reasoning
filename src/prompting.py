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
        "Focus on one primary hazard object only. "
        "Prefer scene-specific cues such as crosswalk, occlusion, dense traffic, "
        "lane ambiguity, curve, merge, rider, or limited sight distance when visible. "
        "Avoid generic phrases like 'be careful' unless you also mention a concrete reason. "
        "The explanation must be written in English and must explicitly mention how weather, visibility, "
        "illumination, or road condition increases risk. "
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
            "under these conditions. Choose exactly one primary hazard object. "
            "Keep the reason concise, but make it scene-specific instead of generic. "
            "If relevant, mention cues such as crosswalk, parked vehicles, occlusion, "
            "dense traffic, lane boundary ambiguity, or a rider/two-wheeler. "
            "Provide an English explanation that explicitly includes the weather impact."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_reasoning_user_prompt_no_weather() -> str:
    """User prompt without any weather context — pure image-based reasoning."""
    payload = {
        "image": "<image>",
        "instruction": (
            "Analyze the driving scene and explain why it is risky for autonomous driving. "
            "Choose exactly one primary hazard object. "
            "Keep the reason concise but scene-specific. "
            "If relevant, mention cues such as crosswalk, parked vehicles, occlusion, "
            "dense traffic, lane boundary ambiguity, or a rider/two-wheeler. "
            "Provide an English explanation of the hazard."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_reasoning_system_prompt_no_weather() -> str:
    """System prompt for pure image-based reasoning without weather context."""
    return (
        "You are an autonomous-driving hazard reasoning assistant. "
        "Analyze the image and explain why the scene is risky for autonomous driving. "
        "Focus on one primary hazard object only. "
        "Prefer scene-specific cues such as crosswalk, occlusion, dense traffic, "
        "lane ambiguity, curve, merge, rider, or limited sight distance when visible. "
        "Avoid generic phrases like 'be careful' unless you also mention a concrete reason. "
        "Return structured JSON only with keys: "
        "hazard_object, risk_level, reason, explanation."
    )


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
