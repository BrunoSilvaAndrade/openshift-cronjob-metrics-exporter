class StructValidateException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StructColectorsException(StructValidateException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)