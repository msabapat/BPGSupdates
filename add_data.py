"""
Add a file to the BPGS Data Room.

Usage:
    python add_data.py "Title" "Description" path/to/file.csv --owner mani
    python add_data.py "Title" "Description" path/to/file.csv --owner arvind
    python add_data.py "Title" "Description" path/to/file.csv --owner mani --replace

--replace  Remove all previous data_files.json entries sharing the same base
           filename, then add this one fresh.
"""
import json
import math
import os
import shutil
import sys
from datetime import date

DATA_DIR  = "data"
DATA_JSON = "data_files.json"
OWNERS = {
    "mani":   {"label": "Mani Sabapathi",  "folder": "mani"},
    "arvind": {"label": "Arvind Rajan",    "folder": "arvind"},
}


def main():
    args = sys.argv[1:]
    owner_key = None
    replace   = False

    if "--replace" in args:
        replace = True
        args = [a for a in args if a != "--replace"]

    if "--owner" in args:
        i = args.index("--owner")
        owner_key = args[i + 1].lower()
        args = args[:i] + args[i + 2:]

    if len(args) != 3:
        print('Usage: python add_data.py "Title" "Description" path/to/file.csv --owner mani|arvind [--replace]')
        sys.exit(1)

    title, description, filepath = args

    if owner_key not in OWNERS:
        print(f"Error: --owner must be 'mani' or 'arvind', got '{owner_key}'")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    owner_info = OWNERS[owner_key]
    today      = str(date.today())
    basename   = os.path.basename(filepath)
    stem, ext  = os.path.splitext(basename)
    dest_name  = f"{stem}_{today}{ext}"
    dest_folder = os.path.join(DATA_DIR, owner_info["folder"])
    dest_path   = os.path.join(dest_folder, dest_name)
    rel_path    = f"{owner_info['folder']}/{dest_name}"

    os.makedirs(dest_folder, exist_ok=True)

    size_kb = math.ceil(os.path.getsize(filepath) / 1024)

    # Load existing entries
    entries = []
    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, encoding="utf-8") as f:
            entries = json.load(f)

    if replace:
        # Remove old entries + files with the same base stem
        removed = []
        kept    = []
        for e in entries:
            e_stem = os.path.splitext(os.path.basename(e["file"]))[0]
            # strip trailing _YYYY-MM-DD from stem for comparison
            e_base = e_stem[:-11] if len(e_stem) > 11 and e_stem[-11] == "_" else e_stem
            if e["owner"] == owner_info["label"] and e_base == stem:
                old_path = os.path.join(DATA_DIR, e["file"])
                if os.path.exists(old_path):
                    os.remove(old_path)
                removed.append(e["file"])
            else:
                kept.append(e)
        entries = kept
        if removed:
            print(f"Replaced: {', '.join(removed)}")

    shutil.copy2(filepath, dest_path)

    new_entry = {
        "date":        today,
        "title":       title,
        "description": description,
        "file":        rel_path,
        "filename":    dest_name,
        "owner":       owner_info["label"],
        "size_kb":     size_kb,
    }
    entries.insert(0, new_entry)

    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Added: {title}")
    print(f"Owner: {owner_info['label']}")
    print(f"File:  {dest_path}  ({size_kb} KB)")
    print()
    print("Now push to GitHub:")
    print(f"  git add data/{owner_info['folder']}/{dest_name} data_files.json")
    print('  git commit -m "data: ' + title + '"')
    print("  git push")
    print()
    print("File will be downloadable at /data after ~30s.")


if __name__ == "__main__":
    main()
