# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2026-10-29 by weewx-packages: moved from sdr.py. Earlier
# modifications are recorded in the header of sdr.py.
# Modified 2026-10-29 by weewx-packages: stop parse_text from looping on a
# model whose parser has no text format.
"""Parsers for the packets that rtl_433 emits, one module per manufacturer.

PacketFactory turns rtl_433 output into packets. Each parser is a subclass of
user.sdr_packets.base.Packet with an IDENTIFIER that names the rtl_433 model.
"""

import importlib
import inspect
import re
import time
from calendar import timegm

try:
    import cjson as json
    setattr(json, 'dumps', json.encode)
    setattr(json, 'loads', json.decode)
except (ImportError, AttributeError):
    try:
        import simplejson as json
    except ImportError:
        import json

from user.sdr_packets.base import logdbg, logerr
from user.sdr_packets.fineoffset import FOWH65BAltPacket
from user.sdr_packets.lacrosse import LaCrosseTXPacket

# The modules that hold the parsers. PacketFactory searches only these, so a
# new module has to be listed here and in the file list of install.py. A module
# left on disk by an older version of the driver is not listed, and is never
# loaded.
PARSER_MODULES = (
    'acurite', 'alecto', 'ambient', 'auriol', 'bresser', 'calibeur', 'cotech',
    'ecowitt', 'emax', 'esperanza', 'fineoffset', 'hideki', 'holman',
    'infactory', 'kedsum', 'lacrosse', 'nexus', 'oregon', 'prologue',
    'rubicson', 'springfield', 'tfa', 'tsft002', 'vevor', 'ws2032', 'wt0124',
)


class PacketFactory(object):

    # known packets will be lazy-loaded by introspecting at first request
    KNOWN_PACKETS = []

    @staticmethod
    def known_packets():
        if not PacketFactory.KNOWN_PACKETS:
            parsers = []
            for module_name in PARSER_MODULES:
                module = importlib.import_module('%s.%s' % (__name__, module_name))
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip classes a module imports from another one, such
                    # as Packet, so that every parser is listed once.
                    if obj.__module__ == module.__name__ and hasattr(obj, 'IDENTIFIER'):
                        parsers.append(obj)
            # The first parser whose IDENTIFIER occurs in the model name wins,
            # and some identifiers contain others: 'Fineoffset-WH32' is part of
            # 'Fineoffset-WH32B'. Sorting by class name keeps the order of the
            # single-module driver, which listed its classes alphabetically.
            parsers.sort(key=lambda parser: parser.__name__)
            PacketFactory.KNOWN_PACKETS.extend(parsers)
        return PacketFactory.KNOWN_PACKETS

    @staticmethod
    def create(lines):
        # return a list of packets from the specified lines
        while lines:
            pkt = None
            if lines[0].startswith('{'):
                pkt = PacketFactory.parse_json(lines)
                if pkt is None:
                    logdbg("punt unrecognized line '%s'" % lines[0])
                lines.pop(0)
            else:
                pkt = PacketFactory.parse_text(lines)
            if pkt is not None:
                yield pkt

    @staticmethod
    def parse_json(lines):
        try:
            obj = json.loads(lines[0])
            if obj.get('model') == 'LaCrosse TX Sensor':
                return LaCrosseTXPacket.parse_json(obj)
            if obj.get('model') == 'Fineoffset-WS69':
                return FOWH65BAltPacket.parse_json(obj)
            if 'model' in obj:
                for parser in PacketFactory.known_packets():
                    if obj['model'].find(parser.IDENTIFIER) >= 0:
                        return parser.parse_json(obj)
                logdbg("parse_json: unknown model %s" % obj['model'])
        except ValueError as e:
            logdbg("parse_json failed: %s" % e)
        return None

    @staticmethod
    def parse_text(lines):
        ts, payload = PacketFactory.parse_firstline(lines[0])
        if ts and payload:
            logdbg("parse_text: ts=%s payload=%s" % (ts, payload))
            for parser in PacketFactory.known_packets():
                if payload.find(parser.IDENTIFIER) >= 0:
                    count = len(lines)
                    pkt = parser.parse_text(ts, payload, lines)
                    logdbg("pkt=%s" % pkt)
                    # A parser without a text format inherits
                    # Packet.parse_text, which leaves the lines alone. Drop
                    # the first line, as for an unknown model below, otherwise
                    # create() hands the same lines to the same parser forever.
                    if len(lines) == count:
                        lines.pop(0)
                    return pkt
            logdbg("parse_text: unknown format: ts=%s payload=%s" %
                   (ts, payload))
        logdbg("parse_text failed: ts=%s payload=%s line=%s" %
               (ts, payload, lines[0]))
        lines.pop(0)
        return None

    TS_PATTERN = re.compile(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)[\s]+:*(.*)')

    @staticmethod
    def parse_firstline(line):
        ts = payload = None
        try:
            m = PacketFactory.TS_PATTERN.search(line)
            if m:
                utc = time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                ts = timegm(utc)
                payload = m.group(2).strip()
        except Exception as e:
            logerr("parse timestamp failed for '%s': %s" % (line, e))
        return ts, payload
