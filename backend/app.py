import os
import json
import shutil
import threading
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Student, Scenario
from models import student_scenario

from libs.hints import HINTS, INPUT_KIND_MAP, SKIP_NAMES, load_hints, guess_platform, guess_source, guess_manufacturer, is_mobile_camera, normalize
from libs.obs_actions import ObsActions, ObsNotRunningError, ObsConnectionError
from libs.obs_export_import import OBSExportImport

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "__settings__", "settings.json")
CONFIG_PATH = os.path.join(BASE_DIR, "__settings__", "config.json")
HINTS_PATH = os.path.join(BASE_DIR, "__settings__", "hints.json")

def get_global_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        traceback.print_exc()
        cfg = {}

    return cfg

def write_global_config(path, cfg):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        traceback.print_exc()

def get_scenario_config(path, scenario_name):
    cfg = {}

    scenario_path = os.path.join(path, "scenarios", scenario_name, "__settings__", "config.json")
    if os.path.exists(scenario_path):
        try:
            with open(scenario_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            traceback.print_exc()
            cfg = {}

    return cfg

def write_scenario_config(path, scenario_name, cfg, backup_dir=None):
    try:
        settings_dir = os.path.join(path, "scenarios", scenario_name, "__settings__")

        filename = os.path.join(backup_dir, "config.json") if backup_dir else "config.json"
        config_path = os.path.join(settings_dir, filename)

        if backup_dir:
            backup_path = os.path.join(settings_dir, backup_dir)
            os.makedirs(backup_path, exist_ok=True)

            for fname in ["scenario_template.json", "scenario.json"]:
                src = os.path.join(settings_dir, fname)
                dst = os.path.join(backup_path, fname)
                if os.path.exists(src):
                    shutil.copy2(src, dst)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        traceback.print_exc()

settings = get_global_config(SETTINGS_PATH)
db_password = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{settings["db"]['user']}:{db_password}@"
    f"{settings["db"]['host']}:{settings["db"]['port']}/{settings["db"]['database']}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

global_cfg = get_global_config(CONFIG_PATH)
load_hints(HINTS_PATH)
devices_lock = threading.Lock()

def get_obs_instance():
    return ObsActions.ensure_obs_ready(global_cfg, settings)

obs = None
get_obs_instance()

def make_stub(name="Нет устройства", input_kind="stub"):
    return {
        "device_id": "stub",
        "name": name,
        "inputKind": input_kind,
        "is_stub": True
    }

# @app.before_request
# def check_obs():
#     get_obs_instance()

@app.route("/api/config", methods=["GET"])
def get_config():
    global_cfg = get_global_config(CONFIG_PATH)

    scenario_cfg = {}
    scenario_name = request.args.get("scenario")

    if scenario_name == "Streaming":
        scenario_cfg = get_scenario_config(BASE_DIR, scenario_name) or {}

        if "camera" not in scenario_cfg or not scenario_cfg["camera"]:
            scenario_cfg["camera"] = make_stub("Нет камеры")

        if "microphone" not in scenario_cfg or not scenario_cfg["microphone"]:
            scenario_cfg["microphone"] = make_stub("Нет микрофона")

    elif scenario_name == "Math":
        scenario_cfg = get_scenario_config(BASE_DIR, scenario_name) or {}

        if "cameras" not in scenario_cfg or not scenario_cfg["cameras"]:
            scenario_cfg["cameras"] = [make_stub("Нет камеры"), make_stub("Нет камеры")]
        elif len(scenario_cfg["cameras"]) == 1:
            scenario_cfg["cameras"].append(make_stub("Нет камеры"))

        if "microphone" not in scenario_cfg or not scenario_cfg["microphone"]:
            scenario_cfg["microphone"] = make_stub("Нет микрофона")

    return jsonify({
        "global": global_cfg,
        "scenario": scenario_cfg
    })

@app.route("/api/config", methods=["PUT"])
def update_config():
    data = request.get_json(force=True) or {}
    global_cfg = data.get("global", {})
    scenario_cfg = data.get("scenario", {})
    scenario_name = data.get("scenario_name")
    backup_dir = data.get("backup_dir")

    if global_cfg:
        write_global_config(CONFIG_PATH, global_cfg)
    if scenario_name and scenario_cfg:
        write_scenario_config(BASE_DIR, scenario_name, scenario_cfg, backup_dir)

    return jsonify({"ok": True})

@app.route("/api/backup/restore/<scenario>", methods=["POST"])
def restore_backup(scenario):
    try:
        scenario_dir = os.path.join(BASE_DIR, "scenarios", scenario)
        if not os.path.isdir(scenario_dir):
            return jsonify({"status": "error", "message": "Сценарий не найден"}), 404

        settings_dir = os.path.join(scenario_dir, "__settings__")

        backup_dirs = [d for d in os.listdir(settings_dir)
                       if d.startswith("backup_") and os.path.isdir(os.path.join(settings_dir, d))]
        if not backup_dirs:
            return jsonify({"status": "error", "message": "Нет ни одной папки бэкапа"}), 404

        backup_dirs.sort()
        latest_backup = backup_dirs[-1]
        backup_path = os.path.join(settings_dir, latest_backup)

        restored_files = []
        for fname in ["config.json", "scenario_template.json", "scenario.json"]:
            src = os.path.join(backup_path, fname)
            dst = os.path.join(settings_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                restored_files.append(fname)

        if not restored_files:
            return jsonify({"status": "error", "message": "В бэкапе нет файлов для восстановления"}), 404

        return jsonify({
            "status": "ok",
            "message": f"Восстановлены файлы {', '.join(restored_files)} из {latest_backup}"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

def classify_device(inp, hints):
    input_kind = inp.get("inputKind") or ""
    name = inp.get("inputName") or inp.get("sourceName") or ""
    settings = inp.get("inputSettings", {}) or {}
    device_id = settings.get("device_id") or settings.get("device", "") or "unknown"

    if name in SKIP_NAMES:
        return None, None

    lname = name.lower()

    if "dshow" in input_kind or "v4l2" in input_kind or "av_capture" in input_kind:
        return "camera", (input_kind, name, device_id)
    if "wasapi" in input_kind or "pulse" in input_kind or "coreaudio" in input_kind:
        return "microphone", (input_kind, name, device_id)

    if device_id != "unknown":
        if any(word in lname for word in hints.get("camera_hints", [])):
            return "camera", (input_kind or "dshow_input", name, device_id)
        if any(word in lname for word in hints.get("microphone_hints", [])):
            return "microphone", (input_kind or "wasapi_input_capture", name, device_id)
        if any(word in device_id.lower() for word in hints.get("id_hints", [])):
            return "camera", (input_kind or "dshow_input", name, device_id)

    return None, None

def get_audio_property_items(client, input_name, input_kind):
    candidates = ["device_id", "device", "audio_device_id"]

    last_err = None
    for prop in candidates:
        try:
            return client.get_input_properties_list_property_items(input_name, prop).property_items
        except Exception as e:
            last_err = e
            continue
    k = (input_kind or "").lower()
    if "pulse" in k or "coreaudio" in k:
        try:
            return client.get_input_properties_list_property_items(input_name, "device").property_items
        except Exception as e:
            last_err = e

    raise last_err

def get_input_kind(kind: str, platform: str) -> str:
    return INPUT_KIND_MAP.get(kind, {}).get(platform, "dshow_input")

def build_device_info(kind, name, device_id, input_kind=None):
    platform = guess_platform(input_kind or get_input_kind(kind, None))
    source = guess_source(name, device_id)
    manufacturer = guess_manufacturer(name, device_id)
    info = {
        "name": name,
        "kind": kind,
        "device_id": device_id,
        "platform": platform,          # windows/linux/apple/unknown
        "source": source,              # usb/network/virtual_driver/unknown
        "manufacturer": manufacturer,  # for example "Apple", "Samsung", or null
        "inputKind": input_kind or get_input_kind(kind, platform)
    }
    if kind == "camera":
        mobile, hints_list = is_mobile_camera(input_kind or "dshow_input", name, device_id)
        info["is_mobile"] = mobile     # True/False
        info["hints"] = hints_list     # list of successful heuristics for transparency
        info["scrcpy"] = False
    return info

@app.route("/api/devices", methods=["GET"])
def get_devices():
    try:
        obs = get_obs_instance()
    except ObsNotRunningError:
        return jsonify({"status": "error", "message": "OBS не запущен."}), 500
    except ObsConnectionError as e:
        return jsonify({"status": "error", "message": f"Ошибка подключения: {e}"}), 500

    with devices_lock:
        try:
            cameras, microphones = [], []

            temp_scene = obs.ensure_unique_scene_name("TempSceneForDevices")
            scenes = obs.client.get_scene_list().scenes
            if not any(s["sceneName"] == temp_scene for s in scenes):
                obs.client.create_scene(temp_scene)
            obs.client.set_current_program_scene(temp_scene)

            cam_source = obs.ensure_unique_input_name("TempVideoCapture")
            mic_source = obs.ensure_unique_input_name("TempAudioCapture")

            obs.client.create_input(
                sceneName=temp_scene,
                inputName=cam_source,
                inputKind="dshow_input",
                inputSettings={},
                sceneItemEnabled=True
            )
            obs.client.create_input(
                sceneName=temp_scene,
                inputName=mic_source,
                inputKind="wasapi_input_capture",
                inputSettings={},
                sceneItemEnabled=True
            )

            try:
                cam_items = obs.client.get_input_properties_list_property_items(cam_source, "video_device_id").property_items
                for dev in cam_items:
                    cameras.append(build_device_info("camera", dev["itemName"], dev["itemValue"], "dshow_input"))
            except Exception:
                traceback.print_exc()

            try:
                mic_items = get_audio_property_items(obs.client, mic_source, "wasapi_input_capture")
                for dev in mic_items:
                    microphones.append(build_device_info("microphone", dev["itemName"], dev["itemValue"], "wasapi_input_capture"))
            except Exception:
                traceback.print_exc()

            resp = obs.client.get_input_list()
            for inp in resp.inputs:
                if inp["inputName"] in {"TempVideoCapture", "TempAudioCapture"}:
                    continue

                kind, data = classify_device(inp, HINTS)
                if kind == "camera":
                    cameras.append(build_device_info("camera", data[1], data[2], data[0]))
                elif kind == "microphone":
                    microphones.append(build_device_info("microphone", data[1], data[2], data[0]))

            obs.client.remove_scene(temp_scene)

            # try:
            #     obs.client.save_project()
            # except Exception:
            #     traceback.print_exc()

            return jsonify({"status": "ok", "cameras": cameras, "microphones": microphones})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/export", methods=["POST"])
def export_to_obs():
    try:
        obs = get_obs_instance()
    except ObsNotRunningError:
        return jsonify({"status": "error", "message": "OBS не запущен."}), 500
    except ObsConnectionError as e:
        return jsonify({"status": "error", "message": f"Ошибка подключения: {e}"}), 500

    with devices_lock:
        try:
            data = request.get_json(force=True) or {}
            global_cfg = data.get("global", {})
            scenario_cfg = data.get("scenario", {})
            scenario_name = data.get("scenario_name")
            use_template = data.get("use_template")

            if global_cfg.get("allow_delete_scenes", True):
                obs.clear_scenes()
                # obs.clear_profiles()

            scenario_dir = os.path.join(BASE_DIR, "scenarios", scenario_name)
            if not os.path.isdir(scenario_dir):
                return jsonify({"status": "error", "message": "Сценарий не найден"}), 404

            config_path = os.path.join(scenario_dir, "__settings__", "config.json")
            config_data = get_global_config(config_path)

            camera_settings = config_data.get("camera_settings", [])
            if scenario_name == "Math":
                cameras = config_data.get("cameras", [])
            else:
                cameras = []
                cameras.append(config_data.get("camera", {}))
            microphone = config_data.get("microphone", {})

            scenario_path = os.path.join(scenario_dir, "__settings__", "scenario.json")

            if use_template:
                scenario_template_path = os.path.join(scenario_dir, "__settings__", "scenario_template.json")
                scenario_template_data = get_global_config(scenario_template_path)

                video_settings = scenario_template_data["profile"]["settings"]["video"]
                out_w = video_settings["output_width"]
                out_h = video_settings["output_height"]

                for scene in scenario_template_data["scenes"]:
                    for idx, item in enumerate(scene["items"]):
                        if item.get("sourceName", "").startswith("DefaultCamera"):
                            transform = item.get("transform", {})
                            if transform.get("boundsWidth") == "${output_width}":
                                transform["boundsWidth"] = out_w
                            if transform.get("boundsHeight") == "${output_height}":
                                transform["boundsHeight"] = out_h

                            if scenario_name == "Math" and idx == 1:
                                if transform.get("boundsWidth") == "${boundsWidth}":
                                    transform["boundsWidth"] = camera_settings[idx].get("boundsWidth", 320)
                                if transform.get("boundsHeight") == "${boundsHeight}":
                                    transform["boundsHeight"] = camera_settings[idx].get("boundsHeight", 240)

                write_global_config(scenario_path, scenario_template_data)

            scenario_data = get_global_config(scenario_path)

            inputs = scenario_data.get("inputs", [])

            for idx, cam in enumerate(cameras):
                if not cam.get("is_stub", False):
                    found = next((i for i in inputs if i["inputName"] == "DefaultCamera"), None)
                    if found:
                        found["inputKind"] = cam.get("inputKind", found.get("inputKind"))
                        found["inputSettings"] = {"video_device_id": cam.get("device_id", "unknown")}
                    else:
                        inputs.append({
                            "inputName": "DefaultCamera",
                            "inputKind": cam.get("inputKind", "dshow_input"),
                            "inputSettings": {"video_device_id": cam.get("device_id", "unknown")}
                        })

            if microphone:
                found = next((i for i in inputs if i["inputName"] == "DefaultMicrophone"), None)
                if found:
                    found["inputKind"] = microphone.get("inputKind", found.get("inputKind"))
                    found["inputSettings"] = {"device_id": microphone.get("device_id", "unknown")}
                else:
                    inputs.append({
                        "inputName": "DefaultMicrophone",
                        "inputKind": microphone.get("inputKind", "wasapi_input_capture"),
                        "inputSettings": {"device_id": microphone.get("device_id", "unknown")}
                    })

            scenario_data["inputs"] = inputs
            write_global_config(scenario_path, scenario_data)

            obs_export_import = OBSExportImport(obs)
            obs_export_import.load_from_file(scenario_path)

            return jsonify({"status": "ok", "message": "Сцены и источники обновлены в OBS"})
        except RuntimeError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/import", methods=["POST"])
def import_from_obs():
    try:
        obs = get_obs_instance()
    except ObsNotRunningError:
        return jsonify({"status": "error", "message": "OBS не запущен."}), 500
    except ObsConnectionError as e:
        return jsonify({"status": "error", "message": f"Ошибка подключения: {e}"}), 500

    with devices_lock:
        try:
            data = request.get_json(force=True) or {}
            global_cfg = data.get("global", {})
            scenario_cfg = data.get("scenario", {})
            scenario_name = data.get("scenario_name")

            scenario_dir = os.path.join(BASE_DIR, "scenarios", scenario_name)
            if not os.path.isdir(scenario_dir):
                return jsonify({"status": "error", "message": "Сценарий не найден"}), 404

            scenario_path = os.path.join(scenario_dir, "__settings__", "scenario.json")
            config_path = os.path.join(scenario_dir, "__settings__", "config.json")

            obs_export_import = OBSExportImport(obs)
            obs_export_import.save_to_file(scenario_path)

            scenario_data = get_global_config(scenario_path)
            cameras, microphones = [], []

            for inp in scenario_data.get("inputs", []):
                if inp["inputName"] in {"DefaultCamera", "DefaultCamera1", "DefaultCamera2"}:
                    video_id = inp["inputSettings"].get("video_device_id")
                    try:
                        cam_items = obs.client.get_input_properties_list_property_items(inp["inputName"], "video_device_id").property_items
                        for dev in cam_items:
                            if dev["itemValue"] == video_id:
                                cameras.append(build_device_info("camera", dev["itemName"], dev["itemValue"], inp["inputKind"]))
                                break
                    except Exception:
                        traceback.print_exc()

                elif inp["inputName"] == "DefaultMicrophone":
                    mic_id = inp["inputSettings"].get("device_id")
                    try:
                        mic_items = get_audio_property_items(obs.client, inp["inputName"], "wasapi_input_capture")
                        for dev in mic_items:
                            if dev["itemValue"] == mic_id:
                                microphones.append(build_device_info("microphone", dev["itemName"], dev["itemValue"], inp["inputKind"]))
                                break
                    except Exception:
                        traceback.print_exc()

            config_data = get_global_config(config_path)
            if cameras:
                if scenario_name == "Math":
                    config_data["cameras"].append(cameras[0])
                    config_data["cameras"].append(cameras[1])
                else:
                    config_data["camera"] = cameras[0]
            if microphones:
                config_data["microphone"] = microphones[0]

            write_global_config(config_path, config_data)

            return jsonify({"status": "ok", "message": "Настройки импортированы из OBS"})
        except RuntimeError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/students", methods=["GET"])
def get_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return jsonify([{
        "id": s.id,
        "first_name": s.first_name,
        "last_name": s.last_name,
        "email": s.email,
        "city": s.city,
        "address": s.address,
        "phone": s.phone,
        "chapter": s.chapter,
        "paragraph": s.paragraph,
        "section": s.section,
        "position": s.position,
        "task_number": s.task_number
    } for s in students])

@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json(force=True)
    db = SessionLocal()
    student = Student(**data)
    db.add(student)
    db.commit()
    db.refresh(student)
    db.close()
    return jsonify({"id": student.id, "status": "created"})

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(force=True)
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        db.close()
        return jsonify({"error": "Student not found"}), 404
    for key, value in data.items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    db.close()
    return jsonify({"id": student.id, "status": "updated"})

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        db.close()
        return jsonify({"error": "Student not found"}), 404
    db.delete(student)
    db.commit()
    db.close()
    return jsonify({"id": student_id, "status": "deleted"})

@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    db = SessionLocal()
    scenarios = db.query(Scenario).all()
    db.close()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "description": s.description
    } for s in scenarios])

@app.route("/api/scenarios/<int:scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    db.close()
    if not scenario:
        return jsonify({"error": "Scenario not found"}), 404

    scenario_path = os.path.join(BASE_DIR, "scenarios", scenario.name)
    if not os.path.exists(scenario_path):
        return jsonify({"error": "Сценарий не реализован"}), 400

    return jsonify({
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description
    })

@app.route("/api/scenarios", methods=["POST"])
def create_scenario():
    data = request.get_json(force=True)
    db = SessionLocal()
    scenario = Scenario(**data)
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    db.close()
    return jsonify({"id": scenario.id, "status": "created"})

@app.route("/api/scenarios/<int:scenario_id>", methods=["PUT"])
def update_scenario(scenario_id):
    data = request.get_json(force=True)
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        db.close()
        return jsonify({"error": "Scenario not found"}), 404
    for key, value in data.items():
        setattr(scenario, key, value)
    db.commit()
    db.refresh(scenario)
    db.close()
    return jsonify({"id": scenario.id, "status": "updated"})

@app.route("/api/scenarios/<int:scenario_id>", methods=["DELETE"])
def delete_scenario(scenario_id):
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        db.close()
        return jsonify({"error": "Scenario not found"}), 404

    scenario_path = os.path.join(BASE_DIR, "scenarios", scenario.name)
    if os.path.exists(scenario_path):
        db.close()
        return jsonify({"error": "Нельзя удалить сценарий: существует папка с реализацией"}), 400

    db.delete(scenario)
    db.commit()
    db.close()
    return jsonify({"id": scenario_id, "status": "deleted"})

@app.route("/api/students/<int:student_id>/scenarios/<int:scenario_id>", methods=["POST"])
def assign_scenario(student_id, scenario_id):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not student or not scenario:
        db.close()
        return jsonify({"error": "Student or Scenario not found"}), 404

    if scenario not in student.scenarios:
        student.scenarios.append(scenario)
        db.commit()
        db.refresh(student)

    db.close()
    return jsonify({
        "status": "ok",
        "student_id": student_id,
        "scenario_id": scenario_id
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
