"""Reusable crystallization behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CrystalGrowthResult:
    crystal_mass_g: float
    saturated: bool


class CrystallizationEngine:
    def update(self, apparatus, dt: float) -> CrystalGrowthResult:
        cooling = apparatus.mixture.temperature < 35.0
        concentrated = apparatus.mixture.volume_ml < apparatus.capacity_ml * 0.35
        saturated = cooling and concentrated and apparatus.mixture.volume_ml > 0
        if saturated:
            current = float(getattr(apparatus, "crystal_mass_g", 0.0))
            apparatus.crystal_mass_g = current + 0.08 * dt
            apparatus.state.transition("crystal_growth", mass_g=apparatus.crystal_mass_g)
        return CrystalGrowthResult(float(getattr(apparatus, "crystal_mass_g", 0.0)), saturated)
