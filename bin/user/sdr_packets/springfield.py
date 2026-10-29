# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.

import weewx

from user.sdr_packets.base import Packet


class SpringfieldTMPacket(Packet):
    # {"time" : "2019-01-20 11:14:00", "model" : "Springfield Temperature & Moisture", "sid" : 224, "channel" : 3, "battery" : "OK", "transmit" : "MANUAL", "temperature_C" : -204.800, "moisture" : 0, "mic" : "CHECKSUM"}

    IDENTIFIER = "Springfield Temperature & Moisture"

    @staticmethod
    def parse_json(obj):
        pkt = dict()
        pkt['dateTime'] = Packet.parse_time(obj.get('time'))
        pkt['usUnits'] = weewx.METRIC
        sensor_id = obj.get('sid')
        pkt['temperature'] = Packet.get_float(obj, 'temperature_C')
        pkt['moisture'] = Packet.get_float(obj, 'moisture')
        pkt['battery'] = Packet.get_battery(obj)
        pkt['channel'] = obj.get('channel')
        pkt['transmit'] = obj.get('transmit')
        pkt = Packet.add_identifiers(pkt, sensor_id, SpringfieldTMPacket.__name__)
        return pkt
