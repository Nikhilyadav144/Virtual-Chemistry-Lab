"""
simulation/reaction_engine.py
Rule-based chemistry reactions for virtual lab mixtures.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulation.chemistry_engine import Chemical, Mixture, clamp
from simulation.reaction_database import REACTION_RULES, ReactionRule, matching_rules


@dataclass
class ReactionEvent:
    type: str
    intensity: float = 1.0
    temperature_change: float = 0.0
    gas: bool = False
    precipitate: bool = False
    color: tuple[int, int, int] | None = None
    message: str = ""


REACTIONS = {
    rule.reactants: {
        "type": rule.type,
        "products": list(rule.products),
        "temperature_change": rule.heat_generation_c,
        "gas": rule.gas,
        "precipitate": rule.precipitate,
        "color": rule.color_change,
    }
    for rule in REACTION_RULES
}


class ReactionEngine:
    def apply(self, mixture: Mixture, added: Chemical | None = None) -> list[ReactionEvent]:
        events = []
        mixture.normalize()
        formulas = mixture.formulas()

        for rule in matching_rules(formulas):
            events.append(self._apply_rule(mixture, rule))

        indicator = self._apply_indicator(mixture)
        if indicator:
            events.append(indicator)

        return events

    def _apply_rule(self, mixture: Mixture, rule: ReactionRule) -> ReactionEvent:
        intensity = 1.0
        if rule.type == "neutralization":
            acid = mixture.acid_moles()
            base = mixture.base_moles()
            if max(acid, base) > 0:
                intensity = min(acid, base) / max(acid, base)
            mixture.temperature += rule.heat_generation_c * max(0.2, intensity)
            if rule.color_change:
                mixture.color = rule.color_change
        elif rule.color_change:
            mixture.color = rule.color_change

        return ReactionEvent(
            type=rule.type,
            intensity=clamp(intensity, 0.15, 1.0),
            temperature_change=rule.heat_generation_c,
            gas=rule.gas,
            precipitate=rule.precipitate,
            color=rule.color_change,
            message=rule.message or rule.type.replace("_", " ").title(),
        )

    def _apply_indicator(self, mixture: Mixture) -> ReactionEvent | None:
        formulas = mixture.formulas()
        old_color = mixture.color
        if "PHEN" in formulas:
            mixture.color = (180, 105, 255) if mixture.pH > 8.2 else (240, 230, 230)
        elif "METHYL_ORANGE" in formulas:
            if mixture.pH < 3.2:
                mixture.color = (60, 80, 255)
            elif mixture.pH > 4.4:
                mixture.color = (80, 220, 255)
            else:
                mixture.color = (40, 150, 255)
        elif "UNIVERSAL" in formulas:
            if mixture.pH < 3:
                mixture.color = (60, 60, 255)
            elif mixture.pH < 6:
                mixture.color = (80, 190, 255)
            elif mixture.pH < 8:
                mixture.color = (120, 210, 120)
            elif mixture.pH < 11:
                mixture.color = (220, 100, 120)
            else:
                mixture.color = (190, 60, 150)
        else:
            return None

        if mixture.color != old_color:
            return ReactionEvent(
                type="color_change",
                intensity=0.7,
                color=mixture.color,
                message=f"Indicator changed at pH {mixture.pH:.1f}",
            )
        return None
