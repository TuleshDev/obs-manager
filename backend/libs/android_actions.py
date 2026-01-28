import subprocess
import time
import threading
import libs.adb_utils as adb_utils
from typing import Optional

class AndroidActions:
    def __init__(self, scrcpy: bool, config_data: dict, settings_data: dict):
        self.scrcpy = scrcpy
        self.config_data = config_data
        self.settings_data = settings_data

        self.camera_proc: Optional[subprocess.Popen] = None
        self.scrcpy_proc: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()

        self.old_stay_awake: Optional[str] = None
        self.old_battery_saver: Optional[str] = None

    def _ensure_camera_stopped(self, device_serial: str, camera_package: str):
        try:
            if adb_utils.is_app_running(device_serial, camera_package):
                print(f"📱 Камера {camera_package} уже запущена, останавливаем...")
                adb_utils.close_specific_apps(device_serial, [camera_package])
        except Exception as e:
            print(f"Не удалось проверить/остановить камеру {camera_package}: {e}")

    def _prepare_phone(self, device_serial: str, camera_package: str, close_mode: str, apps_to_close: list):
        self._ensure_camera_stopped(device_serial, camera_package)

        if close_mode == "all":
            adb_utils.close_all_apps(device_serial)
        else:
            adb_utils.close_specific_apps(device_serial, apps_to_close)

        self.old_stay_awake = adb_utils.get_setting(device_serial, "global", "stay_on_while_plugged_in")
        self.old_battery_saver = adb_utils.get_setting(device_serial, "global", "low_power")

        adb_utils.stay_awake(device_serial, True)
        adb_utils.disable_battery_saver(device_serial)

    def _restore_settings(self, device_serial: str):
        try:
            if self.old_stay_awake is not None:
                adb_utils.set_setting(device_serial, "global", "stay_on_while_plugged_in", self.old_stay_awake)
            if self.old_battery_saver is not None:
                adb_utils.set_setting(device_serial, "global", "low_power", self.old_battery_saver)
        except Exception as e:
            print(f"Не удалось восстановить настройки телефона: {e}")

    def _start_camera(self, device_serial: str, camera_package: str):
        if self.scrcpy:
            self.scrcpy_proc = subprocess.Popen(["scrcpy", "--stay-awake"])
        else:
            adb_utils.launch_app(device_serial, camera_package)

            iriun_path = self.settings_data.get("IriunWebcam", {}).get(
                "path", r"C:\Android\Iriun Webcam\IriunWebcam.exe"
            )
            self.camera_proc = subprocess.Popen([iriun_path])

    def _pipeline(self):
        device_serial = self.config_data.get("device_serial")
        camera_package = self.config_data["camera_package"]
        close_mode = self.config_data.get("close_mode", "")
        apps_to_close = self.config_data.get("apps_to_close", [])

        self._prepare_phone(device_serial, camera_package, close_mode, apps_to_close)
        self._start_camera(device_serial, camera_package)

        try:
            while not self.stop_flag.is_set():
                active_procs = [p for p in (self.camera_proc, self.scrcpy_proc) if p]
                if not any(proc.poll() is None for proc in active_procs):
                    break

                if not self.scrcpy and not adb_utils.is_app_running(device_serial, camera_package):
                    print("⚠️ Iriun Webcam не работает, перезапуск...")
                    adb_utils.restart_app(device_serial, camera_package)

                time.sleep(10)
        finally:
            self._restore_settings(device_serial)

    def start(self):
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self._pipeline, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()

        for proc in (self.camera_proc, self.scrcpy_proc):
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()

        self.camera_proc = None
        self.scrcpy_proc = None

        device_serial = self.config_data.get("device_serial")
        self._restore_settings(device_serial)

        if self.thread:
            self.thread.join()
            self.thread = None

    @staticmethod
    def create(scrcpy: bool, config_data: dict, settings_data: dict):
        instance = AndroidActions(scrcpy, config_data, settings_data)
        instance.start()
        return instance
