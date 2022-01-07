from .dreame_vacuum_base import DreameVacuumBase
from .dreame_vacuum_base import ChargingState, CleaningMode, OperatingMode,\
        FaultStatus, DeviceStatus, MopMode, WarningCode
from .dreame_vacuum_base import percent_format,\
        minutes_format, hours_format, epoch_time_format

import logging
logger = logging.getLogger(__name__)

class DreameVacuumMB1808(DreameVacuumBase):
    def __init__(self, ip, token, *args, **kwargs):
        self.commands = {
            # Battery
            'battery_level'              : {'siid': 2, 'piid': 1, 'mode': {'r': percent_format}},
            'battery_state'              : {'siid': 2, 'piid': 2, 'mode': {'r': ChargingState}},
            'battery_start_charge'       : {'siid': 2, 'aiid': 1, 'mode': 'a'},
            # Robot Cleaner
            'robot_fault'                : {'siid': 3, 'piid': 1, 'mode': {'r': bool}},
            'robot_status'               : {'siid': 3, 'piid': 2, 'mode': {'r': DeviceStatus}},
            'robot_start_sweep'          : {'siid': 3, 'aiid': 1, 'mode': 'a'},
            'robot_stop_sweeping'        : {'siid': 3, 'aiid': 2, 'mode': 'a'},
            # Identify I am here
            'identify'                   : {'siid': 17, 'aiid': 1, 'mode': 'a'},
            # Clean
            'clean_work_mode'            : {'siid': 18, 'piid': 1, 'mode': {'r': OperatingMode}},
            'clean_time_duration'        : {'siid': 18, 'piid': 2, 'mode': {'r': minutes_format}},
            'clean_size'                 : {'siid': 18, 'piid': 3, 'mode': {'r': str}},
            'clean_area'                 : {'siid': 18, 'piid': 4, 'mode': {'r': str}},
            'clean_timer'                : {'siid': 18, 'piid': 5, 'mode': {'r': str, 'w': str}},
            'clean_mode'                 : {'siid': 18, 'piid': 6, 'mode': {'r': CleaningMode, 'w': int}},
            'clean_delete_timer'         : {'siid': 18, 'piid': 8, 'mode': {'w': int}},
            'clean_water_box'            : {'siid': 18, 'piid': 9, 'mode': {'r': int}},
            'clean_object_name'          : {'siid': 18, 'piid': 11, 'mode': {'r': str}},
            'clean_start_time'           : {'siid': 18, 'piid': 12, 'mode': {'r': str}},
            'clean_total_clean_time'     : {'siid': 18, 'piid': 13, 'mode': {'r': minutes_format}},
            'clean_total_clean_times'    : {'siid': 18, 'piid': 14, 'mode': {'r': int}},
            'clean_total_clean_area'     : {'siid': 18, 'piid': 15, 'mode': {'r': int}},
            'clean_clean_log_start_time' : {'siid': 18, 'piid': 16, 'mode': {'r': epoch_time_format}},
            'clean_button_led'           : {'siid': 18, 'piid': 17, 'mode': {'r': int}},
            'clean_task_done'            : {'siid': 18, 'piid': 18, 'mode': {'r': bool}},
            'clean_mopmode'              : {'siid': 18, 'piid': 20, 'mode': {'r': MopMode, 'w': int}},
            'clean_clean_info'           : {'siid': 18, 'piid': 21, 'mode': {'w': str}}, # rectangle to clean "x1,y1,x2,y2"
            'clean_clean_status'         : {'siid': 18, 'piid': 22, 'mode': {'r': percent_format}},
            'clean_save_map_status'      : {'siid': 18, 'piid': 23, 'mode': {'r': bool, 'w': int}},
            'clean_start'                : {'siid': 18, 'aiid': 1, 'mode': 'a'}, # in clean_info
            'clean_stop'                 : {'siid': 18, 'aiid': 2, 'mode': 'a'},
            # Consumable
            'consumable_life_sieve'      : {'siid': 19, 'piid': 1, 'mode': {'r': str, 'w': str}},
            'consumable_life_brush_side' : {'siid': 19, 'piid': 2, 'mode': {'r': str, 'w': str}},
            'consumable_life_brush_main' : {'siid': 19, 'piid': 3, 'mode': {'r': str, 'w': str}},
            # Annoy
            'annoy_enable'               : {'siid': 20, 'piid': 1, 'mode': {'r': bool, 'w': int}},
            'annoy_start_time'           : {'siid': 20, 'piid': 2, 'mode': {'r': str, 'w': str}},
            'annoy_stop_time'            : {'siid': 20, 'piid': 3, 'mode': {'r': str, 'w': str}},
            # Remote
            'remote_deg'                 : {'siid': 21, 'piid': 1, 'mode': {'w': str}},
            'remote_speed'               : {'siid': 21, 'piid': 2, 'mode': {'w': str}},
            'remote_start'               : {'siid': 21, 'aiid': 1, 'mode': 'a'}, # in = [deg, speed]
            'remote_stop'                : {'siid': 21, 'aiid': 2, 'mode': 'a'},
            'remote_exit'                : {'siid': 21, 'aiid': 3, 'mode': 'a'},
            # Warnings
            'warn_code'                  : {'siid': 22, 'piid': 1, 'mode': {'r': WarningCode}},
            # Map
            'map_view'                   : {'siid': 23, 'piid': 1, 'mode': {'r': WarningCode}},
            'map_frame_info'             : {'siid': 23, 'piid': 2, 'mode': {'w': str}},
            'map_object_name'            : {'siid': 23, 'piid': 3, 'mode': {'r': str}},
            'map_extend_data'            : {'siid': 23, 'piid': 4, 'mode': {'r': str, 'w': str}},
            'map_robot_time'             : {'siid': 23, 'piid': 5, 'mode': {'r': minutes_format}},
            'map_req'                    : {'siid': 23, 'aiid': 1, 'mode': 'a'}, # in = [frame_info]
            'map_update'                 : {'siid': 23, 'aiid': 2, 'mode': 'a'}, # in = [map_extend_data]
            # Audio
            'audio_volume'               : {'siid': 24, 'piid': 1, 'mode': {'r': percent_format, 'w': int}},
            'audio_voice_packets'        : {'siid': 24, 'piid': 3, 'mode': {'r': str, 'w': str}},
            'audio_position'             : {'siid': 24, 'aiid': 1, 'mode': 'a'},
            'audio_set_voice'            : {'siid': 24, 'aiid': 2, 'mode': 'a'}, # in = voice_packets ???
            'audio_play_sound'           : {'siid': 24, 'aiid': 3, 'mode': 'a'}, # in = voice_packets ???
            # Time
            'time_zone'                  : {'siid': 25, 'piid': 1, 'mode': {'r': str, 'w': str}},
            # Main Cleaning Brush
            'main_brush_time_left'       : {'siid': 26, 'piid': 1, 'mode': {'r': hours_format}},
            'main_brush_life_level'      : {'siid': 26, 'piid': 2, 'mode': {'r': percent_format}},
            'main_brush_reset_life'      : {'siid': 26, 'aiid': 1, 'mode': 'a'},
            # Filter
            'filter_life_level'          : {'siid': 27, 'piid': 1, 'mode': {'r': percent_format}},
            'filter_time_left'           : {'siid': 27, 'piid': 2, 'mode': {'r': hours_format}},
            'filter_reset_life'          : {'siid': 27, 'aiid': 1, 'mode': 'a'},
            # Side Cleaning Brush
            'side_brush_time_left'       : {'siid': 28, 'piid': 1, 'mode': {'r': hours_format}},
            'side_brush_life_level'      : {'siid': 28, 'piid': 2, 'mode': {'r': percent_format}},
            'side_brush_reset_life'      : {'siid': 28, 'aiid': 1, 'mode': 'a'},
            }
        super().__init__(ip, token, *args, **kwargs)
