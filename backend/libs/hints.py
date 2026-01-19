import os
import json
import re

HINTS = {}

INPUT_KIND_MAP = {
    "camera": {
        "windows": "dshow_input",
        "linux": "v4l2_input",
        "apple": "av_capture_input",
        "unknown": "dshow_input"
    },
    "microphone": {
        "windows": "wasapi_input_capture",
        "linux": "pulse_input_capture",
        "apple": "coreaudio_input_capture",
        "unknown": "wasapi_input_capture"
    }
}

SKIP_NAMES = {"DefaultCamera", "DefaultCamera1", "DefaultCamera2", "DefaultMicrophone"}

def load_hints(path: str):
    global HINTS
    try:
        with open(path, "r", encoding="utf-8") as f:
            HINTS = json.load(f)
        HINTS["manufacturers"] = [m.lower() for m in HINTS.get("manufacturers", [])]
        HINTS["aliases"] = {k.lower(): v for k, v in HINTS.get("aliases", {}).items()}
        HINTS["name_hints"] = [s.lower() for s in HINTS.get("name_hints", [])]
        HINTS["id_hints"] = [s.lower() for s in HINTS.get("id_hints", [])]
        HINTS["mobile_apps"] = [s.lower() for s in HINTS.get("mobile_apps", [])]
        HINTS["pc_webcams"] = [s.lower() for s in HINTS.get("pc_webcams", [])]
    except Exception:
        HINTS = {
            "manufacturers": [], "aliases": {}, "name_hints": [],
            "id_hints": [], "mobile_apps": [], "pc_webcams": []
        }

def normalize(s: str) -> str:
    return (s or "").strip().lower()

def guess_platform(kind: str) -> str:
    k = normalize(kind)
    if "dshow" in k: return "windows"
    if "v4l2" in k: return "linux"
    if "av_capture" in k or "coreaudio" in k: return "apple"
    if "wasapi" in k: return "windows"
    if "pulse" in k: return "linux"
    return "unknown"

def guess_source(name: str, device_id: str) -> str:
    n, d = normalize(name), normalize(device_id)
    if any(tag in d for tag in ["rtsp://", "rtmp://", "http://", "https://"]) or any(tag in d for tag in ["rtsp", "rtmp", "ipcam", "ip webcam"]):
        return "network"
    if any(tag in n for tag in HINTS.get("mobile_apps", [])) or any(tag in d for tag in HINTS.get("mobile_apps", [])):
        return "virtual_driver"
    if any(tag in d for tag in ["usb", "vid_", "pid_", "vendor", "product"]) or re.search(r"(vid|pid|usb)", d):
        return "usb"
    return "unknown"

def guess_manufacturer(name: str, device_id: str) -> str | None:
    n, d = normalize(name), normalize(device_id)

    for m in HINTS["manufacturers"]:
        if m in n or m in d:
            return m.capitalize()

    for alias, brand in HINTS["aliases"].items():
        if alias in n or alias in d:
            return brand

    if any(tag in (n + " " + d) for tag in ["iphone", "ipad", "facetime"]):
        return "Apple"

    return None

def is_mobile_camera(kind: str, name: str, device_id: str) -> tuple[bool, list[str]]:
    hints = []
    n, d, k = normalize(name), normalize(device_id), normalize(kind)

    if any(h in n for h in HINTS["name_hints"]):
        hints.append("name_hint")
    if any(h in d for h in HINTS["id_hints"]):
        hints.append("id_hint")
    if any(app in n for app in HINTS["mobile_apps"]):
        hints.append("mobile_app")
    if any(tag in d for tag in ["rtsp", "http", "ipcam"]):
        hints.append("network")

    manufacturer = guess_manufacturer(name, device_id)
    if manufacturer:
        hints.append(f"manufacturer:{manufacturer}")

    if any(pc in n for pc in HINTS["pc_webcams"]):
        hints.append("pc_webcam_brand")

    if any(h in n for h in ["integrated", "built-in", "facetime hd camera"]):
        hints.append("integrated_laptop")

    positive = any(h in hints for h in ["name_hint", "id_hint", "mobile_app", "network", "manufacturer:Apple"])
    negative = "integrated_laptop" in hints or "pc_webcam_brand" in hints
    return (positive and not negative, hints)
