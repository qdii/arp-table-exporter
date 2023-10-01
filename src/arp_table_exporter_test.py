#!/usr/bin/python3
"""Tests the arp_table_exporter module."""

import datetime
import unittest
import python_arptable

from absl.testing import absltest
from freezegun import freeze_time
from unittest.mock import patch
import src.arp_table_exporter as exporter


FAKE_MAC_ADDR_1 = '00:12:79:d2:b9:67'
FAKE_NEIGHBOR_1 = exporter.Neighbor(
        device='eth0',
        flags='0x2',
        mac_addr='00:12:79:d2:b9:67',
        hw_type='0x1',
        ip_addr='10.3.0.1',
        mask='*')


class TestARPTableExporter(unittest.TestCase):
    """Tests the arp_table_exporter module."""

    def setUp(self):
        exporter.LAST_SEEN_TABLE = {}

    def testUpdate_UpdatesLastSeenTimeTableCorrectly(self):
        """Checks that update() changes the time of newly seen neighbors."""
        self.assertDictEqual(exporter.LAST_SEEN_TABLE, {})
        with freeze_time('2023-10-01'):
            exporter.update({FAKE_MAC_ADDR_1: FAKE_NEIGHBOR_1})
        self.assertDictEqual(exporter.LAST_SEEN_TABLE, {
            FAKE_MAC_ADDR_1: datetime.datetime(2023, 10, 1)})
        with freeze_time('2023-10-02'):
            exporter.update({FAKE_MAC_ADDR_1: FAKE_NEIGHBOR_1})
        self.assertDictEqual(exporter.LAST_SEEN_TABLE, {
            FAKE_MAC_ADDR_1: datetime.datetime(2023, 10, 2)})

    @freeze_time('2023-10-02')
    def testExport_UpdatesMetric(self):
        """Checks that export() update the metrics."""
        with patch.object(exporter, 'LAST_SEEN_METRIC') as mock_metric:
            exporter.update({FAKE_MAC_ADDR_1: FAKE_NEIGHBOR_1})
            exporter.export()
            mock_metric.labels.assert_called_once_with(
                    mac_address=FAKE_MAC_ADDR_1)

    @patch.object(python_arptable, 'get_arp_table')
    def testArpTable_DictIsKeyedByMacAddress(self, mock_get_arp_table):
        """Checks that arp_table() returns a correct dictionary."""
        mock_get_arp_table.return_value = [
                {'Device': 'eth0',
                 'Flags': '0x2',
                 'HW address': FAKE_MAC_ADDR_1,
                 'HW type': '0x1',
                 'IP address': '10.3.0.1',
                 'Mask': '*'}]
        self.assertDictEqual(
                exporter.arp_table(), {FAKE_MAC_ADDR_1: FAKE_NEIGHBOR_1})


if __name__ == '__main__':
    absltest.main()
