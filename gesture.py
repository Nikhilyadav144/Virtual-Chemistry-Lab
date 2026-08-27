"""
simulation/gesture.py
─────────────────────
Gesture controller with multiple fallback backends.

Priority order:
1. Legacy MediaPipe Solutions API
2. OpenCV Zoo palm + hand-pose models
3. Newer MediaPipe Tasks API
"""

import math
from pathlib import Path

import cv2
import mediapipe as mp


mp_hands = getattr(getattr(mp, "solutions", None), "hands", None)

try:
    from simulation.opencv_hand.mp_palmdet import MPPalmDet
    from simulation.opencv_hand.mp_handpose import MPHandPose
except Exception:
    MPPalmDet = None
    MPHandPose = None

try:
    from mediapipe.tasks.python import vision as mp_vision
    from mediapipe.tasks.python.core.base_options import BaseOptions
    from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
except Exception:
    mp_vision = None
    BaseOptions = None
    HandLandmark = None


BASE_DIR = Path(__file__).resolve().parent
TASK_MODEL_PATH = BASE_DIR / "hand_landmarker.task"
PALM_MODEL_PATH = BASE_DIR / "opencv_hand" / "palm_detection_mediapipe_2023feb.onnx"
HANDPOSE_MODEL_PATH = BASE_DIR / "opencv_hand" / "handpose_estimation_mediapipe_2023feb.onnx"


class HandState:
    IDLE = "idle"
    HOVERING = "hovering"
    GRABBED = "grabbed"


class _NormPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class _LandmarkEnum:
    WRIST = 0
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    PINKY_MCP = 17


HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
]


class TrackedHand:
    """Tracks one hand's position, pinch state, and grab history."""

    PINCH_RATIO_THRESHOLD = 0.58
    RELEASE_RATIO_THRESHOLD = 0.78
    SMOOTH_FACTOR = 0.4
    HOLD_MISSING_FRAMES = 8

    def __init__(self, label):
        self.label = label
        self.state = HandState.IDLE
        self.px = 0
        self.py = 0
        self.raw_px = 0
        self.raw_py = 0
        self.pinching = False
        self.grabbed_id = None
        self._frames_pinching = 0
        self._frames_releasing = 0
        self._frames_missing = 0
        self.is_pouring = False
        self.pour_direction = 0
        self.pour_strength = 0.0
        self._roll_score = 0.0
        self._frames_pouring = 0

    def update(self, landmarks, fw, fh, hand_landmark_enum):
        tx = landmarks[hand_landmark_enum.THUMB_TIP].x
        ty = landmarks[hand_landmark_enum.THUMB_TIP].y
        ix = landmarks[hand_landmark_enum.INDEX_FINGER_TIP].x
        iy = landmarks[hand_landmark_enum.INDEX_FINGER_TIP].y

        new_px = int(((tx + ix) / 2) * fw)
        new_py = int(((ty + iy) / 2) * fh)

        if self.state == HandState.GRABBED:
            self.px = int(self.px * self.SMOOTH_FACTOR +
                          new_px * (1 - self.SMOOTH_FACTOR))
            self.py = int(self.py * self.SMOOTH_FACTOR +
                          new_py * (1 - self.SMOOTH_FACTOR))
        else:
            self.px = new_px
            self.py = new_py

        self.raw_px = new_px
        self.raw_py = new_py
        self._frames_missing = 0

        pinch_dist = math.hypot(tx - ix, ty - iy)
        palm_width = math.hypot(
            landmarks[hand_landmark_enum.INDEX_FINGER_MCP].x -
            landmarks[hand_landmark_enum.PINKY_MCP].x,
            landmarks[hand_landmark_enum.INDEX_FINGER_MCP].y -
            landmarks[hand_landmark_enum.PINKY_MCP].y,
        )
        palm_height = math.hypot(
            landmarks[hand_landmark_enum.WRIST].x -
            landmarks[hand_landmark_enum.MIDDLE_FINGER_MCP].x,
            landmarks[hand_landmark_enum.WRIST].y -
            landmarks[hand_landmark_enum.MIDDLE_FINGER_MCP].y,
        )
        reference_span = max(palm_width, palm_height, 0.04)
        pinch_ratio = pinch_dist / reference_span

        close_threshold = self.PINCH_RATIO_THRESHOLD
        release_threshold = self.RELEASE_RATIO_THRESHOLD
        if self.grabbed_id is not None:
            close_threshold += 0.06
            release_threshold += 0.08

        if pinch_ratio < close_threshold:
            self._frames_pinching += 1
            self._frames_releasing = 0
        elif pinch_ratio > release_threshold:
            self._frames_releasing += 1
            self._frames_pinching = 0

        if self._frames_pinching >= 1:
            self.pinching = True
        release_frames = 5 if self.grabbed_id is not None else 3
        if self._frames_releasing >= release_frames:
            self.pinching = False

        wrist = landmarks[hand_landmark_enum.WRIST]
        middle_mcp = landmarks[hand_landmark_enum.MIDDLE_FINGER_MCP]
        index_mcp = landmarks[hand_landmark_enum.INDEX_FINGER_MCP]
        pinky_mcp = landmarks[hand_landmark_enum.PINKY_MCP]

        palm_dx = middle_mcp.x - wrist.x
        palm_dy = middle_mcp.y - wrist.y
        palm_len = max(math.hypot(palm_dx, palm_dy), 0.04)
        palm_roll = palm_dx / palm_len

        knuckle_roll = (index_mcp.y - pinky_mcp.y) / max(palm_width, 0.04)
        raw_roll = max(-1.0, min(1.0, palm_roll * 0.75 + knuckle_roll * 0.25))
        self._roll_score = self._roll_score * 0.45 + raw_roll * 0.55

        roll_threshold = 0.18
        release_roll_threshold = 0.10
        if abs(self._roll_score) > roll_threshold:
            self._frames_pouring += 1
            self.pour_direction = 1 if self._roll_score > 0 else -1
            self.pour_strength = min(
                1.0,
                (abs(self._roll_score) - release_roll_threshold) / 0.42
            )
        elif abs(self._roll_score) < release_roll_threshold:
            self._frames_pouring = 0
            self.pour_direction = 0
            self.pour_strength = 0.0

        self.is_pouring = self._frames_pouring >= 2

    def mark_missing(self):
        self._frames_missing += 1
        if self.grabbed_id is not None and self._frames_missing <= self.HOLD_MISSING_FRAMES:
            return
        self.clear()

    def clear(self):
        self.pinching = False
        self._frames_pinching = 0
        self._frames_releasing = 0
        self._frames_missing = 0
        self.is_pouring = False
        self.pour_direction = 0
        self.pour_strength = 0.0
        self._roll_score = 0.0
        self._frames_pouring = 0


class GestureController:
    def __init__(self):
        self.detector = None
        self.mp_draw = None
        self._mode = "none"
        self._seen = set()
        self._task_timestamp = 0
        self._task_connections = []
        self._task_landmark_enum = None
        self._landmark_enum = _LandmarkEnum
        self._palm_detector = None
        self._handpose_detector = None

        self.hands = {
            "Left": TrackedHand("Left"),
            "Right": TrackedHand("Right"),
        }

        self._init_solutions()
        if self.detector is None:
            self._init_opencv()
        if self.detector is None:
            self._init_tasks()

    def _init_solutions(self):
        if mp_hands is None:
            return
        try:
            self._mode = "solutions"
            self.detector = mp_hands.Hands(
                min_detection_confidence=0.65,
                min_tracking_confidence=0.65,
                max_num_hands=2,
                model_complexity=0,
            )
            self.mp_draw = mp.solutions.drawing_utils
            self._landmark_enum = mp_hands.HandLandmark
        except Exception:
            self.detector = None
            self._mode = "none"

    def _init_opencv(self):
        if MPPalmDet is None or MPHandPose is None:
            return
        if not PALM_MODEL_PATH.exists() or not HANDPOSE_MODEL_PATH.exists():
            return
        try:
            self._palm_detector = MPPalmDet(str(PALM_MODEL_PATH))
            self._handpose_detector = MPHandPose(str(HANDPOSE_MODEL_PATH))
            self.detector = self._palm_detector
            self._mode = "opencv"
        except Exception:
            self._palm_detector = None
            self._handpose_detector = None
            self.detector = None
            self._mode = "none"

    def _init_tasks(self):
        if mp_vision is None or BaseOptions is None or not TASK_MODEL_PATH.exists():
            return
        try:
            options = mp_vision.HandLandmarkerOptions(
                base_options=BaseOptions(
                    model_asset_path=str(TASK_MODEL_PATH),
                    delegate=BaseOptions.Delegate.CPU,
                ),
                running_mode=mp_vision.RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=0.65,
                min_hand_presence_confidence=0.65,
                min_tracking_confidence=0.65,
            )
            self.detector = mp_vision.HandLandmarker.create_from_options(options)
            self._mode = "tasks"
            self._task_connections = mp_vision.HandLandmarksConnections.HAND_CONNECTIONS
            self._task_landmark_enum = HandLandmark
        except Exception:
            self.detector = None
            self._mode = "none"

    @property
    def available(self):
        return self.detector is not None

    def update(self, rgb_frame, fw, fh):
        if self._mode == "solutions":
            return self._update_solutions(rgb_frame, fw, fh)
        if self._mode == "opencv":
            return self._update_opencv(rgb_frame, fw, fh)
        if self._mode == "tasks":
            return self._update_tasks(rgb_frame, fw, fh)

        for hand in self.hands.values():
            hand.clear()
        return rgb_frame

    def _update_solutions(self, rgb_frame, fw, fh):
        results = self.detector.process(rgb_frame)
        self._seen = set()

        if results.multi_hand_landmarks and results.multi_handedness:
            for lm, hd in zip(results.multi_hand_landmarks,
                               results.multi_handedness):
                raw = hd.classification[0].label
                label = "Right" if raw == "Left" else "Left"
                self._seen.add(label)
                self.hands[label].update(lm.landmark, fw, fh, self._landmark_enum)

                color = (0, 255, 80) if label == "Right" else (0, 200, 255)
                self.mp_draw.draw_landmarks(
                    rgb_frame,
                    lm,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=color, thickness=2, circle_radius=3),
                )

        for label in ("Left", "Right"):
            if label not in self._seen:
                self.hands[label].mark_missing()

        return rgb_frame

    def _update_opencv(self, rgb_frame, fw, fh):
        self._seen = set()
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        palms = self._palm_detector.infer(bgr_frame)
        if palms is None or len(palms) == 0:
            for label in ("Left", "Right"):
                self.hands[label].clear()
            return rgb_frame

        candidates = []
        for palm in palms[:2]:
            try:
                result = self._handpose_detector.infer(bgr_frame, palm)
            except Exception:
                continue
            if result is None:
                continue
            candidates.append(result)

        for result in candidates[:2]:
            landmarks_px = result[4:67].reshape(21, 3)
            handedness = result[130]
            raw = "Right" if handedness >= 0.5 else "Left"
            label = "Right" if raw == "Left" else "Left"
            landmarks = [
                _NormPoint(
                    float(point[0]) / max(fw, 1),
                    float(point[1]) / max(fh, 1),
                )
                for point in landmarks_px
            ]
            self._seen.add(label)
            self.hands[label].update(landmarks, fw, fh, self._landmark_enum)
            self._draw_opencv_landmarks(rgb_frame, landmarks_px, label)

        for label in ("Left", "Right"):
            if label not in self._seen:
                self.hands[label].mark_missing()

        return rgb_frame

    def _update_tasks(self, rgb_frame, fw, fh):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self._task_timestamp += 33
        result = self.detector.detect_for_video(image, self._task_timestamp)
        self._seen = set()

        for landmarks, handedness_list in zip(
            result.hand_landmarks, result.handedness
        ):
            raw = handedness_list[0].category_name
            label = "Right" if raw == "Left" else "Left"
            self._seen.add(label)
            self.hands[label].update(
                landmarks, fw, fh, self._task_landmark_enum
            )
            self._draw_task_landmarks(rgb_frame, landmarks, label)

        for label in ("Left", "Right"):
            if label not in self._seen:
                self.hands[label].mark_missing()

        return rgb_frame

    def _draw_opencv_landmarks(self, frame, landmarks_px, label):
        color = (0, 255, 80) if label == "Right" else (0, 200, 255)
        for start, end in HAND_CONNECTIONS:
            p1 = landmarks_px[start]
            p2 = landmarks_px[end]
            cv2.line(
                frame,
                (int(p1[0]), int(p1[1])),
                (int(p2[0]), int(p2[1])),
                color,
                2,
            )
        for point in landmarks_px:
            cv2.circle(frame, (int(point[0]), int(point[1])), 3, color, -1)

    def _draw_task_landmarks(self, frame, landmarks, label):
        color = (0, 255, 80) if label == "Right" else (0, 200, 255)
        h, w = frame.shape[:2]

        for conn in self._task_connections:
            p1 = landmarks[conn.start]
            p2 = landmarks[conn.end]
            cv2.line(
                frame,
                (int(p1.x * w), int(p1.y * h)),
                (int(p2.x * w), int(p2.y * h)),
                color,
                2,
            )

        for point in landmarks:
            cv2.circle(
                frame,
                (int(point.x * w), int(point.y * h)),
                3,
                color,
                -1,
            )

    def get_active_hands(self):
        return [h for h in self.hands.values() if h.pinching]

    def close(self):
        if self._mode == "solutions" and self.detector is not None:
            self.detector.close()
        if self._mode == "tasks" and self.detector is not None:
            self.detector.close()
