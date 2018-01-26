import base64
from construct import (
    Struct, Const, Rebuild, this, len_, Adapter, Computed,
    Int16ul, Int32ul, Int16ub, Array, BitStruct, BitsInteger,
)
from .device import Device, DeviceException


class ChuangmiIrException(DeviceException):
    pass


class ChuangmiIr(Device):
    """Main class representing Chuangmi IR Remote Controller."""

    def learn(self, key: int):
        """Learn an infrared command.

        :param int key: Storage slot, must be between 1 and 1000000"""

        if key < 1 or key > 1000000:
            raise ChuangmiIrException("Invalid storage slot.")
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

    def play_pronto(self, pronto: str, repeats: int=0):
        """Play a Pronto Hex encoded IR command.
        Supports only raw Pronto format, starting with 0000.

        :param str pronto: Pronto Hex string.
        :param int repeats: Number of extra signal repeats."""
        if repeats < 0:
            raise ChuangmiIrException('Invalid repeats value')

        try:
            pronto_data = Pronto.parse(bytearray.fromhex(pronto))
        except Exception as ex:
            raise ChuangmiIrException from ex

        if len(pronto_data.intro) == 0:
            repeats += 1

        times = set()
        for pair in pronto_data.intro + pronto_data.repeat * (1 if repeats else 0):
            times.add(pair.pulse)
            times.add(pair.gap)

        times = sorted(times)
        times_map = {t: idx for idx, t in enumerate(times)}
        edge_pairs = []
        for pair in pronto_data.intro + pronto_data.repeat * repeats:
            edge_pairs.append({
                'pulse': times_map[pair.pulse],
                'gap': times_map[pair.gap],
            })

        signal_code = base64.b64encode(ChuangmiIrSignal.build({
            'times_index': times + [0] * (16 - len(times)),
            'edge_pairs': edge_pairs,
        })).decode()

        return self.play(signal_code, int(round(pronto_data.frequency)))


class ProntoPulseAdapter(Adapter):
    def _decode(self, obj, context):
        return int(obj * context._.modulation_period)

    def _encode(self, obj, context):
        raise RuntimeError('Not implemented')


ChuangmiIrSignal = Struct(
    Const(0xa567, Int16ul),
    'edge_count' / Rebuild(Int16ul, len_(this.edge_pairs) * 2 - 1),
    'times_index' / Array(16, Int32ul),
    'edge_pairs' / Array((this.edge_count + 1) / 2, BitStruct(
        'gap' / BitsInteger(4),
        'pulse' / BitsInteger(4),
    ))
)

ProntoBurstPair = Struct(
    'pulse' / ProntoPulseAdapter(Int16ub),
    'gap' / ProntoPulseAdapter(Int16ub),
)

Pronto = Struct(
    Const(0, Int16ub),
    '_ticks' / Int16ub,
    'modulation_period' / Computed(this._ticks * 0.241246),
    'frequency' / Computed(1000000 / this.modulation_period),
    'intro_len' / Int16ub,
    'repeat_len' / Int16ub,
    'intro' / Array(this.intro_len, ProntoBurstPair),
    'repeat' / Array(this.repeat_len, ProntoBurstPair),
)
