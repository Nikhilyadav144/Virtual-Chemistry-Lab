"""
simulation/experiment_framework.py
Normalizes experiment dictionaries into a reusable simulation config.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from simulation.experiment_validator import ExperimentValidator, ValidationResult


@dataclass
class ExperimentConfig:
    name: str
    required_apparatus: list[str] = field(default_factory=list)
    required_chemicals: list[str] = field(default_factory=list)
    steps: list = field(default_factory=list)
    success_conditions: list[str] = field(default_factory=list)
    reaction_rules: list[str] = field(default_factory=list)
    titration: bool = False
    validation: ValidationResult | None = None


def build_experiment_config(exp_data: dict) -> ExperimentConfig:
    sim = exp_data.get("simulation", {})
    name = exp_data.get("name", "")
    steps = exp_data.get("steps", [])
    success_conditions = sim.get("success_conditions", [])
    reaction_rules = sim.get("reaction_rules", sim.get("reactions", []))
    titration = bool(
        sim.get("titration")
        or "titration" in name.lower()
        or any("titration" in str(step).lower() for step in steps)
    )

    config = ExperimentConfig(
        name=name,
        required_apparatus=list(sim.get("tools", [])),
        required_chemicals=list(exp_data.get("chemicals", [])),
        steps=list(steps),
        success_conditions=list(success_conditions),
        reaction_rules=list(reaction_rules),
        titration=titration,
    )
    config.validation = ExperimentValidator().validate_config(config)
    return config
