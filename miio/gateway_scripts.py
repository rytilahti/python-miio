from json import dumps as dumps_orig, loads

separators = (',', ':')
dumps = lambda data: dumps_orig(data, separators=separators)

# token in script doesn't match token of device which is used for (enc/dec)ryption
# but they are linked somehow
tokens = {
    "real": "9bc7c7ce6291d3e443fd7708608b9892",
    "encoded": "79cf21b08fb051499389f23c113477a4",
}

action_prefix = "x.scene."
action_id = {
    "move": action_prefix + "2732711973",
    "rotate": action_prefix + "2732711975",
}


def build_move(
    source_sid="lumi.158d000103ec74",
    source_model="lumi.sensor_cube.v1",
    target_model="chuangmi.plug.v3",
    target_ip="192.168.2.176",
    target_id="120009025",
    message_id=0,
):

    move = [
        [
            action_id["move"],
            [
                "1.0",
                1590158059,
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
                        "command": target_model + ".move",
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
    source_sid="lumi.158d000103ec74",
    source_model="lumi.sensor_cube.v1",
    target_model="chuangmi.plug.v3",
    target_ip="192.168.2.176",
    target_id="120009025",
    message_id=0,
):

    rotate = [
        [
            "x.scene.2723857884",
            [
                "1.0",
                1590161094,
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": "[1,12,3,85,[1,0],0,0]",
                        "key": "event." + source_model + ".rotate",
                        "model": source_model,
                        "src": "device",
                        "timespan": ["0 0 * * 0,1,2,3,4,5,6", "0 0 * * 0,1,2,3,4,5,6"],
                        "token": "",
                    },
                ],
                [
                    {
                        "command": target_model + ".rotate",
                        "did": target_id,
                        "extra": "[1,19,7,1006,[42,[6066005667474548,12,3,85,0]],0,0]",
                        "id": 0,
                        "ip": target_ip,
                        "model": target_model,
                        "token": tokens["encoded"],
                        "value": [20, 500],
                    }
                ],
            ],
        ]
    ]

    return dumps(rotate)


#print(build_move())
#print(build_rotate())
