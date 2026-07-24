import json
import os

SETTINGS_PATH = "settings.json"

class file:
    @staticmethod
    def create(force:bool=False):
        if os.path.exists(SETTINGS_PATH) and not force:
            return
        with open(SETTINGS_PATH, "w") as f:
            json.dump({}, f)

    @staticmethod
    def read():
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)

if not os.path.exists(SETTINGS_PATH):
    file.create()

class BaseSetting:
    def __init__(self, name:str, default_value):
        self.name = name
        self.default_value = default_value

    def get(self):
        settings = file.read()
        return settings.get(self.name, self.default_value)

    def set(self, value):
        settings = file.read()
        settings[self.name] = value
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f)
        return True

class settings:
    # Determines if this instance is intended to be a data receiving end-point from other Doctor instances.
    # Alerts for OTHER computers.
    class HubMode(BaseSetting):
        def __init__(self):
            super().__init__("hub_mode", False)
    # Determines what level of "pedanticness" doctor checks with.
    # At verbosity 4, even just the kernel being tainted by propriety nvidia drivers is checked for.
    class Verbosity(BaseSetting):
        def __init__(self):
            super().__init__("verbosity", 3)  # 4 = highest possible
    # The below setting is used to uniquely identify the computer in Hub mode, and also, in a diagnosis report, allows you to distinquish if the report
    # came from another computer.
    class pc_uuid4(BaseSetting):
        def __init__(self):
            super().__init__("pc_uuid4", None)
    # This is a setting to determine how we notify users. Headless means either there's no desktop, or nobody ever checks it.
    # If its headless, and hub mode is enabled, we send it to the hub. The difference between this and hub mode is, on hub mode, 
    # if it was not headless, we would still notify the user. 
    class headless(BaseSetting):
        def __init__(self):
            super().__init__("headless", False)
    # This setting is for critical services that are not included in the original list.
    class extra_critical_services(BaseSetting):
        def __init__(self):
            super().__init__("extra_critical_services", [])

        def append(self, value: str):
            data: dict = file.read()
            if not self.name in data.keys():
                data[self.name] = []
            data[self.name].append(value)