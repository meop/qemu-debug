import aiofiles
import json
import yaml
import os.path as ospath

from enum import Enum

OUT_DIR = './out'


class Format(Enum):
  json = 'json'
  yaml = 'yaml'


async def out(name: str, data: dict, fmt: Format = Format.json):
  path = ospath.join(ospath.dirname(__file__), '..', OUT_DIR, f'{name}.{fmt.name}')

  async with aiofiles.open(path, mode='w') as f:
    output = ''
    match fmt:
      case Format.json:
        output = json.dumps(data, indent=2)
      case Format.yaml:
        output = yaml.dump(data, indent=2)
    await f.write(output)
