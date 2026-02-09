import psutil
import pygetwindow as gw
import subprocess
import time
import threading
import libs.adb_utils as adb_utils
from typing import Optional

class AndroidActions:
    def __init__(self, is_scrcpy: bool, scrcpy_title: str, config_data: dict, settings_data: dict, phone_config: str):
        self.is_scrcpy = is_scrcpy
        self.scrcpy_title = scrcpy_title
        self.config_data = config_data
        self.settings_data = settings_data
        self.phone_config = phone_config

        self.camera_proc: Optional[subprocess.Popen] = None
        self.scrcpy_proc: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()

        self.old_stay_awake: Optional[str] = None
        self.old_battery_saver: Optional[str] = None

    def _ensure_camera_stopped(self, device_serial: str, driver_package: str):
        try:
            if adb_utils.is_app_running(device_serial, driver_package):
                print(f"📱 Камера {driver_package} уже запущена, останавливаем...")
                adb_utils.close_specific_apps(device_serial, [driver_package])
        except Exception as e:
            print(f"Не удалось проверить/остановить камеру {driver_package}: {e}")

    def _prepare_phone(self, device_serial: str, driver_package: str, close_mode: str, apps_to_close: list):
        self._ensure_camera_stopped(device_serial, driver_package)

        if close_mode == "all":
            adb_utils.close_all_apps(device_serial, x=511, y=2044)
        else:
            adb_utils.close_specific_apps(device_serial, apps_to_close)

        self.old_stay_awake = adb_utils.get_setting(device_serial, "global", "stay_on_while_plugged_in")
        self.old_battery_saver = adb_utils.get_setting(device_serial, "global", "low_power")

        adb_utils.disable_auto_rotation(device_serial)
        adb_utils.stay_awake(device_serial, True)
        adb_utils.disable_battery_saver(device_serial)

    def _restore_settings(self, device_serial: str):
        try:
            adb_utils.enable_auto_rotation(device_serial)
            if self.old_stay_awake is not None:
                adb_utils.set_setting(device_serial, "global", "stay_on_while_plugged_in", self.old_stay_awake)
            if self.old_battery_saver is not None:
                adb_utils.set_setting(device_serial, "global", "low_power", self.old_battery_saver)
        except Exception as e:
            print(f"Не удалось восстановить настройки телефона: {e}")

    def _start_camera(self, device_serial: str, driver_package: str):
        if self.is_scrcpy:
            camera_package = None
            camera_activity = None
            scrcpy_command = None
            if self.phone_config:
                camera_package = self.phone_config.get("camera_package")
                camera_activity = self.phone_config.get("camera_activity")
                scrcpy_command = self.phone_config.get("scrcpy_command")

            if camera_package and camera_activity:
                adb_utils.start_back_camera(device_serial, camera_package, camera_activity)
            else:
                adb_utils.start_back_camera(device_serial)

            if scrcpy_command:
                args = scrcpy_command.split()
            else:
                args = [
                    "scrcpy",
                    "--max-size", "800",
                    "--video-bit-rate", "2M",
                    "--audio-bit-rate", "64K",
                    "--max-fps", "15"
                ]

            args.append(f"--window-title={self.scrcpy_title}")
            self.scrcpy_proc = subprocess.Popen(args)
        else:
            adb_utils.launch_app(device_serial, driver_package)

            iriun_path = self.settings_data.get("IriunWebcam", {}).get(
                "path", r"C:\Android\Iriun Webcam\IriunWebcam.exe"
            )
            self.camera_proc = subprocess.Popen([iriun_path])

    def _pipeline(self):
        device_serial = self.config_data.get("device_serial")
        driver_package = self.config_data["driver_package"]
        close_mode = self.config_data.get("close_mode", "")
        apps_to_close = self.config_data.get("apps_to_close", [])

        self._prepare_phone(device_serial, driver_package, close_mode, apps_to_close)
        self._start_camera(device_serial, driver_package)

        try:
            while not self.stop_flag.is_set():
                active_procs = [p for p in (self.camera_proc, self.scrcpy_proc) if p]
                if not any(proc.poll() is None for proc in active_procs):
                    break

                if not self.is_scrcpy and not adb_utils.is_app_running(device_serial, driver_package):
                    print("⚠️ Iriun Webcam не работает, перезапуск...")
                    adb_utils.restart_app(device_serial, driver_package)

                time.sleep(10)
        finally:
            self._restore_settings(device_serial)

    def wait_for_process_ready(self, proc_getter, timeout=180, window_title=None, min_cpu_activity=0.5):
        start = time.time()

        while time.time() - start < timeout:
            proc = proc_getter()
            if proc is not None:
                if proc.poll() is not None:
                    raise RuntimeError("Процесс завершился преждевременно")

                if proc.pid is not None:
                    ps_proc = psutil.Process(proc.pid)
                    try:
                        cpu = ps_proc.cpu_percent(interval=1)
                        if cpu < min_cpu_activity:
                            time.sleep(1)
                            continue
                    except psutil.NoSuchProcess:
                        raise RuntimeError("Процесс исчез")

                    if window_title:
                        windows = gw.getWindowsWithTitle(window_title)
                        if windows:
                            return True
                    else:
                        return True

            time.sleep(1)

        raise TimeoutError(f"Программа не стала готовой за {timeout} секунд")

    def wait_for_scrcpy_ready(self):
        self.wait_for_process_ready(lambda: self.scrcpy_proc, window_title=self.scrcpy_title)

    def wait_for_IriunWebcam_ready(self):
        self.wait_for_process_ready(lambda: self.camera_proc)

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
    def create(is_scrcpy: bool, scrcpy_title: str, config_data: dict, settings_data: dict, phone_config: str):
        instance = AndroidActions(is_scrcpy, scrcpy_title, config_data, settings_data, phone_config)
        instance.start()
        return instance
