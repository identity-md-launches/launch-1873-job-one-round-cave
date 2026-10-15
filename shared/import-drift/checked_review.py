#!/usr/bin/env python3
"""Audit key readiness before reconciling CSV exports; offline, read-only."""
import argparse
import html
import json
import sys

import audit
import reconcile
import review


def compare(before, after, keys, ignore=()):
    # Both parsers run before emitting anything. Inputs must stay immutable
    # throughout this call: this local CLI is not a concurrent-filesystem sandbox.
    key_report = audit.audit([before, after], keys)
    result = {'schema': 'checked-csv-review/v1', 'ready': key_report['passes'],
              'key_audit': key_report, 'comparison': None}
    if key_report['passes']:
        result['comparison'] = reconcile.reconcile(before, after, keys, ignore)
    return result


def render_html(result):
    notice = ('<section aria-label="Key readiness"><h2>Key readiness: '
              + ('PASS' if result['ready'] else 'REVIEW REQUIRED') + '</h2><pre>'
              + html.escape(audit.render_text(result['key_audit']), quote=True)
              + '</pre></section>')
    if result['ready']:
        body = '\n'.join(review.iter_html(result['comparison']))
        return body.replace('<h2>Comparison settings</h2>', notice + '<h2>Comparison settings</h2>', 1)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
            'style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
            '<title>CSV comparison withheld</title><style>body{font:16px/1.5 system-ui;'
            'margin:2rem;max-width:80ch}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
            '</style></head><body><h1>CSV comparison withheld</h1><p>Resolve duplicate '
            'or empty keys, or supply data records, before comparing these exports.</p>'
            + notice + '</body></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('before')
    parser.add_argument('after')
    parser.add_argument('--key', action='append', required=True)
    parser.add_argument('--ignore', action='append', default=[])
    parser.add_argument('--format', choices=('json', 'html'), default='json')
    args = parser.parse_args(argv)
    try:
        if set(args.key) & set(args.ignore):
            raise ValueError('key columns cannot be ignored')
        result = compare(args.before, args.after, args.key, args.ignore)
        output = render_html(result) if args.format == 'html' else json.dumps(result, indent=2, ensure_ascii=True)
    except (OSError, ValueError, RecursionError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=True), file=sys.stderr)
        return 2
    print(output)
    if not result['ready']:
        return 1
    return 0 if result['comparison']['equal'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
