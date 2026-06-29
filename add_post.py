"""
Add a post to the BPGS Updates site.

Usage:
    python add_post.py "Title" "One-line summary" path/to/file.html
    python add_post.py "Title" "One-line summary" path/to/file.html --author "Arvind Rajan"
    python add_post.py "Title" "One-line summary" path/to/file.html --category top-down
    python add_post.py "Title" "One-line summary" path/to/file.html --author "Arvind Rajan" --category bottom-up

Categories: top-down, bottom-up, strategies, research  (default: root posts/ folder)
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

    if len(args) != 3:
        print("Usage: python add_post.py \"Title\" \"Summary\" path/to/file.html [--author Name] [--category CATEGORY]")
        sys.exit(1)

    title, summary, filepath = args

    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    today = str(date.today())
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    dest_name = f"{name}_{today}{ext}"

    subfolder = os.path.join(POSTS_DIR, category) if category else POSTS_DIR
    os.makedirs(subfolder, exist_ok=True)
    dest_path = os.path.join(subfolder, dest_name)
    shutil.copy(filepath, dest_path)

    file_key = f"{category}/{dest_name}" if category else dest_name

    posts = []
    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, encoding="utf-8") as f:
            posts = json.load(f)

    entry = {"date": today, "title": title, "summary": summary, "file": file_key}
    if author:
        entry["author"] = author
    if category:
        entry["category"] = category

    posts.insert(0, entry)

    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    print(f"\nAdded: {title}")
    print(f"File:  {dest_path}")
    print(f"Category: {category or '(root)'}")
    print(f"\nNow push to GitHub:")
    print(f'  git add .')
    print(f'  git commit -m "post: {title}"')
    print(f'  git push')
    print(f"\nSite updates in ~30 seconds.")


if __name__ == "__main__":
    main()
