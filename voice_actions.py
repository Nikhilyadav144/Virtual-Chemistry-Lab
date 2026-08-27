"""Command execution bridge between Atom and the existing GUI/simulation."""

from data.experiments import EXPERIMENTS


TUTOR_ANSWERS = {
    "neutralization": (
        "Neutralization happens when acid hydrogen ions and base hydroxide ions "
        "form water. The remaining ions form a salt."
    ),
    "titration": (
        "Titration measures an unknown concentration by adding a known solution "
        "until the endpoint shows equivalence."
    ),
    "pink": (
        "Phenolphthalein turns pink in basic solution. It becomes colorless when "
        "acid neutralizes the base near the endpoint."
    ),
}


class VoiceActionRouter:
    def __init__(self, main_window):
        self.main = main_window

    def execute(self, command):
        intent = command.intent
        target = command.target

        if intent == "wake":
            return "I am listening."
        if intent == "tutor":
            sim = self.main.current_simulation_page()
            if sim:
                return sim.handle_voice_command(command)
            return self._tutor(target)
        if intent == "open_class":
            class_num = int(target)
            self.main._go_exp_list(class_num)
            return f"Opening Class {class_num} experiments."
        if intent == "go_home":
            self.main._go_home()
            return "Going home."
        if intent == "open_experiment":
            return self._open_experiment(target)
        if intent == "start_simulation":
            if self.main._chosen_exp_id:
                self.main._go_simulation()
                return "Starting simulation."
            return "Select an experiment first."

        sim = self.main.current_simulation_page()
        if sim:
            return sim.handle_voice_command(command)

        return self._not_in_simulation(intent)

    def _open_experiment(self, target):
        target = self._normalize_experiment_target(target)
        for class_num, experiments in EXPERIMENTS.items():
            for exp in experiments:
                name = exp.get("name", "").lower()
                exp_id = exp.get("id", "").lower()
                if target in name or target == exp_id:
                    self.main._chosen_class = class_num
                    self.main._go_exp_details(exp["id"])
                    return f"Opening {exp['name']}."
        return "I could not find that experiment."

    def _tutor(self, text):
        lowered = text.lower()
        for key, answer in TUTOR_ANSWERS.items():
            if key in lowered:
                return answer
        return "I can explain the reaction, apparatus, or current guided step."

    def _normalize_experiment_target(self, target):
        target = (target or "").lower().strip()
        aliases = {
            "titration": "titration",
            "acid base titration": "titration",
            "neutralization": "neutralization",
            "neutralisation": "neutralization",
            "ph": "ph",
            "electrolysis": "electrolysis",
            "flame test": "flame test",
            "chromatography": "chromatography",
        }
        return aliases.get(target, target)

    def _not_in_simulation(self, intent):
        if intent in {"select", "add", "remove", "set_mode", "reset", "pause", "resume"}:
            return "Open a simulation first for that command."
        return "I did not understand that command."
