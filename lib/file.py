import json
import os
import os.path as ospath
from enum import Enum
from typing import List

import aiofiles
import yaml
from prettytable import PrettyTable

SAVE_DIR = ospath.join(ospath.dirname(ospath.dirname(__file__)), 'save')


class Format(Enum):
  text = 'text'
  json = 'json'
  yaml = 'yaml'


def to_str(data: List[dict], format: Format = Format.text):
  output = ''
  match format:
    case Format.text:
      table = PrettyTable()
      table.field_names = list(data[0].keys())
      for r in data:
        table.add_row(list(r.values()))
      output = table.get_string()
    case Format.json:
      output = json.dumps(data, indent=2)
    case Format.yaml:
      output = yaml.dump(data, indent=2)
  return output


async def to_file(data: str, name: str, ext: str, append: bool = False):
  os.makedirs(SAVE_DIR, exist_ok=True)
  path = ospath.join(SAVE_DIR, f'{name}.{ext}')

  mode = 'a' if append else 'w'
  async with aiofiles.open(path, mode) as f:
    if not data.endswith('\n'):
      data += '\n'
    await f.write(data)
