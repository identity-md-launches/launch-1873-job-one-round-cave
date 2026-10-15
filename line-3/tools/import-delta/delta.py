#!/usr/bin/env python3
"""Compare static Python import structure in two workspace source trees."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_mapper():
    path = Path(__file__).resolve().parents[1] / 'import-map' / 'import_map.py'
    spec = importlib.util.spec_from_file_location('line3_delta_mapper', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def differences(before, after):
    """Return stable added/removed values, preserving full JSON objects."""
    encode = lambda item: json.dumps(item, sort_keys=True, ensure_ascii=True)
    old = {encode(item): item for item in before}
    new = {encode(item): item for item in after}
    return {'added': [new[key] for key in sorted(new.keys() - old.keys())],
            'removed': [old[key] for key in sorted(old.keys() - new.keys())]}


def warnings(report):
    return {'issues': report['issues'],
            'dynamic_imports': [{'module': item['module'], 'path': item['path'], 'line': line}
                                for item in report['modules']
                                for line in item['dynamic_import_lines']]}


def compare(before, after):
    old = {item['module']: item for item in before['modules']}
    new = {item['module']: item for item in after['modules']}
    changes = {
        'modules': differences(list(old), list(new)),
        'edges': differences(before['edges'], after['edges']),
        'entrypoints': differences(before['summary']['entrypoints'], after['summary']['entrypoints']),
        'cycle_groups': differences(before['cycles'], after['cycles']),
        'source_paths': [{'module': name, 'before': old[name]['path'], 'after': new[name]['path']}
                         for name in sorted(old.keys() & new.keys())
                         if old[name]['path'] != new[name]['path']],
    }
    has_changes = bool(changes['source_paths']) or any(
        value['added'] or value['removed'] for key, value in changes.items() if key != 'source_paths')
    scans = {'before': warnings(before), 'after': warnings(after)}
    has_warnings = any(side['issues'] or side['dynamic_imports'] for side in scans.values())
    return {'changes': changes, 'has_changes': bool(has_changes),
            'has_warnings': has_warnings, 'scans': scans,
            'summary': {'before': before['summary'], 'after': after['summary']},
            'scope': 'Static explicit local imports only. Changes are graph changes, not all source edits; warnings can hide edges.'}


def scan(mapper, path, workspace):
    root = path.resolve()
    if not root.is_relative_to(workspace) or not root.is_dir():
        raise ValueError('each root must be an existing directory inside the current workspace')
    # Validate all files selected by the mapper before it reads any source.
    for source in mapper.source_files(root):
        if not source.resolve().is_relative_to(workspace):
            raise ValueError('source resolves outside the current workspace')
    return mapper.inspect(root)


def format_text(result):
    lines = ['Import structure changed: ' + str(result['has_changes']).lower()]
    for kind, change in result['changes'].items():
        if kind == 'source_paths':
            for item in change:
                lines.append(f"source path: {item['module']}: {item['before']} -> {item['after']}")
            continue
        for direction in ('added', 'removed'):
            for item in change[direction]:
                if kind == 'edges':
                    label = item['from'] + ' -> ' + item['to']
                elif kind == 'cycle_groups':
                    label = ', '.join(item)
                else:
                    label = item
                lines.append(f'{kind} {direction}: {label}')
    for side, scan_result in result['scans'].items():
        lines.append(f"{side} warnings: {len(scan_result['issues'])} issues, {len(scan_result['dynamic_imports'])} dynamic import calls")
    lines.append(result['scope'])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--check', action='store_true', help='exit 1 for structural differences')
    parser.add_argument('--strict', action='store_true', help='also exit 1 for scan issues or recognized dynamic imports')
    args = parser.parse_args(argv)
    try:
        mapper = load_mapper()
        workspace = Path.cwd().resolve()
        result = compare(scan(mapper, args.before, workspace), scan(mapper, args.after, workspace))
    except (OSError, ValueError, RuntimeError, RecursionError) as exc:
        print('import-delta: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else format_text(result))
    return int((args.check and result['has_changes']) or (args.strict and result['has_warnings']))


if __name__ == '__main__':
    sys.exit(main())
