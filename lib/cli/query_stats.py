import asyncio
from typing import List

import click
import pandas as pd

from lib.cli.query_cpus_fast import QueryCpusFastCmd
from lib.cmd import Cmd, coroutine
from lib.qmp import QmpClientSocket

TARGET_TO_PROVIDER_TO_NAMES = {
  'vcpu': {
    'kvm': [
      'notify_window_exits',
      'guest_mode',
      'preemption_other',
      'preemption_reported',
      'directed_yield_successful',
      'directed_yield_attempted',
      'nested_run',
      'req_event',
      'nmi_injections',
      'irq_injections',
      'hypercalls',
      'insn_emulation_fail',
      'insn_emulation',
      'fpu_reload',
      'host_state_reload',
      'irq_exits',
      'request_irq_exits',
      'halt_exits',
      'l1d_flush',
      'nmi_window_exits',
      'irq_window_exits',
      'signal_exits',
      'mmio_exits',
      'io_exits',
      'exits',
      'invlpg',
      'tlb_flush',
      'pf_guest',
      'pf_mmio_spte_created',
      'pf_fast',
      'pf_spurious',
      'pf_emulate',
      'pf_fixed',
      'pf_taken',
      'blocking',
      'halt_wait_hist',
      'halt_poll_fail_hist',
      'halt_poll_success_hist',
      'halt_wait_ns',
      'halt_poll_fail_ns',
      'halt_poll_success_ns',
      'halt_wakeup',
      'halt_poll_invalid',
      'halt_attempted_poll',
      'halt_successful_poll',
    ],
  },
  'vm': {
    'kvm': [
      'max_mmu_page_hash_collisions',
      'max_mmu_rmap_size',
      'nx_lpage_splits',
      'pages_1g',
      'pages_2m',
      'pages_4k',
      'mmu_unsync',
      'mmu_cache_miss',
      'mmu_recycled',
      'mmu_flooded',
      'mmu_pde_zapped',
      'mmu_pte_write',
      'mmu_shadow_zapped',
      'remote_tlb_flush_requests',
      'remote_tlb_flush',
    ]
  },
  'cryptodev': {
    'cryptodev': [
      'asym-verify-bytes',
      'asym-sign-bytes',
      'asym-decrypt-bytes',
      'asym-encrypt-bytes',
      'asym-verify-ops',
      'asym-sign-ops',
      'asym-decrypt-ops',
      'asym-encrypt-ops',
      'sym-decrypt-bytes',
      'sym-encrypt-bytes',
      'sym-decrypt-ops',
      'sym-encrypt-ops',
    ],
  },
}


class QueryStatsCmd(Cmd):
  def __init__(self, socket: QmpClientSocket):
    super().__init__(socket, 'query-stats')

  async def __call__(
    self, obj: dict, index: int, loop: bool, target: str, providers: List[str]
  ):
    providers_names = []
    for p in providers if providers else TARGET_TO_PROVIDER_TO_NAMES[target].keys():
      providers_names.append(
        {'provider': p, 'names': TARGET_TO_PROVIDER_TO_NAMES[target][p]}
      )

    arg_base = {'target': target, 'providers': providers_names}
    args = []
    if target == 'vcpu':
      for r in await QueryCpusFastCmd(self.socket)(
        {**obj, 'print': False, 'save': False}
      ):
        arg_base_new = arg_base.copy()
        arg_base_new.update({'vcpus': [r['qom_path']]})
        args.append(arg_base_new)
    else:
      args.append(arg_base)

    if index != -1:
      args = [args[index]]

    datas = []

    while True:
      for idx, arg in enumerate(args):
        res = await super().__call__(arg)
        if not res:
          return

        df = pd.json_normalize(
          res,
          record_path=['stats'],
          record_prefix='stat_',
          meta=['provider'],
          errors='ignore',
        )
        if 'vcpus' in arg:
          df['vcpu'] = arg['vcpus'][0]

        data = self.to_dict(df)
        data_str = self.to_str(data, obj['format'])

        if obj['print']:
          print(data_str)

        if obj['save']:
          name = f'{self.name}-{target}'
          if target == 'vcpu':
            name = f'{name}-{idx if index == -1 else index}'
          await self.save(data_str, name, obj['format'])

        datas.append(data)

      if loop:
        datas.clear()
        await asyncio.sleep(2)
      else:
        break

    return datas


@click.command()
@click.option('-i', '--index', default=-1, type=click.INT)
@click.option('-l', '--loop', is_flag=True)
@click.argument('target', required=True)
@click.argument('providers', nargs=-1)
@click.pass_obj
@coroutine
async def query_stats(
  obj: dict, index: int, loop: bool, target: str, providers: List[str]
):
  socket = QmpClientSocket(obj['name'])
  return await QueryStatsCmd(socket)(obj, index, loop, target, providers)
