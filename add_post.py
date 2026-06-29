"""
Add a post to the BPGS Updates site.

Usage:
    python add_post.py "Title" "Summary" path/to/file.html
    python add_post.py "Title" "Summary" path/to/file.html --author "Arvind Rajan"
    python add_post.py "Title" "Summary" path/to/file.html --category strategies
    python add_post.py "Title" "Summary" path/to/file.html --category strategies --replace

Categories: top-down, bottom-up, strategies, research  (default: root posts/ folder)

--replace  Remove all previous posts.json entries and files sharing the same base
           filename (e.g. bpgs_blend_report), then add this one fresh. Use this
           to fix a bug in a report that was already pushed.
"""
import json
import os
import shutil
import sys
from datetime import date

POSTS_DIR = "posts"
POSTS_JSON = "posts.json"
VALID_CATEGORIES = {"top-down", "bottom-up", "strategies", "research"}


def main():
    args = sys.argv[1:]
    author = None
    category = None
    replace = False

    for flag in ("--author", "--category"):
        if flag in args:
            i = args.index(flag)
            val = args[i + 1]
            args = args[:i] + args[i + 2:]
            if flag == "--author":
                author = val
            else:
                if val not in VALID_CATEGORIES:
                    print(f"Warning: unknown category '{val}'. Valid: {', '.join(sorted(VALID_CATEGORIES))}")
                category = val

    if "--replace" in args:
        replace = True
        args = [a for a in args if a != "--replace"]

    if len(args) != 3:
        print('Usage: python add_post.py "Title" "Summary" path/to/file.html '
              '[--author Name] [--category CATEGORY] [--replace]')
        sys.exit(1)

    title, summary, filepath = args

    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    today = str(date.today())
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)           # e.g. "bpgs_blend_report", ".html"
    dest_name = f"{name}_{today}{ext}"

    subfolder = os.path.join(POSTS_DIR, category) if category else POSTS_DIR
    os.makedirs(subfolder, exist_ok=True)
    dest_path = os.path.join(subfolder, dest_name)

    posts = []
    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, encoding="utf-8") as f:
            posts = json.load(f)

    if replace:
        # Remove every existing entry whose file key ends with the same base name
        # (regardless of date stamp or category subfolder).
        removed = []
        kept = []
        for p in posts:
            file_key = p.get("file", "")
            old_file = os.path.basename(file_key)
            old_name, _ = os.path.splitext(old_file)
            # Match base: "bpgs_blend_report_2026-06-29" starts with "bpgs_blend_report"
            if old_name == name or old_name.startswith(name + "_"):
                removed.append(p)
                # Delete the physical file if it exists
                old_path = os.path.join(POSTS_DIR, file_key)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    print(f"Removed file:  {old_path}")
                else:
                    print(f"(file already gone: {old_path})")
            else:
                kept.append(p)
        if removed:
            print(f"Removed {len(removed)} old post(s) matching '{name}':")
            for p in removed:
                print(f"  [{p['date']}] {p['title']}")
        else:
            print(f"No existing posts matched '{name}' — adding fresh.")
        posts = kept

    shutil.copy(filepath, dest_path)

    file_key = f"{category}/{dest_name}" if category else dest_name
    entry = {"date": today, "title": title, "summary": summary, "file": file_key}
    if author:
        entry["author"] = author
    if category:
        entry["category"] = category

    posts.insert(0, entry)

    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    action = "Replaced" if replace else "Added"
    print(f"\n{action}: {title}")
    print(f"File:     {dest_path}")
    print(f"Category: {category or '(root)'}")
    print(f"\nNow push to GitHub:")
    print(f'  git add .')
    print(f'  git commit -m "{"fix" if replace else "post"}: {title}"')
    print(f'  git push')
    print(f"\nSite updates in ~30 seconds.")


if __name__ == "__main__":
    main()
