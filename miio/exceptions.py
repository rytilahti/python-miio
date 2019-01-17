class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""
    pass


class DeviceError(DeviceException):
    """Exception communicating an error delivered by the target device."""
    pass


class RecoverableError(DeviceError):
    """Exception communicating an recoverable error delivered by the target device."""
    pass
