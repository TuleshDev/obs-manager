import traceback
from obsws_python import ReqClient

class ObsActions:
    def __init__(self, host="127.0.0.1", port=4455, password="mysecret"):
        try:
            self.ws = ReqClient(host=host, port=port, password=password)
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка подключения к OBS WebSocket: {e}")

    def clear_scenes(self):
        try:
            scenes = self.ws.get_scene_list().scenes
            for scene in scenes:
                self.ws.remove_scene(scene["sceneName"])
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при удалении сцен: {e}")

    def create_main_scene(self, scene_name="SafeScene"):
        try:
            self.ws.create_scene(scene_name)
            self.ws.set_current_program_scene(scene_name)
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при создании/переключении сцены: {e}")

    def add_camera(self, scene_name="SafeScene",
                   input_name="Webcam1",
                   input_kind="dshow_input",
                   device_id="default"):
        try:
            inputs = self.ws.get_input_list().inputs
            if any(inp["inputName"] == input_name for inp in inputs):
                print(f"Источник {input_name} уже существует, пропускаем создание")
                return

            self.ws.create_input(
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
            inputs = self.ws.get_input_list().inputs
            if any(inp["inputName"] == input_name for inp in inputs):
                print(f"Источник {input_name} уже существует, пропускаем создание")
                return

            self.ws.create_input(
                sceneName=scene_name,
                inputName=input_name,
                inputKind=input_kind,
                inputSettings={"device_id": device_id},
                sceneItemEnabled=True
            )
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Ошибка при добавлении микрофона: {e}")
