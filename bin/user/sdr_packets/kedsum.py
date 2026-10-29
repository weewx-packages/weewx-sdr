# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.

import weewx

from user.sdr_packets.base import Packet


class KedsumTHPacket(Packet):
    # {"time" : "2022-06-17 00:23:59", "model" : "Kedsum-TH", "id" : 235, "channel" : 1, "battery_ok" : 0, "flags" : 8, "temperature_F" : 59.000, "humidity" : 74, "mic" : "CRC"}

    IDENTIFIER = "Kedsum-TH"

    @staticmethod
    def parse_json(obj):
        sensor_id = obj.get('id')
        pkt = dict()
        pkt['dateTime'] = Packet.parse_time(obj.get('time'))
        pkt['usUnits'] = weewx.US
        pkt['temperature'] = Packet.get_float(obj, 'temperature_F')
        pkt['humidity'] = Packet.get_float(obj, 'humidity')
        pkt['battery'] = Packet.get_battery(obj)
        pkt['channel'] = obj.get('channel')
        pkt['flags'] = obj.get('flags')
        pkt = Packet.add_identifiers(pkt, sensor_id, KedsumTHPacket.__name__)
        return pkt
