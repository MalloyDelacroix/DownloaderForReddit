from Core.SettingsManager import SettingsManager


settings_manager = None
count = 1

def get_settings_manager():
    global settings_manager
    global count
    if settings_manager is None:
        settings_manager = SettingsManager()
        settings_manager.count = count
        count += 1
    return settings_manager
