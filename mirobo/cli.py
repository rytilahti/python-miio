# -*- coding: UTF-8 -*-
import logging
import click
import pretty_cron
import ast
import sys

if sys.version_info < (3,4):
    print("To use this script you need python 3.4 or newer! got %s" % sys.version_info)
    sys.exit(1)

import mirobo

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(mirobo.Vacuum)

@click.group(invoke_without_command=True)
@click.option('--ip', envvar="MIROBO_IP", required=True)
@click.option('--token', envvar="MIROBO_TOKEN", required=True)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, ip, token, debug):
    """A tool to command Xiaomi Vacuum robot."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    # if we are scanning, we do not try to connect.
    if ctx.invoked_subcommand == "discover":
        return

    vac = mirobo.Vacuum(ip, token)

    ctx.obj = vac

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)

@cli.command()
def discover():
    """Search for robots in the network."""
    mirobo.Vacuum.discover()


@cli.command()
@pass_dev
def status(vac):
    """Returns the state information."""
    res = vac.status()
    if not res:
        return  # bail out

    if res.error_code:
        click.echo(click.style("Error: %s !" % res.error,
                               bold=True, fg='red'))
    click.echo(click.style("State: %s" % res.state, bold=True))
    click.echo("Battery: %s" % res.battery)
    click.echo("Fanspeed: %s" % res.fanspeed)
    click.echo("Cleaning since: %s" % res.clean_time)
    click.echo("Cleaned area: %s m²" % res.clean_area)
    click.echo("DND enabled: %s" % res.dnd)
    click.echo("Map present: %s" % res.map)
    click.echo("in_cleaning: %s" % res.in_cleaning)


@cli.command()
@pass_dev
def consumables(vac):
    """Return consumables status."""
    res = vac.consumable_status()
    click.echo(res)

@cli.command()
@pass_dev
def start(vac):
    """Start cleaning."""
    click.echo("Starting cleaning: %s" % vac.start())


@cli.command()
@pass_dev
def spot(vac):
    """Start spot cleaning."""
    click.echo("Starting spot cleaning: %s" % vac.spot())


@cli.command()
@pass_dev
def pause(vac):
    """Pause cleaning."""
    click.echo("Pausing: %s" % vac.pause())


@cli.command()
@pass_dev
def stop(vac):
    """Stop cleaning."""
    click.echo("Stop cleaning: %s" % vac.stop())


@cli.command()
@pass_dev
def home(vac):
    """Return home."""
    click.echo("Requesting return to home: %s" % vac.home())


@cli.command()
@click.argument('cmd', required=False)
@click.argument('start_hr', required=False)
@click.argument('start_min', required=False)
@click.argument('end_hr', required=False)
@click.argument('end_min', required=False)
@pass_dev
def dnd(vac, cmd, start_hr, start_min, end_hr, end_min):
    """Query and adjust do-not-disturb mode."""
    if cmd == "off":
        click.echo("Disabling DND..")
        print(vac.disable_dnd())
    elif cmd == "on":
        click.echo("Enabling DND %s:%s to %s:%s" % (start_hr, start_min,
                                                    end_hr, end_min))
        print(vac.set_dnd(start_hr, start_min, end_hr, end_min))
    else:
        x = vac.dnd_status()[0]
        click.echo("DND %02i:%02i to %02i:%02i (enabled: %s)" % (
            x['start_hour'], x['start_minute'],
            x['end_hour'], x['end_minute'],
            x['enabled']))


@cli.command()
@click.argument('speed', type=int, required=False)
@pass_dev
def fanspeed(vac, speed):
    """Query and adjust the fan speed."""
    if speed:
        click.echo("Setting fan speed to %s" % speed)
        print(vac.set_fan_speed(speed))
    else:
        click.echo("Current fan speed: %s" % vac.fan_speed())


@cli.command()
@click.argument('timer', required=False, default=None)
@pass_dev
def timer(vac, timer):
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
@click.argument('stop', required=False)
@pass_dev
def find(vac, stop):
    """Finds the robot."""
    if stop:
        click.echo("Stopping find calls..")
        click.echo(vac.find_stop())
    else:
        click.echo("Sending find the robot calls.")
        click.echo(vac.find())


@cli.command()
@pass_dev
def map(vac):
    """Get the map."""
    click.echo(vac.map())


@cli.command()
@pass_dev
def cleaning_history(vac):
    """Query the cleaning history."""
    res = vac.clean_history()
    click.echo("Total clean count: %s" % res.count)
    for idx, id_ in enumerate(res.ids):
        for e in vac.clean_details(id_):
            color = "green" if e.complete else "yellow"
            click.echo(click.style("Clean #%s: %s-%s (complete: %s, unknown: %s)" %
                                   (idx, e.start, e.end,
                                    e.complete, e.unknown), bold=True, fg=color))
            click.echo("  Area cleaned: %s m²" % e.area)
            click.echo("  Duration: (%s)" % e.duration)

@cli.command()
@click.argument('cmd', required=True)
@click.argument('parameters', required=False)
@pass_dev
def raw_command(vac, cmd, parameters):
    """Run a raw command."""
    params = []
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo("Sending cmd %s with params %s" % (cmd, params))
    click.echo(vac.raw_command(cmd, params))

if __name__ == "__main__":
    cli()
