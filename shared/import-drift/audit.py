#!/usr/bin/env python3
"""Check proposed CSV keys before exact offline comparison or merging."""
import argparse
import json
from pathlib import Path
import sys

from reconcile import InputError, load_table

MAX_FILES = 8
MAX_EXAMPLES = 20
PREVIEW_CHARS = 160


def audit(paths, keys, examples=5):
    """Audit exact key tuples; never infer semantic identity or change values."""
    if not keys or len(set(keys)) != len(keys) or any(not k for k in keys):
        raise InputError('provide distinct, nonempty key columns')
    if not 1 <= len(paths) <= MAX_FILES:
        raise InputError(f'provide 1 to {MAX_FILES} CSV files')
    if type(examples) is not int or not 0 <= examples <= MAX_EXAMPLES:
        raise InputError(f'examples must be from 0 to {MAX_EXAMPLES}')

    def preview(key):
        return {column: {'text': value[:PREVIEW_CHARS], 'characters': len(value),
                         'truncated': len(value) > PREVIEW_CHARS}
                for column, value in zip(keys, key)}

    datasets = []
    anchor = None
    for index, path in enumerate(paths):
        _, groups, count = load_table(path, keys)
        # Empty components are literal empty strings. Whitespace is preserved.
        empty_groups = [(key, rows) for key, rows in sorted(groups.items()) if '' in key]
        duplicate_groups = [(key, rows) for key, rows in sorted(groups.items()) if len(rows) > 1]
        eligible = {key for key, rows in groups.items() if '' not in key and len(rows) == 1}

        def samples(items):
            return [{'key_preview': preview(key), 'record_count': len(rows),
                     'records': [row['record'] for row in rows[:examples]],
                     'omitted_records': max(0, len(rows) - examples)}
                    for key, rows in items[:examples]]

        issue_codes = []
        if count == 0:
            issue_codes.append('no_data_records')
        if empty_groups:
            issue_codes.append('empty_key_component')
        if duplicate_groups:
            issue_codes.append('duplicate_key')
        item = {'input_index': index, 'input': str(path), 'records': count,
                'distinct_keys': len(groups), 'eligible_keys': len(eligible),
                'passes': not issue_codes, 'issues': issue_codes,
                'empty_key_records': sum(len(rows) for _, rows in empty_groups),
                'empty_key_groups': len(empty_groups),
                'empty_examples': samples(empty_groups),
                'omitted_empty_groups': max(0, len(empty_groups) - examples),
                'duplicate_groups': len(duplicate_groups),
                'duplicate_records': sum(len(rows) for _, rows in duplicate_groups),
                'duplicate_examples': samples(duplicate_groups),
                'omitted_duplicate_groups': max(0, len(duplicate_groups) - examples)}
        if anchor is None:
            anchor = eligible
        else:
            item['overlap_with_first'] = {'shared_eligible_keys': len(anchor & eligible),
                                         'only_first': len(anchor - eligible),
                                         'only_this': len(eligible - anchor)}
        datasets.append(item)
    return {'format': 'csv-key-audit/v1', 'keys': list(keys),
            'passes': all(item['passes'] for item in datasets),
            'example_limit': examples, 'datasets': datasets,
            'caution': 'Unique nonempty keys in these files do not prove stable identity across exports.'}


def render_text(result):
    lines = ['CSV key audit: ' + ('PASS' if result['passes'] else 'REVIEW'),
             'Keys: ' + json.dumps(result['keys'], ensure_ascii=False)]
    for item in result['datasets']:
        lines.append(f"Input {item['input_index']}: {json.dumps(item['input'], ensure_ascii=False)}")
        lines.append(f"  {item['records']} records; {item['eligible_keys']} unique nonempty keys; "
                     f"{item['duplicate_groups']} duplicate groups; "
                     f"{item['empty_key_records']} records with empty key components.")
        lines.append('  Issues: ' + (', '.join(item['issues']) or 'none'))
        for label in ('empty', 'duplicate'):
            for sample in item[label + '_examples']:
                lines.append('  ' + label + ': ' + json.dumps(sample, ensure_ascii=False, sort_keys=True))
            omitted = item['omitted_' + label + '_groups']
            if omitted:
                lines.append(f'  {omitted} more {label} groups omitted.')
        if 'overlap_with_first' in item:
            lines.append('  Eligible-key overlap with input 0: ' +
                         json.dumps(item['overlap_with_first'], sort_keys=True))
    lines.append(result['caution'])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', help='CSV files under the current working directory (1–8)')
    parser.add_argument('--key', action='append', required=True, help='key column; repeat for composite keys')
    parser.add_argument('--examples', type=int, default=5, help='maximum example groups and records per group (0–20)')
    parser.add_argument('--format', choices=('json', 'text'), default='json')
    args = parser.parse_args(argv)
    try:
        result = audit(args.files, args.key, args.examples)
        output = render_text(result) if args.format == 'text' else json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    except (InputError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(output)
    return 0 if result['passes'] else 1


if __name__ == '__main__':
    sys.exit(main())
