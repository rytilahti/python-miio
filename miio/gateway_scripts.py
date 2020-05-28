from json import dumps as dumps_orig
from random import randint

separators = (",", ":")


def dumps(data):
    return dumps_orig(data, separators=separators)


# token in script doesn't match token of device which is used for (enc/dec)ryption
# but they are linked somehow
tokens = {
    "real": "9bc7c7ce6291d3e443fd7708608b9892",
    "encoded": "79cf21b08fb051499389f23c113477a4",
    "data_tkn": 29576,
}

fake_device_id = "120009025"
fake_device_model = "chuangmi.plug.v3"


def sid_to_num(sid):
    lumi, hex_id = sid.split(".")
    num_id = int.from_bytes(bytes.fromhex(hex_id), byteorder="big")
    return str(num_id)[-6:]


action_prefix = "x.scene."

# Keeping action script tail decimal int it might be used as index in some db
action_id = {
    "move": lambda sid: action_prefix + "1" + sid_to_num(sid),
    "rotate": lambda sid: action_prefix + "2" + sid_to_num(sid),
    "singlepress": lambda sid: action_prefix + "3" + sid_to_num(sid),
    "doublepress": lambda sid: action_prefix + "4" + sid_to_num(sid),
    "shake": lambda sid: action_prefix + "5" + sid_to_num(sid),
    "longpress": lambda sid: action_prefix + "6" + sid_to_num(sid),
    "flip90": lambda sid: action_prefix + "7" + sid_to_num(sid),
    "flip180": lambda sid: action_prefix + "8" + sid_to_num(sid),
    "shakeair": lambda sid: action_prefix + "9" + sid_to_num(sid),
    "taptap": lambda sid: action_prefix + "10" + sid_to_num(sid),
}


def _inflate(
    action,
    extra,
    source_sid,
    source_model,
    target_id,
    target_ip,
    target_model,
    message_id,
    event=None,
    command_extra="",
):
    if event is None:
        event = action

    lumi, source_id = source_sid.split(".")

    return [
        [
            action_id[action](source_sid),
            [
                "1.0",
                randint(1590161094, 1590162094),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": extra,
                        "key": "event." + source_model + "." + event,
                        "model": source_model,
                        "src": "device",
                        "timespan": ["0 0 * * 0,1,2,3,4,5,6", "0 0 * * 0,1,2,3,4,5,6"],
                        "token": "",
                    },
                ],
                [
                    {
                        "command": target_model + "." + action + "_" + source_id,
                        "did": target_id,
                        "extra": command_extra,
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": "",
                    }
                ],
            ],
        ]
    ]


def build_move(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    move = _inflate(
        "move",
        "[1,18,2,85,[6,256],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
    )
    return dumps(move)


def build_flip90(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    flip90 = _inflate(
        "flip90",
        "[1,18,2,85,[6,64],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
    )
    return dumps(flip90)


def build_flip180(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    flip180 = _inflate(
        "flip180",
        "[1,18,2,85,[6,128],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
    )
    return dumps(flip180)


def build_taptap(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    taptap = _inflate(
        "taptap",
        "[1,18,2,85,[6,512],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "tap_twice",
    )
    return dumps(taptap)


def build_shakeair(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    shakeair = _inflate(
        "shakeair",
        "[1,18,2,85,[0,0],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "shake_air",
    )
    return dumps(shakeair)


def build_rotate(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    rotate = _inflate(
        "rotate",
        "[1,12,3,85,[1,0],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "rotate",
        "[1,19,7,1006,[42,[6066005667474548,12,3,85,0]],0,0]",
    )
    return dumps(rotate)


def build_singlepress(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_switch.aq3",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    singlepress = _inflate(
        "singlepress",
        "[1,13,1,85,[0,1],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "click",
    )
    return dumps(singlepress)


def build_doublepress(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_switch.aq3",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    doublepress = _inflate(
        "doublepress",
        "[1,13,1,85,[0,2],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "double_click",
    )
    return dumps(doublepress)


def build_longpress(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_switch.aq3",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    longpress = _inflate(
        "longpress",
        "[1,13,1,85,[0,16],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
        "long_click_press",
    )
    return dumps(longpress)


def build_shake(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_switch.aq3",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    shake = _inflate(
        "shake",
        "[1,13,1,85,[0,18],0,0]",
        source_sid,
        source_model,
        target_id,
        target_ip,
        target_model,
        message_id,
    )
    return dumps(shake)
