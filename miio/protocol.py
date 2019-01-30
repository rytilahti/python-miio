"""miIO protocol implementation

This module contains the implementation of the routines to encrypt and decrypt
miIO payloads with a device-specific token.

The payloads to be encrypted (to be passed to a device) are excpected to be
JSON objects, the same applies for decryption where they are converted
automatically to JSON objects.
If the decryption fails, raw bytes as returned by the device are returned.

An usage example can be seen in the source of :func:`miio.Device.send`.
"""
import calendar
import datetime
import hashlib
import json
import logging
from typing import Any, Dict, Tuple

import construct
from construct import (Struct, Bytes, Const, Int16ub, Int32ub, GreedyBytes,
                       Adapter, Checksum, RawCopy, Rebuild, IfThenElse,
                       Default, Pointer, Hex, )
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_LOGGER = logging.getLogger(__name__)


class Utils:
    """ This class is adapted from the original xpn.py code by gst666 """

    @staticmethod
    def verify_token(token: bytes):
        """Checks if the given token is of correct type and length."""
        if not isinstance(token, bytes):
            raise TypeError("Token must be bytes")
        if len(token) != 16:
            raise ValueError("Wrong token length")

    @staticmethod
    def md5(data: bytes) -> bytes:
        """Calculates a md5 hashsum for the given bytes object."""
        checksum = hashlib.md5()
        checksum.update(data)
        return checksum.digest()

    @staticmethod
    def key_iv(token: bytes) -> Tuple[bytes, bytes]:
        """Generate an IV used for encryption based on given token."""
        key = Utils.md5(token)
        iv = Utils.md5(key + token)
        return key, iv

    @staticmethod
    def encrypt(plaintext: bytes, token: bytes) -> bytes:
        """Encrypt plaintext with a given token.

        :param bytes plaintext: Plaintext (json) to encrypt
        :param bytes token: Token to use
        :return: Encrypted bytes"""
        if not isinstance(plaintext, bytes):
            raise TypeError("plaintext requires bytes")
        Utils.verify_token(token)
        key, iv = Utils.key_iv(token)
        padder = padding.PKCS7(128).padder()

        padded_plaintext = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=default_backend())

        encryptor = cipher.encryptor()
        return encryptor.update(padded_plaintext) + encryptor.finalize()

    @staticmethod
    def decrypt(ciphertext: bytes, token: bytes) -> bytes:
        """Decrypt ciphertext with a given token.

        :param bytes ciphertext: Ciphertext to decrypt
        :param bytes token: Token to use
        :return: Decrypted bytes object"""
        if not isinstance(ciphertext, bytes):
            raise TypeError("ciphertext requires bytes")
        Utils.verify_token(token)
        key, iv = Utils.key_iv(token)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=default_backend())

        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        unpadded_plaintext = unpadder.update(padded_plaintext)
        unpadded_plaintext += unpadder.finalize()
        return unpadded_plaintext

    @staticmethod
    def checksum_field_bytes(ctx: Dict[str, Any]) -> bytearray:
        """Gather bytes for checksum calculation"""
        x = bytearray(ctx["header"].data)
        x += ctx["_"]["token"]
        if "data" in ctx:
            x += ctx["data"].data
            # print("DATA: %s" % ctx["data"])

        return x

    @staticmethod
    def get_length(x) -> int:
        """Return total packet length."""
        datalen = x._.data.length  # type: int
        return datalen + 32

    @staticmethod
    def is_hello(x) -> bool:
        """Return if packet is a hello packet."""
        # not very nice, but we know that hellos are 32b of length
        if 'length' in x:
            val = x['length']
        else:
            val = x.header.value['length']

        return bool(val == 32)


class TimeAdapter(Adapter):
    """Adapter for timestamp conversion."""
    def _encode(self, obj, context, path):
        return calendar.timegm(obj.timetuple())

    def _decode(self, obj, context, path):
        return datetime.datetime.utcfromtimestamp(obj)


class EncryptionAdapter(Adapter):
    """Adapter to handle communication encryption."""
    def _encode(self, obj, context, path):
        """Encrypt the given payload with the token stored in the context.

        :param obj: JSON object to encrypt"""
        # pp(context)
        return Utils.encrypt(json.dumps(obj).encode('utf-8') + b'\x00',
                             context['_']['token'])

    def _decode(self, obj, context, path):
        """Decrypts the given payload with the token stored in the context.

        :return str: JSON object"""
        try:
            # pp(context)
            decrypted = Utils.decrypt(obj, context['_']['token'])
            decrypted = decrypted.rstrip(b"\x00")
        except Exception:
            _LOGGER.debug("Unable to decrypt, returning raw bytes: %s", obj)
            return obj

        # list of adaption functions for malformed json payload (quirks)
        decrypted_quirks = [
            # try without modifications first
            lambda decrypted_bytes: decrypted_bytes,
            # powerstrip returns malformed JSON if the device is not
            # connected to the cloud, so we try to fix it here carefully.
            lambda decrypted_bytes: decrypted_bytes.replace(b',,"otu_stat"', b',"otu_stat"'),
            # xiaomi cloud returns malformed json when answering _sync.batch_gen_room_up_url
            # command so try to sanitize it
            lambda decrypted_bytes:
                decrypted_bytes[:decrypted_bytes.rfind(b'\x00')]
                if b'\x00' in decrypted_bytes
                else decrypted_bytes
        ]

        for i, quirk in enumerate(decrypted_quirks):
            decoded = quirk(decrypted).decode('utf-8')
            try:
                return json.loads(decoded)
            except Exception as ex:
                # log the error when decrypted bytes couldn't be loaded
                # after trying all quirk adaptions
                if i == len(decrypted_quirks) - 1:
                    _LOGGER.error("unable to parse json '%s': %s", decoded, ex)

        return None


Message = Struct(
    # for building we need data before anything else.
    "data" / Pointer(32, RawCopy(EncryptionAdapter(GreedyBytes))),
    "header" / RawCopy(Struct(
        Const(0x2131, Int16ub),
        "length" / Rebuild(Int16ub, Utils.get_length),
        "unknown" / Default(Int32ub, 0x00000000),
        "device_id" / Hex(Bytes(4)),
        "ts" / TimeAdapter(Default(Int32ub, datetime.datetime.utcnow()))
    )),
    "checksum" / IfThenElse(
        Utils.is_hello,
        Bytes(16),
        Checksum(Bytes(16),
                 Utils.md5,
                 Utils.checksum_field_bytes)),
)
