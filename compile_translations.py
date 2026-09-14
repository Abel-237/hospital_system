import os
import struct
from pathlib import Path

def parse_po(content):
    lines = content.splitlines()
    entries = {}
    current_msgid = None
    current_msgstr = None
    mode = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('msgid '):
            if current_msgid is not None and current_msgstr is not None:
                entries[current_msgid] = current_msgstr
            raw = line[6:].strip()
            current_msgid = eval(raw)
            current_msgstr = ""
            mode = 'msgid'
        elif line.startswith('msgstr '):
            raw = line[7:].strip()
            current_msgstr = eval(raw)
            mode = 'msgstr'
        elif line.startswith('"'):
            val = eval(line)
            if mode == 'msgid':
                current_msgid += val
            elif mode == 'msgstr':
                current_msgstr += val

    if current_msgid is not None and current_msgstr is not None:
        entries[current_msgid] = current_msgstr

    return entries

def generate_mo(entries, out_path):
    if "" not in entries or "Content-Type" not in entries[""]:
        entries[""] = "Content-Type: text/plain; charset=UTF-8\nMIME-Version: 1.0\nContent-Transfer-Encoding: 8bit\nPlural-Forms: nplurals=2; plural=(n != 1);\n"
    keys = sorted(entries.keys())
    num_strings = len(keys)

    magic = 0x950412de
    orig_table_offset = 7 * 4
    trans_table_offset = orig_table_offset + num_strings * 8
    data_start = trans_table_offset + num_strings * 8

    orig_data = bytearray()
    orig_index = []
    current_offset = data_start
    for k in keys:
        b = k.encode('utf-8') + b'\x00'
        orig_index.append((len(b) - 1, current_offset))
        orig_data.extend(b)
        current_offset += len(b)

    trans_data = bytearray()
    trans_index = []
    for k in keys:
        b = entries[k].encode('utf-8') + b'\x00'
        trans_index.append((len(b) - 1, current_offset))
        trans_data.extend(b)
        current_offset += len(b)

    header = struct.pack('Iiiiiii', magic, 0, num_strings, orig_table_offset, trans_table_offset, 0, 0)

    orig_table = bytearray()
    for length, offset in orig_index:
        orig_table.extend(struct.pack('ii', length, offset))

    trans_table = bytearray()
    for length, offset in trans_index:
        trans_table.extend(struct.pack('ii', length, offset))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(header)
        f.write(orig_table)
        f.write(trans_table)
        f.write(orig_data)
        f.write(trans_data)

def compile_all(base_dir=None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent
    locale_dir = base_dir / 'locale'
    
    for lang_dir in locale_dir.iterdir():
        if not lang_dir.is_dir():
            continue
        lc_messages = lang_dir / 'LC_MESSAGES'
        po_file = lc_messages / 'django.po'
        if po_file.exists():
            mo_file = lc_messages / 'django.mo'
            with open(po_file, 'r', encoding='utf-8') as f:
                entries = parse_po(f.read())
            generate_mo(entries, str(mo_file))
            print(f"[OK] Compiled {len(entries)} strings for '{lang_dir.name}' -> {mo_file}")

if __name__ == '__main__':
    compile_all()
