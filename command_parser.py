"""Rule-based command parser for Atom."""

from __future__ import annotations

from dataclasses import dataclass
import re

from voice_assistant.command_registry import CommandRegistry, normalize
from voice_assistant.wake_word import WakeWordDetector


@dataclass
class VoiceCommand:
    intent: str
    target: str = ""
    raw_text: str = ""
    metadata: dict | None = None


class CommandParser:
    def __init__(self, wake_detector: WakeWordDetector | None = None, registry: CommandRegistry | None = None):
        self.wake_detector = wake_detector or WakeWordDetector()
        self.registry = registry or CommandRegistry()

    def parse(self, text: str) -> VoiceCommand | None:
        wake = self.wake_detector.detect(text)
        raw = wake.original_text
        if not raw:
            return None

        command = wake.command_text if wake.woke else raw
        if not wake.woke and not self._is_direct_command(command):
            return None

        if not command:
            return VoiceCommand("wake", raw_text=raw)

        class_match = re.search(r"(open|go to|show)\s+class\s+(\d+)", command)
        if class_match:
            return VoiceCommand("open_class", class_match.group(2), raw)
        if "go home" in command or command == "home":
            return VoiceCommand("go_home", raw_text=raw)
        if "start simulation" in command or "open simulation" in command:
            return VoiceCommand("start_simulation", raw_text=raw)
        experiment_match = re.search(r"(open|start|show)\s+(.+?)\s+experiment", command)
        if experiment_match:
            return VoiceCommand("open_experiment", experiment_match.group(2).strip(), raw)
        if command.startswith("open "):
            target = command.removeprefix("open ").strip()
            if "class" not in target:
                return VoiceCommand("open_experiment", target, raw)

        if command in ("next step", "continue", "continue step"):
            return VoiceCommand("next_step", raw_text=raw)
        if command in ("undo", "undo action"):
            return VoiceCommand("undo", raw_text=raw)
        if command in ("redo", "redo action"):
            return VoiceCommand("redo", raw_text=raw)
        if command.startswith("rinse"):
            return VoiceCommand("rinse_selected", command.removeprefix("rinse").strip(), raw)

        for prefix, intent in (
            ("select ", "select"),
            ("choose ", "select"),
            ("add ", "add"),
            ("remove ", "remove"),
            ("delete ", "remove"),
        ):
            if command.startswith(prefix):
                target = command[len(prefix):].strip()
                return VoiceCommand(intent, target, raw, self._target_metadata(target))

        if "guided mode" in command:
            return VoiceCommand("set_mode", "guided", raw)
        if "free mode" in command:
            return VoiceCommand("set_mode", "free", raw)
        if "reset experiment" in command or command == "reset":
            return VoiceCommand("reset", raw_text=raw)
        if "pause simulation" in command or command == "pause":
            return VoiceCommand("pause", raw_text=raw)
        if "resume simulation" in command or command == "resume":
            return VoiceCommand("resume", raw_text=raw)
        if command.startswith("heat"):
            return VoiceCommand("heat_selected", raw_text=raw)

        for prefix in ("explain ", "what is ", "why ", "how "):
            if command.startswith(prefix):
                return VoiceCommand("tutor", command, raw)

        return VoiceCommand("unknown", command, raw)

    def _is_direct_command(self, command: str) -> bool:
        starters = (
            "open ", "go home", "start simulation", "select ", "choose ",
            "add ", "remove ", "delete ", "guided mode", "free mode",
            "reset", "pause", "resume", "heat ", "explain ", "what is ",
            "why ", "how ", "next step", "continue", "undo", "redo",
            "rinse ",
        )
        return command.startswith(starters)

    def _target_metadata(self, target: str) -> dict:
        apparatus = self.registry.match_apparatus(target)
        chemical = self.registry.match_chemical_alias(target)
        return {
            "normalized": normalize(target),
            "apparatus": apparatus.canonical if apparatus else None,
            "chemical": chemical.canonical if chemical else None,
        }
