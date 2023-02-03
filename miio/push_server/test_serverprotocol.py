import pytest

from miio import Message

from .serverprotocol import (
    ERR_INVALID,
    ERR_METHOD_EXEC_FAILED,
    ERR_UNSUPPORTED,
    ServerProtocol,
)

HOST = "127.0.0.1"
PORT = 1234
DEVICE_ID = 4141
DUMMY_TOKEN = bytes.fromhex("0" * 32)


@pytest.fixture
def protocol(mocker, event_loop) -> ServerProtocol:
    server = mocker.Mock()

    # Mock server id
    type(server).device_id = mocker.PropertyMock(return_value=DEVICE_ID)
    socket = mocker.Mock()

    proto = ServerProtocol(event_loop, socket, server)
    proto.transport = mocker.Mock()

    yield proto


def test_send_ping_ack(protocol: ServerProtocol, mocker):
    """Test that ping acks are send as expected."""
    protocol.send_ping_ACK(HOST, PORT)
    protocol.transport.sendto.assert_called()

    cargs = protocol.transport.sendto.call_args[0]

    m = Message.parse(cargs[0])
    assert int.from_bytes(m.header.value.device_id, "big") == DEVICE_ID
    assert m.data.length == 0

    assert cargs[1][0] == HOST
    assert cargs[1][1] == PORT


def test_send_response(protocol: ServerProtocol):
    """Test that send_response sends valid messages."""
    payload = {"foo": 1}
    protocol.send_response(HOST, PORT, 1, DUMMY_TOKEN, payload)
    protocol.transport.sendto.assert_called()

    cargs = protocol.transport.sendto.call_args[0]
    m = Message.parse(cargs[0], token=DUMMY_TOKEN)
    payload = m.data.value
    assert payload["id"] == 1
    assert payload["foo"] == 1


def test_send_error(protocol: ServerProtocol, mocker):
    """Test that error payloads are created correctly."""
    ERR_MSG = "example error"
    ERR_CODE = -1
    protocol.send_error(HOST, PORT, 1, DUMMY_TOKEN, code=ERR_CODE, message=ERR_MSG)
    protocol.send_response = mocker.Mock()  # type: ignore[assignment]
    protocol.transport.sendto.assert_called()

    cargs = protocol.transport.sendto.call_args[0]
    m = Message.parse(cargs[0], token=DUMMY_TOKEN)
    payload = m.data.value

    assert "error" in payload
    assert payload["error"]["code"] == ERR_CODE
    assert payload["error"]["error"] == ERR_MSG


def test__handle_datagram_from_registered_device(protocol: ServerProtocol, mocker):
    """Test that events from registered devices are handled correctly."""
    protocol.server._registered_devices = {HOST: {}}
    protocol.server._registered_devices[HOST]["token"] = DUMMY_TOKEN
    dummy_callback = mocker.Mock()
    protocol.server._registered_devices[HOST]["callback"] = dummy_callback

    PARAMS = {"test_param": 1}
    payload = {"id": 1, "method": "action:source_device", "params": PARAMS}
    msg_from_device = protocol._create_message(payload, DUMMY_TOKEN, 4242)

    protocol._handle_datagram_from_registered_device(HOST, PORT, msg_from_device)

    # Assert that a response is sent back
    protocol.transport.sendto.assert_called()

    # Assert that the callback is called
    dummy_callback.assert_called()
    cargs = dummy_callback.call_args[0]
    assert cargs[2] == PARAMS
    assert cargs[0] == "source.device"
    assert cargs[1] == "action"


def test_datagram_with_known_method(protocol: ServerProtocol, mocker):
    """Test that regular client messages are handled properly."""
    protocol.send_response = mocker.Mock()  # type: ignore[assignment]

    response_payload = {"result": "info response"}
    protocol.server.methods = {"miIO.info": response_payload}

    msg = protocol._create_message({"id": 1, "method": "miIO.info"}, DUMMY_TOKEN, 1234)
    protocol._handle_datagram_from_client(HOST, PORT, msg)

    protocol.send_response.assert_called()  # type: ignore
    cargs = protocol.send_response.call_args[1]  # type: ignore
    assert cargs["payload"] == response_payload


@pytest.mark.parametrize(
    "method,err_code", [("unknown_method", ERR_UNSUPPORTED), (None, ERR_INVALID)]
)
def test_datagram_with_unknown_method(
    method, err_code, protocol: ServerProtocol, mocker
):
    """Test that invalid payloads are erroring out correctly."""
    protocol.send_error = mocker.Mock()  # type: ignore[assignment]
    protocol.server.methods = {}

    data = {"id": 1}

    if method is not None:
        data["method"] = method

    msg = protocol._create_message(data, DUMMY_TOKEN, 1234)
    protocol._handle_datagram_from_client(HOST, PORT, msg)

    protocol.send_error.assert_called()  # type: ignore
    cargs = protocol.send_error.call_args[0]  # type: ignore
    assert cargs[4] == err_code


def test_datagram_with_exception_raising(protocol: ServerProtocol, mocker):
    """Test that exception raising callbacks are ."""
    protocol.send_error = mocker.Mock()  # type: ignore[assignment]

    def _raise(*args, **kwargs):
        raise Exception("error message")

    protocol.server.methods = {"raise": _raise}

    data = {"id": 1, "method": "raise"}

    msg = protocol._create_message(data, DUMMY_TOKEN, 1234)
    protocol._handle_datagram_from_client(HOST, PORT, msg)

    protocol.send_error.assert_called()  # type: ignore
    cargs = protocol.send_error.call_args[0]  # type: ignore
    assert cargs[4] == ERR_METHOD_EXEC_FAILED
    assert "error message" in cargs[5]
