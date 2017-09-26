#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a fork from original work by BlueC0re <coding@bluec0re.eu>
# https://github.com/bluec0re/android-backup-tools
# License: GPLv3
import tarfile
import zlib
import enum
import io
import pickle
import os
import binascii

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto import Random
except ImportError:
    AES = None


class CompressionType(enum.IntEnum):
    NONE = 0
    ZLIB = 1


class EncryptionType(enum.Enum):
    NONE = 'none'
    AES256 = 'AES-256'


class AndroidBackup:
    def __init__(self, fname=None):
        if fname:
            self.open(fname)

    def open(self, fname, mode='rb'):
        self.fp = open(fname, mode)

    def close(self):
        self.fp.close()

    def parse(self):
        self.fp.seek(0)
        magic = self.fp.readline()
        assert magic == b'ANDROID BACKUP\n'
        self.version = int(self.fp.readline().strip())
        self.compression = CompressionType(int(self.fp.readline().strip()))
        self.encryption = EncryptionType(self.fp.readline().strip().decode())

    def is_encrypted(self):
        return self.encryption == EncryptionType.AES256

    def _decrypt(self, enc, password):
        if AES is None:
            raise ImportError("PyCrypto required")

        user_salt, enc = enc.split(b'\n', 1)
        user_salt = binascii.a2b_hex(user_salt)
        ck_salt, enc = enc.split(b'\n', 1)
        ck_salt = binascii.a2b_hex(ck_salt)
        rounds, enc = enc.split(b'\n', 1)
        rounds = int(rounds)
        iv, enc = enc.split(b'\n', 1)
        iv = binascii.a2b_hex(iv)
        master_key, enc = enc.split(b'\n', 1)
        master_key = binascii.a2b_hex(master_key)

        user_key = PBKDF2(password, user_salt, dkLen=256//8, count=rounds)
        cipher = AES.new(user_key,
                         mode=AES.MODE_CBC,
                         IV=iv)

        master_key = list(cipher.decrypt(master_key))
        l = master_key.pop(0)
        master_iv = bytes(master_key[:l])
        master_key = master_key[l:]
        l = master_key.pop(0)
        mk = bytes(master_key[:l])
        master_key = master_key[l:]
        l = master_key.pop(0)
        master_ck = bytes(master_key[:l])

        # gen checksum

        # double encode utf8
        utf8mk = self.encode_utf8(mk)
        calc_ck = PBKDF2(utf8mk, ck_salt, dkLen=256//8, count=rounds)
        assert calc_ck == master_ck

        cipher = AES.new(mk,
                         mode=AES.MODE_CBC,
                         IV=master_iv)

        dec = cipher.decrypt(enc)
        pad = dec[-1]

        return dec[:-pad]

    @staticmethod
    def encode_utf8(mk):
        utf8mk = mk.decode('raw_unicode_escape')
        utf8mk = list(utf8mk)
        for i in range(len(utf8mk)):
            c = ord(utf8mk[i])
            # fix java encoding (add 0xFF00 to non ascii chars)
            if 0x7f < c < 0x100:
                c += 0xff00
                utf8mk[i] = chr(c)
        return ''.join(utf8mk).encode('utf-8')

    def _encrypt(self, dec, password):
        if AES is None:
            raise ImportError("PyCrypto required")

        master_key = Random.get_random_bytes(32)
        master_salt = Random.get_random_bytes(64)
        user_salt = Random.get_random_bytes(64)
        master_iv = Random.get_random_bytes(16)
        user_iv = Random.get_random_bytes(16)
        rounds = 10000

        l = len(dec)
        pad = 16 - (l % 16)
        dec += bytes([pad] * pad)
        cipher = AES.new(master_key, IV=master_iv, mode=AES.MODE_CBC)
        enc = cipher.encrypt(dec)

        master_ck = PBKDF2(self.encode_utf8(master_key),
                           master_salt, dkLen=256//8, count=rounds)

        user_key = PBKDF2(password,
                          user_salt, dkLen=256//8, count=rounds)

        master_dec = b"\x10" + master_iv + b"\x20" + master_key + b"\x20" + master_ck
        l = len(master_dec)
        pad = 16 - (l % 16)
        master_dec += bytes([pad] * pad)
        cipher = AES.new(user_key, IV=user_iv, mode=AES.MODE_CBC)
        master_enc = cipher.encrypt(master_dec)

        enc = binascii.b2a_hex(user_salt).upper() + b"\n" + \
                binascii.b2a_hex(master_salt).upper() + b"\n" + \
                str(rounds).encode() + b"\n" + \
                binascii.b2a_hex(user_iv).upper() + b"\n" + \
                binascii.b2a_hex(master_enc).upper() + b"\n" + enc

        return enc

    def read_data(self, password):
        """Reads from the file and returns a TarFile object."""
        data = self.fp.read()

        if self.encryption == EncryptionType.AES256:
            if password is None:
                raise Exception("Password need to be provided to extract encrypted archives")
            data = self._decrypt(data, password)

        if self.compression == CompressionType.ZLIB:
            data = zlib.decompress(data, zlib.MAX_WBITS)

        tar = tarfile.TarFile(fileobj=io.BytesIO(data))
        return tar

    def unpack(self, target_dir=None, password=None):
        tar = self.read_data(password)

        members = tar.getmembers()

        if target_dir is None:
            target_dir = os.path.basename(self.fp.name) + '_unpacked'
        pickle_fname = os.path.basename(self.fp.name) + '.pickle'
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        tar.extractall(path=target_dir)

        with open(pickle_fname, 'wb') as fp:
            pickle.dump(members, fp)

    def list(self, password=None):
        tar = self.read_tar(password)
        return tar.list()

    def pack(self, fname, password=None):
        target_dir = os.path.basename(fname) + '_unpacked'
        pickle_fname = os.path.basename(fname) + '.pickle'

        data = io.BytesIO()
        tar = tarfile.TarFile(name=fname,
                              fileobj=data,
                              mode='w',
                              format=tarfile.PAX_FORMAT)

        with open(pickle_fname, 'rb') as fp:
            members = pickle.load(fp)

        os.chdir(target_dir)
        for member in members:
            if member.isreg():
                tar.addfile(member, open(member.name, 'rb'))
            else:
                tar.addfile(member)

        tar.close()

        data.seek(0)
        if self.compression == CompressionType.ZLIB:
            data = zlib.compress(data.read())
        if self.encryption == EncryptionType.AES256:
            data = self._encrypt(data, password)

        with open(fname, 'wb') as fp:
            fp.write(b'ANDROID BACKUP\n')
            fp.write('{}\n'.format(self.version).encode())
            fp.write('{:d}\n'.format(self.compression).encode())
            fp.write('{}\n'.format(self.encryption.value).encode())

            fp.write(data)

    def __exit__(self, *args, **kwargs):
        self.close()

    def __enter__(self):
        self.parse()
        return self
