"""
simulation/step_manager.py
"""


class StepStatus:
    PENDING   = "pending"
    ACTIVE    = "active"
    COMPLETED = "completed"
    FAILED    = "failed"


class ExperimentStep:
    def __init__(self, data):
        # FIX: data can be a plain string (from experiments.py procedure list)
        # or a proper dict. Handle both.
        if isinstance(data, str):
            data = {
                "action":   "observe_reaction",
                "reaction": "general",
                "hint":     data
            }
        self.action       = data.get("action", "")
        self.apparatus    = data.get("apparatus", "")
        self.liquid       = data.get("liquid", "")
        self.amount_ml    = float(data.get("amount_ml", 0))
        self.target       = data.get("target", "")
        self.reaction     = data.get("reaction", "")
        self.hint         = data.get("hint", "")
        self.status       = StepStatus.PENDING
        self._progress_ml = 0.0

    def description(self):
        if self.hint:
            return self.hint
        if self.action == "select_apparatus":
            return f"Select a {self.apparatus}"
        elif self.action == "add_liquid":
            return f"Add {self.amount_ml:.0f} ml of {self.liquid} to {self.target}"
        elif self.action == "pour":
            return f"Pour from {self.apparatus} into {self.target}"
        elif self.action == "observe_reaction":
            return f"Observe the reaction: {self.reaction}"
        elif self.action == "heat":
            return f"Heat the {self.target} with the Bunsen burner"
        return self.action


class StepManager:
    def __init__(self, steps_data, mode="guided"):
        self.steps       = [ExperimentStep(s) for s in steps_data]
        self.mode        = mode
        self.current_idx = 0
        self.message     = ""
        self.completed   = False

        if self.steps:
            self.steps[0].status = StepStatus.ACTIVE

    @classmethod
    def from_config(cls, config, mode="guided"):
        return cls(config.steps, mode=mode)

    def current_step(self):
        if self.current_idx < len(self.steps):
            return self.steps[self.current_idx]
        return None

    def progress_text(self):
        total = len(self.steps)
        if total == 0:
            return "No guided steps"
        done  = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        current = min(self.current_idx + 1, total)
        return f"Step {current} / {total}  ({done} done)"

    def complete_current_step(self):
        step = self.current_step()
        if not step:
            return
        self._complete_step("✅  Step completed")

    def set_current_step(self, index):
        if not self.steps:
            return
        index = max(0, min(index, len(self.steps) - 1))
        self.current_idx = index
        self.completed = False
        for i, step in enumerate(self.steps):
            if i < index:
                step.status = StepStatus.COMPLETED
            elif i == index:
                step.status = StepStatus.ACTIVE
            else:
                step.status = StepStatus.PENDING
        self.message = ""

    def notify_apparatus_selected(self, atype):
        step = self.current_step()
        if not step or self.mode == "free":
            return True
        if step.action == "select_apparatus":
            if step.apparatus == atype:
                self._complete_step(f"✅  {atype.title()} selected!")
                return True
            else:
                self.message = f"⚠  Need {step.apparatus}, not {atype}"
                return False
        return True

    def notify_liquid_added(self, liquid_name, amount_ml, target_atype):
        step = self.current_step()
        if not step or self.mode == "free":
            return True
        if step.action == "add_liquid":
            if step.liquid != liquid_name:
                self.message = f"⚠  Need {step.liquid}, not {liquid_name}"
                return False
            if step.target and step.target != target_atype:
                self.message = f"⚠  Add to {step.target}, not {target_atype}"
                return False
            step._progress_ml += amount_ml
            remaining = step.amount_ml - step._progress_ml
            if remaining <= 0:
                self._complete_step(
                    f"✅  Added {step.amount_ml:.0f} ml {step.liquid}!")
            else:
                self.message = f"⏳  Add {remaining:.0f} ml more of {step.liquid}"
        return True

    def notify_reaction(self, reaction_name):
        step = self.current_step()
        if not step:
            return
        if (step.action == "observe_reaction" and
                step.reaction == reaction_name):
            self._complete_step(f"✅  Reaction observed: {reaction_name}!")

    def notify_heat(self, target_atype):
        step = self.current_step()
        if not step or self.mode == "free":
            return
        if step.action == "heat" and step.target == target_atype:
            self._complete_step(f"✅  Heated {target_atype}!")

    def _complete_step(self, msg):
        step = self.current_step()
        if step:
            step.status = StepStatus.COMPLETED
        self.message     = msg
        self.current_idx += 1
        if self.current_idx >= len(self.steps):
            self.completed = True
            self.message   = "🎉  Experiment complete!"
        else:
            self.steps[self.current_idx].status = StepStatus.ACTIVE
