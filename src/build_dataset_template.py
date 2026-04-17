"""Build a starter annotation template from an image directory."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from utils import DEFAULT_REASONING_OUTPUT, DEFAULT_WEATHER_TOKEN, dump_json, iter_image_files


def build_template(image_dir: str) -> List[dict]:
    """Create a template annotation list from all images in a directory."""
    samples = []
    for image_path in iter_image_files(image_dir):
        samples.append(
            {
                "id": image_path.stem,
                "image_path": str(image_path),
                "weather": dict(DEFAULT_WEATHER_TOKEN),
                "target": {
                    "hazard_object": DEFAULT_REASONING_OUTPUT["hazard_object"],
                    "risk_level": DEFAULT_REASONING_OUTPUT["risk_level"],
                    "reason": "",
                    "explanation_ko": "",
                },
            }
        )
    return samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an annotation template from image files.")
    parser.add_argument("--image_dir", required=True, help="Directory containing jpg/png/jpeg files.")
    parser.add_argument(
        "--output_file",
        default="examples/generated_template.json",
        help="Where to save the template JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = build_template(args.image_dir)
    output_file = Path(args.output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    dump_json(samples, output_file)
    print(f"Saved template with {len(samples)} samples to {output_file}")


if __name__ == "__main__":
    main()

