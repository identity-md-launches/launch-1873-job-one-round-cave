import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import report_delta as d


def report(ok=True):
    return {'schema': 'endpoint-sentry/v1', 'url': 'https://api.imd.fun/launches',
            'ok': ok, 'limits': {'timeout_seconds': 4, 'max_bytes': 1048576, 'max_redirects': 3},
            'hops': [{'url': 'https://api.imd.fun/launches', 'status': 200 if ok else 503,
                      'body_sha256': 'a' * 64}],
            'checks': [{'name': 'status', 'expected': 200, 'ok': ok}]}


class DeltaTests(unittest.TestCase):
    def test_regression_and_recovery(self):
        self.assertEqual(d.compare(report(), report(False), True)['verdict'], 'regressed')
        self.assertEqual(d.compare(report(False), report(), True)['verdict'], 'recovered')

    def test_body_change_not_health(self):
        a, b = report(), report()
        b['hops'][0]['body_sha256'] = 'b' * 64
        b.update(checked_at='later', elapsed_ms=900)
        result = d.compare(a, b, True)
        self.assertEqual(result['verdict'], 'still_healthy')
        self.assertEqual([c['field'] for c in result['changes']], ['body_sha256'])

    def test_failed_before_checks(self):
        b = report(False)
        b.update(hops=[], checks=[], error={'kind': 'dns', 'message': 'no answer'})
        self.assertEqual(d.compare(report(), b, True)['verdict'], 'regressed')

    def test_unknown_expectations(self):
        self.assertEqual(d.compare(report(), report())['verdict'], 'inconclusive')

    def test_different_url_limits_expectations(self):
        for change in ('url', 'limits', 'checks'):
            b = report()
            if change == 'url':
                b['url'] += '/other'
            elif change == 'limits':
                b['limits']['max_bytes'] = 12
            else:
                b['checks'][0]['expected'] = 201
            self.assertEqual(d.compare(report(), b, True)['verdict'], 'inconclusive')

    def test_wrapper_and_timeout(self):
        a = {'schema': 'deadline-sentry/v1', 'ok': True, 'probe': report()}
        self.assertEqual(d.compare(a, report(), True)['verdict'], 'still_healthy')
        with self.assertRaises(ValueError):
            d.observation({'schema': 'deadline-sentry/v1', 'ok': False, 'error': {'kind': 'deadline'}})
        a['ok'] = False
        with self.assertRaises(ValueError):
            d.observation(a)

    def test_strict_json(self):
        for raw in ('{"ok":true,"ok":false}', '{"n":NaN}', '{"n":1e999}'):
            with self.assertRaises(ValueError):
                d.strict_json(raw)

    def test_invalid_evidence(self):
        for key, value in [('limits', {'timeout_seconds': 10**400, 'max_bytes': 1, 'max_redirects': 0}),
                           ('checks', [{'name': [], 'ok': True}]), ('ok', 1), ('hops', [{}]), ('checks', [{'name': 'other', 'ok': True}]),
                           ('error', {'kind': 'dns'})]:
            a = report()
            a[key] = value
            with self.assertRaises(ValueError):
                d.observation(a)

    def test_loader_and_cli(self):
        # All temporary files are inside the authorized scratch tree.
        root = Path('test/scratch/report-delta')
        root.mkdir(parents=True, exist_ok=True)
        a, b = root / 'before.json', root / 'after.json'
        a.write_text(json.dumps(report()))
        b.write_text(json.dumps(report(False)))
        cli = Path(d.__file__)
        result = subprocess.run([sys.executable, '-B', str(cli), str(a), str(b), '--same-expectations'],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['verdict'], 'regressed')
        b.write_bytes(b' ' * (d.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            d.load(b)
        with self.assertRaises(ValueError):
            d.load('../outside-workspace.json')


if __name__ == '__main__':
    unittest.main()
