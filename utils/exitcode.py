class _ExitCode:
    exit_codes=["OK","FAIL"]
    def __getattr__(self, name):  
        if name in _ExitCode.exit_codes:
            return _ExitCode.exit_codes.index(name)
        raise AttributeError("Exit code %s not found" % name)