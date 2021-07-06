"""Xiaomi Gateway Radio implementation."""

import click

from ..click_common import command
from .gatewaydevice import GatewayDevice


class Radio(GatewayDevice):
    """Radio controls for the gateway."""

    @command()
    def get_radio_info(self):
        """Radio play info."""
        return self._gateway.send("get_prop_fm")

    @command(click.argument("volume"))
    def set_radio_volume(self, volume):
        """Set radio volume."""
        return self._gateway.send("set_fm_volume", [volume])

    def play_music_new(self):
        """Unknown."""
        # {'from': '4', 'id': 9514,
        #  'method': 'set_default_music', 'params': [2, '21']}
        # {'from': '4', 'id': 9515,
        #  'method': 'play_music_new', 'params': ['21', 0]}
        raise NotImplementedError()

    def play_specify_fm(self):
        """play specific stream?"""
        raise NotImplementedError()
        # {"from": "4", "id": 65055, "method": "play_specify_fm",
        # "params": {"id": 764, "type": 0,
        # "url": "http://live.xmcdn.com/live/764/64.m3u8"}}
        return self._gateway.send("play_specify_fm")

    def play_fm(self):
        """radio on/off?"""
        raise NotImplementedError()
        # play_fm","params":["off"]}
        return self._gateway.send("play_fm")

    def volume_ctrl_fm(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("volume_ctrl_fm")

    def get_channels(self):
        """Unknown."""
        raise NotImplementedError()
        # "method": "get_channels", "params": {"start": 0}}
        return self._gateway.send("get_channels")

    def add_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("add_channels")

    def remove_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("remove_channels")

    def get_default_music(self):
        """seems to timeout (w/o internet)."""
        # params [0,1,2]
        raise NotImplementedError()
        return self._gateway.send("get_default_music")

    @command()
    def get_music_info(self):
        """Unknown."""
        info = self._gateway.send("get_music_info")
        click.echo("info: %s" % info)
        free_space = self._gateway.send("get_music_free_space")
        click.echo("free space: %s" % free_space)

    @command()
    def get_mute(self):
        """mute of what?"""
        return self._gateway.send("get_mute")

    def download_music(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("download_music")

    def delete_music(self):
        """delete music."""
        raise NotImplementedError()
        return self._gateway.send("delete_music")

    def download_user_music(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("download_user_music")

    def get_download_progress(self):
        """progress for music downloads or updates?"""
        # returns [':0']
        raise NotImplementedError()
        return self._gateway.send("get_download_progress")

    @command()
    def set_sound_playing(self):
        """stop playing?"""
        return self._gateway.send("set_sound_playing", ["off"])

    def set_default_music(self):
        """Unknown."""
        raise NotImplementedError()
        # method":"set_default_music","params":[0,"2"]}
