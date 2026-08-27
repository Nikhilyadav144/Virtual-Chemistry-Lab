"""Command-line diagnostics for Atom voice setup."""

from __future__ import annotations

from pathlib import Path


MODEL_PATH = Path("models/vosk-model-small-en-us-0.15")


def main():
    ok = True

    try:
        import vosk
        print("vosk: ok")
    except Exception as exc:
        ok = False
        print(f"vosk: missing ({exc})")
        vosk = None

    try:
        import sounddevice as sd
        print("sounddevice: ok")
    except Exception as exc:
        ok = False
        print(f"sounddevice: missing ({exc})")
        sd = None

    if MODEL_PATH.is_dir():
        print(f"model: ok ({MODEL_PATH})")
        if vosk:
            try:
                vosk.SetLogLevel(-1)
                vosk.Model(str(MODEL_PATH))
                print("model load: ok")
            except Exception as exc:
                ok = False
                print(f"model load: failed ({exc})")
    else:
        ok = False
        print(f"model: missing ({MODEL_PATH})")

    if sd:
        try:
            devices = [
                device["name"] for device in sd.query_devices()
                if device.get("max_input_channels", 0) > 0
            ]
            if devices:
                print("microphone input: ok")
                for name in devices:
                    print(f"  - {name}")
            else:
                ok = False
                print("microphone input: none found")
                print("Fix: enable Microphone permission for the app/Terminal that runs Python.")
        except Exception as exc:
            ok = False
            print(f"microphone input: failed ({exc})")

    print("atom voice:", "ready" if ok else "not ready")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
