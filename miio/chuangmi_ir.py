from .device import Device, DeviceException


class ChuangmiIr(Device):
    """Main class representing Chuangmi IR Remote Controller."""

    def learn(self, key: int):
        """Learn an infrared command.

        :param int key: Storage slot, must be between 1 and 1000000"""

        if key < 1 or key > 1000000:
            raise DeviceException("Invalid parameter FIXME wrong exception")
        return self.send("miIO.ir_learn", {'key': str(key)})

    def read(self, key: int):
        """Read a learned command.

        FIXME what is the return value? Examples needed.

        :param int key: Slot to read from"""
        return self.send("miIO.ir_read", {'key': str(key)})

    def play(self, command: str, frequency: int):
        """Play a captured command.

        :param str command: Command to execute
        :param int frequence: Execution frequency"""
        if frequency is None:
            frequency = 38400
        return self.send("miIO.ir_play",
                         {'freq': frequency, 'code': command})
