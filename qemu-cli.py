import click

from lib.cli.query_cpus_fast import query_cpus_fast
from lib.cli.query_stats import query_stats
from lib.cli.query_stats_schemas import query_stats_schemas
from lib.file import Format


@click.group
@click.option(
  '-f',
  '--format',
  'fmt',
  default=Format.text.name,
  type=click.Choice([f.name for f in Format]),
)
@click.option('-l', '--loop', 'loop', is_flat=True)
@click.option('-p', '--print', 'print', is_flag=True)
@click.option('-s', '--save', 'save', is_flag=True)
@click.argument('name', required=True)
@click.pass_context
def cli(ctx: dict, fmt: str, print: bool, save: bool, name: str):
  ctx.obj = {'name': name, 'fmt': Format(fmt), 'print': print, 'save': save}


cli.add_command(query_cpus_fast)
cli.add_command(query_stats)
cli.add_command(query_stats_schemas)


if __name__ == '__main__':
  cli()
