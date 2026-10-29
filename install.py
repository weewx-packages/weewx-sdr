# installer for the weewx-sdr driver
# Modified 2026-10-22 by weewx-packages.
# Modified 2026-10-29 by weewx-packages: install the package user.sdr_packets.
# Copyright 2016-2024 Matthew Wall
# Copyright (c) 2026 Manuel Hilgert <hilman2@gmail.com>
# Distributed under the terms of the GNU Public License (GPLv3)

from weecfg.extension import ExtensionInstaller

# WeeWX removes exactly these files when the extension is uninstalled, using
# the copy of this file it saved at installation. The list therefore has to be
# written out, not collected from the directory.
FILES = [
    'bin/user/sdr.py',
    'bin/user/sdr_packets/__init__.py',
    'bin/user/sdr_packets/acurite.py',
    'bin/user/sdr_packets/alecto.py',
    'bin/user/sdr_packets/ambient.py',
    'bin/user/sdr_packets/auriol.py',
    'bin/user/sdr_packets/base.py',
    'bin/user/sdr_packets/bresser.py',
    'bin/user/sdr_packets/calibeur.py',
    'bin/user/sdr_packets/cotech.py',
    'bin/user/sdr_packets/ecowitt.py',
    'bin/user/sdr_packets/emax.py',
    'bin/user/sdr_packets/esperanza.py',
    'bin/user/sdr_packets/fineoffset.py',
    'bin/user/sdr_packets/hideki.py',
    'bin/user/sdr_packets/holman.py',
    'bin/user/sdr_packets/infactory.py',
    'bin/user/sdr_packets/kedsum.py',
    'bin/user/sdr_packets/lacrosse.py',
    'bin/user/sdr_packets/nexus.py',
    'bin/user/sdr_packets/oregon.py',
    'bin/user/sdr_packets/prologue.py',
    'bin/user/sdr_packets/rubicson.py',
    'bin/user/sdr_packets/springfield.py',
    'bin/user/sdr_packets/tfa.py',
    'bin/user/sdr_packets/tsft002.py',
    'bin/user/sdr_packets/vevor.py',
    'bin/user/sdr_packets/ws2032.py',
    'bin/user/sdr_packets/wt0124.py',
]

def loader():
    return SDRInstaller()

class SDRInstaller(ExtensionInstaller):
    def __init__(self):
        super(SDRInstaller, self).__init__(
            version="0.99.2",
            name='sdr',
            description='Capture data from rtl_433',
            author="Matthew Wall",
            author_email="mwall@users.sourceforge.net",
            files=[('bin/user', FILES)]
            )
