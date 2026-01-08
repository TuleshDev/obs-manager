import os
import json
import re

HINTS = {}

def load_hints(path: str):
    global HINTS

    try:
        with open(path, "r", encoding="utf-8") as f:
            HINTS = json.load(f)
        HINTS["manufacturers"] = [m.lower() for m in HINTS.get("manufacturers", [])]
        HINTS["aliases"] = {k.lower(): v for k, v in HINTS.get("aliases", {}).items()}
        HINTS["name_hints"] = [s.lower() for s in HINTS.get("name_hints", [])]
        HINTS["id_hints"] = [s.lower() for s in HINTS.get("id_hints", [])]
    except Exception as e:
        HINTS = {"manufacturers": [], "aliases": {}, "name_hints": [], "id_hints": []}

def normalize(s):
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
    if any(tag in d for tag in ["rtsp://", "rtmp://", "http://", "https://"]) or any(tag in d for tag in ["rtsp", "rtmp"]):
        return "network"
    if any(tag in n for tag in ["droidcam", "epoccam", "ivcam"]) or any(tag in d for tag in ["droidcam", "epoccam", "ivcam"]):
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

    source = guess_source(name, device_id)
    if source in ["network", "virtual_driver"]:
        hints.append(source)

    if "av_capture" in k and any(h in (n + " " + d) for h in ["iphone", "ipad", "ios", "facetime"]):
        hints.append("platform_apple_mobile")

    if any(h in n for h in ["integrated", "built-in", "facetime hd camera"]):
        hints.append("integrated_laptop")

    positive = any(h in hints for h in ["name_hint", "id_hint", "network", "virtual_driver", "platform_apple_mobile"])
    negative = "integrated_laptop" in hints
    return (positive and not negative, hints)
