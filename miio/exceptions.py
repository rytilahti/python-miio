class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""

    pass


class DeviceError(DeviceException):
    """Exception communicating an error delivered by the target device."""

    def __init__(self, error):
        self.code = error.get("code")
        self.message = error.get("message")


class RecoverableError(DeviceError):
    """Exception communicating an recoverable error delivered by the target device."""

    pass
