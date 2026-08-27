"""
simulation.workspace_builder
Builds a prepared lab workspace from experiment configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from data.experiments import get_chemical_profile, get_chemical_options
from simulation.apparatus import ApparatusRegistry


TOOL_TO_APPARATUS = {
    "BEAKER": "beaker",
    "TEST_TUBE": "test_tube",
    "CYLINDER": "cylinder",
    "BUNSEN": "bunsen",
    "WATER_BATH": "water_bath",
    "CONICAL": "flask",
    "FLASK": "flask",
    "DROPPER_WATER": "dropper",
    "DROPPER_ACID": "dropper",
    "DROPPER_BASE": "dropper",
    "DROPPER_INDICATOR": "dropper",
    "BURETTE": "burette",
}

PREFILL_CATEGORY = {
    "WATER": "water",
    "ACID": "acid",
    "BASE": "base",
    "SALT": "salt",
    "INDICATOR": "indicator",
    "ALCOHOL": "alcohol",
}


@dataclass
class WorkspaceBuildResult:
    apparatus: list = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


class WorkspaceBuilder:
    def __init__(self, fw: int, fh: int):
        self.fw = fw
        self.fh = fh

    def build(self, exp_data: dict) -> WorkspaceBuildResult:
        sim = exp_data.get("simulation", {})
        layout = sim.get("workspace", {}).get("layout", [])
        result = WorkspaceBuildResult()

        if layout:
            for item in layout:
                apparatus = self._create_from_layout_item(item)
                if apparatus:
                    result.apparatus.append(apparatus)
            self._apply_initial_fills(exp_data, result.apparatus, sim.get("initial_quantities", {}))
        else:
            result.apparatus.extend(self._build_from_legacy_simulation(exp_data))

        result.messages.append(f"Workspace prepared with {len(result.apparatus)} apparatus.")
        return result

    def _create_from_layout_item(self, item: dict):
        atype = item.get("type") or item.get("apparatus")
        if not atype:
            return None
        x = float(item.get("x", self.fw * 0.25))
        y = float(item.get("y", self.fh - 30))
        apparatus = ApparatusRegistry.create(atype, x, y, self.fw, self.fh)
        apparatus.object_id = item.get("id", f"{atype}_{id(apparatus)}")
        apparatus.state.transition(item.get("state", "empty"))
        return apparatus

    def _build_from_legacy_simulation(self, exp_data: dict) -> list:
        sim = exp_data.get("simulation", {})
        tools = sim.get("tools", ["BEAKER"])
        apparatus_list = []
        slot = 0
        seen = {}

        for tool in tools:
            atype = TOOL_TO_APPARATUS.get(tool, "beaker")
            key = tool.lower()
            x = self._slot_x(slot, len(tools))
            y = self.fh - 30
            apparatus = ApparatusRegistry.create(atype, x, y, self.fw, self.fh)
            apparatus.object_id = key
            apparatus.state.transition("empty")
            apparatus_list.append(apparatus)
            seen[key] = apparatus
            slot += 1

        self._legacy_prefill(exp_data, apparatus_list, seen)
        return apparatus_list

    def _slot_x(self, slot: int, total: int) -> float:
        total = max(total, 1)
        margin = self.fw * 0.12
        usable = self.fw - margin * 2
        return margin + usable * ((slot + 1) / (total + 1))

    def _legacy_prefill(self, exp_data: dict, apparatus_list: list, seen: dict):
        sim = exp_data.get("simulation", {})
        prefill = sim.get("prefill", {})
        chemical_options = get_chemical_options(exp_data)

        for raw_key, amount in prefill.items():
            category = PREFILL_CATEGORY.get(raw_key.upper(), raw_key.lower())
            target = self._find_prefill_target(category, seen, apparatus_list)
            if not target:
                continue
            label = self._first_label_for_category(chemical_options, category)
            profile = get_chemical_profile(label)
            target.add_liquid(
                profile["category"],
                float(amount),
                display_name=profile["display_name"],
                color=profile["color_bgr"],
            )
            target.state.transition("filled", chemical=profile["display_name"])

    def _apply_initial_fills(self, exp_data: dict, apparatus_list: list, fills: dict):
        by_id = {getattr(a, "object_id", ""): a for a in apparatus_list}
        for object_id, fill in fills.items():
            target = by_id.get(object_id)
            if not target:
                continue
            label = fill.get("chemical", "Distilled Water")
            profile = get_chemical_profile(label)
            target.add_liquid(
                profile["category"],
                float(fill.get("volume_ml", 0.0)),
                display_name=profile["display_name"],
                color=profile["color_bgr"],
            )
            target.mixture.temperature = float(fill.get("temperature_c", target.mixture.temperature))
            target.state.transition("filled", chemical=profile["display_name"])

    def _find_prefill_target(self, category: str, seen: dict, apparatus_list: list):
        if category == "base":
            preferred_keys = ["conical", "flask", "beaker", "dropper_base"]
        elif category == "indicator":
            preferred_keys = ["dropper_indicator", "conical", "flask", "beaker"]
        elif category == "acid":
            preferred_keys = ["dropper_acid", "burette", "beaker", "conical", "flask"]
        elif category == "water":
            preferred_keys = ["dropper_water", "water_bath", "beaker", "cylinder"]
        else:
            preferred_keys = [f"dropper_{category}", "beaker", "test_tube", "conical", "flask"]
        for key in preferred_keys:
            if key and key in seen:
                return seen[key]
        for apparatus in apparatus_list:
            if apparatus.atype not in ("bunsen",):
                return apparatus
        return None

    def _first_label_for_category(self, chemical_options: dict, category: str) -> str:
        options = chemical_options.get(category) or []
        if options:
            return options[0]
        fallback = {
            "water": "Distilled Water",
            "acid": "Dilute Hydrochloric Acid (HCl)",
            "base": "Sodium Hydroxide Solution (NaOH)",
            "indicator": "Phenolphthalein Indicator",
            "salt": "Common Salt (NaCl)",
            "alcohol": "Ethanol",
        }
        return fallback.get(category, "Distilled Water")
