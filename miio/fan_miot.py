import logging

import click

from .click_common import EnumType, command, format_output
from .fan_common import FanException, MoveDirection, OperationMode
from .miot_spec_v2 import DeviceSpec
from .miot_v2_device import MiotV2Device

_LOGGER = logging.getLogger(__name__)

MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"
MODEL_FAN_P11 = "dmaker.fan.p11"


class PropertyAdapter:
    def __init__(
        self,
        service: str,
        property: str,
        value_decoder=lambda v: v,
        value_encoder=lambda v: v,
    ):
        self.service = service
        self.property = property
        self.value_decoder = value_decoder
        self.value_encoder = value_encoder


class FanMiotDeviceAdapter:
    def __init__(
        self,
        spec_file_name: str,
        spec=None,
        on=PropertyAdapter("fan", "on"),
        level=PropertyAdapter("fan", "fan-level"),
        lock=PropertyAdapter("physical-controls-locked", "physical-controls-locked"),
        speed=PropertyAdapter("fan", "speed-level"),
        swing=PropertyAdapter("fan", "horizontal-swing"),
        angle=PropertyAdapter("fan", "horizontal-angle"),
        off_delay=PropertyAdapter("fan", "off-delay-time"),
        alarm=PropertyAdapter("fan", "alarm"),
        brightness=PropertyAdapter("fan", "brightness"),
        mode=PropertyAdapter(
            "fan",
            "mode",
            value_decoder=lambda v: OperationMode.Normal
            if v == 0
            else OperationMode.Nature,
            value_encoder=lambda v: 0 if v == OperationMode.Normal else 1,
        ),
        motor_control=PropertyAdapter(
            "fan",
            "motor-control",
            value_encoder=lambda v: 1 if v == MoveDirection.Left else 2,
        ),
    ):
        self.spec_file_name = spec_file_name
        self.spec = DeviceSpec.load(spec_file_name) if spec is None else spec
        self.on = on
        self.level = level
        self.lock = lock
        self.speed = speed
        self.swing = swing
        self.angle = angle
        self.off_delay = off_delay
        self.alarm = alarm
        self.brightness = brightness
        self.mode = mode
        self.motor_control = motor_control

    def check_validation(self):
        for name, value in vars(self).items():
            if type(value) != PropertyAdapter:
                continue
            if not self.spec.contains(value.service, value.property):
                raise FanException(
                    f"invalid adapter for spec {self.spec_file_name}: "
                    f"service '{value.service}' property '{value.property}' not found"
                )


ADAPTERS = {
    MODEL_FAN_P9: FanMiotDeviceAdapter(
        "urn:miot-spec-v2:device:fan:0000A005:dmaker-p9:1.json"
    ),
    MODEL_FAN_P10: FanMiotDeviceAdapter(
        "urn:miot-spec-v2:device:fan:0000A005:dmaker-p10:1.json"
    ),
    MODEL_FAN_P11: FanMiotDeviceAdapter(
        "urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1.json",
        speed=PropertyAdapter("fan", "status"),
        off_delay=PropertyAdapter("off-delay-time", "off-delay-time"),
        alarm=PropertyAdapter("alarm", "alarm"),
        brightness=PropertyAdapter("indicator-light", "on"),
        motor_control=PropertyAdapter("motor-controller", "motor-control"),
    ),
}


class FanStatusMiot:
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan DMaker P9/P10/P10."""

    def __init__(self, rawData, spec: DeviceSpec, adapter: FanMiotDeviceAdapter):
        """
        Response of a FanMiot (dmaker.fan.p10):
        {
          'id': 1,
          'result': [
            {'did': 'fan.on', 'siid': 2, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'fan.fan-level', 'siid': 2, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'physical-controls-locked', 'siid': 3, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'fan.speed-level', 'siid': 2, 'piid': 10, 'code': 0, 'value': 54},
            {'did': 'fan.horizontal-swing', 'siid': 2, 'piid': 4, 'code': 0, 'value': False},
            {'did': 'fan.horizontal-angle', 'siid': 2, 'piid': 5, 'code': 0, 'value': 30},
            {'did': 'fan.off-delay-time', 'siid': 2, 'piid': 6, 'code': 0, 'value': 0},
            {'did': 'fan.alarm', 'siid': 2, 'piid': 8, 'code': 0, 'value': False},
            {'did': 'fan.brightness', 'siid': 2, 'piid': 7, 'code': 0, 'value': True},
            {'did': 'fan.mode', 'siid': 2, 'piid': 3, 'code': 0, 'value': 0}
          ],
          'exe_time': 280
        }
        """
        self.adapter = adapter
        self.data = {}
        for prop in rawData:
            if prop["code"] != 0:
                continue
            service = spec.find_service_by_iid(prop["siid"])
            property = service.find_property_by_iid(prop["piid"])
            service_name = service.type.name
            property_name = property.type.name
            if service_name not in self.data:
                self.data[service_name] = {}
            self.data[service_name][property_name] = prop["value"]

    def get_value(self, adapter: PropertyAdapter):
        return adapter.value_decoder(self.data[adapter.service][adapter.property])

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.get_value(self.adapter.on)

    @property
    def mode(self) -> OperationMode:
        """Operation mode."""
        return self.get_value(self.adapter.mode)

    @property
    def speed(self) -> int:
        """Speed of the motor."""
        return self.get_value(self.adapter.speed)

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.get_value(self.adapter.swing)

    @property
    def angle(self) -> int:
        """Oscillation angle."""
        return self.get_value(self.adapter.angle)

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.get_value(self.adapter.off_delay)

    @property
    def led(self) -> bool:
        """True if LED is turned on, if available."""
        return self.get_value(self.adapter.brightness)

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.get_value(self.adapter.alarm)

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.get_value(self.adapter.lock)

    def __repr__(self) -> str:
        s = (
            "<FanStatus power=%s, "
            "mode=%s, "
            "speed=%s, "
            "oscillate=%s, "
            "angle=%s, "
            "led=%s, "
            "buzzer=%s, "
            "child_lock=%s, "
            "delay_off_countdown=%s>"
            % (
                self.power,
                self.mode,
                self.speed,
                self.oscillate,
                self.angle,
                self.led,
                self.buzzer,
                self.child_lock,
                self.delay_off_countdown,
            )
        )
        return s


class FanMiot(MiotV2Device):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P10,
    ) -> None:
        if model in ADAPTERS:
            self.model = model
        else:
            raise FanException("Invalid FanMiot model: %s" % model)
        self.adapter = ADAPTERS[model]
        self.adapter.check_validation()
        super().__init__(
            self.adapter.spec,
            ip,
            token,
            start_id,
            debug,
            lazy_discover,
        )

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Operation mode: {result.mode}\n"
            "Speed: {result.speed}\n"
            "Oscillate: {result.oscillate}\n"
            "Angle: {result.angle}\n"
            "LED: {result.led}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown}\n",
        )
    )
    def status(self) -> FanStatusMiot:
        """Retrieve properties."""
        request_props = [
            (value.service, value.property)
            for name, value in vars(self.adapter).items()
            if type(value) == PropertyAdapter
        ]
        return FanStatusMiot(
            self.get_readable_properties(request_props), self.spec, self.adapter
        )

    def set_value(self, adapter: PropertyAdapter, value):
        return self.set_property(
            adapter.service, adapter.property, adapter.value_encoder(value)
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_value(self.adapter.on, True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_value(self.adapter.on, False)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.set_value(self.adapter.mode, mode)

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed to {speed}"),
    )
    def set_speed(self, speed: int):
        """Set speed."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.set_value(self.adapter.speed, speed)

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in [30, 60, 90, 120, 140]:
            raise FanException(
                "Unsupported angle. Supported values: 30, 60, 90, 120, 140"
            )

        return self.set_value(self.adapter.angle, angle)

    @command(
        click.argument("oscillate", type=bool),
        default_output=format_output(
            lambda oscillate: "Turning on oscillate"
            if oscillate
            else "Turning off oscillate"
        ),
    )
    def set_oscillate(self, oscillate: bool):
        """Set oscillate on/off."""
        if oscillate:
            return self.set_value(self.adapter.swing, True)
        else:
            return self.set_value(self.adapter.swing, False)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.set_value(self.adapter.brightness, True)
        else:
            return self.set_value(self.adapter.brightness, False)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.set_value(self.adapter.alarm, True)
        else:
            return self.set_value(self.adapter.alarm, False)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.set_value(self.adapter.lock, lock)

    @command(
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0:
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_value(self.adapter.off_delay, minutes)

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        return self.set_value(self.adapter.motor_control, direction)


class FanP9(FanMiot):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_P9)


class FanP10(FanMiot):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_P10)


class FanP11(FanMiot):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_P11)
