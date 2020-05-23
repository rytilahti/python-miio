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
    "longpress": lambda sid: action_prefix + "6" + sid_to_num(sid),
    "shake": lambda sid: action_prefix + "5" + sid_to_num(sid),
}


def build_move(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    method_name = f"move_{source_id}"

    move = [
        [
            action_id["move"](source_sid),
            [
                "1.0",
                randint(1590161094, 1590162094),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,18,2,85,[6,256],0,0]",
                        "key": "event." + source_model + ".move",
                        "model": source_model,
                        "src": "device",
                        "timespan": ["0 0 * * 0,1,2,3,4,5,6", "0 0 * * 0,1,2,3,4,5,6"],
                        "token": "",
                    },
                ],
                [
                    {
                        "command": target_model + "." + method_name,
                        "did": target_id,
                        "extra": "",
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

    return dumps(move)


def build_rotate(
    source_sid,
    target_ip,
    target_model=fake_device_model,
    target_id=fake_device_id,
    source_model="lumi.sensor_cube.v1",
    message_id=0,
):

    lumi, source_id = source_sid.split(".")
    method_name = f"rotate_{source_id}"

    rotate = [
        [
            action_id["rotate"](source_sid),
            [
                "1.0",  # version??
                randint(
                    1590161094, 1590162094
                ),  # id of automation in mi home database??
                [
                    "0",  # just zero..
                    {
                        "did": source_sid,  # gateway subdevice sid / origin of action zigbee sid
                        "extra": "[1,12,3,85,[1,0],0,0]",  # ???
                        "key": "event." + source_model + ".rotate",  # event_id
                        "model": source_model,
                        "src": "device",
                        "timespan": [
                            "0 0 * * 0,1,2,3,4,5,6",
                            "0 0 * * 0,1,2,3,4,5,6",
                        ],  # cron-style always do??
                        "token": "",
                    },
                ],
                [
                    {
                        "command": target_model
                        + "."
                        + method_name,  # part after last dot (rotate) will be used as miio method in gateway callback
                        "did": target_id,  # device identifier used in all responses of device
                        "extra": "[1,19,7,1006,[42,[6066005667474548,12,3,85,0]],0,0]",  # ???
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": [
                            20,
                            500,
                        ],  # don't fire event if rotation_angle < 20 and rotation_angle > 500 ??
                    }
                ],
            ],
        ]
    ]

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
    method_name = f"singlepress_{source_id}"

    singlepress = [
        [
            action_id["singlepress"](source_sid),
            [
                "1.0",
                randint(
                    1590161094, 1590162094
                ),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,13,1,85,[0,1],0,0]",
                        "key": "event." + source_model + ".click",  # event_id
                        "model": source_model,
                        "src": "device",
                        "timespan": [
                            "0 0 * * 0,1,2,3,4,5,6",
                            "0 0 * * 0,1,2,3,4,5,6"
                        ],
                        "token": ""
                    }
                ],
                [
                    {
                        "command": target_model
                        + "."
                        + method_name,
                        "did": target_id,
                        "extra": "",
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": ""
                    }
                ]
            ]
        ]
    ]
    print(dumps(singlepress))
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
    method_name = f"doublepress_{source_id}"

    doublepress = [
        [
            action_id["doublepress"](source_sid),
            [
                "1.0",
                randint(
                    1590161094, 1590162094
                ),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,13,1,85,[0,2],0,0]",
                        "key": "event." + source_model + ".double_click",  # event_id
                        "model": source_model,
                        "src": "device",
                        "timespan": [
                            "0 0 * * 0,1,2,3,4,5,6",
                            "0 0 * * 0,1,2,3,4,5,6"
                        ],
                        "token": ""
                    }
                ],
                [
                    {
                        "command": target_model
                        + "."
                        + method_name,
                        "did": target_id,
                        "extra": "",
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": ""
                    }
                ]
            ]
        ]
    ]
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
    method_name = f"longpress_{source_id}"

    longpress = [
        [
            action_id["longpress"](source_sid),
            [
                "1.0",
                randint(
                    1590161094, 1590162094
                ),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,13,1,85,[0,16],0,0]",
                        "key": "event." + source_model + ".long_click_press",  # event_id
                        "model": source_model,
                        "src": "device",
                        "timespan": [
                            "0 0 * * 0,1,2,3,4,5,6",
                            "0 0 * * 0,1,2,3,4,5,6"
                        ],
                        "token": ""
                    }
                ],
                [
                    {
                        "command": target_model
                        + "."
                        + method_name,
                        "did": target_id,
                        "extra": "",
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": ""
                    }
                ]
            ]
        ]
    ]
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
    method_name = f"shake_{source_id}"

    shake = [
        [
            action_id["shake"](source_sid),
            [
                "1.0",
                randint(
                    1590161094, 1590162094
                ),
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,13,1,85,[0,18],0,0]",
                        "key": "event." + source_model + ".shake",  # event_id
                        "model": source_model,
                        "src": "device",
                        "timespan": [
                            "0 0 * * 0,1,2,3,4,5,6",
                            "0 0 * * 0,1,2,3,4,5,6"
                        ],
                        "token": ""
                    }
                ],
                [
                    {
                        "command": target_model
                        + "."
                        + method_name,
                        "did": target_id,
                        "extra": "",
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": ""
                    }
                ]
            ]
        ]
    ]
    return dumps(shake)
