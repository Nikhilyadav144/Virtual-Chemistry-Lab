"""Reusable heating and cooling behavior for lab apparatus."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HeatingResult:
    temperature_c: float
    boiling: bool = False
    evaporated_ml: float = 0.0
    steam: bool = False


class HeatingEngine:
    def heat(self, apparatus, dt: float, flame_level: str = "medium") -> HeatingResult:
        rates = {"low": 2.0, "medium": 5.0, "high": 9.0}
        rate = rates.get(flame_level, rates["medium"])
        apparatus.mixture.temperature += rate * dt
        boiling = apparatus.mixture.temperature >= 100.0 and apparatus.mixture.volume_ml > 0
        evaporated = 0.0
        if boiling:
            evaporated = min(apparatus.mixture.volume_ml, 0.15 * dt * rate)
            apparatus.mixture.remove(evaporated)
        apparatus.state.transition("heating", temperature=apparatus.mixture.temperature)
        return HeatingResult(apparatus.mixture.temperature, boiling, evaporated, boiling)

    def cool(self, apparatus, dt: float, ambient_c: float = 25.0) -> HeatingResult:
        delta = apparatus.mixture.temperature - ambient_c
        apparatus.mixture.temperature -= delta * min(1.0, 0.12 * dt)
        apparatus.state.transition("cooling", temperature=apparatus.mixture.temperature)
        return HeatingResult(apparatus.mixture.temperature)
