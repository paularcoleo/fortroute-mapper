import os
import json

class SettingsManager():
    default_settings = {
        'location_folder': '',
        'resolution': '1920x1080'
    }

    settings_file = 'settings.json'

    @staticmethod
    def reset_default_settings():
        with open(SettingsManager.settings_file, 'w') as f:
            json.dump(SettingsManager.default_settings, f)
        return SettingsManager.default_settings

    @staticmethod
    def load_settings():
        with open(SettingsManager.settings_file, 'r') as f:
            settings = json.load(f)
        return settings

    @staticmethod
    def initialize_settings():
        if not os.path.isfile(SettingsManager.settings_file):
            print('No Settings File found - initializing settings')
            SettingsManager.reset_default_settings()
            return SettingsManager.default_settings
        else:
            return SettingsManager.load_settings()

    @staticmethod
    def change_setting(setting, value):
        settings = SettingsManager.load_settings()
        settings[setting] = value
        with open(SettingsManager.settings_file, 'w') as f:
            json.dump(settings, f)
        return settings