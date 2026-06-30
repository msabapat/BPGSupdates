import json
import os
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)
POSTS_DIR     = os.path.join(os.path.dirname(__file__), "posts")
POSTS_JSON    = os.path.join(os.path.dirname(__file__), "posts.json")
DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
DATA_JSON     = os.path.join(os.path.dirname(__file__), "data_files.json")


def load_posts():
    if not os.path.exists(POSTS_JSON):
        return []
    with open(POSTS_JSON, encoding="utf-8") as f:
        return json.load(f)


def load_data_files():
    if not os.path.exists(DATA_JSON):
        return []
    with open(DATA_JSON, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)


@app.route("/data")
def data_room():
    files = load_data_files()
    return render_template("data.html", files=files)


@app.route("/posts/<path:filename>")
def view_post(filename):
    if not os.path.exists(os.path.join(POSTS_DIR, filename)):
        abort(404)
    return send_from_directory(POSTS_DIR, filename)


@app.route("/data/download/<path:filename>")
def download_file(filename):
    full = os.path.join(DATA_DIR, filename)
    if not os.path.exists(full):
        abort(404)
    directory = os.path.dirname(full)
    basename  = os.path.basename(full)
    return send_from_directory(directory, basename, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
