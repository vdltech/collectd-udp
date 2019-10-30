#!/usr/bin/env python

import subprocess
import collectd
import signal
from pprint import pprint


def get_udp_stats():
    result = {}

    for filename in ['/proc/net/udp', '/proc/net/udp6']:
        with open(filename) as file:
            for line in file:
                parts = line.split()

                # Skip Header
                if parts[0] == 'sl':
                    continue

                # Get hex port number and convert to decimal
                port_hex = parts[1].split(':')[1]
                port = int(port_hex, 16)

                # Metrics
                tx_queue, rx_queue = parts[4].split(':')
                drops = parts[12]

                if port not in result:
                    result[port] = {
                        'tx_queue': 0,
                        'rx_queue': 0,
                        'drops': 0,
                    }

                result[port]['tx_queue'] += int(tx_queue)
                result[port]['rx_queue'] += int(rx_queue)
                result[port]['drops'] += int(drops)

    return result


def configure_callback(config):
    collectd.info('Imported udpstats module')


def read_callback(data=None):
    udpstats = get_udp_stats()

    for port, data in udpstats.items():
        for metricname, value in data.items():
            metric = collectd.Values()
            metric.plugin = 'udp_stats'
            metric.plugin_instance = str(port)
            metric.type = 'counter'
            metric.type_instance = metricname
            metric.dispatch(values=[value])


collectd.register_read(read_callback)
collectd.register_config(configure_callback)
