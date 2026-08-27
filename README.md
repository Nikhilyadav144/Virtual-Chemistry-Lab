# ⚗ Virtual Chemistry Lab
### AI-Powered · Hand-Tracked · Interactive Simulations
**B.Tech Major Project — Computer Science**

---

## 📁 Folder Structure

```
virtual_chem_lab/
│
├── main.py                          ← Entry point, MainWindow, page router
│
├── requirements.txt                 ← pip dependencies
│
├── data/
│   └── experiments.py               ← All curriculum data (5 classes × 2 experiments)
│
├── utils/
│   ├── theme.py                     ← Design tokens (colours, fonts, spacing)
│   └── widgets.py                   ← Reusable PyQt5 widgets (NavBar, GlowButton, etc.)
│
└── pages/
    ├── splash_page.py               ← Animated loading splash screen
    ├── home_page.py                 ← Welcome / landing screen
    ├── class_page.py                ← Class selection (8–12) with cards
    ├── experiment_list_page.py      ← Scrollable list of experiments per class
    ├── experiment_details_page.py   ← Full experiment details + Start button
    └── simulation_page.py           ← Webcam + hand tracking + particle simulation
```

---

## 🏗️ Architecture

```
MainWindow (QMainWindow, Fullscreen)
└── QStackedWidget  ← page router (like a browser history)
      ├── SplashPage           (static, shown once)
      ├── HomePage             (static)
      ├── ClassPage            (static)
      ├── ExperimentListPage   (rebuilt per class selection)
      ├── ExperimentDetailsPage (rebuilt per experiment)
      └── SimulationPage       (rebuilt per experiment)
```

**Key design decisions:**
- **QStackedWidget** acts as a single-page application router — only one page visible at a time.
- Pages are **decoupled** — they never import each other. Navigation is done via callbacks passed from MainWindow.
- The simulation runs in a **QThread (SimWorker)** so the GUI never freezes.
- The simulation emits frames as numpy arrays; the main thread converts them to QPixmap and renders them.

---

## 🖥️ GUI Framework Choice: PyQt5

| Framework | Verdict |
|-----------|---------|
| **PyQt5** ✅ | Best choice — native look, full widget set, excellent theming via QSS, QThread for background tasks, QStackedWidget for page routing |
| PySide6   | Nearly identical to PyQt5 but newer; compatible code |
| Tkinter   | Too basic — poor theming, no real layout engine |
| Dear PyGui | Good for tools but not educational apps |

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
```

**Keyboard shortcuts:**
- `ESC` → Exit application
- `F11` → Toggle fullscreen / windowed mode
- `Ctrl+Q` → Quit

---

## 🖐 Simulation Controls

| Gesture | Action |
|---------|--------|
| **Pinch** (thumb + index) | Grab nearest apparatus |
| **Hold pinch + move** | Carry apparatus around |
| **Release pinch** | Drop apparatus |
| **Hold dropper** | Continuously pour liquid |
| **Bunsen Burner** | Emits fire particles automatically |

## 🎙 Atom Voice Assistant

Atom is a secondary control layer. Hand gestures remain the main system for
physical manipulation such as dragging, grabbing, positioning, tilting, and
pouring apparatus.

When Atom hears a valid wake phrase or command, a floating assistant overlay
appears on top of the lab, similar to a desktop voice assistant.

Voice commands are routed like this:

```
SpeechEngine / typed command
→ WakeWordDetector
→ CommandParser + CommandRegistry
→ VoiceActionRouter
→ MainWindow or SimulationPage actions
```

Examples:

```text
Hey Atom, open class 9
Atom, open titration experiment
Hey Atom, add burette
Atom, select hydrochloric acid
Hey Atom, add phenolphthalein
Atom, guided mode
Hey Atom, heat this
Atom, explain neutralization
```

Offline speech recognition uses Vosk. Install a local English model and either
set `ATOM_VOSK_MODEL` or place it at `models/vosk-model-small-en-us-0.15`.
When the model or microphone package is unavailable, Atom automatically remains
usable through the text command box in the bottom assistant panel.

---

## ⚗ Experiments Included

| Class | Experiment 1 | Experiment 2 |
|-------|-------------|-------------|
| 8 | Separation of Mixtures | Magnetic Separation |
| 9 | Preparation of Hydrogen | pH of Solutions |
| 10 | Electrolysis of Water | Reactivity Series of Metals |
| 11 | Flame Test for Metal Ions | Determination of Melting Point |
| 12 | Acid-Base Titration | Paper Chromatography |

---

## 🔧 How to Add More Experiments

Edit `data/experiments.py` and add a new dict to the appropriate class list:

```python
{
    "id":        "c9_e3",               # unique ID
    "name":      "Crystal Formation",
    "aim":       "To grow crystals of copper sulphate from a saturated solution.",
    "theory":    "...",
    "apparatus": ["Beaker", "Stirring Rod", ...],
    "chemicals": ["Copper Sulphate", "Distilled Water"],
    "steps":     ["Step 1...", "Step 2...", ...],
    "safety":    ["Safety note 1...", ...],
    "simulation": {
        "tools":   ["BEAKER", "BUNSEN"],
        "prefill": {"WATER": 60},
        "reactions": ["heating"],
        "theme_color": "#00BFFF",
    },
}
```

No changes needed anywhere else — the UI reads from the data automatically.

---

## 📦 Dependencies

```
PyQt5       — GUI framework
opencv-python — webcam capture, image processing, drawing
mediapipe   — real-time hand landmark detection
numpy       — frame buffer manipulation
```
