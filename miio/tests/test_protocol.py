import binascii

import pytest

from miio.exceptions import DeviceError, RecoverableError

from .. import Utils
from ..miioprotocol import MiIOProtocol
from ..protocol import Message

METHOD = "method"
PARAMS = "params"


@pytest.fixture
def proto() -> MiIOProtocol:
    return MiIOProtocol()


def test_incrementing_id(proto):
    old_id = proto.raw_id
    proto._create_request("dummycmd", "dummy")
    assert proto.raw_id > old_id


def test_id_loop(proto):
    proto.__id = 9999
    proto._create_request("dummycmd", "dummy")
    assert proto.raw_id == 1


def test_request_with_none_param(proto):
    req = proto._create_request("dummy", None)
    assert isinstance(req["params"], list)
    assert len(req["params"]) == 0


def test_request_with_string_param(proto):
    req = proto._create_request("command", "single")
    assert req[METHOD] == "command"
    assert req[PARAMS] == "single"


def test_request_with_list_param(proto):
    req = proto._create_request("command", ["item"])
    assert req[METHOD] == "command"
    assert req[PARAMS] == ["item"]


def test_request_extra_params(proto):
    req = proto._create_request("command", ["item"], extra_parameters={"sid": 1234})
    assert "sid" in req
    assert req["sid"] == 1234


def test_device_error_handling(proto: MiIOProtocol):
    retry_error = -30001
    with pytest.raises(RecoverableError):
        proto._handle_error({"code": retry_error})

    with pytest.raises(DeviceError):
        proto._handle_error({"code": 1234})


def test_non_bytes_payload():
    payload = "hello world"
    valid_token = 32 * b"0"
    with pytest.raises(TypeError):
        Utils.encrypt(payload, valid_token)
    with pytest.raises(TypeError):
        Utils.decrypt(payload, valid_token)


def test_encrypt():
    payload = b"hello world"
    token = bytes.fromhex(32 * "0")

    encrypted = Utils.encrypt(payload, token)
    decrypted = Utils.decrypt(encrypted, token)
    assert payload == decrypted


def test_invalid_token():
    payload = b"hello world"
    wrong_type = 1234
    wrong_length = bytes.fromhex(16 * "0")
    with pytest.raises(TypeError):
        Utils.encrypt(payload, wrong_type)
    with pytest.raises(TypeError):
        Utils.decrypt(payload, wrong_type)

    with pytest.raises(ValueError):
        Utils.encrypt(payload, wrong_length)
    with pytest.raises(ValueError):
        Utils.decrypt(payload, wrong_length)


def test_decode_json_payload():
    token = bytes.fromhex(32 * "0")
    ctx = {"token": token}

    def build_msg(data):
        encrypted_data = Utils.encrypt(data, token)

        # header
        magic = binascii.unhexlify(b"2131")
        length = (32 + len(encrypted_data)).to_bytes(2, byteorder="big")
        unknown = binascii.unhexlify(b"00000000")
        did = binascii.unhexlify(b"01234567")
        epoch = binascii.unhexlify(b"00000000")

        checksum = Utils.md5(
            magic + length + unknown + did + epoch + token + encrypted_data
        )

        return magic + length + unknown + did + epoch + checksum + encrypted_data

    # can parse message with valid json
    serialized_msg = build_msg(b'{"id": 123456}')
    parsed_msg = Message.parse(serialized_msg, **ctx)
    assert parsed_msg.data.value
    assert isinstance(parsed_msg.data.value, dict)
    assert parsed_msg.data.value["id"] == 123456

    # can parse message with invalid json for edge case powerstrip
    # when not connected to cloud
    serialized_msg = build_msg(b'{"id": 123456,,"otu_stat":0}')
    parsed_msg = Message.parse(serialized_msg, **ctx)
    assert parsed_msg.data.value
    assert isinstance(parsed_msg.data.value, dict)
    assert parsed_msg.data.value["id"] == 123456
    assert parsed_msg.data.value["otu_stat"] == 0

    # can parse message with invalid json for edge case xiaomi cloud
    # reply to _sync.batch_gen_room_up_url
    serialized_msg = build_msg(b'{"id": 123456}\x00k')
    parsed_msg = Message.parse(serialized_msg, **ctx)
    assert parsed_msg.data.value
    assert isinstance(parsed_msg.data.value, dict)
    assert parsed_msg.data.value["id"] == 123456
