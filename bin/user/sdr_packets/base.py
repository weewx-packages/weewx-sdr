# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.
"""Base class and helpers shared by the packet parsers and the driver."""

import logging
import re
import time
from calendar import timegm

# The parsers lived in user.sdr before they moved into this package. Logging
# under that name keeps the log lines unchanged, and keeps a level set for the
# logger user.sdr in the [Logging] section of weewx.conf applying to them.
log = logging.getLogger('user.sdr')


def logdbg(msg):
    log.debug(msg)


def loginf(msg):
    log.info(msg)


def logerr(msg):
    log.error(msg)


# utilities for inline unit conversions.  respect the None!
def to_F(v):
    if v is not None:
        v  = v * 1.8 + 32
    return v

def to_C(v):
    if v is not None:
        v  = 5 / 9 * (v - 32)
    return v

def to_mph(v):
    if v is not None:
        v *= 0.621371
    return v

def to_in(v):
    if v is not None:
        v /= 25.4
    return v

def to_v(v):
    if v is not None:
        v /= 1000
    return v

def kmh_to_mps(v):
    if v is not None:
        v /= 3.6
    return v


class Packet:

    def __init__(self):
        pass

    @staticmethod
    def parse_text(ts, payload, lines):
        return None

    @staticmethod
    def parse_json(obj):
        return None

    TS_PATTERN = re.compile(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)')

    @staticmethod
    def parse_time(line):
        ts = None
        try:
            m = Packet.TS_PATTERN.search(line)
            if m:
                utc = time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                ts = timegm(utc)
        except Exception as e:
            logerr("parse timestamp failed for '%s': %s" % (line, e))
        return ts

    @staticmethod
    def get_float(obj, key_):
        if key_ in obj:
            try:
                return float(obj[key_])
            except ValueError:
                pass
        return None

    @staticmethod
    def get_int(obj, key_):
        if key_ in obj:
            try:
                return int(obj[key_])
            except ValueError:
                pass
        return None

    @staticmethod
    def get_battery(obj):
        # deal with boolean battery status indicators.  older rtl_433 used a
        # field called 'battery' with string 'OK'.  later rtl_433 uses a field
        # called 'battery_ok' with value 1 to indicate battery is ok and 0 to
        # indicate battery is not ok.  at one point rtl_433 was emitting a
        # field called 'battery_low', so check for that too.
        #
        # for some sensors we see 'battery_ok' with a floating value.  not sure
        # what this means.
        #
        # map these to the WeeWX convention of boolean battery indicators of
        # 0=OK 1=notOK
        bs = None
        if 'battery_ok' in obj:
            level = Packet.get_float(obj, 'battery_ok')
            if level is not None:
                bs = 0 if level >= 1.0 else 1
        elif 'battery' in obj:
            bs = 0 if obj.get('battery') == 'OK' else 1
        elif 'battery_low' in obj:
            bs = Packet.get_int(obj, 'battery_low')
        return bs

    @staticmethod
    def parse_lines(lines, parseinfo=None):
        # parse each line, splitting on colon for name:value
        # tuple in parseinfo is label, pattern, lambda
        # if there is a label, use it to transform the name
        # if there is a pattern, use it to match the value
        # if there is a lamba, use it to convert the value
        if parseinfo is None:
            parseinfo = dict()
        packet = dict()
        for line in lines[1:]:
            if line.count(':') == 1:
                try:
                    (name, value) = [x.strip() for x in line.split(':')]
                    if name in parseinfo:
                        if parseinfo[name][1]:
                            m = parseinfo[name][1].search(value)
                            if m:
                                value = m.group(1)
                            else:
                                logdbg("regex failed for %s:'%s'" %
                                       (name, value))
                        if parseinfo[name][2]:
                            value = parseinfo[name][2](value)
                        if parseinfo[name][0]:
                            name = parseinfo[name][0]
                        packet[name] = value
                    else:
                        logdbg("ignoring %s:%s" % (name, value))
                except Exception as e:
                    logerr("parse failed for line '%s': %s" % (line, e))
            else:
                logdbg("skip line '%s'" % line)
        while lines:
            lines.pop(0)
        return packet

    @staticmethod
    def add_identifiers(pkt, sensor_id='', packet_type=''):
        # qualify each field name with details about the sensor.  not every
        # sensor has all three fields.
        # observation.<sensor_id>.<packet_type>
        packet = dict()
        if 'dateTime' in pkt:
            packet['dateTime'] = pkt.pop('dateTime', 0)
        if 'usUnits' in pkt:
            packet['usUnits'] = pkt.pop('usUnits', 0)
        for n in pkt:
            packet["%s.%s.%s" % (n, sensor_id, packet_type)] = pkt[n]
        return packet
