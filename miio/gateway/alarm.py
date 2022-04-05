"""Xiaomi Gateway Alarm implementation."""
import logging
from datetime import datetime

from .gatewaydevice import GatewayDevice

_LOGGER = logging.getLogger(__name__)


class Alarm(GatewayDevice):
    """Class representing the Xiaomi Gateway Alarm."""

    def status(self) -> str:
        """Return the alarm status from the device."""
        # Response: 'on', 'off', 'oning'
        return self._gateway.send("get_arming").pop()

    def on(self):
        """Turn alarm on."""
        return self._gateway.send("set_arming", ["on"])

    def off(self):
        """Turn alarm off."""
        return self._gateway.send("set_arming", ["off"])

    def arming_time(self) -> int:
        """Return time in seconds the alarm stays 'oning' before transitioning to
        'on'."""
        # Response: 5, 15, 30, 60
        return self._gateway.send("get_arm_wait_time").pop()

    def set_arming_time(self, seconds):
        """Set time the alarm stays at 'oning' before transitioning to 'on'."""
        return self._gateway.send("set_arm_wait_time", [seconds])

    def triggering_time(self) -> int:
        """Return the time in seconds the alarm is going off when triggered."""
        # Response: 30, 60, etc.
        return self._gateway.get_prop("alarm_time_len").pop()

    def set_triggering_time(self, seconds):
        """Set the time in seconds the alarm is going off when triggered."""
        return self._gateway.set_prop("alarm_time_len", seconds)

    def triggering_light(self) -> int:
        """Return the time the gateway light blinks when the alarm is triggerd."""
        # Response: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.get_prop("en_alarm_light").pop()

    def set_triggering_light(self, seconds):
        """Set the time the gateway light blinks when the alarm is triggerd."""
        # values: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.set_prop("en_alarm_light", seconds)

    def triggering_volume(self) -> int:
        """Return the volume level at which alarms go off [0-100]."""
        return self._gateway.send("get_alarming_volume").pop()

    def set_triggering_volume(self, volume):
        """Set the volume level at which alarms go off [0-100]."""
        return self._gateway.send("set_alarming_volume", [volume])

    def last_status_change_time(self) -> datetime:
        """Return the last time the alarm changed status."""
        return datetime.fromtimestamp(self._gateway.send("get_arming_time").pop())

    def install_push_callbacks(self):
        """Generate and install script which captures events and sends miio package to
        the push server."""
        if self._gateway._push_server is None:
            _LOGGER.error("Can not install push callback withouth a push_server")
            return False

        if self._gateway._push_server.server_ip is None:
            _LOGGER.error(
                "Can not install push callback withouth starting the push_server"
            )
            return False

        alarm_scripts = {"alarm_triggering": {"extra": "[1,19,1,111,[0,1],2,0]"}}

        for action in alarm_scripts:
            self._gateway._gatway_script_i = self._gateway._gatway_script_i + 1
            script_id = f"x.scene.{self._gateway._gatway_script_i}000000"

            script = self._gateway._push_server.construct_script(
                script_id=script_id,
                action=action,
                extra=alarm_scripts[action]["extra"],
                source_sid=str(self._gateway.device_id),
                source_model=self._gateway.model,
                source_token=self._gateway.token,
                trigger_token=self._gateway.token,
            )

            result = self._gateway.install_script(script_id, script)
            if result == ["ok"]:
                self._script_ids.append(script_id)
            else:
                _LOGGER.error(
                    "Error installing script_id %s, response %s, script_data %s",
                    script_id,
                    result,
                    script,
                )

        return True

    def uninstall_push_callbacks(self):
        """uninstall scripts registered in the gateway memory."""
        for script_id in self._script_ids:
            self._gateway.delete_script(script_id)
            if script_id in self._script_ids:
                self._script_ids.remove(script_id)
