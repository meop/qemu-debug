import click
import pandas as pd

from lib.cmd import Cmd, coroutine
from lib.qmp import QmpClientSocket


class QueryBlockstatsCmd(Cmd):
  def __init__(self, socket: QmpClientSocket):
    super().__init__(socket, 'query-blockstats')

  async def __call__(self, obj: dict):
    res = await super().__call__()
    if not res:
      return

    df = pd.json_normalize(
      res,
      errors='ignore',
      sep='_',
    )

    data = self.to_dict(df)
    data_str = self.to_str(data, obj['format'])

    if obj['print']:
      print(data_str)

    if obj['save']:
      await self.save(data_str, self.name, obj['format'])


@click.command
@click.argument('-n', '--name')
@click.pass_obj
@coroutine
async def query_blockstats(obj: dict):
  socket = QmpClientSocket(obj['name'])
  return await QueryBlockstatsCmd(socket)(obj)
