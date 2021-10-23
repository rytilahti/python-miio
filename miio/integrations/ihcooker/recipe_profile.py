import random

import construct as c

from . import DEVICE_ID, StageMode
from .custom_construct import ArrayDefault, RebuildStream

RECIPE_NAME_MAX_LEN_V1 = 13
RECIPE_NAME_MAX_LEN_V2 = 28
DEFAULT_FIRE_ON_OFF = 20
DEFAULT_THRESHOLD_CELCIUS = 249
DEFAULT_TEMP_TARGET_CELCIUS = 229
DEFAULT_FIRE_LEVEL = 45
DEFAULT_PHASE_MINUTES = 50


def crc16(data: bytes, offset=0, length=None):
    """Computes 16bit CRC for IHCooker recipe profiles.

    Based on variant by Amin Saidani posted on https://stackoverflow.com/a/55850496.
    """
    if length is None:
        length = len(data)
    if (
        data is None
        or offset < 0
        or offset > len(data) - 1
        and offset + length > len(data)
    ):
        return 0
    crc = 0x0000
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for _ in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def profile_base(is_v1, recipe_name_encoding="GBK"):
    """Build a Construct for IHCooker recipes based on version and name encoding."""
    return c.Struct(
        c.Const(3, c.Int8un),
        "device_version" / c.Default(c.Enum(c.Int8ub, **DEVICE_ID), 1 if is_v1 else 2),
        "menu_location"
        / c.Default(c.ExprValidator(c.Int8ub, lambda o, _: 0 <= o < 10), 9),
        "recipe_name"
        / c.Default(
            c.ExprAdapter(
                c.StringEncoded(  # PaddedString wrapper does not support GBK encoding.
                    c.FixedSized(
                        RECIPE_NAME_MAX_LEN_V1 if is_v1 else RECIPE_NAME_MAX_LEN_V2,
                        c.NullStripped(c.GreedyBytes),
                    ),
                    recipe_name_encoding,
                ),
                lambda x, _: x.replace("\n", " "),
                lambda x, _: x.replace(" ", "\n"),
            ),
            "Unnamed",
        ),
        c.Padding(1) if is_v1 else c.Padding(2),
        "recipe_id" / c.Default(c.Int32ub, lambda _: random.randint(0, 2 ** 32 - 1)),
        "menu_settings"
        / c.Default(
            c.BitStruct(  # byte 37
                "save_recipe" / c.Default(c.Flag, 0),
                "confirm_start" / c.Default(c.Flag, 0),
                "menu_unknown3" / c.Default(c.Flag, 0),
                "menu_unknown4" / c.Default(c.Flag, 0),
                "menu_unknown5" / c.Default(c.Flag, 0),
                "menu_unknown6" / c.Default(c.Flag, 0),
                "menu_unknown7" / c.Default(c.Flag, 0),
                "menu_unknown8" / c.Default(c.Flag, 0),
            ),
            {},
        ),
        "duration_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_minutes", 0) // 60
        ),  # byte 38
        "duration_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub, lambda obj, ctx: obj + ctx.duration_hours * 60, c.obj_ % 60
            ),
            60,
        ),  # byte 39
        "duration_max_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_max_minutes", 0) // 60
        ),  # byte 40
        "duration_max_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub,
                lambda obj, ctx: obj + ctx.duration_max_hours * 60,
                c.obj_ % 60,
            ),
            0,
        ),  # byte 41
        "duration_min_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_min_minutes", 0) // 60
        ),  # byte 42
        "duration_min_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub,
                lambda obj, ctx: obj + ctx.duration_min_hours * 60,
                c.obj_ % 60,
            ),
            0,
        ),  # byte 43
        c.Padding(2),  # byte 44, 45
        "unknown_46" / c.Default(c.Byte, 1),  # byte 46, should be set to 1
        c.Padding(7) if is_v1 else c.Padding(1),
        "stages"
        / c.Default(
            ArrayDefault(
                15,
                c.Struct(  # byte 48-168
                    "mode" / c.Default(c.Enum(c.Byte, StageMode), StageMode.FireMode),
                    "hours"
                    / c.Rebuild(
                        c.Int8ub, lambda ctx: (ctx.get("minutes", 0) // 60) + 128
                    ),
                    "minutes"
                    / c.Default(
                        c.ExprAdapter(
                            c.Int8ub,
                            decoder=lambda obj, ctx: obj + (ctx.hours - 128) * 60,
                            encoder=c.obj_ % 60,
                        ),
                        DEFAULT_PHASE_MINUTES,
                    ),
                    "temp_threshold" / c.Default(c.Int8ub, DEFAULT_THRESHOLD_CELCIUS),
                    "temp_target" / c.Default(c.Int8ub, DEFAULT_TEMP_TARGET_CELCIUS),
                    "power" / c.Default(c.Int8ub, DEFAULT_FIRE_LEVEL),
                    "fire_off" / c.Default(c.Int8ub, DEFAULT_FIRE_ON_OFF),
                    "fire_on" / c.Default(c.Int8ub, DEFAULT_FIRE_ON_OFF),
                ),
                default=dict(
                    mode=StageMode.FireMode,
                    minutes=DEFAULT_PHASE_MINUTES,
                    temp_threshold=DEFAULT_THRESHOLD_CELCIUS,
                    temp_target=DEFAULT_TEMP_TARGET_CELCIUS,
                    power=DEFAULT_FIRE_LEVEL,
                    fire_off=DEFAULT_FIRE_ON_OFF,
                    fire_on=DEFAULT_FIRE_ON_OFF,
                ),
            ),
            [],
        ),
        c.Padding(16) if is_v1 else c.Padding(6),  # byte 169-174
        "unknown175" / c.Default(c.Int8ub, 0),
        "unknown176" / c.Default(c.Int8ub, 0),
        "unknown177" / c.Default(c.Int8ub, 0),
        "crc"  # byte 178-179
        / RebuildStream(
            c.Bytes(2), crc16
        ),  # Default profiles have invalid crc, c.Checksum() raises undesired error when parsed.
    )


profile_v1 = profile_base(is_v1=True)
profile_v2 = profile_base(is_v1=False)
profile_korea = profile_base(is_v1=False, recipe_name_encoding="euc-kr")

_profile_example = dict(profile_v1.parse(profile_v1.build(dict())))
profile_keys = _profile_example.keys()
stage_keys = dict(_profile_example["stages"][0]).keys()
menu_keys = dict(_profile_example["menu_settings"]).keys()
