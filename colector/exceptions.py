class ColectorError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ColectorInitError(ColectorError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ColectorGetLogsError(ColectorError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ColectorGetPodsError(ColectorError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)