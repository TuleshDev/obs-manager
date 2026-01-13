import json
import obsws_python as obs

from libs.obs_actions import ObsActions


class OBSExportImport:
    def __init__(self, client: obs.ReqClient):
        self.client = client

    def export_scene_collection(self):
        result = self.client.get_scene_list()
        scenes = []

        for scene in result.scenes:
            scene_name = scene["sceneName"]
            scene_data = {
                "name": scene_name,
                "items": [],
                "filters": []
            }

            try:
                flist = self.client.get_source_filter_list(scene_name).filters
                for f in flist:
                    fsettings = self.client.get_source_filter(scene_name, f["filterName"]).filterSettings
                    scene_data["filters"].append({
                        "name": f["filterName"],
                        "kind": f["filterKind"],
                        "settings": fsettings
                    })
            except Exception:
                pass

            items_resp = self.client.get_scene_item_list(scene_name)
            items = items_resp.scene_items
            for item in items:
                input_name = item["sourceName"]
                input_kind = None
                input_settings = {}
                filters = []

                try:
                    input_info = self.client.get_input_settings(input_name)
                    input_kind = input_info.inputKind
                    input_settings = input_info.inputSettings

                    flist = self.client.get_source_filter_list(input_name).filters
                    for f in flist:
                        fsettings = self.client.get_source_filter(input_name, f["filterName"]).filterSettings
                        filters.append({
                            "name": f["filterName"],
                            "kind": f["filterKind"],
                            "settings": fsettings
                        })
                except Exception:
                    pass

                transform_resp = self.client.get_scene_item_transform(scene_name, item["sceneItemId"])
                transform = transform_resp.scene_item_transform

                scene_data["items"].append({
                    "sourceName": input_name,
                    "inputKind": input_kind,
                    "inputSettings": input_settings,
                    "transform": transform,
                    "filters": filters
                })

            scenes.append(scene_data)

        transitions = []
        try:
            tlist = self.client.get_transition_list().transitions
            for t in tlist:
                tsettings = self.client.get_transition_settings(t["transitionName"]).transitionSettings
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
            plist = self.client.get_profile_list().profiles
            current_profile = self.client.get_current_profile().profileName

            for p in plist:
                self.client.set_current_profile(p["profileName"])
                vsettings = self.client.get_video_settings()
                asettings = self.client.get_audio_settings()

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
        for scene in data.get("scenes", []):
            scene_name = scene["name"]
            self.client.create_scene(scene_name)

            for f in scene.get("filters", []):
                self.client.create_source_filter(
                    scene_name, f["name"], f["kind"], f["settings"]
                )

            for item in scene.get("items", []):
                inputs = [i["inputName"] for i in self.client.get_input_list().inputs]
                if item["sourceName"] not in inputs:
                    self.client.create_input(
                        scene_name,
                        item["sourceName"],
                        item["inputKind"],
                        item["inputSettings"],
                        True
                    )

                si = self.client.create_scene_item(scene_name, item["sourceName"])
                self.client.set_scene_item_transform(
                    scene_name,
                    si.scene_item_id,
                    item["transform"]
                )

                for f in item.get("filters", []):
                    self.client.create_source_filter(
                        item["sourceName"], f["name"], f["kind"], f["settings"]
                    )

        for t in data.get("transitions", []):
            self.client.create_transition(t["name"], t["kind"], t["settings"])

        for p in data.get("profiles", []):
            self.client.create_profile(p["name"])
            self.client.set_current_profile(p["name"])
            self.client.set_video_settings(
                baseWidth=p["video"]["baseWidth"],
                baseHeight=p["video"]["baseHeight"],
                outputWidth=p["video"]["outputWidth"],
                outputHeight=p["video"]["outputHeight"],
                fpsNumerator=p["video"]["fpsNumerator"],
                fpsDenominator=p["video"]["fpsDenominator"]
            )
            self.client.set_audio_settings(
                sampleRate=p["audio"]["sampleRate"],
                channels=p["audio"]["channels"]
            )

        if "currentProfile" in data:
            self.client.set_current_profile(data["currentProfile"])

    def load_from_file(self, filename="scene_collection.json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.import_scene_collection(data)
