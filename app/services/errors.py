class RegistrationError(Exception):
    """A business-rule failure, reported against one form field (or the whole form)."""

    def __init__(self, message: str, field: str = "form") -> None:
        super().__init__(message)
        self.message = message
        self.field = field
