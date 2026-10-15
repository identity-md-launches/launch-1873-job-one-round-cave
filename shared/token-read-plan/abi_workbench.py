#!/usr/bin/env python3
"""Small offline Ethereum ABI function calldata encoder and return decoder."""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_ABI_BYTES = 1024 * 1024
MAX_ARRAY_ITEMS = 4096

MASK = (1 << 64) - 1
ROT = [0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14]
RC = [0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]

def rol(x, n):
    return x if n == 0 else ((x << n) | (x >> (64 - n))) & MASK

def keccak256(data):
    rate = 136
    padded = bytearray(data)
    padding = rate - len(padded) % rate
    padded.extend(b'\0' * padding)
    padded[-padding] = 0x01
    padded[-1] |= 0x80
    a = [0] * 25
    for off in range(0, len(padded), rate):
        block = padded[off:off + rate]
        for i in range(rate // 8):
            a[i] ^= int.from_bytes(block[i*8:i*8+8], 'little')
        for rc in RC:
            c = [a[x] ^ a[x+5] ^ a[x+10] ^ a[x+15] ^ a[x+20] for x in range(5)]
            d = [c[(x-1)%5] ^ rol(c[(x+1)%5], 1) for x in range(5)]
            for y in range(5):
                for x in range(5): a[x+5*y] ^= d[x]
            b = [0] * 25
            for y in range(5):
                for x in range(5): b[y + 5*((2*x+3*y)%5)] = rol(a[x+5*y], ROT[x+5*y])
            for y in range(5):
                for x in range(5): a[x+5*y] = b[x+5*y] ^ ((~b[(x+1)%5+5*y]) & b[(x+2)%5+5*y])
            a[0] ^= rc
    return b''.join(v.to_bytes(8, 'little') for v in a)[:32]

def canonical(param):
    if not isinstance(param, dict):
        raise ValueError('ABI parameter must be an object')
    t = param.get('type', '')
    if not isinstance(t, str):
        raise ValueError('ABI parameter type must be a string')
    if t.startswith('tuple'):
        raise ValueError('tuple types are not supported in this compact tool')
    array = re.fullmatch(r'(.+)\[([0-9]*)\]', t)
    if array:
        base, count = array.groups()
        # This step supports one-dimensional arrays of static scalar elements.
        if '[' in base or base in ('string', 'bytes'):
            raise ValueError(f'unsupported ABI type: {t!r}')
        base = canonical({'type': base})
        if count:
            if len(count) > 4 or count[0] == '0' or not 1 <= int(count) <= MAX_ARRAY_ITEMS:
                raise ValueError(f'array length must be 1..{MAX_ARRAY_ITEMS}')
        return base + '[' + count + ']'
    if not re.fullmatch(r'(address|bool|string|bytes|bytes(?:[1-9]|[12][0-9]|3[0-2])|u?int(?:8|16|24|32|40|48|56|64|72|80|88|96|104|112|120|128|136|144|152|160|168|176|184|192|200|208|216|224|232|240|248|256)?)', t):
        raise ValueError(f'unsupported ABI type: {t!r}')
    return {'uint': 'uint256', 'int': 'int256'}.get(t, t)

def array_parts(t):
    match = re.fullmatch(r'(.+)\[([0-9]*)\]', t)
    return (match.group(1), int(match.group(2)) if match.group(2) else None) if match else None

def dynamic(t):
    parts = array_parts(t)
    return t in ('string', 'bytes') or (parts is not None and parts[1] is None)

def head_words(t):
    parts = array_parts(t)
    return 1 if dynamic(t) else (parts[1] if parts else 1)

def word(n):
    if n < 0 or n >= 1 << 256: raise ValueError('ABI word is outside uint256 range')
    return n.to_bytes(32, 'big')

def encode_value(t, value):
    t = canonical({'type': t})
    parts = array_parts(t)
    if parts:
        base, count = parts
        if not isinstance(value, list): raise ValueError(f'{t} argument must be a JSON array')
        if len(value) > MAX_ARRAY_ITEMS: raise ValueError(f'array exceeds {MAX_ARRAY_ITEMS} items')
        if count is not None and len(value) != count: raise ValueError(f'{t} requires exactly {count} items')
        payload = b''.join(encode_value(base, item) for item in value)
        return (word(len(value)) if count is None else b'') + payload
    if t == 'address':
        if not isinstance(value, str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', value): raise ValueError('address must be 0x followed by 40 hex digits')
        return bytes.fromhex(value[2:]).rjust(32, b'\0')
    if t == 'bool':
        if not isinstance(value, bool): raise ValueError('bool argument must be true or false')
        return word(int(value))
    if t == 'string': raw = value.encode('utf-8') if isinstance(value, str) else (_ for _ in ()).throw(ValueError('string argument must be text'))
    elif t == 'bytes':
        if not isinstance(value, str) or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*', value): raise ValueError('bytes argument must be even-length 0x hex')
        raw = bytes.fromhex(value[2:])
    else:
        m = re.fullmatch(r'bytes([0-9]+)', t)
        if m:
            size = int(m.group(1))
            if not isinstance(value, str) or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*', value): raise ValueError(f'{t} argument must be 0x hex')
            raw = bytes.fromhex(value[2:])
            if len(raw) != size: raise ValueError(f'{t} requires exactly {size} bytes')
            return raw.ljust(32, b'\0')
        m = re.fullmatch(r'(u?int)([0-9]*)', t)
        if m:
            bits = int(m.group(2) or '256')
            if type(value) is int:
                n = value
            elif isinstance(value, str) and re.fullmatch(r'-?(?:0|[1-9][0-9]*)', value):
                n = int(value)
            else:
                raise ValueError(f'{t} argument must be an integer or decimal integer string')
            signed = m.group(1) == 'int'
            lo, hi = (-(1 << (bits-1)), (1 << (bits-1))-1) if signed else (0, (1 << bits)-1)
            if not lo <= n <= hi: raise ValueError(f'{t} value is out of range')
            return word(n % (1 << 256))
        raise ValueError(f'unsupported ABI type: {t}')
    return word(len(raw)) + raw + b'\0' * ((-len(raw)) % 32)

def encode_tuple(params, values):
    if len(params) != len(values): raise ValueError(f'expected {len(params)} arguments, received {len(values)}')
    types = [canonical(p) for p in params]
    head_size = 32 * sum(head_words(t) for t in types)
    head, tail = bytearray(), bytearray()
    for t, v in zip(types, values):
        if dynamic(t):
            encoded = encode_value(t, v)
            head.extend(word(head_size + len(tail))); tail.extend(encoded)
        else: head.extend(encode_value(t, v))
    return bytes(head + tail)

def decode_scalar(t, w):
    if t=='address':
        if any(w[:12]): raise ValueError('invalid high bits for address')
        val='0x'+w[-20:].hex()
    elif t=='bool':
        n=int.from_bytes(w,'big')
        if n not in (0,1): raise ValueError('invalid encoded bool')
        val=bool(n)
    elif t.startswith('bytes') and t!='bytes':
        n=int(t[5:])
        if any(w[n:]): raise ValueError(f'invalid padding for {t}')
        val='0x'+w[:n].hex()
    else:
        signed=t.startswith('int'); bits=int(re.search(r'[0-9]+$',t).group(0)) if re.search(r'[0-9]+$',t) else 256
        n=int.from_bytes(w,'big')
        if signed and n & (1 << 255): n-=1 << 256
        lo, hi = (-(1 << (bits-1)), (1 << (bits-1))-1) if signed else (0, (1 << bits)-1)
        if not lo <= n <= hi: raise ValueError(f'invalid high bits or sign extension for {t}')
        val=n
    return val

def decode_tuple(params, data, *, strict=False):
    """Decode supported outputs; strict mode requires their canonical encoding.

    Re-encoding also detects aliasing, gaps, reordered/overlapping tails and
    unused suffixes without maintaining a second set of offset rules.
    """
    if len(data) % 32: raise ValueError('return data must be whole 32-byte words')
    types = [canonical(p) for p in params]
    head_size = 32 * sum(head_words(t) for t in types)
    if len(data) < head_size: raise ValueError('return data is shorter than the ABI output head')
    out=[]; pos=0
    for i,(p,t) in enumerate(zip(params, types)):
        parts = array_parts(t)
        if dynamic(t):
            off=int.from_bytes(data[pos:pos+32],'big')
            if off < head_size or off%32 or off+32>len(data): raise ValueError('invalid dynamic return offset')
            n=int.from_bytes(data[off:off+32],'big')
            if parts:
                if n > MAX_ARRAY_ITEMS: raise ValueError(f'array exceeds {MAX_ARRAY_ITEMS} items')
                end = off + 32 + 32*n
                if end > len(data): raise ValueError('truncated dynamic return array')
                base = parts[0]
                val=[decode_scalar(base, data[j:j+32]) for j in range(off+32, end, 32)]
            else:
                raw=data[off+32:off+32+n]
                end = off + 32 + n
                padded_end = end + (-n) % 32
                if len(raw)!=n or padded_end > len(data): raise ValueError('truncated dynamic return value')
                if any(data[end:padded_end]): raise ValueError('nonzero dynamic return padding')
                val=raw.decode('utf-8') if t=='string' else '0x'+raw.hex()
        elif parts:
            base, count = parts
            val=[decode_scalar(base, data[j:j+32]) for j in range(pos, pos+32*count, 32)]
        else:
            val=decode_scalar(t, data[pos:pos+32])
        out.append({'name':p.get('name') or f'arg{i}', 'type':t, 'value':val})
        pos += 32 * head_words(t)
    if strict and encode_tuple(params, [item['value'] for item in out]) != data:
        raise ValueError('noncanonical return data: strict mode requires exact re-encoding')
    return out

def unique_object(pairs):
    """Do not silently accept contradictory duplicate JSON fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON field: {key!r}')
        result[key] = value
    return result

def validate_abi(abi):
    if not isinstance(abi, list):
        raise ValueError('ABI must be a JSON array of entry objects')
    for i, entry in enumerate(abi):
        if not isinstance(entry, dict):
            raise ValueError(f'ABI entry {i} must be an object')
        kind = entry.get('type')
        if kind not in ('function', 'constructor', 'event', 'error', 'fallback', 'receive'):
            raise ValueError(f'ABI entry {i} has an invalid entry type')
        if kind in ('function', 'event', 'error'):
            name = entry.get('name')
            if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', name):
                raise ValueError(f'ABI entry {i} must have a valid name')
        for field in ('inputs', 'outputs'):
            params = entry.get(field, [])
            if not isinstance(params, list):
                raise ValueError(f'ABI entry {i} {field} must be an array')
            for j, param in enumerate(params):
                if not isinstance(param, dict) or not isinstance(param.get('type'), str) or not param['type']:
                    raise ValueError(f'ABI entry {i} {field}[{j}] must have a nonempty string type')
                if 'name' in param and not isinstance(param['name'], str):
                    raise ValueError(f'ABI entry {i} {field}[{j}] name must be a string')
    return abi

def load_function(path, name):
    # Explicit ABI inputs stay under the workspace from which the CLI is run.
    root = Path.cwd().resolve()
    source = Path(path).resolve()
    if not source.is_relative_to(root):
        raise ValueError('ABI path must stay inside the current workspace')
    with source.open('rb') as f:
        raw = f.read(MAX_ABI_BYTES + 1)
    if len(raw) > MAX_ABI_BYTES:
        raise ValueError('ABI file exceeds the 1 MiB input limit')
    try:
        abi = validate_abi(json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object))
    except RecursionError as e:
        raise ValueError('ABI JSON nesting is too deep') from e
    matches=[x for x in abi if x.get('type')=='function' and x.get('name')==name]
    if len(matches)!=1: raise ValueError(f'expected exactly one ABI function named {name!r}; found {len(matches)}')
    fn=matches[0]
    for param in fn.get('outputs', []):
        canonical(param)
    sig=fn['name']+'('+','.join(canonical(p) for p in fn.get('inputs',[]))+')'
    return fn,sig

def demo():
    sig='transfer(address,uint256)'; args=['0xd782bdea4ef02a0bd391eb9089470c8080f0a68e',123]
    calldata='0x'+keccak256(sig.encode())[:4].hex()+encode_tuple([{'type':'address'},{'type':'uint256'}],args).hex()
    print(json.dumps({'signature':sig,'selector':'0x'+keccak256(sig.encode())[:4].hex(),'arguments':args,'calldata':calldata},indent=2))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--demo',action='store_true',help='encode a built-in offline transfer example')
    sub=ap.add_subparsers(dest='command')
    enc=sub.add_parser('encode'); enc.add_argument('--abi',required=True); enc.add_argument('--function',required=True); enc.add_argument('--args',required=True,help='JSON array of arguments')
    dec=sub.add_parser('decode'); dec.add_argument('--abi',required=True); dec.add_argument('--function',required=True); dec.add_argument('--data',required=True,help='0x-prefixed return bytes')
    dec.add_argument('--strict', action='store_true', help='require canonical return bytes: no gaps, shared/reordered tails or surplus words')
    a=ap.parse_args()
    try:
        if a.demo: demo(); return 0
        if a.command=='encode':
            fn,sig=load_function(a.abi,a.function); vals=json.loads(a.args)
            if not isinstance(vals,list): raise ValueError('--args must be a JSON array')
            selector=keccak256(sig.encode())[:4]
            payload=encode_tuple(fn.get('inputs',[]),vals)
            print(json.dumps({'signature':sig,'selector':'0x'+selector.hex(),'calldata':'0x'+(selector+payload).hex()},indent=2)); return 0
        if a.command=='decode':
            fn,sig=load_function(a.abi,a.function)
            if not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*',a.data): raise ValueError('--data must be even-length 0x hex')
            print(json.dumps({'signature':sig,'outputs':decode_tuple(fn.get('outputs',[]),bytes.fromhex(a.data[2:]),strict=a.strict)},indent=2)); return 0
        ap.print_help(); return 2
    except (ValueError, KeyError, OSError) as e:
        print(f'error: {e}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
