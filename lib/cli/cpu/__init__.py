import click

from lib.cli.cpu.load import load
from lib.cli.cpu.pin import pin


@click.group
def cpu():
  pass


cpu.add_command(load)
cpu.add_command(pin)
