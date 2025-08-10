import click

from lib.cli.cpu.cpu_load import cpu_load
from lib.cli.cpu.cpu_pin import cpu_pin


@click.group
def cpu():
  pass


cpu.add_command(cpu_load)
cpu.add_command(cpu_pin)
