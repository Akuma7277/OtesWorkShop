import os
import struct
import array


def compile_po_to_mo(po_file_path: str, mo_file_path: str):
    """Compiles a .po file into a binary .mo catalog file without requiring external msgfmt tool."""
    messages = {}
    msgid = None
    msgstr = None
    in_msgid = False
    in_msgstr = False

    with open(po_file_path, "r", encoding="utf-8") as f:
        for line in f:
            raw_line = line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue

            if raw_line.startswith("msgid "):
                if msgid is not None and msgstr is not None:
                    messages[msgid] = msgstr
                msgid = raw_line[6:].strip()
                if msgid.startswith('"') and msgid.endswith('"'):
                    msgid = msgid[1:-1]
                msgstr = ""
                in_msgid = True
                in_msgstr = False
            elif raw_line.startswith("msgstr "):
                msgstr = raw_line[7:].strip()
                if msgstr.startswith('"') and msgstr.endswith('"'):
                    msgstr = msgstr[1:-1]
                in_msgid = False
                in_msgstr = True
            elif raw_line.startswith('"') and raw_line.endswith('"'):
                val = raw_line[1:-1]
                if in_msgid and msgid is not None:
                    msgid += val
                elif in_msgstr and msgstr is not None:
                    msgstr += val

        if msgid is not None and msgstr is not None:
            messages[msgid] = msgstr

    # Process escaped quotes and newlines
    processed_messages = {}
    for k, v in messages.items():
        k_proc = k.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        v_proc = v.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        processed_messages[k_proc] = v_proc

    keys = sorted(processed_messages.keys())
    offsets = []
    ids = b""
    strs = b""

    for k in keys:
        v = processed_messages[k]
        k_bytes = k.encode("utf-8")
        v_bytes = v.encode("utf-8")
        offsets.append((len(ids), len(k_bytes), len(strs), len(v_bytes)))
        ids += k_bytes + b"\x00"
        strs += v_bytes + b"\x00"

    keystart = 7 * 4 + len(keys) * 8 * 2
    valstart = keystart + len(ids)

    koffsets = []
    voffsets = []

    for klen, koff, vlen, voff in [(o[1], o[0], o[3], o[2]) for o in offsets]:
        koffsets.extend([klen, keystart + koff])
        voffsets.extend([vlen, valstart + voff])

    output = struct.pack(
        "IIIIIII",
        0x950412DE,
        0,
        len(keys),
        7 * 4,
        7 * 4 + len(keys) * 8,
        0,
        0,
    )

    output += array.array("i", koffsets).tobytes()
    output += array.array("i", voffsets).tobytes()
    output += ids
    output += strs

    os.makedirs(os.path.dirname(mo_file_path), exist_ok=True)
    with open(mo_file_path, "wb") as f:
        f.write(output)
    print(f"Compiled {po_file_path} -> {mo_file_path} ({len(keys)} strings)")


def compile_all_locales(locales_dir: str = "locales"):
    if not os.path.exists(locales_dir):
        print(f"Locales directory '{locales_dir}' does not exist.")
        return

    for lang in os.listdir(locales_dir):
        lang_dir = os.path.join(locales_dir, lang, "LC_MESSAGES")
        po_path = os.path.join(lang_dir, "bot.po")
        mo_path = os.path.join(lang_dir, "bot.mo")

        if os.path.exists(po_path):
            compile_po_to_mo(po_path, mo_path)


if __name__ == "__main__":
    compile_all_locales()
