#!/usr/bin/python3
"""Monitors neighbors and report them on /metrics."""

from collections import namedtuple
import datetime
import time
from typing import Dict

from absl import app
from absl import flags
from absl import logging
import python_arptable
from prometheus_client import start_http_server, Gauge


_PORT = flags.DEFINE_integer(
    'port', 8000, 'The port on which /metrics is served.')
_FREQ = flags.DEFINE_integer(
    'frequency', 30, 'How often neighbor discovery is perfomed, in seconds.')


Neighbor = namedtuple(
    'Neighbor', ['device', 'flags', 'mac_addr', 'hw_type', 'ip_addr', 'mask'])

# Maps MAC address to the date when the neighbor was last seen.
LAST_SEEN_TABLE: Dict[str, datetime.datetime] = {}

LAST_SEEN_METRIC = Gauge(
    'neighbor_last_seen_time',
    'The time in seconds since epoch when a certain neighbor was last seen '
    'in the ARP table of the machine this script is running on. ',
    ['mac_address'])


def arp_table() -> Dict[str, Neighbor]:
    """Maps a mac address to its associated neighbor."""
    res = {}
    for entry in python_arptable.get_arp_table():
        logging.debug(f"Seen neighbor: {entry['HW address']}")
        res[entry['HW address']] = Neighbor(
                device=entry['Device'],
                flags=entry['Flags'],
                mac_addr=entry['HW address'],
                hw_type=entry['HW type'],
                ip_addr=entry['IP address'],
                mask=entry['Mask'])
    return res


def update(new_arp_table: Dict[str, Neighbor]) -> None:
    """Updates the LAST_SEEN_TABLE from fresh data."""
    for mac_address, _ in new_arp_table.items():
        LAST_SEEN_TABLE[mac_address] = datetime.datetime.now()


def export() -> None:
    """Updates the prometheus metrics."""
    for mac_address, last_seen_time in LAST_SEEN_TABLE.items():
        time_since_epoch = int(last_seen_time.timestamp())
        LAST_SEEN_METRIC.labels(mac_address=mac_address).set(time_since_epoch)


def main(argv):
    """Start the HTTP server and regularly updates the metrics."""
    del argv  # unused
    logging.info(f'Exporting /metrics on port {_PORT.value}')
    start_http_server(_PORT.value)
    # Parse ARP table and export metrics.
    while True:
        update(arp_table())
        export()
        time.sleep(_FREQ.value)


if __name__ == '__main__':
    app.run(main)
