"""
simulation.virtual_lab_engine
Coordinator for reusable lab systems: workspace, apparatus, chemicals,
reactions, object states, validation, and action history.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from simulation.lab_actions import ActionResult, LabAction, LabActionType
from simulation.reaction_engine import ReactionEngine
from simulation.experiment_validator import ExperimentValidator
from simulation.workspace_builder import WorkspaceBuilder


@dataclass
class LabWorkspace:
    apparatus: list = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    action_history: list[ActionResult] = field(default_factory=list)

    def by_id(self, object_id: str):
        for apparatus in self.apparatus:
            if getattr(apparatus, "object_id", "") == object_id:
                return apparatus
        return None


class VirtualLabEngine:
    def __init__(self, exp_data: dict, fw: int, fh: int, mode: str = "guided"):
        self.exp_data = exp_data
        self.fw = fw
        self.fh = fh
        self.mode = mode
        self.workspace = LabWorkspace()
        self.reactions = ReactionEngine()
        self.validator = ExperimentValidator()

    def build_workspace(self) -> LabWorkspace:
        build = WorkspaceBuilder(self.fw, self.fh).build(self.exp_data)
        self.workspace.apparatus = build.apparatus
        self.workspace.observations.extend(build.messages)
        return self.workspace

    def execute(self, action: LabAction) -> ActionResult:
        handler = {
            LabActionType.PICK_UP: self._pick_up,
            LabActionType.MOVE: self._move,
            LabActionType.TILT: self._tilt,
            LabActionType.SWIRL: self._swirl,
            LabActionType.POUR: self._pour,
            LabActionType.HEAT: self._heat,
            LabActionType.RINSE: self._rinse,
            LabActionType.IGNITE_BURNER: self._ignite_burner,
            LabActionType.ADJUST_FLAME: self._adjust_flame,
            LabActionType.OPEN_BURETTE_VALVE: self._open_burette,
            LabActionType.CLOSE_BURETTE_VALVE: self._close_burette,
            LabActionType.MEASURE_PH: self._measure_ph,
            LabActionType.MEASURE_VOLUME: self._measure_volume,
            LabActionType.OBSERVE_COLOUR: self._observe_colour,
        }.get(action.action_type, self._record_only)
        result = handler(action)
        self.workspace.action_history.append(result)
        return result

    def apply_reactions(self, apparatus) -> list:
        events = self.reactions.apply(apparatus.mixture)
        if events:
            apparatus.state.transition("reaction", events=[event.type for event in events])
            self.workspace.observations.extend(event.message for event in events if event.message)
        return events

    def _pick_up(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        target.state.transition("picked_up")
        return ActionResult(action, True, f"Picked up {target.atype}.")

    def _move(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        x, y = action.metadata.get("position", (target.x, target.y))
        target.x = float(x)
        target.y = float(y)
        target.state.transition("moved", position=(target.x, target.y))
        return ActionResult(action, True, f"Moved {target.atype}.")

    def _tilt(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        target.tilt_angle = float(action.value or 0.0)
        target.state.transition("pouring" if abs(target.tilt_angle) > 10 else "tilted")
        return ActionResult(action, True, f"Tilted {target.atype}.")

    def _swirl(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        target.mixing_intensity = min(1.0, getattr(target, "mixing_intensity", 0.0) + 0.18)
        target.state.transition("swirling", intensity=target.mixing_intensity)
        self.apply_reactions(target)
        return ActionResult(action, True, f"Swirled {target.atype}.")

    def _pour(self, action: LabAction) -> ActionResult:
        source = self.workspace.by_id(action.actor_id)
        target = self.workspace.by_id(action.target_id)
        if not source or not target:
            return ActionResult(action, False, "Source or target apparatus not found.")
        portion = source.mixture.remove(action.amount_ml)
        for chemical in portion.contents:
            target.mixture.add(chemical)
        source.state.transition("pouring")
        target.state.transition("receiving_liquid")
        events = self.apply_reactions(target)
        return ActionResult(
            action,
            portion.volume_ml > 0,
            f"Poured {portion.volume_ml:.1f} ml.",
            [event.message for event in events if event.message],
        )

    def _heat(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        delta = float(action.value or 5.0)
        target.mixture.temperature += delta
        target.state.transition("heating", temperature=target.mixture.temperature)
        return ActionResult(action, True, f"Heating {target.atype}.")

    def _rinse(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        target.rinse()
        target.state.transition("empty")
        return ActionResult(action, True, f"Rinsed {target.atype}.")

    def _ignite_burner(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Burner not found.")
        target.state.transition("medium_flame")
        return ActionResult(action, True, "Burner ignited.")

    def _adjust_flame(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Burner not found.")
        level = str(action.value or "medium_flame")
        target.state.transition(level)
        return ActionResult(action, True, f"Flame adjusted to {level}.")

    def _open_burette(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Burette not found.")
        target.state.transition("valve_open")
        return ActionResult(action, True, "Burette valve opened.")

    def _close_burette(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Burette not found.")
        target.state.transition("valve_closed")
        return ActionResult(action, True, "Burette valve closed.")

    def _measure_ph(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        return ActionResult(action, True, f"pH is {target.mixture.pH:.1f}.")

    def _measure_volume(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        return ActionResult(action, True, f"Volume is {target.mixture.volume_ml:.1f} ml.")

    def _observe_colour(self, action: LabAction) -> ActionResult:
        target = self.workspace.by_id(action.target_id)
        if not target:
            return ActionResult(action, False, "Target apparatus not found.")
        return ActionResult(action, True, f"Observed colour {target.mixture.color}.")

    def _record_only(self, action: LabAction) -> ActionResult:
        return ActionResult(action, True, f"Recorded action {action.action_type.value}.")
