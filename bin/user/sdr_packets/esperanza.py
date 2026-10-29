# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.

import weewx

from user.sdr_packets.base import Packet


class EsperanzaEWSPacket(Packet):
    # This is for a Esperanza-EWS temperature humidity sensor

    # {"time" : "2022-06-30 08:29:25", "model" : "Esperanza-EWS", "id" : 198, "channel" : 2, "temperature_F" : 69.200, "humidity" : 0, "mic" : "CRC"}

    IDENTIFIER = "Esperanza-EWS"

    @staticmethod
    def parse_json(obj):
        sensor_id = obj.get('id')
        pkt = dict()
        pkt['dateTime'] = Packet.parse_time(obj.get('time'))
        pkt['usUnits'] = weewx.US
        pkt['temperature'] = Packet.get_float(obj, 'temperature_F')
        pkt['humidity'] = Packet.get_float(obj, 'humidity')
        pkt['channel'] = obj.get('channel')
        pkt = Packet.add_identifiers(pkt, sensor_id, EsperanzaEWSPacket.__name__)
        return pkt
