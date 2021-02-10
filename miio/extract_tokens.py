import json
import logging
import sqlite3
import tempfile
from pprint import pformat as pf
from typing import Iterator

import attr
import click
import defusedxml.ElementTree as ET
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


@attr.s
class DeviceConfig:
    """A presentation of a device including its name, model, ip etc."""

    name = attr.ib()
    mac = attr.ib()
    ip = attr.ib()
    token = attr.ib()
    model = attr.ib()
    everything = attr.ib(default=None)


def read_android_yeelight(db) -> Iterator[DeviceConfig]:
    """Read tokens from Yeelight's android backup."""
    _LOGGER.info("Reading tokens from Yeelight Android DB")
    xml = ET.parse(db)
    devicelist = xml.find(".//set[@name='deviceList']")
    if not devicelist:
        _LOGGER.warning("Unable to find deviceList")
        return []

    for dev_elem in list(devicelist):
        dev = json.loads(dev_elem.text)
        ip = dev["localip"]
        mac = dev["mac"]
        model = dev["model"]
        name = dev["name"]
        token = dev["token"]

        config = DeviceConfig(
            name=name, ip=ip, mac=mac, model=model, token=token, everything=dev
        )

        yield config


class BackupDatabaseReader:
    """Main class for reading backup files.

    Example:
    .. code-block:: python

        r = BackupDatabaseReader()
        devices = r.read_tokens("/tmp/database.sqlite")
        for dev in devices:
            print("Got %s with token %s" % (dev.ip, dev.token)
    """

    def __init__(self, dump_raw=False):
        self.dump_raw = dump_raw

    @staticmethod
    def dump_raw(dev):
        """Dump whole database."""
        raw = {k: dev[k] for k in dev.keys()}
        _LOGGER.info(pf(raw))

    @staticmethod
    def decrypt_ztoken(ztoken):
        """Decrypt the given ztoken, used by apple."""
        if ztoken is None or len(ztoken) <= 32:
            return str(ztoken)

        keystring = "00000000000000000000000000000000"
        key = bytes.fromhex(keystring)
        cipher = Cipher(  # nosec
            algorithms.AES(key), modes.ECB(), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        token = decryptor.update(bytes.fromhex(ztoken[:64])) + decryptor.finalize()

        return token.decode()

    def read_apple(self) -> Iterator[DeviceConfig]:
        """Read Apple-specific database file."""
        _LOGGER.info("Reading tokens from Apple DB")
        c = self.conn.execute("SELECT * FROM ZDEVICE WHERE ZTOKEN IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev["ZLOCALIP"]
            mac = dev["ZMAC"]
            model = dev["ZMODEL"]
            name = dev["ZNAME"]
            token = BackupDatabaseReader.decrypt_ztoken(dev["ZTOKEN"])

            config = DeviceConfig(
                name=name, mac=mac, ip=ip, model=model, token=token, everything=dev
            )
            yield config

    def read_android(self) -> Iterator[DeviceConfig]:
        """Read Android-specific database file."""
        _LOGGER.info("Reading tokens from Android DB")
        c = self.conn.execute("SELECT * FROM devicerecord WHERE token IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev["localIP"]
            mac = dev["mac"]
            model = dev["model"]
            name = dev["name"]
            token = dev["token"]

            config = DeviceConfig(
                name=name, ip=ip, mac=mac, model=model, token=token, everything=dev
            )
            yield config

    def read_tokens(self, db) -> Iterator[DeviceConfig]:
        """Read device information out from a given database file.

        :param str db: Database file
        """
        self.db = db
        _LOGGER.info("Reading database from %s" % db)
        self.conn = sqlite3.connect(db)

        self.conn.row_factory = sqlite3.Row
        with self.conn:
            is_android = (
                self.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='devicerecord';"
                ).fetchone()
                is not None
            )
            is_apple = (
                self.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='ZDEVICE'"
                ).fetchone()
                is not None
            )
            if is_android:
                yield from self.read_android()
            elif is_apple:
                yield from self.read_apple()
            else:
                _LOGGER.error("Error, unknown database type!")


@click.command()
@click.argument("backup")
@click.option(
    "--write-to-disk",
    type=click.File("wb"),
    help="writes sqlite3 db to a file for debugging",
)
@click.option(
    "--password", type=str, help="password if the android database is encrypted"
)
@click.option(
    "--dump-all", is_flag=True, default=False, help="dump devices without ip addresses"
)
@click.option("--dump-raw", is_flag=True, help="dumps raw rows")
def main(backup, write_to_disk, password, dump_all, dump_raw):
    """Reads device information out from an sqlite3 DB.

    If the given file is an Android backup (.ab), the database will be extracted
    automatically. If the given file is an iOS backup, the tokens will be extracted (and
    decrypted if needed) automatically.
    """

    def read_miio_database(tar):
        DBFILE = "apps/com.xiaomi.smarthome/db/miio2.db"
        try:
            db = tar.extractfile(DBFILE)
        except KeyError as ex:
            click.echo("Unable to find miio database file %s: %s" % (DBFILE, ex))
            return []
        if write_to_disk:
            file = write_to_disk
        else:
            file = tempfile.NamedTemporaryFile()
        with file as fp:
            click.echo("Saving database to %s" % fp.name)
            fp.write(db.read())

            return list(reader.read_tokens(fp.name))

    def read_yeelight_database(tar):
        DBFILE = "apps/com.yeelight.cherry/sp/miot.xml"
        _LOGGER.info("Trying to read %s", DBFILE)
        try:
            db = tar.extractfile(DBFILE)
        except KeyError as ex:
            click.echo("Unable to find yeelight database file %s: %s" % (DBFILE, ex))
            return []

        return list(read_android_yeelight(db))

    devices = []
    reader = BackupDatabaseReader(dump_raw)
    if backup.endswith(".ab"):
        try:
            from android_backup import AndroidBackup
        except ModuleNotFoundError:
            click.echo(
                "You need to install android_backup to extract "
                "tokens from Android backup files."
            )
            return

        with AndroidBackup(backup, stream=False) as f:
            tar = f.read_data(password)

            devices.extend(read_miio_database(tar))

            devices.extend(read_yeelight_database(tar))
    else:
        devices = list(reader.read_tokens(backup))

    for dev in devices:
        if dev.ip or dump_all:
            click.echo(
                "%s\n"
                "\tModel: %s\n"
                "\tIP address: %s\n"
                "\tToken: %s\n"
                "\tMAC: %s" % (dev.name, dev.model, dev.ip, dev.token, dev.mac)
            )
            if dump_raw:
                click.echo(dev)


if __name__ == "__main__":
    main()
