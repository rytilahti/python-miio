import datetime
import hashlib
import json
import logging
import calendar

from construct import (Struct, Bytes, Const, Int16ub, Int32ub, GreedyBytes,
                       Adapter, Checksum, RawCopy, Rebuild, IfThenElse,
                       Default, Probe, Pointer, Pass, Enum)

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

_LOGGER = logging.getLogger(__name__)

# Map of device ids
xiaomi_devices = {0x02f2: "Xiaomi Mi Robot Vacuum",
                  0x00c4: "Xiaomi Smart Mi Air Purifier",
                  0x031a: "Xiaomi Smart home gateway",
                  0x0330: "Yeelight color bulb"
                  }
xiaomi_devices = {y: x for x, y in xiaomi_devices.items()}


class Utils:
    """ This class is adapted from the original xpn.py code by gst666 """
    # TODO nicer way to handle tokens
    token = ""

    @staticmethod
    def md5(data):
        checksum = hashlib.md5()
        checksum.update(data)
        return checksum.digest()

    @staticmethod
    def key_iv():
        key = Utils.md5(Utils.token)
        iv = Utils.md5(key + Utils.token)
        return key, iv

    @staticmethod
    def encrypt(plaintext):
        key, iv = Utils.key_iv()
        padder = padding.PKCS7(128).padder()

        padded_plaintext = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=default_backend())

        encryptor = cipher.encryptor()
        return encryptor.update(padded_plaintext) + encryptor.finalize()

    @staticmethod
    def decrypt(ciphertext):
        key, iv = Utils.key_iv()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=default_backend())

        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        unpadded_plaintext = unpadder.update(padded_plaintext) \
                             + unpadder.finalize()
        return unpadded_plaintext

    @staticmethod
    def checksum_field_bytes(ctx):
        """Gatherd bytes for checksum calculation"""
        # print("CHECKSUM: %s" % ctx["header"])
        if Utils.token is None:
            raise Exception("you have to define token")
        # print("CTX: %s" % ctx)
        x = bytearray(ctx["header"].data)
        x += Utils.token
        if "data" in ctx:
            x += ctx["data"].data
            # print("DATA: %s" % ctx["data"])

        return x

    @staticmethod
    def get_length(x):
        """Return total packet length."""
        datalen = x._.data.length
        return datalen + 32

    @staticmethod
    def is_hello(x):
        """Return if packet is a hello packet."""
        # not very nice, but we know that hellos are 32b of length
        if 'length' in x:
            val = x['length']
        else:
            val = x.header.value['length']

        return val == 32


class TimeAdapter(Adapter):
    """Adapter for timestamp conversion."""
    def _encode(self, obj, context):
        return calendar.timegm(obj.timetuple())

    def _decode(self, obj, context):
        return datetime.datetime.fromtimestamp(obj)


class EncryptionAdapter(Adapter):
    """Adapter to handle communication encryption."""
    def _encode(self, obj, context):
        return Utils.encrypt(json.dumps(obj).encode('utf-8') + b'\x00')

    def _decode(self, obj, context):
        try:
            decrypted = Utils.decrypt(obj).rstrip(b"\x00")
        except Exception as ex:
            _LOGGER.warning("Unable to decrypt, returning raw bytes.")
            return obj

        try:
            jsoned = json.loads(decrypted.decode('utf-8'))
        except:
            _LOGGER.error("unable to parse json, was: %s", decrypted)
            jsoned = b'{}'
            raise

        return jsoned


Message = Struct(
    # for building we need data before anything else.
    "data" / Pointer(32, RawCopy(EncryptionAdapter(GreedyBytes))),
    "header" / RawCopy(Struct(
        Const(Int16ub, 0x2131),
        "length" / Rebuild(Int16ub, Utils.get_length),
        "unknown" / Default(Int32ub, 0x00000000),
        "devtype" / Enum(Default(Int16ub, 0x02f2), default=Pass, **xiaomi_devices),
        "serial" / Default(Int16ub, 0xa40d),
        "ts" / TimeAdapter(Default(Int32ub, datetime.datetime.utcnow()))
    )),
    "checksum" / IfThenElse(Utils.is_hello,
                            Bytes(16),
                            Checksum(Bytes(16),
                                     Utils.md5,
                                     Utils.checksum_field_bytes)),
)
