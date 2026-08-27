"""
voice_assistant.command_registry
Central command vocabulary for Atom.

The parser uses this registry for keyword and alias matching. The action layer
still calls existing GUI/simulation methods, so hand gesture manipulation remains
independent from voice commands.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryMatch:
    canonical: str
    spoken_label: str


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


class CommandRegistry:
    APPARATUS_ALIASES = {
        "beaker": ("beaker",),
        "test_tube": ("test tube", "tube", "testtube"),
        "flask": ("flask", "conical flask"),
        "dropper": ("dropper", "pipette"),
        "cylinder": ("cylinder", "measuring cylinder", "graduated cylinder"),
        "burette": ("burette", "buret"),
        "bunsen": ("bunsen", "bunsen burner", "burner"),
        "water_bath": ("water bath", "waterbath"),
    }

    CHEMICAL_ALIASES = {
        "hydrochloric acid": (
            "hydrochloric acid", "dilute hydrochloric acid", "hcl", "acid"
        ),
        "sodium hydroxide": (
            "sodium hydroxide", "sodium hydroxide solution", "naoh", "base"
        ),
        "phenolphthalein": (
            "phenolphthalein", "phenolphthalein indicator", "indicator"
        ),
        "universal indicator": ("universal indicator", "indicator solution"),
        "sulphuric acid": ("sulphuric acid", "sulfuric acid", "h2so4"),
        "water": ("water", "distilled water"),
        "salt": ("salt", "sodium chloride", "nacl"),
    }

    def match_apparatus(self, text: str) -> RegistryMatch | None:
        return self._match_alias_map(text, self.APPARATUS_ALIASES)

    def match_chemical_alias(self, text: str) -> RegistryMatch | None:
        return self._match_alias_map(text, self.CHEMICAL_ALIASES)

    def _match_alias_map(self, text: str, aliases: dict[str, tuple[str, ...]]) -> RegistryMatch | None:
        normalized = normalize(text)
        if not normalized:
            return None
        for canonical, labels in aliases.items():
            for label in labels:
                norm_label = normalize(label)
                if normalized == norm_label or norm_label in normalized or normalized in norm_label:
                    return RegistryMatch(canonical, label)
        return None
