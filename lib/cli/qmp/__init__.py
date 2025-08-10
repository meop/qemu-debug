import click

from lib.cli.qmp.query_blockstats import query_blockstats
from lib.cli.qmp.query_cpus_fast import query_cpus_fast
from lib.cli.qmp.query_stats import query_stats
from lib.cli.qmp.query_stats_schemas import query_stats_schemas


@click.group
@click.argument('name', required=True)
@click.pass_obj
def qmp(obj: dict, name: str):
  obj.update(
    {
      'name': name,
    }
  )


qmp.add_command(query_blockstats)
qmp.add_command(query_cpus_fast)
qmp.add_command(query_stats)
qmp.add_command(query_stats_schemas)
