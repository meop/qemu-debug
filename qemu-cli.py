import asyncio
import click
from functools import wraps

from lib.file import Format, out
from lib.qemu import QemuController


def coroutine(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    return asyncio.run(f(*args, **kwargs))

  return wrapper


@click.group()
@click.option(
  '-f',
  '--format',
  'fmt',
  default=Format.json.name,
  type=click.Choice([f.name for f in Format]),
)
@click.argument('name', required=True)
@click.pass_context
def cli(ctx: dict, fmt: str, name: str):
  ctx.obj = {'name': name, 'fmt': Format(fmt)}


@cli.command()
@click.pass_obj
@coroutine
async def query_stats_schemas(obj: dict):
  ctrl = QemuController(obj['name'])
  cmd = 'query-stats-schemas'
  await out(cmd, await ctrl.run(cmd), obj['fmt'])


if __name__ == '__main__':
  cli()
