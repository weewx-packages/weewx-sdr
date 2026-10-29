# weewx-sdr

WeeWX driver continued from matthewwall/weewx-sdr.

## Commands

Run `python -m pytest -q tests` from this directory.

## Conventions

`bin/user/sdr.py` holds the driver, `bin/user/sdr_packets/` the parsers, one module per manufacturer. A new module goes into `PARSER_MODULES` in `bin/user/sdr_packets/__init__.py` and into `FILES` in `install.py`; tests check both. `tests/examples.json` pins the packets each example produces; update an entry when a parser change alters its packet.

Preserve the existing Python style and copyright notices. Use Google docstrings with types instead of runtime annotations. Changes to GPL files must carry a dated modification notice.

README follows the weewx-packages schema and names no versions or archive URLs; installation links to the catalog page.
