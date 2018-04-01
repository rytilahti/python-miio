import base64
import json
import os
from unittest import TestCase

import pytest

from miio import ChuangmiIr
from miio.chuangmi_ir import ChuangmiIrException
from .dummies import DummyDevice

with open(os.path.join(
        os.path.dirname(__file__), 'test_chuangmi_ir.json')) as inp:
    test_data = json.load(inp)


class DummyChuangmiIr(DummyDevice, ChuangmiIr):
    def __init__(self, *args, **kwargs):
        self.state = {
            'last_ir_played': None,
        }
        self.return_values = {
            'miIO.ir_learn': lambda x: True,
            'miIO.ir_read': lambda x: True,
            'miIO.ir_play': self._ir_play_input_validation,
        }
        super().__init__(args, kwargs)

    def _ir_play_input_validation(self, payload):
        try:
            base64.b64decode(payload['code'])
            self._set_state('last_ir_played', [[
                payload['code'], payload.get('freq')
            ]])
            return True
        except TypeError:
            return False


@pytest.fixture(scope="class")
def chuangmiir(request):
    request.cls.device = DummyChuangmiIr()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("chuangmiir")
class TestChuangmiIr(TestCase):
    def test_learn(self):
        assert self.device.learn() is True
        assert self.device.learn(30) is True

        with pytest.raises(ChuangmiIrException):
            self.device.learn(-1)

        with pytest.raises(ChuangmiIrException):
            self.device.learn(1000001)

    def test_read(self):
        assert self.device.read() is True
        assert self.device.read(30) is True

        with pytest.raises(ChuangmiIrException):
            self.device.read(-1)

        with pytest.raises(ChuangmiIrException):
            self.device.read(1000001)

    def test_play_raw(self):
        for args in test_data['test_raw_ok']:
            with self.subTest():
                self.device._reset_state()
                self.assertTrue(self.device.play_raw(*args['in']))
                self.assertSequenceEqual(
                    self.device.state['last_ir_played'],
                    args['out']
                )

    def test_pronto_to_raw(self):
        for args in test_data['test_pronto_ok']:
            with self.subTest():
                self.assertSequenceEqual(
                    ChuangmiIr.pronto_to_raw(*args['in']),
                    args['out']
                )

        for args in test_data['test_pronto_exception']:
            with self.subTest():
                with pytest.raises(ChuangmiIrException):
                    ChuangmiIr.pronto_to_raw(*args['in'])

    def test_play_pronto(self):
        for args in test_data['test_pronto_ok']:
            with self.subTest():
                self.device._reset_state()
                self.assertTrue(self.device.play_pronto(*args['in']))
                self.assertSequenceEqual(
                    self.device.state['last_ir_played'],
                    args['out']
                )

        for args in test_data['test_pronto_exception']:
            with pytest.raises(ChuangmiIrException):
                self.device.play_pronto(*args['in'])

    def test_play_auto(self):
        for args in test_data['test_raw_ok'] + test_data['test_pronto_ok']:
            if len(args['in']) > 1:  # autodetect doesn't take any extra args
                continue
            with self.subTest():
                self.device._reset_state()
                self.assertTrue(self.device.play(*args['in']))
                self.assertSequenceEqual(
                    self.device.state['last_ir_played'],
                    args['out']
                )

    def test_play_with_type(self):
        for type_, tests in [
                ('raw', test_data['test_raw_ok']),
                ('pronto', test_data['test_pronto_ok'])]:
            for args in tests:
                with self.subTest():
                    command = '{}:{}'.format(
                        type_, ':'.join(map(str, args['in'])))
                    self.assertTrue(self.device.play(command))
                    self.assertSequenceEqual(
                        self.device.state['last_ir_played'],
                        args['out']
                    )
        with pytest.raises(ChuangmiIrException):
            self.device.play('invalid:command')

        with pytest.raises(ChuangmiIrException):
            self.device.play('pronto:command:invalid:argument:count')

        with pytest.raises(ChuangmiIrException):
            self.device.play('pronto:command:invalidargument')
