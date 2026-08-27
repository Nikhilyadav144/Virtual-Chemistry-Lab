"""
simulation/apparatus.py
────────────────────────
Classes:
  Liquid            — a named substance with colour and amount
  ContainerApparatus — drawable container that holds liquid
  ApparatusRegistry  — factory for creating apparatus by name
"""

import cv2
import math

from simulation.apparatus_database import (
    available_apparatus,
    get_apparatus_definition,
)
from simulation.chemistry_engine import Chemical, Mixture
from simulation.liquid_renderer import LiquidRenderer
from simulation.object_state import ObjectState


# ── Substance colour table (BGR for OpenCV) ──────────────────────
LIQUID_BGR = {
    "water":    (255, 191,   0),
    "acid":     ( 47, 255, 120),
    "base":     (200,  80, 255),
    "salt":     (200, 200, 100),
    "indicator":(100, 200, 255),
    "alcohol":  (180, 255, 220),
    "default":  (180, 180, 255),
}

LIQUID_NAMES = list(LIQUID_BGR.keys())


class Liquid:
    """Represents a virtual liquid with name and volume in ml."""
    MAX_ML = 500

    def __init__(self, name="water", amount_ml=0.0, display_name=None, color=None):
        self.name = name
        self.display_name = display_name or name.title()
        self.amount_ml = float(amount_ml)
        self.color = color or LIQUID_BGR.get(name, LIQUID_BGR["default"])
        self.categories = {name} if amount_ml > 0 else set()
        self.labels = {self.display_name} if amount_ml > 0 else set()

    def add(self, ml):
        self.amount_ml = min(self.amount_ml + ml, self.MAX_ML)

    def register_component(self, name, display_name=None, color=None):
        self.categories.add(name)
        if display_name:
            self.labels.add(display_name)
        if color is not None:
            self.color = self._resolve_color(name, color)
        if self.labels:
            if len(self.labels) == 1:
                self.display_name = next(iter(self.labels))
            else:
                self.display_name = "Mixture"

    def remove(self, ml):
        removed = min(ml, self.amount_ml)
        self.amount_ml -= removed
        return removed

    def is_empty(self):
        return self.amount_ml <= 0

    def clone_portion(self, ml):
        portion = Liquid(self.name, ml, self.display_name, self.color)
        portion.categories = set(self.categories)
        portion.labels = set(self.labels)
        return portion

    def _resolve_color(self, added_name, added_color):
        categories = set(self.categories)
        categories.add(added_name)

        labels = {text.lower() for text in self.labels}
        if added_name == "indicator" and "phenolphthalein" in " ".join(labels):
            if "base" in categories and "acid" not in categories:
                return (180, 105, 255)
            return (240, 230, 230)

        if "phenolphthalein indicator" in " ".join(labels):
            if "base" in categories and "acid" not in categories:
                return (180, 105, 255)
            if "acid" in categories:
                return (240, 230, 230)

        if "universal indicator solution" in " ".join(labels):
            if "acid" in categories and "base" not in categories:
                return (70, 110, 255)
            if "base" in categories and "acid" not in categories:
                return (220, 80, 160)
            return (120, 210, 120)

        if "acid" in categories and "base" in categories:
            return (215, 225, 240)
        if "salt" in categories and "water" in categories:
            return (235, 225, 200)

        if self.amount_ml > 0:
            mixed = []
            for old_c, new_c in zip(self.color, added_color):
                mixed.append(int(old_c * 0.55 + new_c * 0.45))
            return tuple(mixed)
        return added_color

    def __repr__(self):
        return f"Liquid({self.display_name}, {self.amount_ml:.1f}ml)"

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "amount_ml": self.amount_ml,
            "color": tuple(self.color),
            "categories": sorted(self.categories),
            "labels": sorted(self.labels),
        }

    @classmethod
    def from_dict(cls, data):
        liquid = cls(
            data.get("name", "water"),
            data.get("amount_ml", 0.0),
            data.get("display_name"),
            tuple(data.get("color", LIQUID_BGR["default"])),
        )
        liquid.categories = set(data.get("categories", []))
        liquid.labels = set(data.get("labels", []))
        return liquid


class LiquidView:
    """Compatibility facade over the new Mixture model."""

    def __init__(self, apparatus):
        self._apparatus = apparatus

    @property
    def name(self):
        return self._apparatus.mixture.dominant_category()

    @property
    def display_name(self):
        return self._apparatus.mixture.display_name()

    @display_name.setter
    def display_name(self, value):
        if self._apparatus.mixture.contents:
            self._apparatus.mixture.contents[-1].name = value
            self._apparatus.mixture.normalize()

    @property
    def amount_ml(self):
        return self._apparatus.mixture.volume_ml

    @amount_ml.setter
    def amount_ml(self, value):
        current = self._apparatus.mixture.volume_ml
        if current <= 0:
            return
        scale = max(0.0, float(value)) / current
        for chemical in self._apparatus.mixture.contents:
            chemical.volume_ml *= scale
        self._apparatus.mixture.normalize()

    @property
    def color(self):
        return self._apparatus.mixture.color

    @color.setter
    def color(self, value):
        self._apparatus.mixture.color = tuple(value)

    @property
    def categories(self):
        return {c.reactivity.replace("strong_", "").replace("weak_", "")
                for c in self._apparatus.mixture.contents}

    @property
    def labels(self):
        return {c.name for c in self._apparatus.mixture.contents}

    def is_empty(self):
        return self._apparatus.mixture.is_empty()


class ContainerApparatus:
    """
    A virtual chemistry apparatus that can hold liquid.
    Renders itself onto an OpenCV frame.
    Liquid is anchored in LOCAL coordinates so it moves with the apparatus.

    NOTE on ml vs pixels:
      Real webcam cannot detect physical ml.
      We use a virtual ml system: the apparatus has a defined capacity_ml.
      Fill level (0.0 to 1.0) = amount_ml / capacity_ml.
      This fill level drives the visual liquid height.
    """

    GRAB_RADIUS = 110   # px — generous for easy grab

    def __init__(self, apparatus_type, x, y, fw, fh):
        self.atype      = apparatus_type   # "beaker","test_tube","flask", etc.
        self.object_id  = f"{apparatus_type}_{self._uid if hasattr(self, '_uid') else id(self)}"
        self.x          = float(x)
        self.y          = float(y)
        self.fw         = fw
        self.fh         = fh
        self.grabbed    = None             # "Left" | "Right" | None
        self.tilt_angle = 0.0              # degrees, for pour animation
        self._uid       = id(self)
        self.object_id  = f"{apparatus_type}_{self._uid}"
        self.definition = get_apparatus_definition(apparatus_type)
        self.state      = ObjectState(self.object_id, apparatus_type)

        self.capacity_ml = self.definition.capacity_ml
        self.maximum_volume_ml = self.definition.max_volume_ml
        self.supported_actions = set(self.definition.supported_actions)
        self.shape = self.definition.shape
        self.pour_point_type = self.definition.pour_point
        self.mixture = Mixture(self.capacity_ml)
        self.liquid = LiquidView(self)
        self.surface_angle = 0.0
        self.surface_velocity = 0.0
        self.surface_damping = 1.8
        self.wave_phase = 0.0
        self.temperature = 25.0
        self._liquid_renderer = LiquidRenderer()

        # Size scaled to frame
        sc = fw / 1280.0
        self._init_size(sc)

        self.desk_y = fh - 30
        if self.y <= 0:
            self.y = self.desk_y

    def _init_size(self, sc):
        w, h = self.definition.size
        self.w = int(w * sc)
        self.h = int(h * sc)
        self.mixture.capacity_ml = self.capacity_ml

    # ── Geometry helpers ─────────────────────────
    def top(self):    return int(self.y - self.h)
    def left(self):   return int(self.x - self.w // 2)
    def right(self):  return int(self.x + self.w // 2)
    def bottom(self): return int(self.y)
    def centre(self): return (self.x, self.y - self.h / 2)

    def near_enough(self, px, py):
        cx, cy = self.centre()
        return math.hypot(px - cx, py - cy) < self.GRAB_RADIUS

    def interior_bounds(self):
        """
        Returns (left, right, bottom, top) pixel bounds of the
        INSIDE of the container — used for liquid rendering and
        particle containment.
        """
        if self.atype in ("beaker", "cylinder", "burette"):
            inset = max(8, int(self.w * 0.10))
            return (self.left()  + inset,
                    self.right() - inset,
                    self.bottom() - 5,
                    self.top()   + int(self.h * 0.05))

        elif self.atype == "water_bath":
            inset = max(10, int(self.w * 0.08))
            return (self.left()  + inset,
                    self.right() - inset,
                    self.bottom() - 10,
                    self.top()   + int(self.h * 0.28))

        elif self.atype == "flask":
            inset = max(8, int(self.w * 0.07))
            return (self.left()  + inset,
                    self.right() - inset,
                    self.bottom() - 5,
                    self.top()   + int(self.h * 0.28))

        elif self.atype == "test_tube":
            inset = max(4, int(self.w * 0.12))
            return (self.left()  + inset,
                    self.right() - inset,
                    self.bottom() - 4,
                    self.top()   + int(self.h * 0.10))

        return None

    # ── Liquid fill level ────────────────────────
    def fill_fraction(self):
        return self.mixture.fill_fraction

    def add_liquid(self, liquid_name, amount_ml, display_name=None, color=None):
        chemical = Chemical.from_label(
            display_name or liquid_name.title(),
            liquid_name,
            amount_ml,
            color=color,
        )
        accepted = self.mixture.add(chemical)
        if accepted > 0:
            self.state.transition("filled", volume_ml=self.mixture.volume_ml)
        self.temperature = self.mixture.temperature
        return accepted

    def _check_reaction(self, added_name):
        """
        Returns reaction name string or None.
        Simplified reaction table.
        """
        pairs = {
            frozenset(["acid",  "base"]):      "neutralization",
            frozenset(["acid",  "indicator"]): "color_change",
            frozenset(["water", "acid"]):       "dilution",
            frozenset(["alcohol","water"]):     "mixing",
            frozenset(["alcohol","acid"]):      "esterification",
        }
        key = frozenset([self.liquid.name, added_name])
        return pairs.get(key)

    def pour_out(self, amount_ml):
        """Remove liquid and return (mixture_portion, actual_ml_removed)."""
        portion = self.mixture.remove(amount_ml)
        actual = portion.volume_ml
        if actual <= 0:
            return None, 0
        self.state.transition("pouring" if self.mixture.volume_ml > 0 else "empty")
        return portion, actual

    def rinse(self):
        """Reset the apparatus to an empty clean state."""
        self.mixture = Mixture(self.capacity_ml)
        self.liquid = LiquidView(self)
        self.state.transition("empty")

    def to_dict(self):
        return {
            "atype": self.atype,
            "object_id": self.object_id,
            "x": self.x,
            "y": self.y,
            "fw": self.fw,
            "fh": self.fh,
            "grabbed": self.grabbed,
            "tilt_angle": self.tilt_angle,
            "capacity_ml": self.capacity_ml,
            "desk_y": self.desk_y,
            "mixture": self.mixture.to_dict(),
            "surface_angle": self.surface_angle,
            "surface_velocity": self.surface_velocity,
            "wave_phase": self.wave_phase,
            "state": self.state.state,
            "state_flags": sorted(self.state.flags),
            "state_metadata": dict(self.state.metadata),
        }

    @classmethod
    def from_dict(cls, data):
        apparatus = cls(
            data["atype"],
            data["x"],
            data["y"],
            data["fw"],
            data["fh"],
        )
        apparatus.object_id = data.get("object_id", apparatus.object_id)
        apparatus.state = ObjectState(apparatus.object_id, apparatus.atype, data.get("state", ""))
        apparatus.state.flags = set(data.get("state_flags", []))
        apparatus.state.metadata = dict(data.get("state_metadata", {}))
        apparatus.grabbed = data.get("grabbed")
        apparatus.tilt_angle = data.get("tilt_angle", 0.0)
        apparatus.capacity_ml = data.get("capacity_ml", apparatus.capacity_ml)
        apparatus.desk_y = data.get("desk_y", apparatus.desk_y)
        if "mixture" in data:
            apparatus.mixture = Mixture.from_dict(data["mixture"])
        elif "liquid" in data:
            old = Liquid.from_dict(data["liquid"])
            apparatus.mixture = Mixture(apparatus.capacity_ml)
            if old.amount_ml > 0:
                apparatus.mixture.add(
                    Chemical.from_label(old.display_name, old.name, old.amount_ml, old.color)
                )
        apparatus.liquid = LiquidView(apparatus)
        apparatus.surface_angle = data.get("surface_angle", 0.0)
        apparatus.surface_velocity = data.get("surface_velocity", 0.0)
        apparatus.wave_phase = data.get("wave_phase", 0.0)
        return apparatus

    # ── Drawing ──────────────────────────────────
    def draw(self, frame):
        if abs(self.tilt_angle) > 0.5:
            self._draw_tilted(frame)
            return
        self._liquid_renderer.draw(frame, self)
        self._draw_vessel(frame)
        self._draw_label(frame)
        if self.grabbed:
            self._draw_grab_indicator(frame)

    def pour_spout(self):
        """Approximate the lowered lip/nozzle position while tilted."""
        direction = -1 if self.tilt_angle >= 0 else 1
        if self.atype in ("dropper", "burette"):
            return int(self.x), int(self.bottom())
        return (
            int(self.x + direction * self.w * 0.48),
            int(self.y - self.h * 0.82),
        )

    def _draw_tilted(self, frame):
        """Render the apparatus to an overlay, rotate it, then composite it."""
        overlay = frame.copy()
        overlay[:] = 0

        self._liquid_renderer.draw(overlay, self)
        self._draw_vessel(overlay)
        if self.grabbed:
            self._draw_grab_indicator(overlay)

        center = (float(self.x), float(self.y - self.h * 0.48))
        matrix = cv2.getRotationMatrix2D(center, self.tilt_angle, 1.0)
        rotated = cv2.warpAffine(
            overlay,
            matrix,
            (frame.shape[1], frame.shape[0]),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )
        mask = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY) > 0
        frame[mask] = rotated[mask]
        self._draw_label(frame)

    def _draw_liquid(self, frame):
        """Draw liquid fill INSIDE the vessel (anchored to vessel)."""
        frac = self.fill_fraction()
        if frac <= 0 or self.liquid.is_empty():
            return
        bnds = self.interior_bounds()
        if not bnds:
            return

        il, ir, ib, it = bnds
        inner_h = ib - it
        fill_h  = int(inner_h * frac)
        liq_top = ib - fill_h

        if fill_h < 2:
            return

        col  = self.liquid.color
        dark = tuple(max(0, c - 50) for c in col)

        # Filled rectangle
        cv2.rectangle(frame, (il, liq_top), (ir, ib), dark, -1)
        # Brighter surface line
        cv2.line(frame, (il, liq_top), (ir, liq_top), col, 3)

        # ml text inside
        ml_text = f"{self.liquid.amount_ml:.0f}ml"
        font_sc = max(0.35, self.fw / 3000.0)
        tx = il + 4
        ty = max(liq_top + 16, ib - 4)
        cv2.putText(frame, ml_text, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, font_sc,
                    (255, 255, 255), 1, cv2.LINE_AA)

    def _draw_vessel(self, frame):
        l, r   = self.left(), self.right()
        t_, b  = self.top(), self.bottom()
        w, h   = self.w, self.h
        col    = (210, 230, 255)

        if self.atype == "beaker":
            cv2.line(frame, (l, t_), (l, b), col, 4)
            cv2.line(frame, (l, b),  (r, b), col, 5)
            cv2.line(frame, (r, b),  (r, t_), col, 4)
            cv2.line(frame, (l-10, t_), (l+10, t_), col, 3)
            cv2.line(frame, (r-10, t_), (r+10, t_), col, 3)
            for pct in [0.25, 0.5, 0.75]:
                my = b - int(h * pct)
                cv2.line(frame, (l+4, my), (l+14, my), (120,160,200), 1)

        elif self.atype == "flask":
            mx   = (l + r) // 2
            neck = max(12, int(w * 0.10))
            nk   = int(h * 0.22)
            cv2.line(frame, (mx-neck, t_),    (mx-neck, t_+nk), col, 4)
            cv2.line(frame, (mx+neck, t_),    (mx+neck, t_+nk), col, 4)
            cv2.line(frame, (mx-neck, t_+nk), (l, b),           col, 4)
            cv2.line(frame, (mx+neck, t_+nk), (r, b),           col, 4)
            cv2.line(frame, (l, b), (r, b), col, 5)
            cv2.line(frame, (mx-neck-6, t_), (mx+neck+6, t_), col, 3)

        elif self.atype == "test_tube":
            cv2.line(frame, (l, t_), (l, b - w//2), col, 3)
            cv2.line(frame, (r, t_), (r, b - w//2), col, 3)
            cv2.ellipse(frame, ((l+r)//2, b - w//2),
                        (w//2, w//2), 0, 0, 180, col, 3)
            cv2.line(frame, (l-6, t_), (r+6, t_), col, 3)

        elif self.atype == "cylinder":
            cv2.line(frame, (l, t_), (l, b), col, 3)
            cv2.line(frame, (r, t_), (r, b), col, 3)
            cv2.line(frame, (l, b),  (r, b), col, 4)
            cv2.ellipse(frame, ((l+r)//2, t_), (w//2, int(w*0.2)),
                        0, 180, 360, col, 2)
            cv2.ellipse(frame, ((l+r)//2, t_), (w//2, int(w*0.2)),
                        0, 0, 180, col, 1)
            for pct in [0.2, 0.4, 0.6, 0.8]:
                my = b - int(h * pct)
                cv2.line(frame, (r-14, my), (r-4, my), (120,160,200), 1)

        elif self.atype == "burette":
            mid = (l + r) // 2
            tap_y = b - int(h * 0.18)
            cv2.line(frame, (mid, t_), (mid, tap_y), col, 3)
            cv2.line(frame, (mid - 10, t_), (mid + 10, t_), col, 2)
            cv2.line(frame, (mid - 16, tap_y), (mid + 16, tap_y), col, 3)
            cv2.line(frame, (mid + 16, tap_y), (mid + 34, tap_y), col, 2)
            cv2.line(frame, (mid + 34, tap_y), (mid + 34, b - 18), col, 2)
            cv2.line(frame, (mid + 34, b - 18), (mid + 26, b), col, 2)
            for pct in [0.15, 0.30, 0.45, 0.60, 0.75, 0.90]:
                my = b - int(h * pct)
                cv2.line(frame, (mid - 10, my), (mid - 3, my), (120,160,200), 1)

        elif self.atype == "dropper":
            cx_  = int(self.x)
            bw   = max(w//2, 22)
            bh   = int(h * 0.28)
            bmid = t_ + bh
            cv2.rectangle(frame, (cx_-bw, bmid),
                          (cx_+bw, bmid+int(h*0.30)), col, 2)
            cv2.ellipse(frame, (cx_, bmid), (bw, bh), 0, 0, 360, col, 2)
            # Fill colour inside bulb
            if not self.liquid.is_empty():
                cv2.ellipse(frame, (cx_, bmid), (bw-3, bh-3),
                            0, 0, 360, self.liquid.color, -1)
            nw = max(5, bw//3)
            nt = bmid + int(h*0.30)
            cv2.rectangle(frame, (cx_-nw, nt), (cx_+nw, b),
                          (220, 220, 220), -1)
            cv2.rectangle(frame, (cx_-nw, nt), (cx_+nw, b),
                          (160, 160, 160), 1)

        elif self.atype == "bunsen":
            bh2 = int(h * 0.18)
            cv2.rectangle(frame, (l, b-bh2), (r, b), (120,120,120), -1)
            cv2.rectangle(frame, (l, b-bh2), (r, b), (180,180,180), 2)
            tw = max(14, int(w*0.22)); tx2 = int(self.x)
            cv2.rectangle(frame, (tx2-tw//2, t_), (tx2+tw//2, b-bh2),
                          (185,185,185), -1)
            cv2.rectangle(frame, (tx2-tw//2, t_), (tx2+tw//2, b-bh2),
                          (215,215,215), 2)

        elif self.atype == "water_bath":
            cv2.rectangle(frame, (l, t_ + int(h * 0.22)), (r, b),
                          (85, 95, 110), -1)
            cv2.rectangle(frame, (l, t_ + int(h * 0.22)), (r, b),
                          col, 3)
            cv2.ellipse(frame, ((l + r) // 2, t_ + int(h * 0.22)),
                        (w // 2, max(10, int(h * 0.14))),
                        0, 180, 360, col, 3)
            cv2.line(frame, (l + 12, b - 8), (r - 12, b - 8),
                     (120, 120, 130), 2)
            for sx in [l + int(w * 0.30), l + int(w * 0.50), l + int(w * 0.70)]:
                cv2.ellipse(frame, (sx, t_ + 12), (7, 16),
                            0, 200, 340, (180, 220, 255), 2)

    def _draw_label(self, frame):
        font_sc = max(0.36, self.fw / 3400.0)
        label   = f"{self.atype.replace('_',' ').title()}"
        cv2.putText(frame, label,
                    (self.left(), self.bottom() + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, font_sc,
                    (170, 210, 255), 1, cv2.LINE_AA)

    def _draw_grab_indicator(self, frame):
        cx_, cy_ = int(self.centre()[0]), int(self.centre()[1])
        cv2.rectangle(frame,
                      (self.left()-3, self.top()-3),
                      (self.right()+3, self.bottom()+3),
                      (60, 255, 120), 3)
        cv2.circle(frame, (cx_, cy_), self.GRAB_RADIUS, (60,255,120), 1)


class ApparatusRegistry:
    """Factory — creates apparatus by type name."""
    AVAILABLE = available_apparatus()

    @staticmethod
    def create(atype, x, y, fw, fh):
        return ContainerApparatus(atype, x, y, fw, fh)
