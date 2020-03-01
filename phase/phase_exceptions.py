class NoPhasesException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Attempted to start a pipeline with no phases.")
