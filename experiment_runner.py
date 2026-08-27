"""
simulation/experiment_runner.py
"""

import cv2
import numpy as np
import math
import random
import time

from PyQt5.QtCore import QThread, pyqtSignal

from data.experiments            import get_chemical_profile
from simulation.experiment_framework import build_experiment_config
from simulation.experiment_validator import ExperimentValidator
from simulation.gesture         import GestureController
from simulation.apparatus       import ContainerApparatus, ApparatusRegistry, LIQUID_BGR
from simulation.fluid_engine    import FluidEngine
from simulation.heating_engine  import HeatingEngine
from simulation.lab_actions     import LabAction, LabActionType
from simulation.particle_system import ParticleSystem
from simulation.reaction_engine import ReactionEngine
from simulation.step_manager    import StepManager
from simulation.titration_engine import TitrationEngine
from simulation.virtual_lab_engine import VirtualLabEngine


class ExperimentRunner(QThread):

    frame_ready   = pyqtSignal(np.ndarray)
    status_update = pyqtSignal(str)
    step_update   = pyqtSignal(str, str)
    ml_update     = pyqtSignal(str)

    def __init__(self, exp_data, fw, fh, mode="guided"):
        super().__init__()
        self.exp_data  = exp_data
        self.fw        = fw
        self.fh        = fh
        self.mode      = mode
        self._stop     = False
        self.config    = build_experiment_config(exp_data)
        self.validator = ExperimentValidator()
        self.lab       = VirtualLabEngine(exp_data, fw, fh, mode=mode)

        self.gesture   = GestureController()
        self.psys      = ParticleSystem()
        self.fluid     = FluidEngine()
        self.heating   = HeatingEngine()
        self.reactions = self.lab.reactions
        self.titration = TitrationEngine(self.config.titration)

        self.step_mgr = StepManager.from_config(self.config, mode=mode)

        self.apparatus_list   = self.lab.build_workspace().apparatus
        self.selected_liquid  = "water"
        self.selected_ml      = 20.0
        self._mouse_dragging  = False
        self._mouse_drag_item = None
        self._mouse_tilting   = False
        self._mouse_tilt_item = None
        self._mouse_offset    = (0, 0)
        self._fire_timer      = 0
        self._hand_pour_frames = {}
        self._swirl_tracks = {}
        self._last_tick = time.perf_counter()
        self._undo_stack      = []
        self._redo_stack      = []
        self._workspace_announced = False

    def _snapshot(self):
        return [a.to_dict() for a in self.apparatus_list]

    def _restore_snapshot(self, snapshot):
        self.apparatus_list = [ContainerApparatus.from_dict(item) for item in snapshot]
        self._mouse_drag_item = None
        self._mouse_dragging = False
        self._mouse_tilt_item = None
        self._mouse_tilting = False
        self._hand_pour_frames.clear()
        self._swirl_tracks.clear()
        self._emit_ml_update()

    def _push_history(self):
        self._undo_stack.append(self._snapshot())
        if len(self._undo_stack) > 30:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def add_apparatus(self, atype):
        self._push_history()
        n   = len(self.apparatus_list)
        gap = self.fw // 8
        x   = min(gap + n * gap, self.fw - 100)
        a   = ApparatusRegistry.create(atype, x, self.fh - 30, self.fw, self.fh)
        self.apparatus_list.append(a)
        self.lab.workspace.apparatus = self.apparatus_list
        a.state.transition("empty")
        self.step_mgr.notify_apparatus_selected(atype)
        self.status_update.emit(f"✅  {atype.title()} added to desk")
        return a

    def fill_apparatus(self, apparatus, liquid_name, amount_ml, display_name=None):
        self._push_history()
        profile = get_chemical_profile(display_name or liquid_name)
        apparatus.add_liquid(
            profile["category"],
            amount_ml,
            display_name=profile["display_name"],
            color=profile["color_bgr"],
        )
        self.step_mgr.notify_liquid_added(liquid_name, amount_ml, apparatus.atype)
        apparatus.state.transition("filled", volume_ml=apparatus.mixture.volume_ml)
        self.status_update.emit(
            f"✅  Added {amount_ml:.0f} ml {profile['display_name']} to {apparatus.atype}")
        self._handle_reactions(apparatus)
        self._emit_ml_update()

    def set_selected_liquid(self, name):
        self.selected_liquid = name

    def set_selected_ml(self, ml):
        self.selected_ml = ml

    def set_mode(self, mode):
        self.mode = mode
        self.step_mgr.mode = mode

    def rinse_apparatus(self, apparatus, liquid_name=None, display_name=None):
        self._push_history()
        apparatus.rinse()
        apparatus.state.transition("empty")
        if display_name:
            self.status_update.emit(
                f"🚿  Rinsed {apparatus.atype} with {display_name}"
            )
        else:
            self.status_update.emit(f"🚿  Rinsed {apparatus.atype}")
        self._emit_ml_update()

    def remove_apparatus(self, apparatus):
        if apparatus not in self.apparatus_list:
            return False
        self._push_history()
        if self._mouse_drag_item is apparatus:
            self._mouse_drag_item = None
            self._mouse_dragging = False
        if self._mouse_tilt_item is apparatus:
            self._mouse_tilt_item = None
            self._mouse_tilting = False
        self.apparatus_list = [a for a in self.apparatus_list if a is not apparatus]
        self.lab.workspace.apparatus = self.apparatus_list
        self.status_update.emit(f"🗑  Removed {apparatus.atype}")
        self._emit_ml_update()
        return True

    def undo(self):
        if not self._undo_stack:
            self.status_update.emit("Nothing to undo")
            return False
        self._redo_stack.append(self._snapshot())
        snapshot = self._undo_stack.pop()
        self._restore_snapshot(snapshot)
        self.status_update.emit("↶ Undo applied")
        return True

    def redo(self):
        if not self._redo_stack:
            self.status_update.emit("Nothing to redo")
            return False
        self._undo_stack.append(self._snapshot())
        snapshot = self._redo_stack.pop()
        self._restore_snapshot(snapshot)
        self.status_update.emit("↷ Redo applied")
        return True

    def next_step(self):
        if self.mode == "guided":
            self.step_mgr.complete_current_step()

    def set_step_index(self, index):
        self.step_mgr.set_current_step(index)

    def mouse_press(self, mx, my):
        for a in reversed(self.apparatus_list):
            if a.near_enough(mx, my):
                self._mouse_drag_item = a
                self._mouse_offset    = (a.x - mx, a.y - my)
                a.grabbed             = "Mouse"
                self._mouse_dragging  = True
                break

    def mouse_move(self, mx, my):
        if self._mouse_dragging and self._mouse_drag_item:
            a   = self._mouse_drag_item
            a.x = mx + self._mouse_offset[0]
            a.y = my + self._mouse_offset[1]
            a.x = max(a.w//2 + 5, min(self.fw - a.w//2 - 5, a.x))
            a.y = max(a.h + 5,    min(self.fh - 5, a.y))
        if self._mouse_tilting and self._mouse_tilt_item:
            self._tilt_toward(self._mouse_tilt_item, mx)

    def mouse_release(self, mx, my):
        if self._mouse_drag_item:
            self._mouse_drag_item.grabbed = None
            self._mouse_drag_item         = None
        self._mouse_dragging = False

    def mouse_tilt_press(self, mx, my):
        for a in reversed(self.apparatus_list):
            if a.near_enough(mx, my):
                self._mouse_tilt_item = a
                self._mouse_tilting = True
                a.grabbed = "Tilt"
                self._tilt_toward_nearest_target(a)
                if a.liquid.is_empty():
                    self.status_update.emit(f"Add liquid to {a.atype} before pouring")
                else:
                    self.status_update.emit("Hold right-click to tilt and pour")
                break

    def mouse_tilt_move(self, mx, my):
        if self._mouse_tilting and self._mouse_tilt_item:
            a = self._mouse_tilt_item
            a.x = max(a.w//2 + 5, min(self.fw - a.w//2 - 5, float(mx)))
            a.y = max(a.h + 5,    min(self.fh - 5, float(my) + a.h * 0.35))
            self._tilt_toward_nearest_target(a)

    def mouse_tilt_release(self, mx, my):
        if self._mouse_tilt_item:
            self._mouse_tilt_item.tilt_angle = 0.0
            self._mouse_tilt_item.grabbed = None
            self._mouse_tilt_item = None
        self._mouse_tilting = False

    def stop(self):
        self._stop = True

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.status_update.emit("⚠  Webcam not found — using mouse controls")
            self._run_no_camera()
            return

        while not self._stop:
            dt = self._tick_dt()
            ret, frame = cap.read()
            if not ret:
                continue

            frame   = cv2.flip(frame, 1)
            frame   = cv2.resize(frame, (self.fw, self.fh),
                                 interpolation=cv2.INTER_LINEAR)
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb     = self.gesture.update(rgb, self.fw, self.fh)
            frame   = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            self._process_gestures(dt)
            self._update_engines(dt)
            self._draw_scene(frame)

            out = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_ready.emit(out)

            step = self.step_mgr.current_step()
            if step:
                self.step_update.emit(
                    step.description(),
                    self.step_mgr.progress_text()
                )
            if self.step_mgr.message:
                self.status_update.emit(self.step_mgr.message)
                self.step_mgr.message = ""

        cap.release()
        self.gesture.close()

    def _run_no_camera(self):
        while not self._stop:
            dt = self._tick_dt()
            frame = np.zeros((self.fh, self.fw, 3), dtype=np.uint8)
            cv2.putText(frame,
                        "No camera detected — use mouse to drag apparatus",
                        (40, self.fh // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (100, 200, 255), 2)
            self._process_mouse_tilt(dt)
            self._update_engines(dt)
            self._draw_scene(frame)
            out = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_ready.emit(out)
            self.msleep(33)

    def _tick_dt(self):
        now = time.perf_counter()
        dt = max(0.001, min(0.06, now - self._last_tick))
        self._last_tick = now
        return dt

    def _update_engines(self, dt):
        if not self._workspace_announced and self.lab.workspace.observations:
            self.status_update.emit(self.lab.workspace.observations[-1])
            self._workspace_announced = True
        for apparatus in self.apparatus_list:
            self.fluid.update_surface(apparatus, dt)
        titration_message = self.titration.observe(self.apparatus_list)
        if titration_message:
            self.status_update.emit(titration_message)

    def _process_gestures(self, dt):
        for hand in self.gesture.hands.values():
            if not hand.pinching:
                if hand.grabbed_id is not None:
                    self._hand_pour_frames.pop(hand.grabbed_id, None)
                    hand.grabbed_id = None
                    for a in self.apparatus_list:
                        if a.grabbed == hand.label:
                            a.tilt_angle = 0.0
                            a.grabbed = None
                continue

            if hand.grabbed_id is None:
                for a in self.apparatus_list:
                    if a.grabbed is None and a.near_enough(hand.px, hand.py):
                        a.grabbed       = hand.label
                        hand.grabbed_id = id(a)
                        break

            for a in self.apparatus_list:
                if a.grabbed == hand.label:
                    a.x = float(hand.px)
                    a.y = float(hand.py) + a.h * 0.5
                    a.x = max(a.w//2 + 5, min(self.fw - a.w//2 - 5, a.x))
                    a.y = max(a.h + 5,    min(self.fh - 5, a.y))
                    self._track_swirl(a, hand.px, hand.py)
                    self._process_hand_hover_pour(a, dt)
                    break

        for a in self.apparatus_list:
            if a.grabbed is None and a.y < a.desk_y:
                a.y = min(a.y + 14, a.desk_y)
                a.tilt_angle *= 0.72

        self._process_mouse_tilt(dt)

    def _track_swirl(self, apparatus, px, py):
        if apparatus.atype not in ("flask", "test_tube", "beaker"):
            return
        track = self._swirl_tracks.setdefault(id(apparatus), [])
        track.append((float(px), float(py), time.perf_counter()))
        if len(track) > 18:
            del track[:-18]
        if self._is_circular_motion(track):
            action = LabAction(
                LabActionType.SWIRL,
                target_id=getattr(apparatus, "object_id", ""),
                metadata={"source": "gesture"},
            )
            self.lab.execute(action)
            self.step_mgr.notify_reaction("mixing")
            track.clear()

    def _is_circular_motion(self, track):
        if len(track) < 10:
            return False
        xs = [p[0] for p in track]
        ys = [p[1] for p in track]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        radii = [math.hypot(x - cx, y - cy) for x, y, _t in track]
        avg_radius = sum(radii) / len(radii)
        if avg_radius < 18:
            return False
        angles = [math.atan2(y - cy, x - cx) for x, y, _t in track]
        total_turn = 0.0
        for prev, cur in zip(angles, angles[1:]):
            delta = cur - prev
            while delta > math.pi:
                delta -= 2 * math.pi
            while delta < -math.pi:
                delta += 2 * math.pi
            total_turn += delta
        duration = track[-1][2] - track[0][2]
        return abs(total_turn) > math.pi * 1.35 and duration <= 2.5

    def _process_mouse_tilt(self, dt):
        if self._mouse_tilting and self._mouse_tilt_item:
            self._try_pour(self._mouse_tilt_item, dt)

    def _process_hand_hover_pour(self, source, dt):
        target = self._pour_target(source)
        can_pour = target is not None and not source.liquid.is_empty()
        if not can_pour:
            self._hand_pour_frames.pop(id(source), None)
            source.tilt_angle *= 0.72
            return

        frames = self._hand_pour_frames.get(id(source), 0) + 1
        self._hand_pour_frames[id(source)] = frames
        self._tilt_toward(source, target.x)
        if frames >= 5:
            self._try_pour(source, dt)

    def _tilt_toward(self, source, target_x):
        source.tilt_angle = -38.0 if target_x >= source.x else 38.0

    def _tilt_toward_nearest_target(self, source):
        dest = self._pour_target(source)
        if dest:
            self._tilt_toward(source, dest.x)
        else:
            source.tilt_angle = -38.0

    def _pour_target(self, source):
        candidates = []
        for dest in self.apparatus_list:
            if dest is source:
                continue
            if dest.interior_bounds() is None:
                continue
            catch_width = max(dest.w * 1.4, source.w * 0.8, 90)
            if dest.y > source.y and abs(dest.x - source.x) < catch_width:
                candidates.append(dest)
        if not candidates:
            return None
        return min(candidates, key=lambda dest: abs(dest.x - source.x) + abs(dest.y - source.y) * 0.35)

    def _try_pour(self, source, dt):
        dest = self._pour_target(source)
        if dest is None:
            return
        flow = self.fluid.flow_volume(source, dt)
        liquid_portion, poured = source.pour_out(flow.volume_ml)
        if poured > 0:
            for chemical in liquid_portion.contents:
                dest.mixture.add(chemical)
            lf, rt, bot, top_open = dest.interior_bounds()
            px = max(lf + 4, min(rt - 4, int(source.pour_spout()[0])))
            py = max(top_open + 4, min(bot - 8, top_open + 8))
            for _ in range(max(1, flow.drops)):
                self.psys.emit_pour(
                    px, py,
                    liquid_portion.color,
                    bounds=(lf, rt, bot, top_open),
                )
            self._handle_reactions(dest)
            source.state.transition("pouring" if source.mixture.volume_ml > 0 else "empty")
            dest.state.transition("receiving_liquid")
            self._emit_ml_update()

    def _handle_reactions(self, apparatus):
        events = self.lab.apply_reactions(apparatus)
        for event in events:
            cx = int(apparatus.x)
            cy = int(apparatus.y - apparatus.h * 0.3)
            self.psys.emit_reaction_event(cx, cy, event)
            self.step_mgr.notify_reaction(event.type)
            if event.message:
                self.status_update.emit(f"Reaction: {event.message}")

    def _emit_bunsen_fire(self, a):
        self._fire_timer += 1
        if self._fire_timer % 2 == 0:
            self.psys.emit(int(a.x), a.top() + 10,
                           (0, 80, 255), n=2, style="fire")
            for dest in self.apparatus_list:
                if dest is a:
                    continue
                if dest.y < a.y and abs(dest.x - a.x) < dest.w:
                    self.heating.heat(dest, 1.0 / 30.0, "medium")
                    self.step_mgr.notify_heat(dest.atype)

    def _draw_scene(self, frame):
        for a in self.apparatus_list:
            if a.atype == "bunsen":
                self._emit_bunsen_fire(a)
            a.draw(frame)

        for hand in self.gesture.hands.values():
            if hand.pinching:
                col = (0, 255, 80) if hand.label == "Right" else (0, 200, 255)
                cv2.circle(frame, (hand.px, hand.py), 18, (0, 255, 255), 3)
                cv2.circle(frame, (hand.px, hand.py),
                           ContainerApparatus.GRAB_RADIUS, col, 1)

        self.psys.update_and_draw(frame, self.apparatus_list, self.fh, self.fw)

    def _emit_ml_update(self):
        lines = []
        for a in self.apparatus_list:
            if not a.liquid.is_empty():
                lines.append(
                    f"{a.atype.title()}: "
                    f"{a.liquid.amount_ml:.0f} ml {a.liquid.display_name} "
                    f"(pH {a.mixture.pH:.1f}, {a.mixture.temperature:.0f}°C)"
                )
        titration = self.titration.status_text()
        if titration:
            lines.append(titration)
        self.ml_update.emit("  |  ".join(lines) if lines else "")
