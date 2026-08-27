"""Reusable electrolysis behavior for future NCERT experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ElectrolysisResult:
    hydrogen_ml: float
    oxygen_ml: float
    running: bool


class ElectrolysisEngine:
    def __init__(self):
        self.running = False
        self.hydrogen_ml = 0.0
        self.oxygen_ml = 0.0

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def update(self, electrolyte, dt: float, voltage: float = 6.0) -> ElectrolysisResult:
        conductive = electrolyte.mixture.volume_ml > 0 and electrolyte.mixture.viscosity > 0
        if self.running and conductive:
            rate = max(0.0, voltage) * 0.08 * dt
            self.hydrogen_ml += rate * 2.0
            self.oxygen_ml += rate
            electrolyte.state.transition("electrolysis")
        return ElectrolysisResult(self.hydrogen_ml, self.oxygen_ml, self.running)
