import os
import json
import copy

from subregions import SubregionManager

class SettingsManager():
    default_settings = {
        'location_folder': os.getcwd().replace('\\', '/') + '/output',
        'resolution': '1920x1080',
        'hud_scale': 100,
        'minimap_region': [1615, 25, 1895, 305],
        'auto_save': True
    }

    settings_file = 'settings.json'

    @staticmethod
    def reset_default_settings():
        return SettingsManager.save_settings(SettingsManager.default_settings)

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
            settings = SettingsManager.load_settings()
            for key in SettingsManager.default_settings.keys():
                if key not in settings.keys():
                    print(f'Could not find setting for {key} - updating with default')
                    settings = SettingsManager.change_setting(key, SettingsManager.default_settings[key])
            return settings

    @staticmethod
    def save_settings(settings):
        with open(SettingsManager.settings_file, 'w') as f:
            json.dump(settings, f)
        return settings

    @staticmethod
    def change_setting(setting, value):
        settings = SettingsManager.load_settings()
        if setting == 'minimap_region':
            value = SubregionManager.get_minimap_subregion(settings['resolution'], settings['hud_scale'])
        settings[setting] = value
        print(f'Changing setting: {setting} to {value}')
        if setting == 'resolution':
            sub = SubregionManager.get_minimap_subregion(value, settings['hud_scale'])
            settings['minimap_region'] = sub
        SettingsManager.save_settings(settings)
        return settings