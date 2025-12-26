import psutil
import subprocess
import os
import json
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

from obs_actions import ObsActions

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

try:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)
except Exception as e:
    traceback.print_exc()
    settings = {}

def ensure_obs_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'obs64.exe' in proc.info['name'].lower():
            return True

    obs_path = settings.get("obs", {}).get("path", "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe")
    obs_dir = settings.get("obs", {}).get("dir", "C:\\Program Files\\obs-studio\\bin\\64bit")

    if os.path.exists(obs_path):
        subprocess.Popen([obs_path], cwd=obs_dir)
        return True

    return False

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    traceback.print_exc()
    config = {}

ensure_obs_running()

try:
    ws_password = os.getenv("WS_PASSWORD")

    obs = ObsActions(
        host=config.get("ws_host", "127.0.0.1"),
        port=config.get("ws_port", 4455),
        password=ws_password
    )
except Exception as e:
    traceback.print_exc()
    obs = None

def write_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        traceback.print_exc()

@app.before_request
def check_obs():
    ensure_obs_running()

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(config)

@app.route("/api/config", methods=["PUT"])
def update_config():
    data = request.get_json(force=True)
    write_config(data)
    return jsonify({"ok": True})

@app.route("/api/apply", methods=["POST"])
def apply_actions():
    if obs is None:
        return jsonify({"status": "error", "message": "OBS клиент не инициализирован"}), 500
    try:
        if config.get("allow_delete_scenes", True):
            obs.clear_scenes()

        main_scene = config.get("main_scene_name", "SafeScene")
        obs.create_main_scene(main_scene)

        obs.add_camera(
            scene_name=main_scene,
            input_name=config.get("camera_source_name", "Webcam1"),
            input_kind=config.get("camera_input_kind", "dshow_input"),
            device_id=config.get("camera_device_id", "default")
        )

        obs.add_microphone(
            scene_name=main_scene,
            input_name=config.get("mic_source_name", "Mic1"),
            input_kind=config.get("mic_input_kind", "wasapi_input_capture"),
            device_id=config.get("mic_device_id", "default")
        )

        return jsonify({"status": "ok", "message": "Сцены и источники обновлены"})
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/devices", methods=["GET"])
def get_devices():
    if obs is None:
        return jsonify({"status": "error", "message": "OBS клиент не инициализирован"}), 500
    try:
        inputs = obs.ws.get_input_list().inputs
        cameras, microphones = [], []
        for inp in inputs:
            kind = inp["inputKind"]
            name = inp["inputName"]
            if "dshow" in kind or "v4l2" in kind or "av_capture" in kind:
                cameras.append({"name": name, "kind": kind})
            elif "wasapi" in kind or "pulse" in kind or "coreaudio" in kind:
                microphones.append({"name": name, "kind": kind})
        return jsonify({"status": "ok", "cameras": cameras, "microphones": microphones})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
