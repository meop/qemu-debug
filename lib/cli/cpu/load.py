from typing import List

import click
from click_params import IntListParamType

from lib.cmd import coroutine


class LoadCmd:
  async def __call__(self, obj: dict, cpus: List[int]):
    pass


@click.command
@click.option('-c', '--cpus', type=IntListParamType(), default=[])
@click.pass_obj
@coroutine
async def load(obj: dict, cpus: List[int]):
  return await LoadCmd()(obj, cpus)
