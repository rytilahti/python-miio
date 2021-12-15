#!/usr/bin/env python3
from getkey import getkey, keys
from miio import DreameVacuumMB1808
import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)

class Control:
    def __init__(self, ip, token):
        self.vac = DreameVacuumMB1808(ip, token)
        self.speed = 0
        self.is_remote_controlled = False
        self.next_keep_going_timestamp = 0
        self.should_quit = False
    @staticmethod
    def print_data(*data):
        for d in data:
            print(f'{d["did"]:40s} {str(d["decoded"]):>6s}')
    def info(self):
        self.print_data(*self.vac.get_properties(
            'battery_level',
            'battery_state',
            'robot_fault',
            'robot_status',
            ))

        self.print_data(*self.vac.get_properties(
            'clean_work_mode',
            'clean_time_duration',
            'clean_size',
            'clean_area',
            'clean_timer',
            'clean_mode',
            'clean_delete_timer',
            'clean_water_box',
            'clean_object_name',
            'clean_start_time',
            'clean_total_clean_time',
            'clean_total_clean_times',
            'clean_total_clean_area',
            'clean_clean_log_start_time',
            'clean_button_led',
            'clean_task_done',
            'clean_mopmode',
            'clean_clean_info',
            'clean_clean_status',
            'clean_save_map_status',
        ))

        self.print_data(*self.vac.get_properties(
            'annoy_enable',
            'annoy_start_time',
            'annoy_stop_time',
            'remote_deg',
            'remote_speed',
            'consumable_life_sieve',
            'consumable_life_brush_side',
            'consumable_life_brush_main',
            'warn_code',
            'audio_volume',
            'audio_voice_packets',
            'time_zone',
            'main_brush_time_left',
            'main_brush_life_level',
            'filter_life_level',
            'filter_time_left',
            'side_brush_time_left',
            'side_brush_life_level',
            ))
    def remote_action(self, deg, speed):
        self.vac.action("remote_start", remote_deg=deg, remote_speed=speed)
        self.next_keep_going_timestamp = time.time() + 1
        self.is_remote_controlled = True
        print(deg, speed)
    def remote_keep_going(self):
        while not self.should_quit:
            if self.is_remote_controlled:
                if time.time() > self.next_keep_going_timestamp:
                    print(self.next_keep_going_timestamp, 'keep')
                    self.remote_action(0, self.speed)
            time.sleep(.1)
    def run(self):
        thread = Thread(target = self.remote_keep_going)
        thread.start()
        while not self.should_quit:
            time.sleep(.1)
            key = getkey()
            if key == keys.LEFT: self.remote_action(15, self.speed)
            elif key == keys.RIGHT: self.remote_action(-15, self.speed)
            elif key == keys.UP:
                if self.speed < 0:
                    self.speed = 0
                else:
                    self.speed = min(max(self.speed**1.3, 10), 500)
                self.remote_action(0, self.speed)
            elif key == keys.DOWN:
                if self.speed > 15:
                    self.speed = self.speed**.9
                elif self.speed > 0:
                    self.speed = 0
                else:
                    self.speed = -10
                self.remote_action(0, self.speed)
            elif key == ' ':
                self.speed = 0
                self.remote_action(0, self.speed)
            elif key == 'Q': self.should_quit = True
            elif key == 'q': self.is_remote_controlled = False
            elif key == 'i': self.info()
            elif key == 'I': self.vac.action("identify")
            elif key == 'H':
                self.vac.action("battery_start_charge")
                self.is_remote_controlled = False
            elif key == 's':
                self.vac.action("robot_start_sweep")
                self.is_remote_controlled = False
            elif key == 'S':
                self.vac.action("robot_stop_sweeping")
                self.is_remote_controlled = False


token = '11111111111111111111111111111111'
ip = '192.168.1.1'
c = Control(ip, token)
c.run()
