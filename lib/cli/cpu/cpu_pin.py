import click

from lib.cmd import coroutine


class CpuPinCmd:
  async def __call__(self, obj: dict):
    pass


@click.command
@click.pass_obj
@coroutine
async def cpu_pin(obj: dict):
  return await CpuPinCmd()(obj)
