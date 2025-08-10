from multiprocessing import Process
from typing import List

import click
import psutil
from click_params import IntListParamType

from lib.cmd import coroutine


class LoadCmd:
  async def __call__(self, obj: dict, cpus: List[int]):
    procs = []
    for cpu in cpus if cpus else list(range(psutil.cpu_count())):
      mp_p = Process(target=self.load, args=())
      p = psutil.Process(mp_p.pid)
      p.cpu_affinity([cpu])
      mp_p.start()
      procs.append(mp_p)

    for p in procs:
      p.join()

  def load(self):
    try:
      while True:
        pass
    except KeyboardInterrupt:
      pass


@click.command
@click.option('-c', '--cpus', type=IntListParamType(), default=[])
@click.pass_obj
@coroutine
async def load(obj: dict, cpus: List[int]):
  return await LoadCmd()(obj, cpus)
