import json
import obsws_python as obs

from collections import OrderedDict
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

    @staticmethod
    def reorder_scenario(data):

        def sort_object(obj):
            if isinstance(obj, dict):
                return OrderedDict((k, sort_object(v)) for k, v in sorted(obj.items()))
            elif isinstance(obj, list):
                return [sort_object(v) for v in obj]
            else:
                return obj

        def sort_with_name(obj):
            if isinstance(obj, dict):
                ordered = OrderedDict()
                if "name" in obj:
                    ordered["name"] = sort_object(obj["name"])
                for k in sorted(obj.keys()):
                    if k != "name":
                        ordered[k] = sort_object(obj[k])
                return ordered
            return obj

        def sort_with_inputName(obj):
            if isinstance(obj, dict):
                ordered = OrderedDict()
                if "inputName" in obj:
                    ordered["inputName"] = sort_object(obj["inputName"])
                for k in sorted(obj.keys()):
                    if k != "inputName":
                        ordered[k] = sort_object(obj[k])
                return ordered
            return obj

        def sort_inputSettings(obj):
            if isinstance(obj, dict):
                ordered = OrderedDict()
                if "device_id" in obj:
                    ordered["device_id"] = sort_object(obj["device_id"])
                if "video_device_id" in obj:
                    ordered["video_device_id"] = sort_object(obj["video_device_id"])
                if "window" in obj:
                    ordered["window"] = sort_object(obj["window"])
                for k in sorted(obj.keys()):
                    if k not in ("device_id", "video_device_id", "window"):
                        ordered[k] = sort_object(obj[k])
                return ordered
            return obj

        def sort_with_sourceName(obj):
            if isinstance(obj, dict):
                ordered = OrderedDict()
                if "sourceName" in obj:
                    ordered["sourceName"] = sort_object(obj["sourceName"])
                for k in sorted(obj.keys()):
                    if k != "sourceName":
                        ordered[k] = sort_object(obj[k])
                return ordered
            return obj

        def sort_scene(obj):
            if isinstance(obj, dict):
                ordered = OrderedDict()
                if "name" in obj:
                    ordered["name"] = sort_object(obj["name"])
                if "items" in obj and isinstance(obj["items"], list):
                    items = sorted(obj["items"], key=lambda x: x.get("sourceName", ""))
                    new_items = [sort_with_sourceName(it) for it in items]
                    ordered["items"] = new_items
                for k in sorted(obj.keys()):
                    if k not in ("name", "items"):
                        ordered[k] = sort_object(obj[k])
                return ordered
            return obj

        ordered = OrderedDict()

        for key in ["profile", "inputs", "scenes"]:
            if key in data:
                if key == "profile" and isinstance(data[key], dict):
                    data[key] = sort_with_name(data[key])
                elif key == "inputs" and isinstance(data[key], list):
                    data[key] = sorted(data[key], key=lambda x: x.get("inputName", ""))
                    new_inputs = []
                    for inp in data[key]:
                        inp_ordered = sort_with_inputName(inp)
                        if "inputSettings" in inp_ordered and isinstance(inp_ordered["inputSettings"], dict):
                            inp_ordered["inputSettings"] = sort_inputSettings(inp_ordered["inputSettings"])
                        new_inputs.append(inp_ordered)
                    data[key] = new_inputs
                elif key == "scenes" and isinstance(data[key], list):
                    data[key] = sorted(data[key], key=lambda x: x.get("name", ""))
                    data[key] = [sort_scene(scene) for scene in data[key]]
                ordered[key] = data[key]

        for key in sorted(k for k in data.keys() if k not in ["profile", "inputs", "scenes"]):
            ordered[key] = sort_object(data[key])

        return ordered

    def save_to_file(self, filename="scene_collection.json"):
        data = self.export_scene_collection()
        ordered_data = OBSExportImport.reorder_scenario(data)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ordered_data, f, ensure_ascii=False, indent=2)

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
