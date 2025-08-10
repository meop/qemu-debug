import click

from lib.cli.cpu.load import load


@click.group
def cpu():
  pass


cpu.add_command(load)
