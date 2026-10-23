# SDR weather sensors for WeeWX

Run `rtl_433` and map its decoded radio observations into WeeWX LOOP packets.
This driver requires a separately installed `rtl_433` executable, its radio
backend and a compatible SDR receiver. A sensor needs both an `rtl_433` decoder
and a matching parser here; support in `rtl_433` alone is insufficient.

Release 0.99.1 independently continues
[matthewwall/weewx-sdr](https://github.com/matthewwall/weewx-sdr). It retains the
single-module driver and incorporates parser and subprocess repairs. See
[NOTICE](NOTICE) for contributions by andylittle, zagamuffin, ChrisM510,
WhatTheBelle and TheButterZone and proposals from PRs #203, #204, #206 and #209.

## Install

An existing WeeWX station is required. Replace `/path/to/weewx.conf`
with its configuration file before running the commands.

The catalog release requires Python >=3.10 and WeeWX >=5.2,<6.

Install [rtl_433](https://github.com/merbanan/rtl_433) and the appropriate
[RTL-SDR backend](https://osmocom.org/projects/rtl-sdr/wiki) for your receiver.
The extension installs only `bin/user/sdr.py`; it does not install radio tools,
USB rules or native libraries. No extra Python dependency is needed beyond WeeWX.

Use the `weectl` from your WeeWX Python environment:

```sh
weectl extension install https://github.com/weewx-packages/weewx-sdr/releases/download/v0.99.1/weewx-sdr-0.99.1.zip --config=/path/to/weewx.conf
weectl station reconfigure --driver=user.sdr --config=/path/to/weewx.conf
```

Stock WeeWX 5 accepts this fixed URL or a downloaded copy of the same archive.
No catalog integration is required. Restart WeeWX yourself after configuration
changes.

## Identify and map sensors

Stop WeeWX before opening its dongle in a standalone process. Use the WeeWX
Python environment and replace the station path:

```sh
PYTHONPATH=/path/to/station/bin python -m user.sdr --action=list-supported
PYTHONPATH=/path/to/station/bin python -m user.sdr --cmd='rtl_433 -M utc -F json'
```

The first command lists implemented parsers without opening a receiver. The
second displays received packets until interrupted. Copy the decoded identifiers
into `weewx.conf`. For a Fine Offset sensor decoded as `FOWH24BPacket` with ID 65:

```ini
[Station]
    station_type = SDR
[SDR]
    driver = user.sdr
    cmd = rtl_433 -M utc -F json
    [[sensor_map]]
        outTemp = temperature.65.FOWH24BPacket
        outHumidity = humidity.65.FOWH24BPacket
        windSpeed = wind_speed.65.FOWH24BPacket
        windDir = wind_dir.65.FOWH24BPacket
        rain_total = rain_total.65.FOWH24BPacket
```

Use your actual packet type, fields and ID. An empty map produces no weather
observations. The default `[[deltas]]` turns `rain_total` into `rain` and
`strikes_total` into `lightning_strike_count`. Restart WeeWX after configuration.
The service user needs USB access, the receiver executable on `PATH`, and its
shared libraries. An absolute executable path in `cmd` avoids PATH differences.

## Parser changes and limits

Model aliases preserve existing FOWH65BAltPacket mappings for Fineoffset-WS69.
Bresser-3CH uses BresserTH, channel-prefixed IDs, and converts Fahrenheit to
Celsius when needed. The Bresser-6in1 moisture field maps to soil_moisture_raw;
Bresser-7in1 and WH46 provide pm2_5_atm and pm10_0_atm. WH46 also provides
pm1_0_atm, pm4_0_atm and co2_atm. Use mapped names, not rtl_433 input keys.
For example, outTemp = temperature.65.FOWH24BPacket and
windSpeed = wind_speed.65.FOWH24BPacket.

The path option is a search directory, for example /usr/bin. An absolute
executable path in cmd also works. Quoted command arguments work without a shell.
For a pipeline, set use_shell = true. Shutdown terminates the process group,
waits for it, and joins the pipe readers before closing their file descriptors.

Delta state lives in the driver's in-memory _counter_values dictionary. On a
counter decrement, that interval is None and the new total becomes the baseline.
The next increase produces a delta. Restarting the driver clears the baseline.
To use StdWXCalculate instead, supply a dummy entry in [[deltas]], e.g.
`dummy = dummy_total`, then configure the equivalent StdWXCalculate delta.

A service's Unix identity, USB device permissions and rtl_433 configuration files
can differ from an interactive shell. Reproduce the command as the configured
service user and compare the actual config path and sensor_map. Changing global
USB memory settings is not established as a fix for missing data in the tracker.


Hardware/RF behavior, USB loss and model-specific output require a device capture
and service logs. Offline fixtures do not establish reception. Only JSON output
is maintained; older text parsers remain for historical formats. The experimental
multi-module refactor in bjmc/weewx-sdr PR #211 is separate from this release.

See the [configuration and diagnostic reference](docs/reference.md) for more
sensor maps, logging, environment settings and adding a parser. Copyright
2016-2024 Matthew Wall. Distributed under [GPLv3](license).

<!-- Documentation updated 2026-10-23 by weewx-packages. -->
