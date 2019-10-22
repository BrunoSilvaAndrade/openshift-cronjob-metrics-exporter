class ConfigException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConfigTimerException(ConfigException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)