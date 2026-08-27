"""
simulation.reaction_database
Declarative reaction rules consumed by ReactionEngine.
"""

from __future__ import annotations

from dataclasses import dataclass, field


ColorBGR = tuple[int, int, int]


@dataclass(frozen=True)
class ReactionRule:
    reactants: frozenset[str]
    type: str
    products: tuple[str, ...] = field(default_factory=tuple)
    heat_generation_c: float = 0.0
    gas: bool = False
    precipitate: bool = False
    color_change: ColorBGR | None = None
    message: str = ""


REACTION_RULES: tuple[ReactionRule, ...] = (
    ReactionRule(
        reactants=frozenset(("HCl", "NaOH")),
        type="neutralization",
        products=("NaCl", "H2O"),
        heat_generation_c=6.0,
        color_change=(235, 230, 215),
        message="Neutralization",
    ),
    ReactionRule(
        reactants=frozenset(("H2SO4", "NaOH")),
        type="neutralization",
        products=("NaCl", "H2O"),
        heat_generation_c=9.0,
        color_change=(235, 230, 215),
        message="Neutralization",
    ),
    ReactionRule(
        reactants=frozenset(("CH3COOH", "NaHCO3")),
        type="gas_evolution",
        products=("CO2", "H2O"),
        heat_generation_c=-2.0,
        gas=True,
        color_change=(210, 230, 255),
        message="Gas Evolution",
    ),
)


def matching_rules(formulas: set[str]) -> list[ReactionRule]:
    return [rule for rule in REACTION_RULES if rule.reactants.issubset(formulas)]
