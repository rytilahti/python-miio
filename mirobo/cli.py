# -*- coding: UTF-8 -*-
import logging
import click
import pretty_cron
import ast
import sys
import json
import ipaddress
from typing import Any

if sys.version_info < (3, 4):
    print("To use this script you need python 3.4 or newer, got %s" %
          sys.version_info)
    sys.exit(1)

import mirobo  # noqa: E402

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(mirobo.Vacuum)


def validate_ip(ctx, param, value):
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError as ex:
        raise click.BadParameter("Invalid IP: %s" % ex)


def validate_token(ctx, param, value):
    token_len = len(value)
    if token_len != 32:
        raise click.BadParameter("Token length != 32 chars: %s" % token_len)
    return value


@click.group(invoke_without_command=True)
@click.option('--ip', envvar="MIROBO_IP", callback=validate_ip)
@click.option('--token', envvar="MIROBO_TOKEN", callback=validate_token)
@click.option('-d', '--debug', default=False, count=True)
@click.option('--id-file', type=click.Path(dir_okay=False, writable=True),
              default='/tmp/python-mirobo.seq')
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
        return

    if ip is None or token is None:
        click.echo("You have to give ip and token!")
        sys.exit(-1)

    start_id = manual_seq = 0
    try:
        with open(id_file, 'r') as f:
            x = json.load(f)
            start_id = x.get("seq", 0)
            manual_seq = x.get("manual_seq", 0)
            _LOGGER.debug("Read stored sequence ids: %s" % x)
    except (FileNotFoundError, TypeError) as ex:
        _LOGGER.error("Unable to read the stored msgid: %s" % ex)
        pass

    vac = mirobo.Vacuum(ip, token, start_id, debug)
    vac.manual_seqnum = manual_seq
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = vac

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)
        cleanup(vac, id_file=id_file)


@cli.resultcallback()
@pass_dev
def cleanup(vac: mirobo.Vacuum, **kwargs):
    id_file = kwargs['id_file']
    seqs = {'seq': vac.raw_id, 'manual_seq': vac.manual_seqnum}
    _LOGGER.debug("Writing %s to %s" % (seqs, id_file))
    with open(id_file, 'w') as f:
        json.dump(seqs, f)
    #with open(id_file, 'w') as f:
    #    f.write(str(vac.raw_id))


@cli.command()
def discover():
    """Search for robots in the network."""
    mirobo.Vacuum.discover()


@cli.command()
@pass_dev
def status(vac: mirobo.Vacuum):
    """Returns the state information."""
    res = vac.status()
    if not res:
        return  # bail out

    if res.error_code:
        click.echo(click.style("Error: %s !" % res.error,
                               bold=True, fg='red'))
    click.echo(click.style("State: %s" % res.state, bold=True))
    click.echo("Battery: %s %%" % res.battery)
    click.echo("Fanspeed: %s %%" % res.fanspeed)
    click.echo("Cleaning since: %s" % res.clean_time)
    click.echo("Cleaned area: %s m²" % res.clean_area)
    # click.echo("DND enabled: %s" % res.dnd)
    # click.echo("Map present: %s" % res.map)
    # click.echo("in_cleaning: %s" % res.in_cleaning)


@cli.command()
@pass_dev
def consumables(vac: mirobo.Vacuum):
    """Return consumables status."""
    res = vac.consumable_status()
    click.echo("Main brush:   %s (left %s)" % (res.main_brush,
                                               res.main_brush_left))
    click.echo("Side brush:   %s (left %s)" % (res.side_brush,
                                               res.side_brush_left))
    click.echo("Filter:       %s (left %s)" % (res.filter,
                                               res.filter_left))
    click.echo("Sensor dirty: %s" % res.sensor_dirty)


@cli.command()
@pass_dev
def start(vac: mirobo.Vacuum):
    """Start cleaning."""
    click.echo("Starting cleaning: %s" % vac.start())


@cli.command()
@pass_dev
def spot(vac: mirobo.Vacuum):
    """Start spot cleaning."""
    click.echo("Starting spot cleaning: %s" % vac.spot())


@cli.command()
@pass_dev
def pause(vac: mirobo.Vacuum):
    """Pause cleaning."""
    click.echo("Pausing: %s" % vac.pause())


@cli.command()
@pass_dev
def stop(vac: mirobo.Vacuum):
    """Stop cleaning."""
    click.echo("Stop cleaning: %s" % vac.stop())


@cli.command()
@pass_dev
def home(vac: mirobo.Vacuum):
    """Return home."""
    click.echo("Requesting return to home: %s" % vac.home())


@cli.group()
@pass_dev
#@click.argument('command', required=False)
def manual(vac: mirobo.Vacuum):
    """Control the robot manually."""
    command = ''
    if command == 'start':
        click.echo("Starting manual control")
        return vac.manual_start()
    if command == 'stop':
        click.echo("Stopping manual control")
        return vac.manual_stop()
    #if not vac.manual_mode and command :

@manual.command()
@pass_dev
def start(vac: mirobo.Vacuum):
    """Activate the manual mode."""
    click.echo("Activating manual controls")
    return vac.manual_start()


@manual.command()
@pass_dev
def stop(vac: mirobo.Vacuum):
    """Deactivate the manual mode."""
    click.echo("Deactivating manual controls")
    return vac.manual_stop()


@manual.command()
@pass_dev
@click.argument('degrees', type=int)
def left(vac: mirobo.Vacuum, degrees: int):
    """Turn to left."""
    click.echo("Turning %s degrees left" % degrees)
    return vac.manual_control(degrees, 0)


@manual.command()
@pass_dev
@click.argument('degrees', type=int)
def right(vac: mirobo.Vacuum, degrees: int):
    """Turn to right."""
    click.echo("Turning right")
    return vac.manual_control(-degrees, 0)


@manual.command()
@click.argument('amount', type=float)
@pass_dev
def forward(vac: mirobo.Vacuum, amount: float):
    """Run forwards."""
    click.echo("Moving forwards")
    return vac.manual_control(0, amount)


@manual.command()
@click.argument('amount', type=float)
@pass_dev
def backward(vac: mirobo.Vacuum, amount:float):
    """Run backwards."""
    click.echo("Moving backwards")
    return vac.manual_control(0, -amount)


@manual.command()
@pass_dev
@click.argument('rotation', type=float)
@click.argument('velocity', type=float)
@click.argument('duration', type=int)
def move(vac: mirobo.Vacuum, rotation: float, velocity: float, duration: int):
    """Pass raw manual values"""
    return vac.manual_control(rotation, velocity, duration)


@cli.command()
@click.argument('cmd', required=False)
@click.argument('start_hr', type=int, required=False)
@click.argument('start_min', type=int, required=False)
@click.argument('end_hr', type=int, required=False)
@click.argument('end_min', type=int, required=False)
@pass_dev
def dnd(vac: mirobo.Vacuum, cmd: str,
        start_hr: int, start_min: int,
        end_hr: int, end_min: int):
    """Query and adjust do-not-disturb mode."""
    if cmd == "off":
        click.echo("Disabling DND..")
        print(vac.disable_dnd())
    elif cmd == "on":
        click.echo("Enabling DND %s:%s to %s:%s" % (start_hr, start_min,
                                                    end_hr, end_min))
        click.echo(vac.set_dnd(start_hr, start_min, end_hr, end_min))
    else:
        x = vac.dnd_status()[0]
        click.echo("DND %02i:%02i to %02i:%02i (enabled: %s)" % (
            x['start_hour'], x['start_minute'],
            x['end_hour'], x['end_minute'],
            x['enabled']))


@cli.command()
@click.argument('speed', type=int, required=False)
@pass_dev
def fanspeed(vac: mirobo.Vacuum, speed):
    """Query and adjust the fan speed."""
    if speed:
        click.echo("Setting fan speed to %s" % speed)
        vac.set_fan_speed(speed)
    else:
        click.echo("Current fan speed: %s" % vac.fan_speed())


@cli.command()
@click.argument('timer', required=False, default=None)
@pass_dev
def timer(vac: mirobo.Vacuum, timer):
    """Schedule vacuuming, times in GMT."""
    if timer:
        raise NotImplementedError()
        # vac.set_timer(x)
        pass
    else:
        timers = vac.timer()
        for idx, timer in enumerate(timers):
            color = "green" if timer.enabled else "yellow"
            #  Note ts == ID for changes
            click.echo(click.style("Timer #%s, id %s (ts: %s)" % (
                idx, timer.id, timer.ts), bold=True, fg=color))
            print("  %s" % timer.cron)
            min, hr, x, y, days = timer.cron.split(' ')
            # hr is in gmt+8 (chinese time), TODO convert to local
            hr = (int(hr) - 8) % 24
            cron = "%s %s %s %s %s" % (min, hr, x, y, days)
            click.echo("  %s" % pretty_cron.prettify_cron(cron))


@cli.command()
@pass_dev
def find(vac: mirobo.Vacuum):
    """Find the robot."""
    click.echo("Sending find the robot calls.")
    click.echo(vac.find())


@cli.command()
@pass_dev
def map(vac: mirobo.Vacuum):
    """Returns the map token."""
    click.echo(vac.map())


@cli.command()
@pass_dev
def cleaning_history(vac: mirobo.Vacuum):
    """Query the cleaning history."""
    res = vac.clean_history()
    click.echo("Total clean count: %s" % res.count)
    click.echo("Cleaned for: %s (area: %s m²)" % (res.total_duration,
                                                  res.total_area))
    click.echo()
    for idx, id_ in enumerate(res.ids):
        for e in vac.clean_details(id_):
            color = "green" if e.complete else "yellow"
            click.echo(click.style(
                "Clean #%s: %s-%s (complete: %s, error: %s)" % (
                    idx, e.start, e.end, e.complete, e.error),
                bold=True, fg=color))
            click.echo("  Area cleaned: %s m²" % e.area)
            click.echo("  Duration: (%s)" % e.duration)
            click.echo()


@cli.command()
@click.argument('cmd', required=True)
@click.argument('parameters', required=False)
@pass_dev
def raw_command(vac: mirobo.Vacuum, cmd, parameters):
    """Run a raw command."""
    params = []  # type: Any
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo("Sending cmd %s with params %s" % (cmd, params))
    click.echo(vac.raw_command(cmd, params))


if __name__ == "__main__":
    cli()
