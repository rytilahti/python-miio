from .device import Device


class ChuangmiIr(Device):
    """Main class representing Chuangmi IR Remote Controller."""

    def learn(self, key: int):
        """Learn a infrared command."""

        # The key is a storage slot. The value must be between 1 and 1000000
        return self.send("miIO.ir_learn", {'key': str(key)})

    def read(self, key: int):
        """Read a learned command."""
        return self.send("miIO.ir_read", {'key': str(key)})

    def play(self, command: str, frequency: int):
        """Play a captured command."""
        if frequency is None:
            frequency = 38400
        return self.send("miIO.ir_play",
                         {'freq': frequency, 'code': command})
