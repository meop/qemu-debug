import asyncio
from functools import wraps
from typing import Optional, TypedDict

from pandas import DataFrame

import lib.file as file
from lib.qmp import QmpClientSocket


def coroutine(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    return asyncio.run(f(*args, **kwargs))

  return wrapper


class FileOpt(TypedDict):
  append: Optional[bool]
  fmt: file.Format
  name: str
  print: Optional[bool]


class Cmd:
  def __init__(self, socket: QmpClientSocket, name: str):
    self.socket = socket
    self.name = name

  async def __call__(self, arg: Optional[dict] = None):
    return await self.socket(self.name, arg)

  async def to_dict(self, df: DataFrame):
    df.columns = df.columns.str.replace('-', '_')
    return df.to_dict(orient='records')

  async def save(self, data: dict, opt: FileOpt):
    output = file.to_str(data, opt['fmt'])
    if 'print' in opt and opt['print']:
      print(output)
    await file.to_file(
      output,
      opt['name'],
      opt['fmt'].name,
      'append' in opt and opt['append'],
    )
