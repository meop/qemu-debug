import click
import pandas as pd

from lib.cmd import QmpCmd, coroutine
from lib.qmp import QmpClientSocket


class QueryStatsSchemasQmpCmd(QmpCmd):
  def __init__(self, socket: QmpClientSocket):
    super().__init__(socket, 'query-stats-schemas')

  async def __call__(self, obj: dict):
    res = await super().__call__()
    if not res:
      return

    df = pd.json_normalize(
      res,
      record_path=['stats'],
      record_prefix='stat_',
      meta=['provider', 'target'],
      errors='ignore',
    )

    data = self.to_dict(df)
    data_str = self.to_str(data, obj['format'])

    if obj['print']:
      print(data_str)

    if obj['save']:
      await self.save(data_str, self.name, obj['format'])

    return data


@click.command
@click.argument('name', required=True)
@click.pass_obj
@coroutine
async def query_stats_schemas(obj: dict, name: str):
  socket = QmpClientSocket(name)
  return await QueryStatsSchemasQmpCmd(socket)(obj)
