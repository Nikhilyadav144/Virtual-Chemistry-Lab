"""
simulation.object_state
State model for reusable laboratory objects.

The state machine is permissive by design: it records meaningful lab states
without blocking existing free-form gesture interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time


DEFAULT_STATES = {
    "filter_paper": "flat",
    "funnel": "empty",
    "flask": "empty",
    "beaker": "empty",
    "burette": "empty",
    "burner": "off",
    "bunsen": "off",
    "test_tube": "empty",
    "dropper": "empty",
    "cylinder": "empty",
    "water_bath": "empty",
}


STATE_ALIASES = {
    "contains_liquid": "filled",
    "reaction_active": "reaction",
    "valve_closed": "valve_closed",
    "valve_open": "valve_open",
}


@dataclass
class ObjectState:
    object_id: str
    object_type: str
    state: str = ""
    flags: set[str] = field(default_factory=set)
    metadata: dict = field(default_factory=dict)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.state:
            self.state = DEFAULT_STATES.get(self.object_type, "idle")

    def transition(self, new_state: str, **metadata):
        self.state = STATE_ALIASES.get(new_state, new_state)
        self.metadata.update(metadata)
        self.updated_at = time.time()

    def add_flag(self, flag: str):
        self.flags.add(flag)
        self.updated_at = time.time()

    def remove_flag(self, flag: str):
        self.flags.discard(flag)
        self.updated_at = time.time()

    def has(self, state_or_flag: str) -> bool:
        return self.state == state_or_flag or state_or_flag in self.flags
