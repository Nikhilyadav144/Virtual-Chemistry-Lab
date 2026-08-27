"""
simulation.apparatus_database
Declarative apparatus definitions used by apparatus and UI factories.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ApparatusDefinition:
    key: str
    label: str
    capacity_ml: float
    shape: str
    size: tuple[int, int]
    pour_point: str = "lip"
    supported_actions: tuple[str, ...] = field(default_factory=tuple)
    maximum_volume_ml: float | None = None

    @property
    def max_volume_ml(self) -> float:
        return self.maximum_volume_ml or self.capacity_ml


APPARATUS: dict[str, ApparatusDefinition] = {
    "beaker": ApparatusDefinition(
        "beaker", "Beaker", 250.0, "beaker", (160, 200),
        supported_actions=("hold", "fill", "pour", "heat", "rinse"),
    ),
    "test_tube": ApparatusDefinition(
        "test_tube", "Test Tube", 50.0, "test_tube", (50, 180),
        supported_actions=("hold", "fill", "heat", "rinse"),
    ),
    "flask": ApparatusDefinition(
        "flask", "Conical Flask", 250.0, "flask", (160, 220),
        supported_actions=("hold", "fill", "pour", "heat", "rinse"),
    ),
    "dropper": ApparatusDefinition(
        "dropper", "Dropper", 10.0, "dropper", (55, 170),
        pour_point="nozzle", supported_actions=("fill", "dropwise_pour", "rinse"),
    ),
    "cylinder": ApparatusDefinition(
        "cylinder", "Measuring Cylinder", 100.0, "cylinder", (70, 240),
        supported_actions=("hold", "fill", "pour", "measure", "rinse"),
    ),
    "burette": ApparatusDefinition(
        "burette", "Burette", 50.0, "burette", (50, 300),
        pour_point="tap", supported_actions=("fill", "dropwise_pour", "titrate", "rinse"),
    ),
    "bunsen": ApparatusDefinition(
        "bunsen", "Bunsen Burner", 0.0, "burner", (90, 130),
        pour_point="none", supported_actions=("heat",),
    ),
    "water_bath": ApparatusDefinition(
        "water_bath", "Water Bath", 500.0, "bath", (190, 120),
        supported_actions=("fill", "heat", "rinse"),
    ),
}


def get_apparatus_definition(key: str) -> ApparatusDefinition:
    return APPARATUS.get(key, APPARATUS["beaker"])


def available_apparatus() -> list[str]:
    return list(APPARATUS.keys())
