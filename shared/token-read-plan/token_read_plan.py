#!/usr/bin/env python3
"""Offline ZTO-first eth_call planning and exact CSV return decoding."""
import argparse
import csv
import io
import json
from pathlib import Path
import re
import sys

import abi_workbench as abi

TOKENS = (
    ('ZTO', '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'),
    ('IMD', '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7'),
)
FUNCTIONS = (('symbol', 'string'), ('decimals', 'uint8'), ('totalSupply', 'uint256'))
MAX_BYTES = 65_536
COLUMNS = ('chain_id', 'token_address', 'expected_symbol', 'field', 'raw_value',
           'display_value', 'block_number')


def make_plan(block):
    """Build six read-only requests pinned to an explicit Ethereum block number."""
    if not isinstance(block, str) or not re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]{0,63})', block):
        raise ValueError('block must be a canonical lowercase hex number; latest is not accepted')
    requests = []
    for _label, address in TOKENS:
        for name, _outtype in FUNCTIONS:
            data = '0x' + abi.keccak256((name + '()').encode('ascii'))[:4].hex()
            requests.append({'jsonrpc': '2.0', 'id': len(requests) + 1,
                             'method': 'eth_call', 'params': [{'to': address, 'data': data}, block]})
    return {'schema': 'token-read-plan/v1', 'chain_id': 1, 'block_number': block,
            'requests': requests}


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'non-finite JSON number: {value}')


def read_json(path):
    """Explicit inputs must resolve inside the caller's workspace, including symlinks."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(Path.cwd().resolve()):
        raise ValueError('input must resolve inside the current working directory')
    with resolved.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f'input exceeds {MAX_BYTES} bytes')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys,
                      parse_constant=reject_constant)


def exact_units(raw, decimals):
    """Integer arithmetic only, retaining every base unit without exponent notation."""
    if type(raw) is not int or raw < 0 or type(decimals) is not int or not 0 <= decimals <= 255:
        raise ValueError('invalid unsigned token quantity or decimals')
    if decimals == 0:
        return str(raw)
    digits = str(raw).rjust(decimals + 1, '0')
    fraction = digits[-decimals:].rstrip('0')
    return digits[:-decimals] + ('.' + fraction if fraction else '')


def decode_rows(plan, responses):
    if not isinstance(plan, dict):
        raise ValueError('plan must be an object')
    expected = make_plan(plan.get('block_number'))
    # JSON comparison distinguishes true from 1 and rejects modified destinations/methods.
    if json.dumps(plan, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('plan must exactly match the six ZTO-first read requests')
    if not isinstance(responses, list) or len(responses) != 6:
        raise ValueError('responses must be a JSON batch containing exactly six results')
    by_id = {}
    for response in responses:
        if not isinstance(response, dict) or set(response) != {'jsonrpc', 'id', 'result'}:
            raise ValueError('each response must contain only jsonrpc, id, result; RPC errors are rejected')
        ident = response['id']
        if type(ident) is not int or ident not in range(1, 7) or ident in by_id:
            raise ValueError('response IDs must be the distinct integers 1 through 6')
        raw = response['result']
        if response['jsonrpc'] != '2.0' or not isinstance(raw, str):
            raise ValueError('invalid JSON-RPC version or result type')
        if len(raw) > 8194 or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*', raw):
            raise ValueError('result must be even-length 0x hex of at most 4096 bytes')
        by_id[ident] = bytes.fromhex(raw[2:])
    rows = []
    for token_index, (label, address) in enumerate(TOKENS):
        values = {}
        for field_index, (name, outtype) in enumerate(FUNCTIONS):
            raw = by_id[token_index * 3 + field_index + 1]
            params = [{'name': name, 'type': outtype}]
            # Use Line 4's canonical-return contract, including surplus rejection.
            value = abi.decode_tuple(params, raw, strict=True)[0]['value']
            values[name] = value
        for name, _outtype in FUNCTIONS:
            value = values[name]
            display = exact_units(value, values['decimals']) if name == 'totalSupply' else str(value)
            rows.append({'chain_id': '1', 'token_address': address, 'expected_symbol': label,
                         'field': name, 'raw_value': str(value), 'display_value': display,
                         'block_number': plan['block_number']})
    return rows


def render_csv(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    plan_parser = commands.add_parser('plan', help='print unsigned read-only RPC requests; no network')
    plan_parser.add_argument('--block', required=True)
    decode_parser = commands.add_parser('decode', help='decode caller-supplied batch results to CSV')
    decode_parser.add_argument('--plan', required=True)
    decode_parser.add_argument('--responses', required=True)
    commands.add_parser('demo', help='decode the bundled public Ethereum observation offline')
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan':
            print(json.dumps(make_plan(args.block), indent=2))
            return 0
        if args.command == 'demo':
            directory = Path(__file__).resolve().parent
            plan, responses = read_json(directory / 'observed-plan.json'), read_json(directory / 'observed-responses.json')
        else:
            plan, responses = read_json(args.plan), read_json(args.responses)
        output = render_csv(decode_rows(plan, responses))
        print(output, end='')
        return 0
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
