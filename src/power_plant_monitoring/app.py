"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = power_plant_monitoring.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys, os, time
from logging.handlers import RotatingFileHandler

import confuse

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from growatt import Growatt

from power_plant_monitoring import __version__

__author__ = "dennis-off"
__copyright__ = "dennis-off"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from power_plant_monitoring.skeleton import fib`,
# when using this Python module as a library.

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version="harvester {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = (
        "%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s"
    )
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = RotatingFileHandler(
        "log/power_plant_monitoring.log", maxBytes=10000 * 1000, backupCount=500
    )
    formatter = logging.Formatter(logformat)
    file_handler.setFormatter(formatter)

    logging.getLogger().addHandler(file_handler)


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)

    # assure log folder exists
    os.makedirs("log", exist_ok=True)
    setup_logging(args.loglevel)

    _logger.debug("Starting power_plant_monitoring.app {ver} ...".format(ver=__version__))
    
    # load configuration
    filename = "config.yml"
    config = confuse.Configuration("harvester", __name__)
    config.set_file(filename)

    interval = config["growatt"]["interval_sec"].get(int)
    offline_interval = config["growatt"]["offline_interval_sec"].get(int)
    error_interval = config["growatt"]["error_interval_sec"].get(int)

    port = config["growatt"]["port"].get(str)
    _logger.debug(f"Growatt (Port): {port}")
    client = ModbusClient(method='rtu', port=port, baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
    client.connect()

    growatt = Growatt(client, "Growatt", 1)

    _logger.debug(f"Growatt connected.")

    url = config["influxdb"]["url"].get(str)
    org = config["influxdb"]["org"].get(str)
    token = config["influxdb"]["token"].get(str)

    _logger.debug(f"InfluxDB: {url}, Organization: {org}")
    influx = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    _logger.debug(f"InfluxDB client created.")

    bucket="monitoring"

    info = growatt.read()

    now = time.time()

    points = [{
                'time': int(now),
                'measurement': 'growatt',
                "fields": info
            }]
    
    bucket="monitoring"
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    write_api.write(bucket=bucket, org="home", record=points)
    
    _logger.info("power_plant_monitoring.app has finished")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m power_plant_monitoring.skeleton 42
    #
    run()
