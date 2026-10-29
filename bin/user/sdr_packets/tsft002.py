# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.

import weewx

from user.sdr_packets.base import Packet


class TSFT002Packet(Packet):
    # time : 2019-12-22 16:57:58
    # model : TS-FT002 Id : 127
    # Depth : 186 Temperature: 20.9 C Transmit Interval: 180 Battery Flag?: 8 MIC : CHECKSUM

    # {"time" : "2019-12-22 22:54:58", "model" : "TS-FT002", "id" : 127, "depth_cm" : 186, "temperature_C" : 20.700, "transmit_s" : 180, "flags" : 8, "mic" : "CHECKSUM"}

    IDENTIFIER = "TS-FT002"

    @staticmethod
    def parse_json(obj):
        sensor_id = obj.get('id', '0000')
        pkt = dict()
        pkt['dateTime'] = Packet.parse_time(obj.get('time'))
        pkt['usUnits'] = weewx.METRIC
        pkt['temperature'] = Packet.get_float(obj, 'temperature_C')
        pkt['depth'] = Packet.get_float(obj, 'depth_cm')
        pkt['transmit'] = Packet.get_float(obj, 'transmit_s')
        pkt['flags'] = Packet.get_int(obj, 'flags')
        pkt = Packet.add_identifiers(pkt, sensor_id, TSFT002Packet.__name__)
        return pkt
