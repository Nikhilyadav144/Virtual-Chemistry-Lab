"""
simulation/chemistry_engine.py
Core chemical state models used by apparatus, reactions, and titration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from simulation.chemical_database import chemical_library_dict, get_chemical_definition


ColorBGR = tuple[int, int, int]


CHEMICAL_LIBRARY = chemical_library_dict()


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def infer_formula(label: str, category: str = "water") -> str:
    text = label.lower()
    if "hcl" in text or "hydrochloric" in text:
        return "HCl"
    if "h2so4" in text or "h₂so₄" in text or "sulphuric" in text or "sulfuric" in text:
        return "H2SO4"
    if "ch3cooh" in text or "ch₃cooh" in text or "vinegar" in text or "acetic" in text:
        return "CH3COOH"
    if "naoh" in text or "sodium hydroxide" in text:
        return "NaOH"
    if "nahco3" in text or "nahco₃" in text or "baking soda" in text:
        return "NaHCO3"
    if "nacl" in text or "sodium chloride" in text or "common salt" in text:
        return "NaCl"
    if "phenolphthalein" in text:
        return "PHEN"
    if "methyl orange" in text:
        return "METHYL_ORANGE"
    if "universal indicator" in text:
        return "UNIVERSAL"
    if "ethanol" in text or "alcohol" in text:
        return "ETHANOL"
    if category == "acid":
        return "HCl"
    if category == "base":
        return "NaOH"
    if category == "salt":
        return "NaCl"
    if category == "indicator":
        return "PHEN"
    if category == "alcohol":
        return "ETHANOL"
    return "H2O"


def concentration_for(label: str, formula: str, category: str) -> float:
    text = label.lower()
    if "0.1" in text:
        return 0.1
    if "unknown" in text and formula == "NaOH":
        return 0.1
    if category in ("acid", "base"):
        return 0.1
    if category == "indicator":
        return 0.01
    return 0.0


@dataclass
class Chemical:
    name: str
    formula: str
    concentration: float = 0.0
    volume_ml: float = 0.0
    pH: float = 7.0
    density: float = 1.0
    viscosity: float = 1.0
    temperature: float = 25.0
    color: ColorBGR = (220, 220, 220)
    state: str = "liquid"
    reactivity: str = "neutral"

    @classmethod
    def from_label(cls, label: str, category: str, volume_ml: float, color: ColorBGR | None = None):
        formula = infer_formula(label, category)
        meta = get_chemical_definition(formula)
        return cls(
            name=label or meta.name,
            formula=formula,
            concentration=concentration_for(label or meta.name, formula, category),
            volume_ml=float(volume_ml),
            pH=float(meta.pH),
            density=float(meta.density),
            viscosity=float(meta.viscosity),
            temperature=25.0,
            color=color or meta.color,
            state=meta.state,
            reactivity=meta.reactivity,
        )

    def clone_portion(self, volume_ml: float) -> "Chemical":
        fraction = 0.0 if self.volume_ml <= 0 else clamp(volume_ml / self.volume_ml, 0.0, 1.0)
        clone = Chemical(
            name=self.name,
            formula=self.formula,
            concentration=self.concentration,
            volume_ml=min(volume_ml, self.volume_ml),
            pH=self.pH,
            density=self.density,
            viscosity=self.viscosity,
            temperature=self.temperature,
            color=self.color,
            state=self.state,
            reactivity=self.reactivity,
        )
        self.volume_ml = max(0.0, self.volume_ml - clone.volume_ml)
        if fraction >= 0.999:
            self.volume_ml = 0.0
        return clone

    def moles(self) -> float:
        return self.concentration * (self.volume_ml / 1000.0)

    def to_dict(self):
        return {
            "name": self.name,
            "formula": self.formula,
            "concentration": self.concentration,
            "volume_ml": self.volume_ml,
            "pH": self.pH,
            "density": self.density,
            "viscosity": self.viscosity,
            "temperature": self.temperature,
            "color": tuple(self.color),
            "state": self.state,
            "reactivity": self.reactivity,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Water"),
            formula=data.get("formula", "H2O"),
            concentration=float(data.get("concentration", 0.0)),
            volume_ml=float(data.get("volume_ml", 0.0)),
            pH=float(data.get("pH", 7.0)),
            density=float(data.get("density", 1.0)),
            viscosity=float(data.get("viscosity", 1.0)),
            temperature=float(data.get("temperature", 25.0)),
            color=tuple(data.get("color", (220, 220, 220))),
            state=data.get("state", "liquid"),
            reactivity=data.get("reactivity", "neutral"),
        )


@dataclass
class Mixture:
    capacity_ml: float
    contents: list[Chemical] = field(default_factory=list)
    temperature: float = 25.0
    pH: float = 7.0
    color: ColorBGR = (220, 220, 220)

    @property
    def volume_ml(self) -> float:
        return sum(c.volume_ml for c in self.contents)

    @property
    def fill_fraction(self) -> float:
        if self.capacity_ml <= 0:
            return 0.0
        return clamp(self.volume_ml / self.capacity_ml, 0.0, 1.0)

    @property
    def viscosity(self) -> float:
        volume = self.volume_ml
        if volume <= 0:
            return 1.0
        return sum(c.viscosity * c.volume_ml for c in self.contents) / volume

    def is_empty(self) -> bool:
        return self.volume_ml <= 0.001

    def add(self, chemical: Chemical):
        accepted = min(chemical.volume_ml, max(0.0, self.capacity_ml - self.volume_ml))
        if accepted <= 0:
            return 0.0
        chemical.volume_ml = accepted
        self.contents.append(chemical)
        self.normalize()
        return accepted

    def remove(self, volume_ml: float) -> "Mixture":
        removed = Mixture(capacity_ml=volume_ml)
        remaining = max(0.0, volume_ml)
        for chem in list(self.contents):
            if remaining <= 0:
                break
            take = min(remaining, chem.volume_ml)
            removed.contents.append(chem.clone_portion(take))
            remaining -= take
        self.contents = [c for c in self.contents if c.volume_ml > 0.001]
        self.normalize()
        removed.normalize()
        return removed

    def normalize(self):
        volume = self.volume_ml
        if volume <= 0:
            self.pH = 7.0
            self.temperature = 25.0
            self.color = (220, 220, 220)
            return
        self.temperature = sum(c.temperature * c.volume_ml for c in self.contents) / volume
        self.color = tuple(
            int(sum(c.color[i] * c.volume_ml for c in self.contents) / volume)
            for i in range(3)
        )
        self.pH = self.estimate_pH()

    def acid_moles(self) -> float:
        return sum(c.moles() for c in self.contents if "acid" in c.reactivity)

    def base_moles(self) -> float:
        return sum(c.moles() for c in self.contents if "base" in c.reactivity)

    def estimate_pH(self) -> float:
        volume_l = max(self.volume_ml / 1000.0, 0.000001)
        acid = self.acid_moles()
        base = self.base_moles()
        if acid > base:
            h = (acid - base) / volume_l
            return clamp(-math.log10(max(h, 1e-14)), 0.0, 14.0)
        if base > acid:
            oh = (base - acid) / volume_l
            return clamp(14.0 + math.log10(max(oh, 1e-14)), 0.0, 14.0)
        return 7.0

    def display_name(self) -> str:
        if self.is_empty():
            return "Empty"
        labels = [c.name for c in self.contents if c.volume_ml > 0.001]
        unique = []
        for label in labels:
            if label not in unique:
                unique.append(label)
        return unique[0] if len(unique) == 1 else "Mixture"

    def dominant_category(self) -> str:
        if self.is_empty():
            return "water"
        totals = {}
        for c in self.contents:
            key = c.reactivity.replace("strong_", "").replace("weak_", "")
            totals[key] = totals.get(key, 0.0) + c.volume_ml
        return max(totals, key=totals.get)

    def formulas(self) -> set[str]:
        return {c.formula for c in self.contents if c.volume_ml > 0.001}

    def to_dict(self):
        return {
            "capacity_ml": self.capacity_ml,
            "temperature": self.temperature,
            "pH": self.pH,
            "color": tuple(self.color),
            "contents": [c.to_dict() for c in self.contents],
        }

    @classmethod
    def from_dict(cls, data):
        mix = cls(
            capacity_ml=float(data.get("capacity_ml", 250.0)),
            temperature=float(data.get("temperature", 25.0)),
            pH=float(data.get("pH", 7.0)),
            color=tuple(data.get("color", (220, 220, 220))),
        )
        mix.contents = [Chemical.from_dict(item) for item in data.get("contents", [])]
        mix.normalize()
        return mix
