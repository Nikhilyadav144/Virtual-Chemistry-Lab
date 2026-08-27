"""
simulation/liquid_renderer.py
OpenCV liquid rendering with slanted, damped surfaces.
"""

from __future__ import annotations

import math
import cv2
import numpy as np


class LiquidRenderer:
    def draw(self, frame, apparatus):
        mixture = apparatus.mixture
        frac = mixture.fill_fraction
        if frac <= 0 or mixture.is_empty():
            return
        bnds = apparatus.interior_bounds()
        if not bnds:
            return

        il, ir, ib, it = bnds
        inner_h = ib - it
        fill_h = int(inner_h * frac)
        base_y = ib - fill_h
        if fill_h < 2:
            return

        width = max(1, ir - il)
        slope = math.tan(math.radians(apparatus.surface_angle))
        wave_amp = max(1.0, min(7.0, abs(apparatus.surface_velocity) * 0.12 + abs(apparatus.tilt_angle) * 0.04))

        xs = np.linspace(il, ir, 18)
        surface = []
        for x in xs:
            centered = (x - (il + ir) / 2.0) / width
            y = base_y + centered * width * slope
            y += math.sin(apparatus.wave_phase + centered * math.pi * 2.0) * wave_amp
            y = max(it + 2, min(ib - 2, y))
            surface.append((int(x), int(y)))

        polygon = [(il, ib), (ir, ib)] + list(reversed(surface))
        color = tuple(int(c) for c in mixture.color)
        dark = tuple(max(0, c - 45) for c in color)

        overlay = frame.copy()
        cv2.fillPoly(overlay, [np.array(polygon, dtype=np.int32)], dark)
        cv2.addWeighted(overlay, 0.58, frame, 0.42, 0, frame)
        cv2.polylines(frame, [np.array(surface, dtype=np.int32)], False, color, 3, cv2.LINE_AA)

        gloss = tuple(min(255, c + 45) for c in color)
        for idx in range(0, len(surface) - 1, 3):
            cv2.line(frame, surface[idx], surface[idx + 1], gloss, 1, cv2.LINE_AA)

        ml_text = f"{mixture.volume_ml:.0f}ml"
        if mixture.pH <= 6.8 or mixture.pH >= 7.2:
            ml_text += f" pH {mixture.pH:.1f}"
        font_sc = max(0.34, apparatus.fw / 3300.0)
        tx = il + 4
        ty = max(min(surface, key=lambda p: p[1])[1] + 17, ib - 5)
        cv2.putText(frame, ml_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                    font_sc, (255, 255, 255), 1, cv2.LINE_AA)
