from typing import List

import click
from click_params import IntListParamType
import pandas as pd

from lib.cli.qmp.query_cpus_fast import QueryCpusFastCmd
from lib.cmd import QmpCmd, coroutine
from lib.qmp import QmpClientSocket

TARGET_PROVIDER_STATS = {
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


class QueryStatsQmpCmd(QmpCmd):
  def __init__(self, socket: QmpClientSocket):
    super().__init__(socket, 'query-stats')

  async def __call__(
    self, obj: dict, cpus: List[int], target: str, provider: str, stats: List[str]
  ):
    providers_to_names = []
    for p in [provider] if provider else TARGET_PROVIDER_STATS[target].keys():
      names = (
        [stat for stat in TARGET_PROVIDER_STATS[target][p] if stat in stats]
        if stats
        else TARGET_PROVIDER_STATS[target][p]
      )
      providers_to_names.append({'provider': p, 'names': names})

    args = []
    for ptn in providers_to_names:
      arg_base = {'target': target, 'providers': [ptn]}
      if target != 'vcpu':
        args.append(arg_base)
        continue

      for i, r in enumerate(
        await QueryCpusFastCmd(self.socket)({**obj, 'print': False, 'save': False})
      ):
        if cpus and i not in cpus:
          continue
        arg_base_copy = arg_base.copy()
        arg_base_copy.update({'vcpus': [r['qom_path']]})
        args.append(arg_base_copy)

    df_combo = pd.DataFrame()
    for arg in args:
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
      provider = df['provider'].iloc[0]
      df = df.pivot(
        index='provider',
        columns='stat_name',
        values='stat_value',
      )
      df.insert(0, 'provider', provider)
      df.insert(1, 'target', target)
      df.insert(2, 'vcpu', arg['vcpus'][0] if 'vcpus' in arg else '')

      if df_combo.empty:
        df_combo = df
        continue
      df_combo = pd.concat([df_combo, df])

    data = self.to_dict(df_combo)
    data_str = self.to_str(data, obj['format'])

    if obj['print']:
      print(data_str)

    if obj['save']:
      await self.save(data_str, f'{self.name}-{target}', obj['format'])

    return df_combo


@click.command
@click.option('-c', '--cpus', type=IntListParamType)
@click.argument('name', required=True)
@click.argument('target', required=True)
@click.argument('provider', required=False, default='')
@click.argument('stats', nargs=-1)
@click.pass_obj
@coroutine
async def query_stats(
  obj: dict, cpus: List[int], name: str, target: str, provider: str, stats: List[str]
):
  socket = QmpClientSocket(name)
  return await QueryStatsQmpCmd(socket)(obj, cpus, target, provider, stats)
