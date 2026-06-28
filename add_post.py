"""
Add a post to the BPGS Updates site.

Usage:
    python add_post.py "Title" "One-line summary" path/to/file.html
    python add_post.py "Title" "One-line summary" path/to/file.html --author Arvind
"""
import json
import os
import shutil
import sys
from datetime import date

POSTS_DIR = "posts"
POSTS_JSON = "posts.json"


def main():
    args = sys.argv[1:]
    author = None
    if "--author" in args:
        i = args.index("--author")
        author = args[i + 1]
        args = args[:i] + args[i + 2:]

    if len(args) != 3:
        print("Usage: python add_post.py \"Title\" \"Summary\" path/to/file.html [--author Name]")
        sys.exit(1)

    title, summary, filepath = args

    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    today = str(date.today())
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    dest_name = f"{name}_{today}{ext}"
    dest_path = os.path.join(POSTS_DIR, dest_name)

    os.makedirs(POSTS_DIR, exist_ok=True)
    shutil.copy(filepath, dest_path)

    posts = []
    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, encoding="utf-8") as f:
            posts = json.load(f)

    entry = {"date": today, "title": title, "summary": summary, "file": dest_name}
    if author:
        entry["author"] = author

    posts.insert(0, entry)

    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    print(f"\nAdded: {title}")
    print(f"File:  {dest_path}")
    print(f"\nNow push to GitHub:")
    print(f'  git add .')
    print(f'  git commit -m "post: {title}"')
    print(f'  git push')
    print(f"\nSite updates in ~30 seconds.")


if __name__ == "__main__":
    main()
