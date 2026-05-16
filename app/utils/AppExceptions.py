class AppBaseException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __call__(self, *args, **kwargs):
        return self.message