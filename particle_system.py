"""
simulation/particle_system.py
──────────────────────────────
Particle effects for reactions (bubbles, smoke, glow, etc.)
Particles are drawn on the OpenCV frame.
"""

import cv2
import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ParticleEffect:
    color: tuple[int, int, int]
    style: str
    count: int


REACTION_EFFECTS: dict[str, ParticleEffect] = {
    "neutralization": ParticleEffect((100, 255, 200), "smoke", 30),
    "color_change": ParticleEffect((200, 80, 255), "glow", 20),
    "dilution": ParticleEffect((200, 220, 255), "bubble", 15),
    "mixing": ParticleEffect((180, 255, 180), "bubble", 10),
    "esterification": ParticleEffect((80, 220, 255), "glow", 24),
    "fire": ParticleEffect((0, 80, 255), "fire", 25),
    "gas_evolution": ParticleEffect((190, 230, 255), "foam", 34),
    "precipitation": ParticleEffect((230, 230, 210), "precipitate", 28),
    "exothermic": ParticleEffect((40, 130, 255), "heat", 24),
}

CELL = 30

def _gc(x, y):
    return (int(x // CELL), int(y // CELL))


class Particle:
    __slots__ = ["x","y","vx","vy","r","color","alpha","style","bounds"]

    def __init__(self, x, y, color, style="bubble", bounds=None):
        self.x     = float(x)
        self.y     = float(y)
        self.color = color
        self.style = style
        self.bounds = bounds
        self.alpha = 255
        self.r     = random.randint(5, 12)

        if style == "fire":
            self.vx = random.uniform(-1.0, 1.0)
            self.vy = random.uniform(-4.0, -2.0)
        elif style == "pour":
            self.r = random.randint(3, 6)
            self.vx = random.uniform(-0.25, 0.25)
            self.vy = random.uniform(1.8, 3.4)
        elif style == "smoke":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-2.0, -0.5)
        elif style == "foam":
            self.r = random.randint(4, 10)
            self.vx = random.uniform(-0.7, 0.7)
            self.vy = random.uniform(-1.0, -0.2)
        elif style == "precipitate":
            self.r = random.randint(2, 5)
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(0.4, 1.2)
        elif style == "heat":
            self.r = random.randint(8, 16)
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(-1.8, -0.4)
        elif style == "bubble":
            self.vx = random.uniform(-0.8, 0.8)
            self.vy = random.uniform(-1.5, -0.3)
        elif style == "glow":
            self.vx = random.uniform(-1.5, 1.5)
            self.vy = random.uniform(-1.5, 1.5)
        else:
            self.vx = random.uniform(-1.0, 1.0)
            self.vy = random.uniform(-1.0, 1.0)


class ParticleSystem:
    def __init__(self, max_p=600):
        self.particles = []
        self.max       = max_p
        self.grid      = {}

    def emit(self, x, y, color, n=5, style="bubble"):
        for _ in range(n):
            if len(self.particles) < self.max:
                self.particles.append(Particle(x, y, color, style))

    def emit_reaction(self, x, y, reaction_name):
        cfg = REACTION_EFFECTS.get(reaction_name)
        if cfg:
            self.emit(x, y, cfg.color, cfg.count, cfg.style)

    def emit_reaction_event(self, x, y, event):
        """Emit reusable particle effects from a ReactionEvent contract."""
        if event.gas:
            self.emit(x, y, event.color or (190, 230, 255),
                      int(36 * event.intensity), "foam")
        if event.precipitate:
            self.emit(x, y, event.color or (230, 230, 210),
                      int(30 * event.intensity), "precipitate")
        if event.temperature_change > 2:
            self.emit(x, y, (40, 130, 255), int(18 * event.intensity), "heat")
        self.emit_reaction(x, y, event.type)

    def emit_pour(self, x, y, color, bounds=None):
        """Small drip particles when pouring, clipped to the receiving tool."""
        if bounds:
            lf, rt, bot, top_open = bounds
            x = max(lf + 4, min(rt - 4, x))
            y = max(top_open + 4, min(bot - 8, y))
        for _ in range(3):
            if len(self.particles) < self.max:
                self.particles.append(Particle(x, y, color, "pour", bounds))

    def update_and_draw(self, frame, apparatus_list, fh, fw):
        """Step all particles and draw them. Confine to containers."""
        # Build containment bounds
        bounds_list = [a.interior_bounds() for a in apparatus_list
                       if a.interior_bounds() is not None]

        to_remove = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy

            rising = p.style in ("fire","smoke","glow","foam","heat")
            p.vy  += -0.20 if rising else 0.35

            if p.style == "precipitate":
                p.alpha -= 2
            elif rising:
                p.alpha -= random.randint(4, 8)
            elif p.style == "pour" and p.bounds:
                lf, rt, bot, top_open = p.bounds
                if not (lf <= p.x <= rt and top_open <= p.y <= bot):
                    to_remove.append(p)
                    continue
                if p.y + p.r >= bot:
                    p.y = bot - p.r
                    p.vy = 0.0
                    p.vx = 0.0
                if p.x - p.r <= lf:
                    p.x = lf + p.r
                if p.x + p.r >= rt:
                    p.x = rt - p.r
                p.alpha -= 18
            else:
                # Confine liquid particles to nearest container
                for bnds in bounds_list:
                    lf, rt, bot, top_open = bnds
                    if lf <= p.x <= rt and p.y >= top_open:
                        if p.y + p.r >= bot:
                            p.y  = bot - p.r
                            p.vy = abs(p.vy) * -0.15
                            p.vx *= 0.8
                        if p.x - p.r <= lf:
                            p.x = lf + p.r; p.vx = abs(p.vx) * 0.5
                        if p.x + p.r >= rt:
                            p.x = rt - p.r; p.vx = -abs(p.vx) * 0.5
                        break
                else:
                    # Fell outside all containers — floor
                    if p.y + p.r >= fh:
                        p.y = fh - p.r; p.vy *= -0.1
                p.alpha -= 1   # very slow fade for liquid

            if p.alpha <= 0 or p.y < -60 or p.x < -60 or p.x > fw+60:
                to_remove.append(p)
                continue

            r_draw = max(3, int(p.r * (p.alpha / 255.0)))
            col    = p.color
            if p.style in ("bubble","glow","pour","foam","heat"):
                dark = tuple(max(0, c - 50) for c in col)
                cv2.circle(frame, (int(p.x), int(p.y)), r_draw+2, dark, -1)
            if p.style == "heat":
                cv2.ellipse(frame, (int(p.x), int(p.y)), (r_draw, r_draw * 2),
                            0, 0, 360, col, 1)
                continue
            cv2.circle(frame, (int(p.x), int(p.y)), r_draw, col, -1)

        for p in to_remove:
            self.particles.remove(p)
