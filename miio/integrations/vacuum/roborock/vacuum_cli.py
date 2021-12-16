import ast
import contextlib
import json
import logging
import pathlib
import sys
import threading
import time
from pprint import pformat as pf
from typing import Any, List  # noqa: F401

import click
from appdirs import user_cache_dir
from tqdm import tqdm

from miio.click_common import (
    ExceptionHandlerGroup,
    LiteralParamType,
    validate_ip,
    validate_token,
)
from miio.device import Device, UpdateState
from miio.exceptions import DeviceInfoUnavailableException
from miio.miioprotocol import MiIOProtocol
from miio.updater import OneShotServer

from .vacuum import CarpetCleaningMode, Consumable, RoborockVacuum, TimerState
from .vacuum_tui import VacuumTUI

from miio.discovery import Discovery

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(Device, ensure=True)


def _read_config(file):
    """Return sequence id information."""
    config = {"seq": 0, "manual_seq": 0}
    with contextlib.suppress(FileNotFoundError, TypeError, ValueError), open(file) as f:
        config = json.load(f)

    return config


@click.group(invoke_without_command=True, cls=ExceptionHandlerGroup)
@click.option("--ip", envvar="MIROBO_IP", callback=validate_ip)
@click.option("--token", envvar="MIROBO_TOKEN", callback=validate_token)
@click.option("-d", "--debug", default=False, count=True)
@click.option(
    "--id-file",
    type=click.Path(dir_okay=False, writable=True),
    default=user_cache_dir("python-miio") + "/python-mirobo.seq",
)
@click.version_option()
@click.pass_context
def cli(ctx, ip: str, token: str, debug: int, id_file: str):
    """A tool to command Xiaomi Vacuum robot."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    # if we are scanning, we do not try to connect.
    if ctx.invoked_subcommand == "discover":
        ctx.obj = "discover"
        return

    if ip is None or token is None:
        click.echo("You have to give ip and token!")
        sys.exit(-1)

    config = _read_config(id_file)

    start_id = config["seq"]
    manual_seq = config["manual_seq"]
    _LOGGER.debug("Using config: %s", config)

    vac = RoborockVacuum(ip, token, start_id, debug)

    vac.manual_seqnum = manual_seq
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = vac

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)
        cleanup(vac, id_file=id_file)


@cli.resultcallback()
@pass_dev
def cleanup(vac: RoborockVacuum, *args, **kwargs):
    if vac.ip is None:  # dummy Device for discovery, skip teardown
        return
    id_file = kwargs["id_file"]
    seqs = {"seq": vac.raw_id, "manual_seq": vac.manual_seqnum}
    _LOGGER.debug("Writing %s to %s", seqs, id_file)

    path_obj = pathlib.Path(id_file)
    dir = path_obj.parents[0]
    dir.mkdir(parents=True, exist_ok=True)

    with open(id_file, "w") as f:
        json.dump(seqs, f)


@cli.command()
@click.option("--handshake", type=bool, default=False)
def discover(handshake):
    """Search for robots in the network."""
    if handshake:
        MiIOProtocol.discover()
    else:
        Discovery.discover_mdns()


@cli.command()
@pass_dev
def status(vac: RoborockVacuum):
    """Returns the state information."""
    res = vac.status()
    if not res:
        return  # bail out

    if res.error_code:
        click.echo(click.style("Error: %s !" % res.error, bold=True, fg="red"))
    if res.is_water_shortage:
        click.echo(click.style("Water is running low!", bold=True, fg="blue"))
    click.echo(click.style("State: %s" % res.state, bold=True))
    click.echo("Battery: %s %%" % res.battery)
    click.echo("Fanspeed: %s %%" % res.fanspeed)
    click.echo("Cleaning since: %s" % res.clean_time)
    click.echo("Cleaned area: %s m²" % res.clean_area)
    click.echo("Water box attached: %s" % res.is_water_box_attached)
    if res.is_water_box_carriage_attached is not None:
        click.echo("Mop attached: %s" % res.is_water_box_carriage_attached)


@cli.command()
@pass_dev
def consumables(vac: RoborockVacuum):
    """Return consumables status."""
    res = vac.consumable_status()
    click.echo(f"Main brush:   {res.main_brush} (left {res.main_brush_left})")
    click.echo(f"Side brush:   {res.side_brush} (left {res.side_brush_left})")
    click.echo(f"Filter:       {res.filter} (left {res.filter_left})")
    click.echo(f"Sensor dirty: {res.sensor_dirty} (left {res.sensor_dirty_left})")


@cli.command()
@click.argument("name", type=str, required=True)
@pass_dev
def reset_consumable(vac: RoborockVacuum, name):
    """Reset consumable state.

    Allowed values: main_brush, side_brush, filter, sensor_dirty
    """
    if name == "main_brush":
        consumable = Consumable.MainBrush
    elif name == "side_brush":
        consumable = Consumable.SideBrush
    elif name == "filter":
        consumable = Consumable.Filter
    elif name == "sensor_dirty":
        consumable = Consumable.SensorDirty
    else:
        click.echo("Unexpected state name: %s" % name)
        return

    click.echo(f"Resetting consumable '{name}': {vac.consumable_reset(consumable)}")


@cli.command()
@pass_dev
def start(vac: RoborockVacuum):
    """Start cleaning."""
    click.echo("Starting cleaning: %s" % vac.start())


@cli.command()
@pass_dev
def spot(vac: RoborockVacuum):
    """Start spot cleaning."""
    click.echo("Starting spot cleaning: %s" % vac.spot())


@cli.command()
@pass_dev
def pause(vac: RoborockVacuum):
    """Pause cleaning."""
    click.echo("Pausing: %s" % vac.pause())


@cli.command()
@pass_dev
def stop(vac: RoborockVacuum):
    """Stop cleaning."""
    click.echo("Stop cleaning: %s" % vac.stop())


@cli.command()
@pass_dev
def home(vac: RoborockVacuum):
    """Return home."""
    click.echo("Requesting return to home: %s" % vac.home())


@cli.command()
@pass_dev
@click.argument("x_coord", type=int)
@click.argument("y_coord", type=int)
def goto(vac: RoborockVacuum, x_coord: int, y_coord: int):
    """Go to specific target."""
    click.echo("Going to target : %s" % vac.goto(x_coord, y_coord))


@cli.command()
@pass_dev
@click.argument("zones", type=LiteralParamType(), required=True)
def zoned_clean(vac: RoborockVacuum, zones: List):
    """Clean zone."""
    click.echo("Cleaning zone(s) : %s" % vac.zoned_clean(zones))


@cli.group()
@pass_dev
# @click.argument('command', required=False)
def manual(vac: RoborockVacuum):
    """Control the robot manually."""
    command = ""
    if command == "start":
        click.echo("Starting manual control")
        return vac.manual_start()
    if command == "stop":
        click.echo("Stopping manual control")
        return vac.manual_stop()
    # if not vac.manual_mode and command :


@manual.command()
@pass_dev
def tui(vac: RoborockVacuum):
    """TUI for the manual mode."""
    VacuumTUI(vac).run()


@manual.command(name="start")
@pass_dev
def manual_start(vac: RoborockVacuum):  # noqa: F811  # redef of start
    """Activate the manual mode."""
    click.echo("Activating manual controls")
    return vac.manual_start()


@manual.command(name="stop")
@pass_dev
def manual_stop(vac: RoborockVacuum):  # noqa: F811  # redef of stop
    """Deactivate the manual mode."""
    click.echo("Deactivating manual controls")
    return vac.manual_stop()


@manual.command()
@pass_dev
@click.argument("degrees", type=int)
def left(vac: RoborockVacuum, degrees: int):
    """Turn to left."""
    click.echo("Turning %s degrees left" % degrees)
    return vac.manual_control(degrees, 0)


@manual.command()
@pass_dev
@click.argument("degrees", type=int)
def right(vac: RoborockVacuum, degrees: int):
    """Turn to right."""
    click.echo("Turning right")
    return vac.manual_control(-degrees, 0)


@manual.command()
@click.argument("amount", type=float)
@pass_dev
def forward(vac: RoborockVacuum, amount: float):
    """Run forwards."""
    click.echo("Moving forwards")
    return vac.manual_control(0, amount)


@manual.command()
@click.argument("amount", type=float)
@pass_dev
def backward(vac: RoborockVacuum, amount: float):
    """Run backwards."""
    click.echo("Moving backwards")
    return vac.manual_control(0, -amount)


@manual.command()
@pass_dev
@click.argument("rotation", type=float)
@click.argument("velocity", type=float)
@click.argument("duration", type=int)
def move(vac: RoborockVacuum, rotation: int, velocity: float, duration: int):
    """Pass raw manual values."""
    return vac.manual_control(rotation, velocity, duration)


@cli.command()
@click.argument("cmd", required=False)
@click.argument("start_hr", type=int, required=False)
@click.argument("start_min", type=int, required=False)
@click.argument("end_hr", type=int, required=False)
@click.argument("end_min", type=int, required=False)
@pass_dev
def dnd(
    vac: RoborockVacuum,
    cmd: str,
    start_hr: int,
    start_min: int,
    end_hr: int,
    end_min: int,
):
    """Query and adjust do-not-disturb mode."""
    if cmd == "off":
        click.echo("Disabling DND..")
        click.echo(vac.disable_dnd())
    elif cmd == "on":
        click.echo(f"Enabling DND {start_hr}:{start_min} to {end_hr}:{end_min}")
        click.echo(vac.set_dnd(start_hr, start_min, end_hr, end_min))
    else:
        x = vac.dnd_status()
        click.echo(
            click.style(
                f"Between {x.start} and {x.end} (enabled: {x.enabled})",
                bold=x.enabled,
            )
        )


@cli.command()
@click.argument("speed", type=int, required=False)
@pass_dev
def fanspeed(vac: RoborockVacuum, speed):
    """Query and adjust the fan speed."""
    if speed:
        click.echo("Setting fan speed to %s" % speed)
        vac.set_fan_speed(speed)
    else:
        click.echo("Current fan speed: %s" % vac.fan_speed())


@cli.group(invoke_without_command=True)
@pass_dev
@click.pass_context
def timer(ctx, vac: RoborockVacuum):
    """List and modify existing timers."""
    if ctx.invoked_subcommand is not None:
        return
    timers = vac.timer()
    click.echo("Timezone: %s\n" % vac.timezone())
    for idx, timer in enumerate(timers):
        color = "green" if timer.enabled else "yellow"
        click.echo(
            click.style(
                f"Timer #{idx}, id {timer.id} (ts: {timer.ts})",
                bold=True,
                fg=color,
            )
        )
        click.echo("  %s" % timer.cron)
        min, hr, x, y, days = timer.cron.split(" ")
        cron = f"{min} {hr} {x} {y} {days}"
        click.echo("  %s" % cron)


@timer.command()
@click.option("--cron")
@click.option("--command", default="", required=False)
@click.option("--params", default="", required=False)
@pass_dev
def add(vac: RoborockVacuum, cron, command, params):
    """Add a timer."""
    click.echo(vac.add_timer(cron, command, params))


@timer.command()
@click.argument("timer_id", type=int, required=True)
@pass_dev
def delete(vac: RoborockVacuum, timer_id):
    """Delete a timer."""
    click.echo(vac.delete_timer(timer_id))


@timer.command()
@click.argument("timer_id", type=int, required=True)
@click.option("--enable", is_flag=True)
@click.option("--disable", is_flag=True)
@pass_dev
def update(vac: RoborockVacuum, timer_id, enable, disable):
    """Enable/disable a timer."""
    if enable and not disable:
        vac.update_timer(timer_id, TimerState.On)
    elif disable and not enable:
        vac.update_timer(timer_id, TimerState.Off)
    else:
        click.echo("You need to specify either --enable or --disable")


@cli.command()
@pass_dev
def find(vac: RoborockVacuum):
    """Find the robot."""
    click.echo("Sending find the robot calls.")
    click.echo(vac.find())


@cli.command()
@pass_dev
def map(vac: RoborockVacuum):
    """Return the map token."""
    click.echo(vac.map())


@cli.command()
@pass_dev
def info(vac: RoborockVacuum):
    """Return device information."""
    try:
        res = vac.info()

        click.echo("%s" % res)
        _LOGGER.debug("Full response: %s", pf(res.raw))
    except DeviceInfoUnavailableException:
        click.echo(
            "Unable to fetch info, this can happen when the vacuum "
            "is not connected to the Xiaomi cloud."
        )


@cli.command()
@pass_dev
def cleaning_history(vac: RoborockVacuum):
    """Query the cleaning history."""
    res = vac.clean_history()
    click.echo("Total clean count: %s" % res.count)
    click.echo(f"Cleaned for: {res.total_duration} (area: {res.total_area} m²)")
    if res.dust_collection_count is not None:
        click.echo("Emptied dust collection bin: %s times" % res.dust_collection_count)
    click.echo()
    for idx, id_ in enumerate(res.ids):
        details = vac.clean_details(id_, return_list=False)
        color = "green" if details.complete else "yellow"
        click.echo(
            click.style(
                "Clean #%s: %s-%s (complete: %s, error: %s)"
                % (idx, details.start, details.end, details.complete, details.error),
                bold=True,
                fg=color,
            )
        )
        click.echo("  Area cleaned: %s m²" % details.area)
        click.echo("  Duration: (%s)" % details.duration)
        click.echo()


@cli.command()
@click.argument("volume", type=int, required=False)
@click.option("--test", "test_mode", is_flag=True, help="play a test tune")
@pass_dev
def sound(vac: RoborockVacuum, volume: int, test_mode: bool):
    """Query and change sound settings."""
    if volume is not None:
        click.echo("Setting sound volume to %s" % volume)
        vac.set_sound_volume(volume)
    if test_mode:
        vac.test_sound_volume()
    click.echo("Current sound: %s" % vac.sound_info())
    click.echo("Current volume: %s" % vac.sound_volume())
    click.echo("Install progress: %s" % vac.sound_install_progress())


@cli.command()
@click.argument("url")
@click.argument("md5sum", required=False, default=None)
@click.option("--sid", type=int, required=False, default=10000)
@click.option("--ip", required=False)
@pass_dev
def install_sound(vac: RoborockVacuum, url: str, md5sum: str, sid: int, ip: str):
    """Install a sound.

    When passing a local file this will create a self-hosting server
     for the given file and the md5sum will be calculated automatically.

    For URLs you have to specify the md5sum manually.

    `--ip` can be used to override automatically detected IP address for
     the device to contact for the update.
    """
    click.echo(f"Installing from {url} (md5: {md5sum}) for id {sid}")

    local_url = None
    server = None
    if url.startswith("http"):
        if md5sum is None:
            click.echo("You need to pass md5 when using URL for updating.")
            return
        local_url = url
    else:
        server = OneShotServer(url)
        local_url = server.url(ip)
        md5sum = server.md5

        t = threading.Thread(target=server.serve_once)
        t.start()
        click.echo("Hosting file at %s" % local_url)

    click.echo(vac.install_sound(local_url, md5sum, sid))

    progress = vac.sound_install_progress()
    while progress.is_installing:
        progress = vac.sound_install_progress()
        click.echo(f"{progress.state.name} ({progress.progress} %)")
        time.sleep(1)

    progress = vac.sound_install_progress()

    if progress.is_errored:
        click.echo("Error during installation: %s" % progress.error)
    else:
        click.echo("Installation of sid '%s' complete!" % sid)

    if server is not None:
        t.join()


@cli.command()
@pass_dev
def serial_number(vac: RoborockVacuum):
    """Query serial number."""
    click.echo("Serial#: %s" % vac.serial_number())


@cli.command()
@click.argument("tz", required=False)
@pass_dev
def timezone(vac: RoborockVacuum, tz=None):
    """Query or set the timezone."""
    if tz is not None:
        click.echo("Setting timezone to: %s" % tz)
        click.echo(vac.set_timezone(tz))
    else:
        click.echo("Timezone: %s" % vac.timezone())


@cli.command()
@click.argument("enabled", required=False, type=bool)
@pass_dev
def carpet_mode(vac: RoborockVacuum, enabled=None):
    """Query or set the carpet mode."""
    if enabled is None:
        click.echo(vac.carpet_mode())
    else:
        click.echo(vac.set_carpet_mode(enabled))


@cli.command()
@click.argument("mode", required=False, type=str)
@pass_dev
def carpet_cleaning_mode(vac: RoborockVacuum, mode=None):
    """Query or set the carpet cleaning/avoidance mode.

    Allowed values: Avoid, Rise, Ignore
    """

    if mode is None:
        click.echo("Carpet cleaning mode: %s" % vac.carpet_cleaning_mode())
    else:
        click.echo(
            "Setting carpet cleaning mode: %s"
            % vac.set_carpet_cleaning_mode(CarpetCleaningMode[mode])
        )


@cli.command()
@click.argument("ssid", required=True)
@click.argument("password", required=True)
@click.argument("uid", type=int, required=False)
@click.option("--timezone", type=str, required=False, default=None)
@pass_dev
def configure_wifi(
    vac: RoborockVacuum, ssid: str, password: str, uid: int, timezone: str
):
    """Configure the wifi settings.

    Note that some newer firmwares may expect you to define the timezone by using
    --timezone.
    """
    click.echo("Configuring wifi to SSID: %s" % ssid)
    click.echo(vac.configure_wifi(ssid, password, uid, timezone))


@cli.command()
@pass_dev
def update_status(vac: RoborockVacuum):
    """Return update state and progress."""
    update_state = vac.update_state()
    click.echo("Update state: %s" % update_state)

    if update_state == UpdateState.Downloading:
        click.echo("Update progress: %s" % vac.update_progress())


@cli.command()
@click.argument("url", required=True)
@click.argument("md5", required=False, default=None)
@click.option("--ip", required=False)
@pass_dev
def update_firmware(vac: RoborockVacuum, url: str, md5: str, ip: str):
    """Update device firmware.

    If `url` starts with http* it is expected to be an URL.
     In that case md5sum of the file has to be given.

    `--ip` can be used to override automatically detected IP address for
     the device to contact for the update.
    """

    # TODO Check that the device is in updateable state.

    click.echo("Going to update from %s" % url)
    if url.lower().startswith("http"):
        if md5 is None:
            click.echo("You need to pass md5 when using URL for updating.")
            return

        click.echo(f"Using {url} (md5: {md5})")
    else:
        server = OneShotServer(url)
        url = server.url(ip)

        t = threading.Thread(target=server.serve_once)
        t.start()
        click.echo("Hosting file at %s" % url)
        md5 = server.md5

    update_res = vac.update(url, md5)
    if update_res:
        click.echo("Update started!")
    else:
        click.echo("Starting the update failed: %s" % update_res)

    with tqdm(total=100) as pbar:
        state = vac.update_state()
        while state == UpdateState.Downloading:
            try:
                state = vac.update_state()
                progress = vac.update_progress()
            except:  # noqa # nosec
                # we may not get our messages through during uploads
                continue

            if state == UpdateState.Installing:
                click.echo("Installation started, please wait until the vacuum reboots")
                break

            pbar.update(progress - pbar.n)
            pbar.set_description("%s" % state.name)
            time.sleep(1)


@cli.command()
@click.argument("cmd", required=True)
@click.argument("parameters", required=False)
@pass_dev
def raw_command(vac: RoborockVacuum, cmd, parameters):
    """Run a raw command."""
    params = []  # type: Any
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo(f"Sending cmd {cmd} with params {params}")
    click.echo(vac.raw_command(cmd, params))


if __name__ == "__main__":
    cli()
