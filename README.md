# SDR

This driver runs `rtl_433` and maps its decoded radio observations into WeeWX
LOOP packets. It does not install `rtl_433`, radio libraries or USB rules. A
sensor needs both an `rtl_433` decoder and a matching parser in this driver;
support in `rtl_433` alone is not enough.

This is an independent continuation of
[matthewwall/weewx-sdr](https://github.com/matthewwall/weewx-sdr). [NOTICE](NOTICE)
lists the incorporated parser and subprocess repairs and their contributors.

## Requirements

- An SDR receiver supported by `rtl_433`.
- [rtl_433](https://github.com/merbanan/rtl_433) and the matching
  [RTL-SDR backend](https://osmocom.org/projects/rtl-sdr/wiki) for the receiver.
- The user running WeeWX needs access to the USB device, the `rtl_433`
  executable on its `PATH` and the shared libraries it links against.

No Python packages are needed beyond WeeWX.

## Installation

Install `sdr` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/sdr.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

Then select the driver. Add a sensor map, described below, before you restart
WeeWX.

```sh
weectl station reconfigure --driver=user.sdr --config=/path/to/weewx.conf
```

## Configuration

The driver collects nothing until the `[[sensor_map]]` maps at least one
sensor. A minimal configuration for a Fine Offset WH24 sensor decoded as
`FOWH24BPacket` with ID 65:

```ini
[Station]
    station_type = SDR

[SDR]
    driver = user.sdr
    [[sensor_map]]
        outTemp = temperature.65.FOWH24BPacket
        outHumidity = humidity.65.FOWH24BPacket
        windSpeed = wind_speed.65.FOWH24BPacket
        windDir = wind_dir.65.FOWH24BPacket
        rain_total = rain_total.65.FOWH24BPacket
```

Options in `[SDR]`:

| Option | Default | Meaning |
|---|---|---|
| `driver` | | Must be `user.sdr`. |
| `cmd` | `rtl_433 -M utc -F json` | Command that starts `rtl_433`. Quoted arguments work without a shell. |
| `use_shell` | `False` | Run `cmd` through a shell. Needed for a pipeline. |
| `path` | none | Directory prepended to `PATH`, for example `/opt/rtl-433/bin`. An absolute executable path in `cmd` also works. |
| `ld_library_path` | none | Value for `LD_LIBRARY_PATH` of the `rtl_433` process. |
| `model` | `SDR` | Hardware name reported to WeeWX. |
| `log_lines` | `False` | Log every line read from `rtl_433`. |
| `log_unknown_sensors` | `False` | Log lines that no parser recognizes. |
| `log_unmapped_sensors` | `False` | Log parsed packets that the sensor map does not select. |
| `log_packets` | `True` | Log each mapped packet. Only with `debug = 1`. |
| `log_duplicate_readings` | `True` | Log ignored duplicate packets. Only with `debug = 1`. |
| `timestamp_match_threshhold` | `1` | Seconds within which a mapped packet that repeats the previous one apart from its timestamp counts as a duplicate and is ignored. |

The `[[sensor_map]]` subsection maps a WeeWX field on the left to an identifier
`<observation>.<sensor_id>.<packet_type>` on the right. Each part accepts glob
patterns such as `*`. Use the mapped names the driver prints, not the
`rtl_433` JSON keys.

The `[[deltas]]` subsection turns cumulative totals into per-interval amounts.
Without it, the driver uses:

```ini
    [[deltas]]
        rain = rain_total
        lightning_strike_count = strikes_total
```

A `[[deltas]]` subsection replaces these defaults completely. The previous
total is kept in memory only. After a restart, or when a total decreases, that
interval has no value and the new total becomes the baseline. To let
StdWXCalculate compute the delta instead, put a dummy entry such as
`dummy = dummy_total` in `[[deltas]]`.

### Identify sensors

Stop WeeWX before running the driver directly, because both open the same
receiver. Use the Python environment of WeeWX and the station's `bin`
directory:

```sh
PYTHONPATH=/path/to/station/bin python -m user.sdr --action=list-supported
PYTHONPATH=/path/to/station/bin python -m user.sdr --cmd='rtl_433 -M utc -F json'
```

The first command lists the implemented parsers without opening a receiver.
The second prints received and parsed packets until interrupted. Copy the
identifiers into `[[sensor_map]]`. The
[configuration and diagnostic reference](docs/reference.md) has more sensor
maps, the `--hide` filter for new sensors and the steps for adding a parser.

### Sensor-specific notes

- Fineoffset-WS69 packets are parsed as `FOWH65BAltPacket`, so existing
  `FOWH65BAltPacket` mappings keep working.
- Bresser-3CH packets use `BresserTH` and channel-prefixed IDs such as `1:55`.
  Fahrenheit readings are converted to Celsius.
- The Bresser-6in1 moisture field maps to `soil_moisture_raw`.
- The Bresser-6in1 UV index maps to `uv_index`. `rtl_433` releases before
  25.12 name it `uv`, which maps to `uv`.
- Bresser-7in1 provides `pm2_5_atm` and `pm10_0_atm`. Fineoffset-WH46 provides
  `pm1_0_atm`, `pm2_5_atm`, `pm4_0_atm`, `pm10_0_atm` and `co2_atm`.

### Running as a service

The user, USB permissions and `rtl_433` configuration files of a service can
differ from an interactive shell. Reproduce the command as the service user and
compare the configuration path and the sensor map. On shutdown the driver stops
the whole process group, including the members of a shell pipeline.

## Limitations

- The tests use recorded packets only. Reception, USB disconnects and
  model-specific output are not covered. Diagnosing them needs a capture from
  the device and the service logs.
- Only JSON output from `rtl_433` is maintained. The plain-text parsers remain
  for historical output formats.
- Changing global USB memory settings has not been shown to fix missing data.

## Development

```sh
python -m pytest -q tests
```

## License

Copyright 2016-2024 Matthew Wall. Distributed under the terms of the GNU
General Public License v3, see [license](license).
