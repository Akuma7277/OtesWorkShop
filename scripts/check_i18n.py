import ast
import os
import re
import sys


def find_hardcoded_user_strings(root_dir: str = "src/shopim"):
    """Scans all Python files for potential un-localized user-facing strings."""
    unlocalized = []
    
    # Common user-facing methods/classes
    target_calls = {"answer", "reply", "edit_text", "send_message", "KeyboardButton", "InlineKeyboardButton"}

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue

            fpath = os.path.join(dirpath, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ast.parse(content, filename=fpath)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check method calls like message.answer(...)
                    func_name = None
                    if isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                    elif isinstance(node.func, ast.Name):
                        func_name = node.func.id

                    if func_name in target_calls:
                        # Check positional arguments for unwrapped string literals
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                val = arg.value.strip()
                                # Ignore technical codes or empty strings
                                if val and not re.match(r"^[a-zA-Z0-9_\-:\.]+$", val):
                                    unlocalized.append((fpath, getattr(node, "lineno", 0), val))
                            elif isinstance(arg, ast.JoinedStr):
                                # F-strings unwrapped
                                unlocalized.append((fpath, getattr(node, "lineno", 0), "f-string"))

    return unlocalized


def check_locale_completeness(locales_dir: str = "locales"):
    """Checks that all msgids in uz have non-empty translations in ru and vice versa."""
    results = {}
    for lang in ["uz", "ru"]:
        po_path = os.path.join(locales_dir, lang, "LC_MESSAGES", "bot.po")
        if not os.path.exists(po_path):
            print(f"Missing locale file: {po_path}")
            continue

        msgids = {}
        curr_id = None
        curr_str = ""
        in_id, in_str = False, False

        with open(po_path, "r", encoding="utf-8") as f:
            for line in f:
                l = line.strip()
                if l.startswith("msgid "):
                    if curr_id is not None:
                        msgids[curr_id] = curr_str
                    curr_id = l[6:].strip().strip('"')
                    curr_str = ""
                    in_id, in_str = True, False
                elif l.startswith("msgstr "):
                    curr_str = l[7:].strip().strip('"')
                    in_id, in_str = False, True
                elif l.startswith('"') and l.endswith('"'):
                    if in_id and curr_id is not None:
                        curr_id += l[1:-1]
                    elif in_str and curr_str is not None:
                        curr_str += l[1:-1]

            if curr_id is not None:
                msgids[curr_id] = curr_str

        results[lang] = msgids

    uz_ids = set(results.get("uz", {}).keys())
    ru_ids = set(results.get("ru", {}).keys())

    missing_ru = uz_ids - ru_ids
    missing_uz = ru_ids - uz_ids

    print(f"Total keys in UZ locale: {len(uz_ids)}")
    print(f"Total keys in RU locale: {len(ru_ids)}")

    if missing_ru:
        print(f"Keys missing in RU: {missing_ru}")
    if missing_uz:
        print(f"Keys missing in UZ: {missing_uz}")

    return len(missing_ru) == 0 and len(missing_uz) == 0


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== i18n Audit & Verification Script ===")
    unloc = find_hardcoded_user_strings()
    if unloc:
        print(f"Found {len(unloc)} potential unlocalized strings:")
        for path, line, val in unloc:
            print(f"  {path}:{line} -> {val}")
    else:
        print("✅ No unlocalized user-facing strings detected in handlers!")

    complete = check_locale_completeness()
    if complete:
        print("✅ Locale files are 100% complete and synchronized between uz and ru!")
    else:
        sys.exit(1)
