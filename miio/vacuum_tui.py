try:
    import curses

    curses_available = True
except ImportError:
    curses_available = False

import enum
from typing import Tuple

from .vacuum import Vacuum


class Control(enum.Enum):

    Quit = "q"
    Forward = "w"
    ForwardFast = "W"
    Backward = "s"
    BackwardFast = "S"
    Left = "a"
    LeftFast = "A"
    Right = "d"
    RightFast = "D"


class VacuumTUI:
    def __init__(self, vac: Vacuum):
        if not curses_available:
            raise ImportError("curses library is not available")

        self.vac = vac
        self.rot = 0
        self.rot_delta = 30
        self.rot_min = Vacuum.MANUAL_ROTATION_MIN
        self.rot_max = Vacuum.MANUAL_ROTATION_MAX
        self.vel = 0.0
        self.vel_delta = 0.1
        self.vel_min = Vacuum.MANUAL_VELOCITY_MIN
        self.vel_max = Vacuum.MANUAL_VELOCITY_MAX
        self.dur = 10 * 1000

    def run(self) -> None:
        self.vac.manual_start()
        try:
            curses.wrapper(self.main)
        finally:
            self.vac.manual_stop()

    def main(self, screen) -> None:
        screen.addstr("Use wasd to control the device.\n")
        screen.addstr("Hold shift to enable fast mode.\n")
        screen.addstr("Press q to quit.\n")
        screen.refresh()
        self.loop(screen)

    def loop(self, win) -> None:
        done = False
        while not done:
            key = win.getkey()
            text, done = self.handle_key(key)
            win.clear()
            win.addstr(text)
            win.refresh()

    def handle_key(self, key: str) -> Tuple[str, bool]:
        try:
            ctl = Control(key)
        except ValueError as e:
            return "Ignoring %s: %s.\n" % (key, e), False

        done = self.dispatch_control(ctl)
        return self.info(), done

    def dispatch_control(self, ctl: Control) -> bool:
        if ctl == Control.Quit:
            return True

        if ctl == Control.Forward:
            self.vel = min(self.vel + self.vel_delta, self.vel_max)
        elif ctl == Control.ForwardFast:
            self.vel = 0 if self.vel < 0 else self.vel_max

        elif ctl == Control.Backward:
            self.vel = max(self.vel - self.vel_delta, self.vel_min)
        elif ctl == Control.BackwardFast:
            self.vel = 0 if self.vel > 0 else self.vel_min

        elif ctl == Control.Left:
            self.rot = min(self.rot + self.rot_delta, self.rot_max)
        elif ctl == Control.LeftFast:
            self.rot = 0 if self.rot < 0 else self.rot_max

        elif ctl == Control.Right:
            self.rot = max(self.rot - self.rot_delta, self.rot_min)
        elif ctl == Control.RightFast:
            self.rot = 0 if self.rot > 0 else self.rot_min

        self.vac.manual_control(rotation=self.rot, velocity=self.vel, duration=self.dur)
        return False

    def info(self) -> str:
        return "Rotation=%s\nVelocity=%s\n" % (self.rot, self.vel)
