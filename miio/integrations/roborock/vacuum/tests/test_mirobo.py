from click.testing import CliRunner

from ..vacuum_cli import cli


def test_config_read(mocker):
    """Make sure config file is being read."""
    x = mocker.patch("miio.integrations.roborock.vacuum.vacuum_cli._read_config")
    mocker.patch("miio.device.Device.send")

    runner = CliRunner()
    runner.invoke(
        cli, ["--ip", "127.0.0.1", "--token", "ffffffffffffffffffffffffffffffff"]
    )

    x.assert_called()
