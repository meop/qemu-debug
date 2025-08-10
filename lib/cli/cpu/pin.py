import click

from lib.cmd import coroutine


class PinCmd:
  async def __call__(self, obj: dict):
    pass


@click.command
@click.pass_obj
@coroutine
async def pin(obj: dict):
  return await PinCmd()(obj)
