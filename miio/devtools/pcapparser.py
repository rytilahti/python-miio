"""Parse PCAP files for miio traffic."""
from collections import Counter, defaultdict
from ipaddress import ip_address
from pprint import pformat as pf
from typing import List

import click

try:
    from rich import print as echo
except ImportError:
    echo = click.echo


from miio import Message


def read_payloads_from_file(file, tokens: List[str]):
    """Read the given pcap file and yield src, dst, and result."""
    try:
        import dpkt
        from dpkt.ethernet import ETH_TYPE_IP, Ethernet
    except ImportError:
        echo("You need to install dpkt to use this tool")
        return

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

    for cat in stats:
        echo(f"\n== {cat} ==")
        for stat, value in stats[cat].items():
            echo(f"\t{stat}: {value}")


@click.command()
@click.argument("file", type=click.File("rb"))
@click.argument("token", nargs=-1)
def parse_pcap(file, token: List[str]):
    """Read PCAP file and output decrypted miio communication."""
    for src_addr, dst_addr, payload in read_payloads_from_file(file, token):
        echo(f"{src_addr:<15} -> {dst_addr:<15} {pf(payload)}")
