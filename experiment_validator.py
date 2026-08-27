"""
simulation.experiment_validator
Validation services for experiment configurations and runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    missing_apparatus: list[str] = field(default_factory=list)
    missing_chemicals: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


class ExperimentValidator:
    def validate_config(self, config) -> ValidationResult:
        messages = []
        if not config.name:
            messages.append("Experiment name is missing.")
        return ValidationResult(valid=not messages, messages=messages)

    def validate_workspace(self, config, apparatus_list) -> ValidationResult:
        present_apparatus = {a.atype for a in apparatus_list}
        present_chemicals = set()
        for apparatus in apparatus_list:
            for chemical in apparatus.mixture.contents:
                present_chemicals.add(chemical.name)
                present_chemicals.add(chemical.formula)

        missing_apparatus = [
            item for item in config.required_apparatus
            if item.lower() not in present_apparatus and item not in present_apparatus
        ]
        missing_chemicals = [
            item for item in config.required_chemicals
            if item not in present_chemicals
        ]
        return ValidationResult(
            valid=not missing_apparatus and not missing_chemicals,
            missing_apparatus=missing_apparatus,
            missing_chemicals=missing_chemicals,
        )

    def validate_step(self, step, event: str, payload: dict | None = None) -> bool:
        if not step:
            return True
        payload = payload or {}
        if step.action == "select_apparatus":
            return event == "select_apparatus" and payload.get("apparatus") == step.apparatus
        if step.action == "add_liquid":
            return event == "add_liquid" and payload.get("liquid") == step.liquid
        if step.action == "observe_reaction":
            return event == "reaction" and payload.get("reaction") == step.reaction
        if step.action == "heat":
            return event == "heat" and payload.get("target") == step.target
        return True
