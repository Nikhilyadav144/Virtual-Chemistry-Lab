"""Dynamic experiment JSON loader."""

from __future__ import annotations

import json
from pathlib import Path


EXPERIMENT_JSON_DIR = Path(__file__).resolve().parent / "experiments_json"


def load_json_experiments(directory: Path = EXPERIMENT_JSON_DIR) -> dict[int, list[dict]]:
    loaded: dict[int, list[dict]] = {}
    if not directory.exists():
        return loaded
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        class_num = int(data.get("class", data.get("class_num", 0)))
        if class_num <= 0:
            continue
        loaded.setdefault(class_num, []).append(_normalize_json_experiment(data))
    return loaded


def _normalize_json_experiment(data: dict) -> dict:
    """Convert JSON schema fields to the existing GUI experiment shape."""
    return {
        "id": data["id"],
        "name": data.get("title", data.get("name", "")),
        "aim": data.get("aim", ""),
        "theory": data.get("theory", ""),
        "apparatus": data.get("apparatus", []),
        "chemicals": data.get("chemicals", []),
        "steps": data.get("procedure", data.get("steps", [])),
        "safety": data.get("safety", []),
        "observations": data.get("observations", []),
        "expected_results": data.get("expected_results", []),
        "completion_conditions": data.get("completion_conditions", []),
        "simulation": {
            **data.get("simulation", {}),
            "workspace": data.get("workspace", data.get("simulation", {}).get("workspace", {})),
            "initial_quantities": data.get(
                "initial_chemical_quantities",
                data.get("simulation", {}).get("initial_quantities", {}),
            ),
            "reaction_rules": data.get("reaction_rules", data.get("simulation", {}).get("reaction_rules", [])),
            "success_conditions": data.get(
                "completion_conditions",
                data.get("simulation", {}).get("success_conditions", []),
            ),
        },
    }
