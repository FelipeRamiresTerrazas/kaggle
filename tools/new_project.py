"""Scaffold a Kaggle project folder that can be pushed to Kaggle as a notebook.

Usage (from the repo root):
    python tools/new_project.py competition titanic
    python tools/new_project.py dataset mlg-ulb/creditcardfraud --title "Credit Card Fraud EDA"

Creates:
    competitions/<slug>/  or  datasets/<slug>/
        notebook.ipynb         starter notebook (works locally and on Kaggle)
        kernel-metadata.json   tells `kaggle kernels push` where to publish it
        data/                  downloaded data (git-ignored)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USER = os.environ.get("KAGGLE_USERNAME", "felipeterrazas")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def kaggle(*args: str) -> int:
    """Run the Kaggle CLI with the same Python interpreter."""
    cmd = [sys.executable, "-m", "kaggle", *args]
    print("$ kaggle " + " ".join(args))
    return subprocess.call(cmd)


def notebook(title: str, source_slug: str, source_url: str) -> dict:
    def md(text: str) -> dict:
        return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

    def code(text: str) -> dict:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": text.splitlines(keepends=True),
        }

    paths = f'''from pathlib import Path

import numpy as np
import pandas as pd

# Same notebook runs locally (VS Code) and on Kaggle.
ON_KAGGLE = Path("/kaggle/input").exists()
SOURCE = "{source_slug}"

if ON_KAGGLE:
    DATA_DIR = next(p for p in Path("/kaggle/input").rglob(SOURCE) if p.is_dir())
    OUT_DIR = Path("/kaggle/working")
else:
    DATA_DIR = Path("data")
    OUT_DIR = Path("submissions")
    OUT_DIR.mkdir(exist_ok=True)

sorted(p.name for p in DATA_DIR.iterdir())'''

    return {
        "cells": [
            md(f"# {title}\n\nSource: {source_url}"),
            code(paths),
            md("## Load data"),
            code("# df = pd.read_csv(DATA_DIR / \"train.csv\")\n# df.head()"),
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["competition", "dataset"])
    parser.add_argument("ref", help="competition slug (titanic) or dataset ref (owner/slug)")
    parser.add_argument("--title", help="notebook title on Kaggle (default: derived from the slug)")
    parser.add_argument("--user", default=DEFAULT_USER, help=f"Kaggle username (default: {DEFAULT_USER})")
    parser.add_argument("--public", action="store_true", help="publish the notebook as public (default: private)")
    parser.add_argument("--gpu", action="store_true", help="enable a GPU on Kaggle")
    parser.add_argument("--no-download", action="store_true", help="skip downloading the data")
    args = parser.parse_args()

    if args.kind == "dataset" and "/" not in args.ref:
        parser.error("dataset ref must look like owner/slug")

    slug = args.ref.split("/")[-1]
    title = args.title or slug.replace("-", " ").title()
    folder = REPO_ROOT / ("competitions" if args.kind == "competition" else "datasets") / slug
    data_dir = folder / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    url = (
        f"https://www.kaggle.com/competitions/{slug}"
        if args.kind == "competition"
        else f"https://www.kaggle.com/datasets/{args.ref}"
    )

    metadata_path = folder / "kernel-metadata.json"
    if not metadata_path.exists():
        metadata = {
            "id": f"{args.user}/{slugify(title)}",
            "title": title,
            "code_file": "notebook.ipynb",
            "language": "python",
            "kernel_type": "notebook",
            "is_private": not args.public,
            "enable_gpu": args.gpu,
            "enable_tpu": False,
            "enable_internet": args.kind == "dataset",  # competitions often require internet off
            "dataset_sources": [args.ref] if args.kind == "dataset" else [],
            "competition_sources": [slug] if args.kind == "competition" else [],
            "kernel_sources": [],
            "model_sources": [],
        }
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        print(f"created {metadata_path.relative_to(REPO_ROOT)}")

    nb_path = folder / "notebook.ipynb"
    if not nb_path.exists():
        nb_path.write_text(json.dumps(notebook(title, slug, url), indent=1) + "\n", encoding="utf-8")
        print(f"created {nb_path.relative_to(REPO_ROOT)}")

    if not args.no_download:
        if args.kind == "competition":
            code = kaggle("competitions", "download", "-c", slug, "-p", str(data_dir))
        else:
            code = kaggle("datasets", "download", args.ref, "-p", str(data_dir))
        if code != 0:
            print(
                f"\nDownload failed. For competitions, accept the rules first at {url}/rules\n"
                f"Then retry with the same command, or download into {data_dir.relative_to(REPO_ROOT)} manually."
            )
            sys.exit(code)
        for zip_path in data_dir.glob("*.zip"):
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(data_dir)
            zip_path.unlink()
        print(f"data ready in {data_dir.relative_to(REPO_ROOT)}")

    print(f"\nNext: open {nb_path.relative_to(REPO_ROOT)} in VS Code. Push with:\n"
          f"    kaggle kernels push -p {folder.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
