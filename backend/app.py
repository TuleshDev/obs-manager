import psutil
import subprocess
import os
import shutil
import json
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Student, Scenario
from models import student_scenario

from libs.hints import load_hints, guess_platform, guess_source, guess_manufacturer, is_mobile_camera
from libs.obs_actions import ObsActions
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

settings = get_global_config(SETTINGS_PATH)
db_password = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{settings["db"]['user']}:{db_password}@"
    f"{settings["db"]['host']}:{settings["db"]['port']}/{settings["db"]['database']}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

ensure_obs_running()

global_cfg = get_global_config(CONFIG_PATH)
load_hints(HINTS_PATH)

try:
    ws_password = os.getenv("WS_PASSWORD")

    obs = ObsActions(
        host=global_cfg.get("ws_host", "127.0.0.1"),
        port=global_cfg.get("ws_port", 4455),
        password=ws_password
    )
except Exception as e:
    traceback.print_exc()
    obs = None

def make_stub(name="Нет устройства", kind="stub"):
    return {
        "device_id": "stub",
        "name": name,
        "kind": kind,
        "is_stub": True
    }

@app.before_request
def check_obs():
    ensure_obs_running()

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

@app.route("/api/devices", methods=["GET"])
def get_devices():
    if obs is None:
        return jsonify({"status": "error", "message": "OBS клиент не инициализирован"}), 500
    try:
        inputs = obs.client.get_input_list().inputs
        cameras, microphones = [], []

        for inp in inputs:
            kind = inp.get("inputKind", "")
            name = inp.get("inputName", "")
            settings = inp.get("inputSettings", {}) or {}
            device_id = settings.get("device_id") or settings.get("device", "") or "unknown"

            platform = guess_platform(kind)
            source = guess_source(name, device_id)

            if "dshow" in kind or "v4l2" in kind or "av_capture" in kind:
                mobile, hints = is_mobile_camera(kind, name, device_id)
                manufacturer = guess_manufacturer(name, device_id)

                cameras.append({
                    "name": name,
                    "kind": kind,
                    "device_id": device_id,
                    "platform": platform,          # windows/linux/apple/unknown
                    "source": source,              # usb/network/virtual_driver/unknown
                    "is_mobile": mobile,           # True/False
                    "manufacturer": manufacturer,  # for example "Apple", "Samsung", or null
                    "hints": hints                 # list of successful heuristics for transparency
                })

            elif "wasapi" in kind or "pulse" in kind or "coreaudio" in kind:
                microphones.append({
                    "name": name,
                    "kind": kind,
                    "device_id": device_id,
                    "platform": platform,
                    "source": source
                })

        return jsonify({
            "status": "ok",
            "cameras": cameras,
            "microphones": microphones
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/export", methods=["POST"])
def export_to_obs():
    if obs is None:
        return jsonify({"status": "error", "message": "OBS клиент не инициализирован"}), 500
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

        scenario_path = os.path.join(scenario_dir, "__settings__", "scenario.json")

        if use_template:
            scenario_template_path = os.path.join(scenario_dir, "__settings__", "scenario_template.json")
            scenario_template_data = get_global_config(scenario_template_path)

            video_settings = scenario_template_data["profile"]["settings"]["video"]
            out_w = video_settings["output_width"]
            out_h = video_settings["output_height"]

            config_path = os.path.join(scenario_dir, "__settings__", "config.json")
            config_data = get_global_config(config_path)

            camera_settings = config_data.get("camera_settings", [])

            for scene in scenario_template_data["scenes"]:
                for idx, item in enumerate(scene["items"]):
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

        obs_export_import = OBSExportImport(obs.client)
        obs_export_import.load_from_file(scenario_path)

        return jsonify({"status": "ok", "message": "Сцены и источники обновлены в OBS"})
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/import", methods=["POST"])
def import_from_obs():
    if obs is None:
        return jsonify({"status": "error", "message": "OBS клиент не инициализирован"}), 500
    try:
        data = request.get_json(force=True) or {}
        global_cfg = data.get("global", {})
        scenario_cfg = data.get("scenario", {})
        scenario_name = data.get("scenario_name")

        scenario_dir = os.path.join(BASE_DIR, "scenarios", scenario_name)
        if not os.path.isdir(scenario_dir):
            return jsonify({"status": "error", "message": "Сценарий не найден"}), 404

        scenario_path = os.path.join(scenario_dir, "__settings__", "scenario.json")

        obs_export_import = OBSExportImport(obs.client)
        obs_export_import.save_to_file(scenario_path)

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
