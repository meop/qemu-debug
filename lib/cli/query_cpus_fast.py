import click
import pandas as pd

from lib.cmd import Cmd, coroutine
from lib.qmp import QmpClientSocket


class QueryCpusFastCmd(Cmd):
  def __init__(self, socket: QmpClientSocket):
    super().__init__(socket, 'query-cpus-fast')

  async def __call__(self, obj: dict):
    res = await super().__call__()
    if not res:
      return

    df = pd.json_normalize(
      res,
      errors='ignore',
      sep='_',
    )

    data = await self.to_dict(df)

    if obj['save']:
      await self.save(
        data,
        {
          'name': self.name,
          'fmt': obj['fmt'],
          'print': obj['print'],
        },
      )

    return data


@click.command()
@click.pass_obj
@coroutine
async def query_cpus_fast(obj: dict):
  socket = QmpClientSocket(obj['name'])
  return await QueryCpusFastCmd(socket)(obj)
