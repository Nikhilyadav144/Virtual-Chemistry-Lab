"""
simulation/fluid_engine.py
Lightweight liquid flow and surface dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class FlowResult:
    volume_ml: float
    drops: int
    dropwise: bool


class FluidEngine:
    def __init__(self):
        self.gravity_factor = 1.0

    def flow_volume(self, source, dt: float, dropwise: bool = False) -> FlowResult:
        if source.mixture.is_empty():
            return FlowResult(0.0, 0, dropwise)

        angle = abs(source.tilt_angle)
        if source.atype == "burette":
            base_rate = 1.2
            threshold = 2.0
            dropwise = True
        elif source.atype == "dropper":
            base_rate = 24.0
            threshold = 6.0
            dropwise = True
        else:
            base_rate = 18.0
            threshold = 16.0

        if angle < threshold:
            return FlowResult(0.0, 0, dropwise)

        angle_factor = math.sin(math.radians(min(angle, 82.0)))
        fill_factor = max(0.15, source.mixture.fill_fraction)
        viscosity = max(source.mixture.viscosity, 0.2)
        rate_ml_s = base_rate * angle_factor * fill_factor / viscosity

        if dropwise:
            max_rate = 2.0 if source.atype == "burette" else 24.0
            rate_ml_s = min(rate_ml_s, max_rate)
            volume = max(0.03, rate_ml_s * dt)
            drops = max(1, int(volume / 0.05))
        else:
            volume = rate_ml_s * dt
            drops = max(1, int(volume / 0.35))

        return FlowResult(min(volume, source.mixture.volume_ml), drops, dropwise)

    def update_surface(self, apparatus, dt: float):
        target = max(-28.0, min(28.0, -apparatus.tilt_angle * 0.45))
        apparatus.surface_velocity += (target - apparatus.surface_angle) * 8.0 * dt
        apparatus.surface_velocity *= max(0.0, 1.0 - 4.5 * dt)
        apparatus.surface_angle += apparatus.surface_velocity * dt
        apparatus.wave_phase += dt * (4.0 + min(abs(apparatus.tilt_angle), 45.0) / 18.0)
        apparatus.surface_angle *= max(0.0, 1.0 - apparatus.surface_damping * dt)
