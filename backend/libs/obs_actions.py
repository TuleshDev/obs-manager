import traceback
from obsws_python import ReqClient

class ObsActions:
    def __init__(self, host, port, password):
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

    def clear_scenes(self):
        try:
            scenes = self.client.get_scene_list().scenes
            for scene in scenes:
                self.client.remove_scene(scene["sceneName"])
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при удалении сцен: {e}")

    def create_main_scene(self, scene_name="SafeScene"):
        try:
            self.client.create_scene(scene_name)
            self.client.set_current_program_scene(scene_name)
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при создании/переключении сцены: {e}")

    def add_camera(self, scene_name="SafeScene",
                   input_name="Webcam1",
                   input_kind="dshow_input",
                   device_id="default"):
        try:
            inputs = self.client.get_input_list().inputs
            if any(inp["inputName"] == input_name for inp in inputs):
                print(f"Источник {input_name} уже существует, пропускаем создание")
                return

            self.client.create_input(
                sceneName=scene_name,
                inputName=input_name,
                inputKind=input_kind,
                inputSettings={"device_id": device_id},
                sceneItemEnabled=True
            )
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при добавлении камеры: {e}")

    def add_microphone(self, scene_name="SafeScene",
                       input_name="Mic1",
                       input_kind="wasapi_input_capture",
                       device_id="default"):
        try:
            inputs = self.client.get_input_list().inputs
            if any(inp["inputName"] == input_name for inp in inputs):
                print(f"Источник {input_name} уже существует, пропускаем создание")
                return

            self.client.create_input(
                sceneName=scene_name,
                inputName=input_name,
                inputKind=input_kind,
                inputSettings={"device_id": device_id},
                sceneItemEnabled=True
            )
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при добавлении микрофона: {e}")

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
