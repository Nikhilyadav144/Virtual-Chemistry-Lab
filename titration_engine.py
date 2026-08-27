"""
simulation/titration_engine.py
Acid-base titration tracking and endpoint detection.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TitrationState:
    active: bool = False
    acid_moles: float = 0.0
    base_moles: float = 0.0
    acid_volume_ml: float = 0.0
    base_volume_ml: float = 0.0
    endpoint_reached: bool = False
    equivalence_error: float = 0.0
    indicator: str = "phenolphthalein"


class TitrationEngine:
    def __init__(self, enabled: bool = False):
        self.state = TitrationState(active=enabled)

    def observe(self, apparatus_list):
        if not self.state.active:
            return None

        acid_moles = 0.0
        base_moles = 0.0
        acid_volume = 0.0
        base_volume = 0.0
        endpoint_error = 1.0
        mixed_endpoint = False
        pH_values = []

        for apparatus in apparatus_list:
            mix = apparatus.mixture
            if mix.is_empty():
                continue
            acid_moles += mix.acid_moles()
            base_moles += mix.base_moles()
            local_acid = mix.acid_moles()
            local_base = mix.base_moles()
            if local_acid > 0 and local_base > 0:
                local_total = max(local_acid + local_base, 1e-9)
                local_error = abs(local_acid - local_base) / local_total
                endpoint_error = min(endpoint_error, local_error)
                if local_error < 0.035:
                    mixed_endpoint = True
            for chem in mix.contents:
                if "acid" in chem.reactivity:
                    acid_volume += chem.volume_ml
                if "base" in chem.reactivity:
                    base_volume += chem.volume_ml
            pH_values.append(mix.pH)

        endpoint = mixed_endpoint

        changed = endpoint and not self.state.endpoint_reached
        self.state.acid_moles = acid_moles
        self.state.base_moles = base_moles
        self.state.acid_volume_ml = acid_volume
        self.state.base_volume_ml = base_volume
        self.state.equivalence_error = endpoint_error
        self.state.endpoint_reached = endpoint

        if changed:
            return "Endpoint reached: acid and base are nearly equivalent"
        return None

    def status_text(self):
        if not self.state.active:
            return ""
        if self.state.endpoint_reached:
            return (
                f"Titration endpoint | Acid {self.state.acid_volume_ml:.1f} ml | "
                f"Base {self.state.base_volume_ml:.1f} ml"
            )
        return (
            f"Acid {self.state.acid_volume_ml:.1f} ml | "
            f"Base {self.state.base_volume_ml:.1f} ml | "
            f"Equiv error {self.state.equivalence_error * 100:.1f}%"
        )
