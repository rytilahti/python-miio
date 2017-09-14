import click
import tarfile
import tempfile
import sqlite3
from Crypto.Cipher import AES
from pprint import pformat as pf


def dump_raw(dev):
    raw = {k: dev[k] for k in dev.keys()}
    click.echo(pf(raw))


def decrypt_ztoken(ztoken):
    if len(ztoken) <= 32:
        return ztoken

    keystring = '00000000000000000000000000000000'
    key = bytes.fromhex(keystring)
    cipher = AES.new(key, AES.MODE_ECB)
    token = cipher.decrypt(bytes.fromhex(ztoken[:64]))

    return token


def read_apple(conn):
    click.echo("Reading tokens from Apple DB")
    c = conn.execute("SELECT * FROM ZDEVICE WHERE ZTOKEN IS NOT '';")
    for dev in c.fetchall():
        token = decrypt_ztoken(dev['ZTOKEN'])
        ip = dev['ZLOCALIP']
        click.echo("device at %s. token: %s" % (ip, token))
        dump_raw(dev)
    raise NotImplementedError("Please report the previous output to developers")


def read_android(conn):
    click.echo("Reading tokens from Android DB")
    c = conn.execute("SELECT * FROM devicerecord WHERE token IS NOT '';")
    for dev in c.fetchall():
        # dump_raw(dev)
        ip = dev['localIP']
        mac = dev['mac']
        model = dev['model']
        name = dev['name']
        ssid = dev['ssid']
        token = dev['token']
        click.echo("%s (%s) at %s. token: %s (mac: %s, ssid: %s)" % (name, model, ip, token, mac, ssid))


def write(db, fp):
    fp.open()
    db.seek(0)  # go to the beginning
    click.echo("Saving db to %s" % fp)
    fp.write(db.read())


def read_tokens(db):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    with conn:
        is_android = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='devicerecord';").fetchone() is not None
        is_apple = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ZDEVICE'").fetchone() is not None
        if is_android:
            read_android(conn)
        elif is_apple:
            read_apple(conn)
        else:
            click.echo("Error, unknown database type!")


@click.command()
@click.argument('backup')
@click.option('--write-to-disk', type=click.File('wb'), help='writes sqlite3 db to a file for debugging')
def main(backup, write_to_disk):
    """Reads device information out from an sqlite3 DB.
     If the given file is a .tar file, the file will be extracted
     and the database automatically located (out of Android backups).
    """
    if backup.endswith(".tar"):
        DBFILE = "apps/com.xiaomi.smarthome/db/miio2.db"
        with tarfile.open(backup) as f:
            click.echo("Opened %s" % backup)
            db = f.extractfile(DBFILE)
            with tempfile.NamedTemporaryFile() as fp:
                click.echo("Extracting to %s" % fp.name)
                fp.write(db.read())
                if write_to_disk:
                    write(db, write_to_disk)

                read_tokens(fp.name)
    else:
        read_tokens(backup)


if __name__ == "__main__":
    main()
