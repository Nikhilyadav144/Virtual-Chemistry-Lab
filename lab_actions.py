"""
simulation.lab_actions
Reusable laboratory action commands.

Experiments should be expressed as combinations of these actions instead of
hardcoded experiment-specific Python branches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time


class LabActionType(str, Enum):
    PICK_UP = "pick_up"
    MOVE = "move"
    ROTATE = "rotate"
    TILT = "tilt"
    SWIRL = "swirl"
    SHAKE = "shake"
    POUR = "pour"
    DROP = "drop"
    HEAT = "heat"
    COOL = "cool"
    FILTER = "filter"
    WASH = "wash"
    RINSE = "rinse"
    DRY = "dry"
    INSERT_FILTER_PAPER = "insert_filter_paper"
    INSERT_STOPPER = "insert_stopper"
    CONNECT_TUBING = "connect_tubing"
    DISCONNECT_TUBING = "disconnect_tubing"
    IGNITE_BURNER = "ignite_burner"
    ADJUST_FLAME = "adjust_flame"
    MEASURE_PH = "measure_ph"
    MEASURE_VOLUME = "measure_volume"
    MEASURE_MASS = "measure_mass"
    OBSERVE_COLOUR = "observe_colour"
    OBSERVE_PRECIPITATE = "observe_precipitate"
    OBSERVE_GAS = "observe_gas_evolution"
    OBSERVE_BUBBLES = "observe_bubbles"
    OBSERVE_SMOKE = "observe_smoke"
    OBSERVE_FLAME_COLOUR = "observe_flame_colour"
    COLLECT_FILTRATE = "collect_filtrate"
    COLLECT_RESIDUE = "collect_residue"
    COLLECT_DISTILLATE = "collect_distillate"
    COLLECT_CRYSTALS = "collect_crystals"
    START_ELECTROLYSIS = "start_electrolysis"
    STOP_ELECTROLYSIS = "stop_electrolysis"
    CONNECT_BATTERY = "connect_battery"
    OPEN_BURETTE_VALVE = "open_burette_valve"
    CLOSE_BURETTE_VALVE = "close_burette_valve"
    USE_DROPPER = "use_dropper"
    USE_WASH_BOTTLE = "use_wash_bottle"
    ADD_INDICATOR = "add_indicator"
    ADD_CATALYST = "add_catalyst"
    STIR = "stir_solution"


@dataclass(frozen=True)
class LabAction:
    action_type: LabActionType
    actor_id: str = ""
    target_id: str = ""
    amount_ml: float = 0.0
    value: float | str | None = None
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ActionResult:
    action: LabAction
    success: bool
    message: str = ""
    observations: list[str] = field(default_factory=list)
