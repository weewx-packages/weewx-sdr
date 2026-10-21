# Copyright 2026 weewx-packages
# Distributed under the terms of the GNU Public License (GPLv3)
import importlib.util
import io
import json
from pathlib import Path
import queue
import shlex
import subprocess
import sys
from unittest.mock import Mock
import warnings

import pytest

path = Path(__file__).parents[1] / 'bin/user/sdr.py'
spec = importlib.util.spec_from_file_location('sdr', path)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def parse(model, **fields):
    obj = {'time': '2026-02-04 13:09:57', 'model': model, 'id': 55}
    obj.update(fields)
    return next(m.PacketFactory.create([json.dumps(obj)]))


def value(packet, field):
    return next(v for k, v in packet.items() if k.split('.')[0] == field)


@pytest.mark.parametrize('model', ['LaCrosse-TX', 'LaCrosse TX Sensor'])
def test_lacrosse_identifiers(model):
    assert value(parse(model, temperature_C=0), 'temperature') == 0


def test_acurite_mph():
    assert value(parse('Acurite-5n1', id=858, wind_avg_mi_h=1.65), 'wind_speed') == 1.65


def test_soil_zero():
    assert value(parse('Bresser-6in1', moisture=0), 'soil_moisture_raw') == 0


def test_bresser_air_quality():
    packet = parse('Bresser-7in1', pm_2_5_ug_m3=5, pm_10_ug_m3=8)
    assert value(packet, 'pm2_5_atm') == 5
    assert value(packet, 'pm10_0_atm') == 8
    assert not any(k.startswith('temperature.') for k in packet)


def test_wh46_all_particle_sizes():
    packet = parse('Fineoffset-WH46', pm1_ug_m3=1, pm2_5_ug_m3=2.5,
                   pm4_ug_m3=4, pm10_ug_m3=10, co2_ppm=541)
    assert value(packet, 'pm1_0_atm') == 1
    assert value(packet, 'pm2_5_atm') == 2.5
    assert value(packet, 'pm4_0_atm') == 4
    assert value(packet, 'pm10_0_atm') == 10
    assert value(packet, 'co2_atm') == 541


@pytest.mark.parametrize('temperature', [{'temperature_C': 0}, {'temperature_F': 32}])
def test_bresser_three_channel_units(temperature):
    packet = parse('Bresser-3CH', channel=1, **temperature)
    assert packet['temperature.1:55.BresserTH'] == pytest.approx(0)


def test_misol_alias_keeps_sensor_mapping():
    fields = dict(id=63, temperature_C=27.3, rain_mm=1.016, wind_avg_m_s=0)
    assert parse('Fineoffset-WS69', **fields) == parse('Fineoffset-WH65B', **fields)


def test_wh3085_existing_uv_parser():
    packet = parse('Fineoffset-WHx080', subtype=2, uv_sensor_id=113, uv_index=0, lux=821, wm=1.202)
    assert packet['uv_index.113.FOWHx080Packet'] == 0
    assert packet['radiation.113.FOWHx080Packet'] == 1.202


def test_counter_reset_and_next_interval():
    driver = object.__new__(m.SDRDriver)
    driver._deltas = {'rain': 'rain_total'}
    driver._counter_values = {}
    results = []
    for total in [10, 12, 0, .2]:
        packet = {'rain_total': total}
        driver._calculate_deltas(packet)
        results.append(packet['rain'])
    assert results == [None, 2, None, .2]
    driver._deltas = {'dummy': 'dummy_total'}
    packet = {'rain_total': 1}
    driver._calculate_deltas(packet)
    assert 'rain' not in packet


def test_issue197_correct_sensor_map():
    packet = parse('Fineoffset-WH24', id=65, temperature_C=10.9, wind_avg_m_s=3.08)
    # The rtl_433 model maps to FOWH24Packet or FOWH24BPacket by model suffix.
    suffix = next(k.split('.', 1)[1] for k in packet if k.startswith('temperature.'))
    mapped = m.SDRDriver.map_to_fields(packet, {'outTemp': 'temperature.' + suffix, 'windSpeed': 'wind_speed.' + suffix})
    assert mapped['outTemp'] == 10.9
    assert mapped['windSpeed'] == 3.08


def test_binary_eof_and_thread_api():
    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        reader = m.AsyncReader(io.BytesIO(b'one\n'), queue.Queue(), 'fixture')
        reader.start()
        reader.join(1)
    assert not reader.is_alive()
    assert reader._queue.get_nowait() == b'one\n'


def test_closed_pipe():
    stream = io.BytesIO()
    stream.close()
    reader = m.AsyncReader(stream, queue.Queue(), 'closed')
    reader.run()
    assert not reader._running


def test_shutdown_is_idempotent():
    manager = m.ProcManager()
    manager.shutdown()
    manager.startup(shlex.join([sys.executable, '-c', 'import time; time.sleep(30)']))
    readers = [manager.stdout_reader, manager.stderr_reader]
    manager.shutdown()
    manager.shutdown()
    assert not manager.running()
    assert all(not reader.is_alive() for reader in readers)


def test_quoted_subprocess_output_is_drained():
    manager = m.ProcManager()
    manager.startup(shlex.join([sys.executable, '-c', "print('fixture with spaces')"]))
    try:
        manager._process.wait(timeout=5)
        manager.stdout_reader.join(1)
        lines = [line for batch in manager.get_stdout() for line in batch]
        assert lines == ['fixture with spaces\n']
    finally:
        manager.shutdown()


def test_shell_pipeline_output_and_shutdown():
    manager = m.ProcManager()
    manager.startup("printf 'hello fixture\\n' | cat", use_shell=True)
    try:
        assert [line for batch in manager.get_stdout() for line in batch] == ['hello fixture\n']
    finally:
        manager.shutdown()


def test_regex_compiles_without_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error', SyntaxWarning)
        compile(path.read_text(), str(path), 'exec')
