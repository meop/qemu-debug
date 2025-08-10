import sys

import click

from lib.cli.cpu import cpu
from lib.cli.qmp import qmp
from lib.file import Format


@click.group
@click.option(
  '-f',
  '--format',
  default=Format.text.name,
  type=click.Choice([f.name for f in Format]),
)
@click.option('-p', '--print', is_flag=True)
@click.option('-s', '--save', is_flag=True)
@click.pass_context
def cli(ctx: dict, format: str, print: bool, save: bool):
  ctx.obj = {
    'format': Format(format),
    'print': print,
    'save': save,
  }


cli.add_command(cpu)
cli.add_command(qmp)


if __name__ == '__main__':
  try:
    cli()
  except KeyboardInterrupt:
    sys.exit(0)
