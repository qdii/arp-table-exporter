# arp-table-exporter
A daemon which continuously exports information the ARP table for consumption by prometheus.

In practice, every minute the daemon scrapes the /proc/net/arp table, and continuously
exports the timestamps at which each of the neighbors were last seen.
