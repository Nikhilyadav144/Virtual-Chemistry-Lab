"""Reusable distillation state and transfer calculations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DistillationResult:
    vapor_ml: float
    condensed_ml: float
    temperature_c: float


class DistillationEngine:
    def distill(self, source, condenser, receiver, dt: float) -> DistillationResult:
        boiling = source.mixture.temperature >= 78.0 and source.mixture.volume_ml > 0
        vapor_ml = min(source.mixture.volume_ml, 1.2 * dt) if boiling else 0.0
        portion = source.mixture.remove(vapor_ml)
        condensed_ml = portion.volume_ml * 0.92
        for chemical in portion.contents:
            chemical.volume_ml *= 0.92
            receiver.mixture.add(chemical)
        source.state.transition("boiling" if boiling else "heating")
        condenser.state.transition("condensing" if vapor_ml else "ready")
        receiver.state.transition("collecting_distillate" if condensed_ml else "empty")
        return DistillationResult(vapor_ml, condensed_ml, source.mixture.temperature)
