#!/usr/bin/env python3
"""Reproduce offline demonstrations of every line plus shared handoffs.

Read the tools before using this runner. Run from the repository root.
Only output evidence under gathering/ and temporary data under test/scratch/.
"""
import json
from pathlib import Path
import subprocess


def main():
    scratch = Path('test/scratch/gathering25')
    scratch.mkdir(parents=True, exist_ok=True)
    results = []

    def run(name, script, args, expected=0, html=False):
        command = ['python3', '-B', script, *args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        evidence = {'name': name, 'command': command, 'exit_code': result.returncode,
                    'expected_exit_code': expected, 'stderr': result.stderr,
                    'passed': result.returncode == expected}
        if html:
            evidence['html_bytes'] = len(result.stdout.encode())
            evidence['has_html_document'] = '<!doctype html>' in result.stdout.lower()
            evidence['passed'] &= evidence['has_html_document']
        else:
            try:
                evidence['output'] = json.loads(result.stdout)
            except ValueError:
                evidence['output'] = result.stdout
        results.append(evidence)
        return result.stdout

    run('Report Delta retained observations', 'line-1/tools/report-delta/report_delta.py',
        ['line-1/tools/report-delta/observed-before.json', 'line-1/tools/report-delta/observed-after.json', '--same-expectations'])
    probes = json.loads(Path('gathering/live-probes25.json').read_text())
    for name, index in [('before', 0), ('after', 1)]:
        (scratch / (name + '.json')).write_text(json.dumps(probes[index]['stdout']))
    run('Report Delta current observations', 'line-1/tools/report-delta/report_delta.py',
        [str(scratch / 'before.json'), str(scratch / 'after.json'), '--same-expectations'])
    run('CSV key audit composite key', 'line-2/tools/csv-key-audit/audit.py',
        ['line-2/tools/csv-key-audit/demo.csv', '--key', 'item', '--key', 'location'])
    run('CSV key audit ambiguous key', 'line-2/tools/csv-key-audit/audit.py',
        ['line-2/tools/csv-key-audit/demo.csv', '--key', 'item'], 1)
    pair = ['line-2/tools/csv-reconcile/demo-before.csv', 'line-2/tools/csv-reconcile/demo-after.csv', '--key', 'item']
    run('CSV exact reconciliation', 'line-2/tools/csv-reconcile/reconcile.py', pair, 1)
    run('CSV HTML review', 'line-2/tools/csv-review/review.py', pair, 1, html=True)
    run('CSV three-way merge', 'line-2/tools/csv-merge/merge.py',
        [f'line-2/tools/csv-merge/demo-{side}.csv' for side in ('base','left','right')] + ['--key', 'item', '--format', 'csv'])
    run('Import Map example', 'line-3/tools/import-map/import_map.py', ['line-3/tools/import-map/examples', '--json'])
    run('Import Impact real worker', 'line-3/tools/import-impact/impact.py',
        ['line-1/tools/deadline-sentry', 'deadline_sentry', '--json', '--strict'])
    run('Import Delta added cycle', 'line-3/tools/import-delta/delta.py',
        ['line-3/tools/import-delta/examples/before', 'line-3/tools/import-delta/examples/after', '--json', '--check'], 1)
    run('Import Delta real worker unchanged', 'line-3/tools/import-delta/delta.py',
        ['line-1/tools/deadline-sentry'] * 2 + ['--json', '--check', '--strict'])
    abi = 'line-4/tools/abi-workbench/abi_workbench.py'
    run('ABI offline demo', abi, ['--demo'])
    run('ABI published array layout', abi, ['encode', '--abi', 'line-4/tools/abi-workbench/array-example.json', '--function', 'f',
        '--args', '[291,[1110,1929],"0x31323334353637383930","0x48656c6c6f2c20776f726c6421"]'])
    strict = ['decode', '--abi', 'line-4/tools/abi-workbench/alias-example.json', '--function', 'transfer', '--strict', '--data']
    boolean = '0x' + '0' * 63 + '1'
    run('ABI strict boolean', abi, strict + [boolean])
    run('ABI strict rejects surplus', abi, strict + [boolean + '0' * 64], 2)
    output = run('Token Read Plan historical ZTO and IMD', 'shared/token-read-plan/token_read_plan.py', ['demo'])
    assert output == Path('shared/token-read-plan/observed.csv').read_text()
    token_pair = ['shared/token-read-plan/observed.csv'] * 2 + ['--key', 'chain_id', '--key', 'token_address', '--key', 'field']
    run('Checked token CSV review', 'shared/import-drift/checked_review.py', token_pair)
    run('Checked token HTML review', 'shared/import-drift/checked_review.py', token_pair + ['--format', 'html'], html=True)
    snap = run('Import Drift real worker', 'shared/import-drift/drift.py', ['snapshot', 'line-1/tools/endpoint-sentry'])
    (scratch / 'sentry.csv').write_text(snap)
    run('Checked import CSV review', 'shared/import-drift/checked_review.py',
        ['shared/import-drift/observed-sentry23.csv', str(scratch / 'sentry.csv'), '--key', 'module'])
    run('Import merge and impact handoff', 'shared/import-drift/handoff.py',
        ['shared/import-drift/observed-sentry23.csv'] * 3 + ['line-1/tools/endpoint-sentry'])
    report = {'ok': all(item['passed'] for item in results), 'results': results,
              'token_historical_csv_byte_identical': True}
    Path('gathering/integration-checks25.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ok': report['ok'], 'checks': len(results),
                      'failed': [r['name'] for r in results if not r['passed']]}, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
