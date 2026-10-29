# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.

import weewx

from user.sdr_packets.base import Packet


class InFactoryTHPacket(Packet):
    # {"time" : "2021-03-03 10:19:53", "model" : "inFactory-TH", "id" : 195, "channel" : 1, "battery_ok" : 1, "temperature_F" : 73.200, "humidity" : 55, "mic" : "CRC"}

    IDENTIFIER = "nFactory-TH"

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
        pkt = Packet.add_identifiers(pkt, sensor_id, InFactoryTHPacket.__name__)
        return pkt
