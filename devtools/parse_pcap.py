"""Parse PCAP files for miio traffic."""
from collections import Counter, defaultdict
from ipaddress import ip_address

import dpkt
import typer
from dpkt.ethernet import ETH_TYPE_IP, Ethernet
from rich import print

from miio import Message

app = typer.Typer()


def read_payloads_from_file(file, tokens: list[str]):
    """Read the given pcap file and yield src, dst, and result."""
    pcap = dpkt.pcap.Reader(file)

    stats: defaultdict[str, Counter] = defaultdict(Counter)
    for _ts, pkt in pcap:
        eth = Ethernet(pkt)
        if eth.type != ETH_TYPE_IP:
            continue

        ip = eth.ip

        if ip.p != 17:
            continue

        transport = ip.udp

        if transport.dport != 54321 and transport.sport != 54321:
            continue

        data = transport.data

        src_addr = str(ip_address(ip.src))
        dst_addr = str(ip_address(ip.dst))

        decrypted = None
        for token in tokens:
            try:
                decrypted = Message.parse(data, token=bytes.fromhex(token))

                break
            except BaseException:
                continue

        if decrypted is None:
            continue

        stats["stats"]["miio_packets"] += 1

        if decrypted.data.length == 0:
            stats["stats"]["empty_packets"] += 1
            continue

        stats["dst_addr"][dst_addr] += 1
        stats["src_addr"][src_addr] += 1

        payload = decrypted.data.value

        if "result" in payload:
            stats["stats"]["results"] += 1
        if "method" in payload:
            method = payload["method"]
            stats["commands"][method] += 1

        yield src_addr, dst_addr, payload

    print(stats)  # noqa: T201


@app.command()
def read_file(
    file: typer.FileBinaryRead, token: list[str] = typer.Option(...)  # noqa: B008
):
    """Read PCAP file and output decrypted miio communication."""
    for src_addr, dst_addr, payload in read_payloads_from_file(file, token):
        print(f"{src_addr:<15} -> {dst_addr:<15} {payload}")  # noqa: T201


if __name__ == "__main__":
    app()
