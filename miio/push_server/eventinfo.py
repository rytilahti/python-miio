from typing import Any

import attr


@attr.s(auto_attribs=True)
class EventInfo:
    """Event info to register to the push server.

    action: user friendly name of the event, can be set arbitrarily and will be received by the server as the name of the event.
    extra: the identification of this event, this determines on what event the callback is triggered.
    event: defaults to the action.
    command_extra: will be received by the push server, hopefully this will allow us to obtain extra information about the event for instance the vibration intesisty or light level that triggered the event (still experimental).
    trigger_value: Only needed if the trigger has a certain threshold value (like a temperature for a wheather sensor), a "value" key will be present in the first part of a scene packet capture.
    trigger_token: Only needed for protected events like the alarm feature of a gateway, equal to the "token" of the first part of of a scene packet caputure.
    source_sid: Normally not needed and obtained from device, only needed for zigbee devices: the "did" key.
    source_model: Normally not needed and obtained from device, only needed for zigbee devices: the "model" key.
    """

    action: str
    extra: str
    event: str | None = None
    command_extra: str = ""
    trigger_value: Any | None = None
    trigger_token: str = ""
    source_sid: str | None = None
    source_model: str | None = None
