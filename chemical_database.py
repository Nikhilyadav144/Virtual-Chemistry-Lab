"""
simulation.chemical_database
Central chemical property catalog for the simulation engine.

The engine reads chemicals from this module instead of embedding chemical
properties inside chemistry logic. Future JSON loading can replace or extend
this catalog without changing apparatus, reactions, or rendering code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


ColorBGR = tuple[int, int, int]


@dataclass(frozen=True)
class ChemicalDefinition:
    formula: str
    name: str
    color: ColorBGR
    state: str = "liquid"
    density: float = 1.0
    viscosity: float = 1.0
    pH: float = 7.0
    boiling_point_c: float | None = 100.0
    melting_point_c: float | None = 0.0
    conductivity: float = 0.0
    flammability: str = "none"
    hazard_level: str = "low"
    reactivity: str = "neutral"

    def to_legacy_dict(self) -> dict:
        data = asdict(self)
        data["formula"] = self.formula
        return data


CHEMICALS: dict[str, ChemicalDefinition] = {
    "H2O": ChemicalDefinition(
        formula="H2O", name="Distilled Water", color=(255, 214, 160),
        pH=7.0, density=1.0, viscosity=1.0, conductivity=0.01,
    ),
    "HCl": ChemicalDefinition(
        formula="HCl", name="Hydrochloric Acid", color=(235, 235, 175),
        pH=1.0, density=1.02, viscosity=1.04, boiling_point_c=110.0,
        conductivity=0.9, hazard_level="high", reactivity="strong_acid",
    ),
    "H2SO4": ChemicalDefinition(
        formula="H2SO4", name="Sulphuric Acid", color=(230, 245, 190),
        pH=0.8, density=1.12, viscosity=1.35, boiling_point_c=337.0,
        melting_point_c=10.0, conductivity=0.95, hazard_level="high",
        reactivity="strong_acid",
    ),
    "CH3COOH": ChemicalDefinition(
        formula="CH3COOH", name="Acetic Acid", color=(200, 230, 255),
        pH=3.0, density=1.01, viscosity=1.15, boiling_point_c=118.0,
        melting_point_c=16.6, conductivity=0.2, hazard_level="medium",
        reactivity="weak_acid",
    ),
    "NaOH": ChemicalDefinition(
        formula="NaOH", name="Sodium Hydroxide", color=(255, 230, 220),
        pH=13.0, density=1.04, viscosity=1.08, boiling_point_c=1388.0,
        melting_point_c=318.0, conductivity=0.85, hazard_level="high",
        reactivity="strong_base",
    ),
    "NaCl": ChemicalDefinition(
        formula="NaCl", name="Sodium Chloride", color=(245, 235, 205),
        pH=7.0, density=1.03, viscosity=1.05, boiling_point_c=1465.0,
        melting_point_c=801.0, conductivity=0.65, reactivity="salt",
    ),
    "NaHCO3": ChemicalDefinition(
        formula="NaHCO3", name="Sodium Bicarbonate", color=(255, 220, 205),
        pH=8.3, density=1.01, viscosity=1.03, conductivity=0.25,
        reactivity="weak_base",
    ),
    "PHEN": ChemicalDefinition(
        formula="PHEN", name="Phenolphthalein", color=(240, 230, 230),
        pH=7.0, density=0.98, viscosity=1.0, boiling_point_c=None,
        melting_point_c=None, hazard_level="medium", reactivity="indicator",
    ),
    "METHYL_ORANGE": ChemicalDefinition(
        formula="METHYL_ORANGE", name="Methyl Orange", color=(70, 160, 255),
        pH=7.0, density=1.0, viscosity=1.0, boiling_point_c=None,
        melting_point_c=None, hazard_level="medium", reactivity="indicator",
    ),
    "UNIVERSAL": ChemicalDefinition(
        formula="UNIVERSAL", name="Universal Indicator", color=(70, 170, 255),
        pH=7.0, density=1.0, viscosity=1.0, boiling_point_c=None,
        melting_point_c=None, hazard_level="medium", reactivity="indicator",
    ),
    "ETHANOL": ChemicalDefinition(
        formula="ETHANOL", name="Ethanol", color=(235, 245, 215),
        pH=7.0, density=0.79, viscosity=1.2, boiling_point_c=78.4,
        melting_point_c=-114.1, conductivity=0.0, flammability="high",
        hazard_level="medium", reactivity="alcohol",
    ),
    "CO2": ChemicalDefinition(
        formula="CO2", name="Carbon Dioxide", color=(210, 230, 255),
        state="gas", density=0.00198, viscosity=0.015, boiling_point_c=-78.5,
        melting_point_c=-78.5, reactivity="gas",
    ),
}


def get_chemical_definition(formula: str) -> ChemicalDefinition:
    return CHEMICALS.get(formula, CHEMICALS["H2O"])


def chemical_library_dict() -> dict[str, dict]:
    return {formula: definition.to_legacy_dict() for formula, definition in CHEMICALS.items()}
