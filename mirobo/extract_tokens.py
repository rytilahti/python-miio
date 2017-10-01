import logging
import click
import tempfile
import sqlite3
from Crypto.Cipher import AES
from pprint import pformat as pf
import attr
from .android_backup import AndroidBackup

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


@attr.s
class DeviceConfig:
    name = attr.ib()
    mac = attr.ib()
    ip = attr.ib()
    token = attr.ib()
    model = attr.ib()


class BackupDatabaseReader:
    def __init__(self, dump_raw=False):
        self.dump_raw = dump_raw

    @staticmethod
    def dump_raw(dev):
        raw = {k: dev[k] for k in dev.keys()}
        _LOGGER.info(pf(raw))

    @staticmethod
    def decrypt_ztoken(ztoken):
        if len(ztoken) <= 32:
            return ztoken

        keystring = '00000000000000000000000000000000'
        key = bytes.fromhex(keystring)
        cipher = AES.new(key, AES.MODE_ECB)
        token = cipher.decrypt(bytes.fromhex(ztoken[:64]))

        return token.decode()

    def read_apple(self):
        _LOGGER.info("Reading tokens from Apple DB")
        c = self.conn.execute("SELECT * FROM ZDEVICE WHERE ZTOKEN IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev['ZLOCALIP']
            mac = dev['ZMAC']
            model = dev['ZMODEL']
            name = dev['ZNAME']
            token = BackupDatabaseReader.decrypt_ztoken(dev['ZTOKEN'])

            config = DeviceConfig(name=name, mac=mac, ip=ip, model=model, token=token)
            yield config

    def read_android(self):
        _LOGGER.info("Reading tokens from Android DB")
        c = self.conn.execute("SELECT * FROM devicerecord WHERE token IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev['localIP']
            mac = dev['mac']
            model = dev['model']
            name = dev['name']
            token = dev['token']

            config = DeviceConfig(name=name, ip=ip, mac=mac,
                                  model=model, token=token)
            yield config

    def read_tokens(self, db):
        self.db = db
        _LOGGER.info("Reading database from %s" % db)
        self.conn = sqlite3.connect(db)

        self.conn.row_factory = sqlite3.Row
        with self.conn:
            is_android = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='devicerecord';").fetchone() is not None
            is_apple = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ZDEVICE'").fetchone() is not None
            if is_android:
                yield from self.read_android()
            elif is_apple:
                yield from self.read_apple()
            else:
                _LOGGER.error("Error, unknown database type!")


@click.command()
@click.argument('backup')
@click.option('--write-to-disk', type=click.File('wb'),
              help='writes sqlite3 db to a file for debugging')
@click.option('--password', type=str,
              help='password if the android database is encrypted')
@click.option('--dump-all', is_flag=True, default=False,
              help='dump devices without ip addresses')
@click.option('--dump-raw', is_flag=True, help='dumps raw rows')
def main(backup, write_to_disk, password, dump_all, dump_raw):
    """Reads device information out from an sqlite3 DB.
     If the given file is an Android backup (.ab), the database
     will be extracted automatically.
     If the given file is an iOS backup, the tokens will be
     extracted (and decrypted if needed) automatically.
    """

    reader = BackupDatabaseReader(dump_raw)
    if backup.endswith(".ab"):
        DBFILE = "apps/com.xiaomi.smarthome/db/miio2.db"
        with AndroidBackup(backup) as f:
            tar = f.read_data(password)
            try:
                db = tar.extractfile(DBFILE)
            except KeyError as ex:
                click.echo("Unable to extract the database file %s: %s" % (DBFILE, ex))
                return
            if write_to_disk:
                file = write_to_disk
            else:
                file = tempfile.NamedTemporaryFile()
            with file as fp:
                click.echo("Saving database to %s" % fp.name)
                fp.write(db.read())

                devices = list(reader.read_tokens(fp.name))
    else:
        devices = list(reader.read_tokens(backup))

    for dev in devices:
        if dev.ip or dump_all:
            click.echo("%s\n"
                       "\tModel: %s\n"
                       "\tIP address: %s\n"
                       "\tToken: %s\n"
                       "\tMAC: %s" % (dev.name, dev.model,
                                      dev.ip, dev.token, dev.mac))


if __name__ == "__main__":
    main()
