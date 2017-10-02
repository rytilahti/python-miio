from unittest import TestCase
from .. import Utils


class TestProtocol(TestCase):
    def test_non_bytes_payload(self):
        payload = "hello world"
        valid_token = 32 * b'0'
        with self.assertRaises(TypeError):
            Utils.encrypt(payload, valid_token)
        with self.assertRaises(TypeError):
            Utils.decrypt(payload, valid_token)

    def test_encrypt(self):
        payload = b"hello world"
        token = bytes.fromhex(32 * '0')

        encrypted = Utils.encrypt(payload, token)
        decrypted = Utils.decrypt(encrypted, token)
        self.assertEquals(payload, decrypted)

    def test_invalid_token(self):
        payload = b"hello world"
        wrong_type = 1234
        wrong_length = bytes.fromhex(16 * '0')
        with self.assertRaises(TypeError):
            Utils.encrypt(payload, wrong_type)
        with self.assertRaises(TypeError):
            Utils.decrypt(payload, wrong_type)

        with self.assertRaises(ValueError):
            Utils.encrypt(payload, wrong_length)
        with self.assertRaises(ValueError):
            Utils.decrypt(payload, wrong_length)
