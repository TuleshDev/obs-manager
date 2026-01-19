import json
import obsws_python as obs

from libs.hints import SKIP_NAMES
from libs.obs_actions import ObsActions

class OBSExportImport:
    def __init__(self, obs: ObsActions):
        self.obs = obs

    def export_scene_collection(self):
        result = self.obs.client.get_scene_list()
        scenes = []
        inputs = []

        try:
            inputs_resp = self.obs.client.get_input_list()
            for inp in inputs_resp.inputs:
                if inp["inputName"] in SKIP_NAMES:
                    try:
                        settings_resp = self.obs.client.get_input_settings(inp["inputName"])
                        inputs.append({
                            "inputName": inp["inputName"],
                            "inputKind": inp["inputKind"],
                            "inputSettings": settings_resp.input_settings
                        })
                    except Exception:
                        continue
        except Exception:
            pass

        for scene in result.scenes:
            scene_name = scene["sceneName"]
            scene_data = {
                "name": scene_name,
                "items": [],
                "filters": []
            }

            try:
                flist = self.obs.client.get_source_filter_list(scene_name).filters
                for f in flist:
                    fsettings = self.obs.client.get_source_filter(scene_name, f["filterName"]).filterSettings
                    scene_data["filters"].append({
                        "name": f["filterName"],
                        "kind": f["filterKind"],
                        "settings": fsettings
                    })
            except Exception:
                pass

            items_resp = self.obs.client.get_scene_item_list(scene_name)
            for item in items_resp.scene_items:
                input_name = item["sourceName"]
                filters = []

                try:
                    flist = self.obs.client.get_source_filter_list(input_name).filters
                    for f in flist:
                        fsettings = self.obs.client.get_source_filter(input_name, f["filterName"]).filterSettings
                        filters.append({
                            "name": f["filterName"],
                            "kind": f["filterKind"],
                            "settings": fsettings
                        })
                except Exception:
                    pass

                transform_resp = self.obs.client.get_scene_item_transform(scene_name, item["sceneItemId"])
                transform = transform_resp.scene_item_transform

                scene_data["items"].append({
                    "sourceName": input_name,
                    "transform": transform,
                    "filters": filters
                })

            scenes.append(scene_data)

        transitions = []
        try:
            tlist = self.obs.client.get_transition_list().transitions
            for t in tlist:
                tsettings = self.obs.client.get_transition_settings(t["transitionName"]).transitionSettings
                transitions.append({
                    "name": t["transitionName"],
                    "kind": t["transitionKind"],
                    "settings": tsettings
                })
        except Exception:
            pass

        profiles = []
        current_profile = None
        try:
            plist = self.obs.client.get_profile_list().profiles
            current_profile = self.obs.client.get_current_profile().profileName

            for p in plist:
                self.obs.client.set_current_profile(p["profileName"])
                vsettings = self.obs.client.get_video_settings()
                asettings = self.obs.client.get_audio_settings()

                profiles.append({
                    "name": p["profileName"],
                    "video": {
                        "baseWidth": vsettings.baseWidth,
                        "baseHeight": vsettings.baseHeight,
                        "outputWidth": vsettings.outputWidth,
                        "outputHeight": vsettings.outputHeight,
                        "fpsNumerator": vsettings.fpsNumerator,
                        "fpsDenominator": vsettings.fpsDenominator
                    },
                    "audio": {
                        "sampleRate": asettings.sampleRate,
                        "channels": asettings.channels
                    }
                })
        except Exception:
            pass

        return {
            "inputs": inputs,
            "scenes": scenes,
            "currentScene": result.current_program_scene_name,
            "transitions": transitions,
            "profiles": profiles,
            "currentProfile": current_profile
        }

    def save_to_file(self, filename="scene_collection.json"):
        data = self.export_scene_collection()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_scene_collection(self, data):
        temp_scene = self.obs.ensure_unique_scene_name("TempImportScene")

        scenes = self.obs.client.get_scene_list().scenes
        if not any(s["sceneName"] == temp_scene for s in scenes):
            self.obs.client.create_scene(temp_scene)

        existing_inputs = {i["inputName"]: i for i in self.obs.client.get_input_list().inputs}
        for inp in data.get("inputs", []):
            name = inp["inputName"]
            if name in existing_inputs:
                try:
                    self.obs.client.set_input_settings(name, inp.get("inputSettings", {}), True)
                except Exception:
                    pass
            else:
                self.obs.client.create_input(
                    sceneName=temp_scene,
                    inputName=name,
                    inputKind=inp["inputKind"],
                    inputSettings=inp.get("inputSettings", {}),
                    sceneItemEnabled=True
                )

        for scene in data.get("scenes", []):
            scene_name = scene["name"]
            scenes = self.obs.client.get_scene_list().scenes
            if not any(s["sceneName"] == scene_name for s in scenes):
                self.obs.client.create_scene(scene_name)

        current_scene = data.get("currentScene", "")
        if current_scene:
            existing_inputs = {i["inputName"]: i for i in self.obs.client.get_input_list().inputs}
            for inp in data.get("inputs", []):
                name = inp["inputName"]
                if name in existing_inputs:
                    try:
                        self.obs.client.set_input_settings(name, inp.get("inputSettings", {}), True)
                    except Exception:
                        pass
                else:
                    self.obs.client.create_input(
                        sceneName=current_scene,
                        inputName=name,
                        inputKind=inp["inputKind"],
                        inputSettings=inp.get("inputSettings", {}),
                        sceneItemEnabled=True
                    )

        for scene in data.get("scenes", []):
            scene_name = scene["name"]

            for f in scene.get("filters", []):
                self.obs.client.create_source_filter(scene_name, f["name"], f["kind"], f["settings"])

            for item in scene.get("items", []):
                src = item["sourceName"]
                si = self.obs.client.create_scene_item(scene_name, src)
                self.obs.client.set_scene_item_transform(scene_name, si.scene_item_id, item["transform"])

                for f in item.get("filters", []):
                    self.obs.client.create_source_filter(src, f["name"], f["kind"], f["settings"])

        for t in data.get("transitions", []):
            self.obs.client.create_transition(t["name"], t["kind"], t["settings"])

        for p in data.get("profiles", []):
            self.obs.client.create_profile(p["name"])
            self.obs.client.set_current_profile(p["name"])
            self.obs.client.set_video_settings(
                baseWidth=p["video"]["baseWidth"],
                baseHeight=p["video"]["baseHeight"],
                outputWidth=p["video"]["outputWidth"],
                outputHeight=p["video"]["outputHeight"],
                fpsNumerator=p["video"]["fpsNumerator"],
                fpsDenominator=p["video"]["fpsDenominator"]
            )
            self.obs.client.set_audio_settings(
                sampleRate=p["audio"]["sampleRate"],
                channels=p["audio"]["channels"]
            )

        current_profile = data.get("currentProfile")
        if current_profile:
            self.obs.client.set_current_profile(current_profile)

        try:
            self.obs.client.remove_scene(temp_scene)
        except Exception:
            pass

    def load_from_file(self, filename="scene_collection.json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.import_scene_collection(data)
