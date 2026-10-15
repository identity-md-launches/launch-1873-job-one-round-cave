#!/usr/bin/env python3
"""Compare two completed Endpoint Sentry observations offline, without probing."""
import argparse
import json
import math
from pathlib import Path
import re
import sys

MAX_BYTES = 262144


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate JSON key')
            out[key] = value
        return out

    def number(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('non-finite JSON number')
        return value

    def invalid(text):
        raise ValueError('non-finite JSON constant')

    return json.loads(raw, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=invalid)


def load(path):
    """Only explicitly supplied reports inside the current workspace are read."""
    root = Path.cwd().resolve()
    resolved = Path(path).resolve()
    if root not in resolved.parents:
        raise ValueError('report must be inside the current workspace')
    with resolved.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('report exceeds 256 KiB')
    return strict_json(raw.decode('utf-8'))


def observation(report):
    if not isinstance(report, dict):
        raise ValueError('report must be an object')
    if report.get('schema') == 'deadline-sentry/v1':
        child = report.get('probe')
        if not isinstance(child, dict) or type(report.get('ok')) is not bool:
            raise ValueError('deadline report has no completed probe; cannot compare')
        if report['ok'] is not child.get('ok'):
            raise ValueError('wrapper outcome contradicts probe')
        report = child
    if report.get('schema') != 'endpoint-sentry/v1':
        raise ValueError('expected endpoint-sentry/v1 or completed deadline-sentry/v1')
    if type(report.get('ok')) is not bool or not isinstance(report.get('url'), str):
        raise ValueError('probe needs boolean ok and string url')
    limits = report.get('limits')
    if not isinstance(limits, dict) or set(limits) != {'timeout_seconds', 'max_bytes', 'max_redirects'}:
        raise ValueError('probe limits are missing or unknown')
    for value in limits.values():
        if type(value) not in (int, float) or not 0 <= value <= 16777216 or not math.isfinite(value):
            raise ValueError('invalid probe limits')
    hops = report.get('hops')
    checks = report.get('checks')
    if not isinstance(hops, list) or len(hops) > 11 or not isinstance(checks, list) or len(checks) > 4:
        raise ValueError('invalid hops or checks')
    chain = []
    body = None
    for hop in hops:
        if not isinstance(hop, dict) or not isinstance(hop.get('url'), str):
            raise ValueError('invalid hop URL')
        status = hop.get('status')
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError('invalid hop status')
        chain.append({'url': hop['url'], 'status': status, 'location': hop.get('location')})
        digest = hop.get('body_sha256')
        if digest is not None:
            if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
                raise ValueError('invalid body digest')
            body = digest
    normalized_checks = []
    seen = set()
    for check in checks:
        if (not isinstance(check, dict) or not isinstance(check.get('name'), str)
                or check['name'] not in {'status', 'json', 'json_pointer', 'json_value'}):
            raise ValueError('invalid check name')
        if type(check.get('ok')) is not bool or check['name'] in seen:
            raise ValueError('invalid or duplicate check')
        seen.add(check['name'])
        normalized_checks.append({key: check[key] for key in ('name', 'path', 'expected', 'ok') if key in check})
    error = report.get('error')
    if error is not None and (not isinstance(error, dict) or not isinstance(error.get('kind'), str)):
        raise ValueError('invalid probe error')
    if report['ok'] and (error is not None or not checks or not all(c['ok'] for c in checks) or not hops):
        raise ValueError('successful probe contradicts its evidence')
    if not report['ok'] and error is None and (not checks or all(c['ok'] for c in checks)):
        raise ValueError('failed probe contradicts its checks')
    return {'url': report['url'], 'ok': report['ok'], 'limits': limits,
            'chain': chain, 'checks': normalized_checks, 'body_sha256': body,
            'error_kind': None if error is None else error['kind']}


def compare(before, after, same_expectations=False):
    a, b = observation(before), observation(after)
    changes = []
    for key in ('ok', 'limits', 'chain', 'checks', 'body_sha256', 'error_kind'):
        if a[key] != b[key]:
            changes.append({'field': key, 'before': a[key], 'after': b[key]})
    reasons = []
    if a['url'] != b['url']:
        reasons.append('different requested URLs')
    if a['limits'] != b['limits']:
        reasons.append('different probe limits')
    # Failed probes can stop before recording checks. Original v1 reports do
    # not retain all requested expectations (notably expected JSON values).
    if not same_expectations:
        reasons.append('v1 reports omit full expectations; confirm identical probe arguments')
    signature = lambda x: [{k: v for k, v in c.items() if k != 'ok'} for c in x['checks']]
    sa, sb = signature(a), signature(b)
    if a['error_kind'] is None and b['error_kind'] is None and len(sa) != len(sb):
        reasons.append('different completed check sets')
    for ca, cb in zip(sa, sb):
        if ca != cb:
            reasons.append('recorded expectations differ')
            break
    if reasons:
        verdict = 'inconclusive'
    elif a['ok'] and not b['ok']:
        verdict = 'regressed'
    elif not a['ok'] and b['ok']:
        verdict = 'recovered'
    else:
        verdict = 'still_healthy' if b['ok'] else 'still_failing'
    return {'schema': 'report-delta/v1', 'verdict': verdict, 'reasons': reasons,
            'before_ok': a['ok'], 'after_ok': b['ok'], 'changes': changes,
            'body_change_is_health_failure': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('before')
    parser.add_argument('after')
    parser.add_argument('--same-expectations', action='store_true',
                        help='assert both probes used identical status/JSON expectation arguments')
    args = parser.parse_args(argv)
    try:
        result = compare(load(args.before), load(args.after), args.same_expectations)
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        print(json.dumps({'schema': 'report-delta/v1', 'error': str(error)}))
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result['verdict'] == 'inconclusive' else (1 if not result['after_ok'] else 0)


if __name__ == '__main__':
    sys.exit(main())
