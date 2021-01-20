class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""


class PayloadDecodeException(DeviceException):
    """Exception for failures in payload decoding.

    This is raised when the json payload cannot be decoded, indicating invalid response
    from a device.
    """


class DeviceInfoUnavailableException(DeviceException):
    """Exception raised when requesting miio.info fails.

    This allows users to gracefully handle cases where the information unavailable. This
    can happen, for instance, when the device has no cloud access.
    """


class DeviceError(DeviceException):
    """Exception communicating an error delivered by the target device.

    The device given error code and message can be accessed with  `code` and `message`
    variables.
    """

    def __init__(self, error):
        self.code = error.get("code")
        self.message = error.get("message")


class RecoverableError(DeviceError):
    """Exception communicating an recoverable error delivered by the target device."""
