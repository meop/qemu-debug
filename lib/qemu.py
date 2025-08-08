import asyncio
import os.path as ospath
import subprocess

from qemu.qmp import QMPClient
from qemu.qmp.events import EventListener
from typing import Optional

TMP_QEMU_DIR_PATH = '/tmp/qemu'
SOCKET_NAME = 'qmp.socket'


class QemuController:
  client: Optional[QMPClient]

  def __init__(self, name: str):
    self.client = None
    self.name = name
    self.socket_path = ospath.join(TMP_QEMU_DIR_PATH, self.name, SOCKET_NAME)

  async def run(self, cmd: str, args: Optional[dict] = None):
    res = subprocess.run(
      ['stat', '--format=%a', self.socket_path], capture_output=True, text=True
    )
    octal = '666'
    if res.stdout.strip() != octal:
      subprocess.run(['sudo', 'chmod', '666', self.socket_path])

    stateless = False
    if self.client is None:
      stateless = True
      await self.setup()
    res = await self.client.execute(cmd, arguments=args)
    if stateless:
      await self.teardown()
    return res

  async def setup(self):
    self.client = QMPClient(self.name)
    await self.client.connect(self.socket_path)

  async def teardown(self):
    await self.client.disconnect()

  async def watch(self, events: EventListener):
    try:
      async for event in events:
        print(f'event: {event["event"]}')
    except asyncio.CancelledError:
      return
