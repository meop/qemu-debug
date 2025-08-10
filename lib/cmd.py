import asyncio
from functools import wraps
from typing import Optional

from pandas import DataFrame

import lib.file as file
from lib.qmp import QmpClientSocket


def coroutine(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    return asyncio.run(f(*args, **kwargs))

  return wrapper


class QmpCmd:
  def __init__(self, socket: QmpClientSocket, name: str):
    self.socket = socket
    self.name = name

  async def __call__(self, arg: Optional[dict] = None):
    return await self.socket(self.name, arg)

  def to_dict(self, df: DataFrame):
    df.columns = df.columns.str.replace('-', '_')
    return df.to_dict(orient='records')

  def to_str(self, data: dict, format: file.Format):
    return file.to_str(data, format)

  async def save(
    self, data_str: str, name: str, format: file.Format, append: bool = False
  ):
    await file.to_file(data_str, name, format.name, append)
