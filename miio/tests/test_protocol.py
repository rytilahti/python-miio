import binascii
from unittest import TestCase

from .. import Utils
from ..protocol import Message


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
        assert payload == decrypted

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

    def test_decode_json_payload(self):
        token = bytes.fromhex(32 * '0')
        ctx = {'token': token}

        def build_msg(data):
            encrypted_data = Utils.encrypt(data, token)

            # header
            magic = binascii.unhexlify(b'2131')
            length = (32 + len(encrypted_data)).to_bytes(2, byteorder='big')
            unknown = binascii.unhexlify(b'00000000')
            did = binascii.unhexlify(b'01234567')
            epoch = binascii.unhexlify(b'00000000')

            checksum = Utils.md5(magic+length+unknown+did+epoch+token+encrypted_data)

            return magic+length+unknown+did+epoch+checksum+encrypted_data

        # can parse message with valid json
        serialized_msg = build_msg(b'{"id": 123456}')
        parsed_msg = Message.parse(serialized_msg, **ctx)
        assert parsed_msg.data.value
        assert isinstance(parsed_msg.data.value, dict)
        assert parsed_msg.data.value['id'] == 123456

        # can parse message with invalid json for edge case powerstrip
        # when not connected to cloud
        serialized_msg = build_msg(b'{"id": 123456,,"otu_stat":0}')
        parsed_msg = Message.parse(serialized_msg, **ctx)
        assert parsed_msg.data.value
        assert isinstance(parsed_msg.data.value, dict)
        assert parsed_msg.data.value['id'] == 123456
        assert parsed_msg.data.value['otu_stat'] == 0

        # can parse message with invalid json for edge case xiaomi cloud
        # reply to _sync.batch_gen_room_up_url
        serialized_msg = build_msg(b'{"id": 123456}\x00k')
        parsed_msg = Message.parse(serialized_msg, **ctx)
        assert parsed_msg.data.value
        assert isinstance(parsed_msg.data.value, dict)
        assert parsed_msg.data.value['id'] == 123456
