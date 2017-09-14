import click
import tarfile
import tempfile
import sqlite3
from Crypto.Cipher import AES
from pprint import pformat as pf


class BackupDatabaseReader:
    def __init__(self, dump_all=False, dump_raw=False):
        self.dump_all = dump_all
        self.dump_raw = dump_raw

    @staticmethod
    def dump_raw(dev):
        raw = {k: dev[k] for k in dev.keys()}
        click.echo(pf(raw))

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
        click.echo("Reading tokens from Apple DB")
        c = self.conn.execute("SELECT * FROM ZDEVICE WHERE ZTOKEN IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev['ZLOCALIP']
            mac = dev['ZMAC']
            model = dev['ZMODEL']
            name = dev['ZNAME']
            token = BackupDatabaseReader.decrypt_ztoken(dev['ZTOKEN'])
            if ip or self.dump_all:
                click.echo("%s\n\tModel: %s\n\tIP address: %s\n\tToken: %s\n\tMAC: %s" % (name, model, ip, token, mac))

    def read_android(self):
        click.echo("Reading tokens from Android DB")
        c = self.conn.execute("SELECT * FROM devicerecord WHERE token IS NOT '';")
        for dev in c.fetchall():
            if self.dump_raw:
                BackupDatabaseReader.dump_raw(dev)
            ip = dev['localIP']
            mac = dev['mac']
            model = dev['model']
            name = dev['name']
            token = dev['token']
            if ip or self.dump_all:
                click.echo("%s\n\tModel: %s\n\tIP address: %s\n\tToken: %s\n\tMAC: %s" % (name, model, ip, token, mac))

    def dump_to_file(self, fp):
        fp.open()
        self.db.seek(0)  # go to the beginning
        click.echo("Saving db to %s" % fp)
        fp.write(self.db.read())

    def read_tokens(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            is_android = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='devicerecord';").fetchone() is not None
            is_apple = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ZDEVICE'").fetchone() is not None
            if is_android:
                self.read_android()
            elif is_apple:
                self.read_apple()
            else:
                click.echo("Error, unknown database type!")


@click.command()
@click.argument('backup')
@click.option('--write-to-disk', type=click.File('wb'), help='writes sqlite3 db to a file for debugging')
@click.option('--dump-all', is_flag=True, default=False, help='dump devices without ip addresses')
@click.option('--dump-raw', is_flag=True, help='dumps raw rows')
def main(backup, write_to_disk, dump_all, dump_raw):
    """Reads device information out from an sqlite3 DB.
     If the given file is a .tar file, the file will be extracted
     and the database automatically located (out of Android backups).
    """
    reader = BackupDatabaseReader(dump_all, dump_raw)
    if backup.endswith(".tar"):
        DBFILE = "apps/com.xiaomi.smarthome/db/miio2.db"
        with tarfile.open(backup) as f:
            click.echo("Opened %s" % backup)
            db = f.extractfile(DBFILE)
            with tempfile.NamedTemporaryFile() as fp:
                click.echo("Extracting to %s" % fp.name)
                fp.write(db.read())
                if write_to_disk:
                    reader.dump_to_file(write_to_disk)

                reader.read_tokens(fp.name)
    else:
        reader.read_tokens(backup)


if __name__ == "__main__":
    main()
