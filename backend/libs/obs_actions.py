import os
import psutil
import re
import subprocess
import time
import traceback
import socket
import threading
from obsws_python import ReqClient

class ObsNotRunningError(Exception):
    pass

class ObsConnectionError(Exception):
    pass

class ObsActions:
    obs_instance = None
    obs_lock = threading.Lock()

    def __init__(self, host="127.0.0.1", port=4455, password=None):
        try:
            self.client = ReqClient(host=host, port=port, password=password)
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка подключения к OBS WebSocket: {e}")

    def is_connected(self) -> bool:
        try:
            self.client.get_scene_list()
            return True
        except Exception:
            return False

    @staticmethod
    def is_port_open(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex((host, port)) == 0

    @staticmethod
    def kill_obs(grace_period: int = 5):
        try:
            print("Команда выхода отправляется OBS через WebSocket.")
            ObsActions.obs_instance.exit()
            return
        except Exception as e:
            print(f"Не удалось закрыть OBS через WebSocket: {e}")

        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'obs64.exe' in proc.info['name'].lower():
                print("Попытка мягко завершить OBS...")
                proc.terminate()
                try:
                    proc.wait(timeout=grace_period)
                    print("OBS завершён корректно.")
                except psutil.TimeoutExpired:
                    print("OBS не завершился, убиваю процесс...")
                    proc.kill()

    @staticmethod
    def start_obs(settings):
        obs_path = settings.get("obs", {}).get(
            "path", r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
        )
        obs_dir = settings.get("obs", {}).get(
            "dir", r"C:\Program Files\obs-studio\bin\64bit"
        )

        if not os.path.exists(obs_path):
            raise ObsNotRunningError(f"OBS exe не найден по пути: {obs_path}")

        locale_file = os.path.join(
            os.path.dirname(os.path.dirname(obs_dir)),
            "data", "obs-studio", "locale", "en-US.ini"
        )
        if not os.path.exists(locale_file):
            raise ObsNotRunningError(f"Файл локализации OBS не найден: {locale_file}")

        print(f"Запускаю OBS: {obs_path}")
        subprocess.Popen([obs_path], cwd=obs_dir)

    @staticmethod
    def ensure_obs_ready(cfg, settings,
                         retries: int = 5, base_delay: int = 2):
        host = cfg.get("ws_host", "127.0.0.1")
        port = cfg.get("ws_port", 4455)
        ws_password = os.getenv("WS_PASSWORD")

        with ObsActions.obs_lock:
            last_error = None
            for attempt in range(1, retries + 1):
                try:
                    process_exists = any(
                        proc.info['name'] and 'obs64.exe' in proc.info['name'].lower()
                        for proc in psutil.process_iter(['name'])
                    )

                    if process_exists and not ObsActions.is_port_open(host, port):
                        print("Обнаружен зависший процесс OBS, перезапускаю...")
                        ObsActions.kill_obs()
                        ObsActions.start_obs(settings)

                    if not process_exists:
                        ObsActions.start_obs(settings)

                    time.sleep(base_delay * (2 ** (attempt - 1)))
                    ObsActions.obs_instance = ObsActions(host=host, port=port, password=ws_password)

                    if ObsActions.obs_instance.is_connected():
                        print("OBS готов к работе.")
                        return ObsActions.obs_instance

                except Exception as e:
                    last_error = e
                    ObsActions.obs_instance = None
                    traceback.print_exc()
                    delay = base_delay * (2 ** (attempt - 1))
                    print(f"Попытка {attempt} не удалась, повтор через {delay} сек...")
                    time.sleep(delay)

            raise ObsConnectionError(
                f"Не удалось подключиться к OBS WebSocket после {retries} попыток: {last_error}"
            )

    def clear_scenes_and_filters(self):
        try:
            scenes = self.client.get_scene_list().scenes
            for scene in scenes:
                scene_name = scene["sceneName"]

                sources = self.client.get_scene_item_list(scene_name).scene_items
                for src in sources:
                    source_name = src["sourceName"]
                    filters = self.client.get_source_filter_list(source_name).filters
                    for f in filters:
                        if f["filterKind"] == "crop_filter":
                            self.client.remove_source_filter(source_name, f["filterName"])

                self.client.remove_scene(scene_name)

        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при удалении сцен и фильтров: {e}")

    def ensure_unique_scene_name(self, base_name="TempScene"):
        scenes = self.client.get_scene_list().scenes
        existing_names = {s["sceneName"] for s in scenes}
        if base_name not in existing_names:
            return base_name
        i = 2
        while f"{base_name}{i}" in existing_names:
            i += 1
        return f"{base_name}{i}"

    def ensure_unique_input_name(self, base_name="TempCapture"):
        resp = self.client.get_input_list()
        inputs = resp.inputs
        existing_names = {inp["inputName"] for inp in inputs}
        if base_name not in existing_names:
            return base_name
        i = 2
        while f"{base_name}{i}" in existing_names:
            i += 1
        return f"{base_name}{i}"

    def import_video_captures(self, device_id):
        try:
            temp_scene = self.ensure_unique_scene_name("TempSceneForDevices")
            scenes = self.client.get_scene_list().scenes
            if not any(s["sceneName"] == temp_scene for s in scenes):
                self.client.create_scene(temp_scene)
            self.client.set_current_program_scene(temp_scene)

            cam_source = self.ensure_unique_input_name("TempVideoCapture")
            self.client.create_input(
                sceneName=temp_scene,
                inputName=cam_source,
                inputKind="dshow_input",
                inputSettings={},
                sceneItemEnabled=True
            )

            try:
                cam_items = self.client.get_input_properties_list_property_items(
                    cam_source, "video_device_id"
                ).property_items
            except Exception:
                traceback.print_exc()

            self.client.remove_scene(temp_scene)

            selected_cam = None
            for dev in cam_items:
                if dev["itemValue"] == device_id:
                    selected_cam = dev
                    break

            if not selected_cam:
                raise ValueError(f"Камера с device_id {device_id} не найдена.")

            return selected_cam
        except Exception as e:
            traceback.print_exc()
            raise e

    def import_window_captures(self, keywords):
        try:
            temp_scene = self.ensure_unique_scene_name("TempSceneForWindows")
            scenes = self.client.get_scene_list().scenes
            if not any(s["sceneName"] == temp_scene for s in scenes):
                self.client.create_scene(temp_scene)
            self.client.set_current_program_scene(temp_scene)

            win_source = self.ensure_unique_input_name("TempWindowCapture")
            self.client.create_input(
                sceneName=temp_scene,
                inputName=win_source,
                inputKind="window_capture",
                inputSettings={},
                sceneItemEnabled=True
            )

            try:
                win_items = self.client.get_input_properties_list_property_items(
                    win_source, "window"
                ).property_items
            except Exception:
                traceback.print_exc()

            self.client.remove_scene(temp_scene)

            encoded_keywords = []
            for kw in keywords:
                encoded_kw = self.encode_obs_title(kw)
                encoded_keywords.append(encoded_kw)

            selected_window = None
            for item in win_items:
                val = item["itemValue"].lower()
                if all(kw.lower() in val for kw in encoded_keywords):
                    selected_window = item["itemValue"]
                    break

            if not selected_window:
                raise ValueError(f"Окно с ключевыми словами {keywords} не найдено.")

            return selected_window
        except Exception as e:
            traceback.print_exc()
            raise e

    # dangerous_level1 = {":", " ", "[", "]", "(", ")", "{", "}", ";", ",", '"', "\\"}
    dangerous_level1 = {":"}
    dangerous_level2 = [
        ("#22", "#2222")
    ]

    def encode_once(self, s: str, dangerous: set) -> str:
        result = []
        for ch in s:
            if ch in dangerous:
                result.append(f"#{ord(ch):02X}")
            else:
                result.append(ch)
        return "".join(result)

    def encode_obs_title(self, s: str, levels: int = 2) -> str:
        encoded = s
        if levels >= 1:
            encoded = self.encode_once(encoded, self.dangerous_level1)
        if levels >= 2:
            for src, dst in self.dangerous_level2:
                encoded = encoded.replace(src, dst)
        return encoded

    def decode_obs_title(self, s: str, levels: int = 2) -> str:
        decoded = s
        if levels >= 2:
            for src, dst in self.dangerous_level2:
                decoded = decoded.replace(dst, src)
        if levels >= 1:
            def repl(match):
                code = match.group(1).upper()
                char = chr(int(code, 16))
                if char in self.dangerous_level1:
                    return char
                return match.group(0)
            decoded = re.sub(r"#([0-9A-Fa-f]{2})", repl, decoded)
        return decoded
