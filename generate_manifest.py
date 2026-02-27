#!/usr/bin/env python3
"""
Auto-generate wiki_manifest.json by scanning the Wiki/ directory.

Usage:
    python generate_manifest.py

How it works:
    - Each subfolder in Wiki/ becomes a category (e.g. Wiki/STM32/ → "STM32")
    - Each .md file in a category folder becomes an article
    - Article title is extracted from: frontmatter 'title' → first '# Heading' → filename
    - Tags and date can be set via YAML frontmatter in the .md file
    - If no date is in frontmatter, the file's last-modified date is used

Supported frontmatter format (optional, at the top of your .md file):
    ---
    title: My Custom Title
    date: 2026-02-26
    tags: [embedded, arm, gpio]
    ---
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

WIKI_DIR = "Wiki"
MANIFEST_FILE = "wiki_manifest.json"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def parse_frontmatter(content):
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if not match:
        return meta, content

    fm = match.group(1)
    body = content[match.end() :]

    # tags: [a, b, c]  or  tags: a, b, c
    tags_inline = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.MULTILINE)
    if tags_inline:
        meta["tags"] = [
            t.strip().strip("\"'") for t in tags_inline.group(1).split(",") if t.strip()
        ]
    else:
        # tags:\n  - a\n  - b
        tags_block = re.search(
            r"^tags:\s*\n((?:\s*-\s+.*\n?)+)", fm, re.MULTILINE
        )
        if tags_block:
            meta["tags"] = [
                re.sub(r"^\s*-\s*", "", line).strip().strip("\"'")
                for line in tags_block.group(1).strip().split("\n")
                if line.strip()
            ]

    date_match = re.search(r"^date:\s*(.+)$", fm, re.MULTILINE)
    if date_match:
        meta["date"] = date_match.group(1).strip().strip("\"'")

    title_match = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
    if title_match:
        meta["title"] = title_match.group(1).strip().strip("\"'")

    return meta, body


def extract_title_from_heading(content):
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def get_file_date(filepath):
    mtime = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def generate():
    script_dir = Path(__file__).parent
    wiki_dir = script_dir / WIKI_DIR

    if not wiki_dir.exists():
        print(f"Error: '{WIKI_DIR}/' directory not found. Create it and add category folders.")
        return

    categories = []

    for category_dir in sorted(wiki_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        cat_name = category_dir.name
        cat_id = slugify(cat_name)
        articles = []

        for md_file in sorted(category_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)

            title = (
                meta.get("title")
                or extract_title_from_heading(body)
                or md_file.stem
            )
            article_id = f"{cat_id}-{slugify(md_file.stem)}"
            date = meta.get("date") or get_file_date(md_file)
            tags = meta.get("tags", [])
            path = f"{WIKI_DIR}/{cat_name}/{md_file.name}"

            article = {
                "id": article_id,
                "title": title,
                "path": path,
                "date": date,
            }
            if tags:
                article["tags"] = tags

            articles.append(article)

        categories.append({
            "id": cat_id,
            "name": cat_name,
            "articles": articles,
        })

    manifest = {"categories": categories}

    manifest_path = script_dir / MANIFEST_FILE
    manifest_path.write_text(
        json.dumps(manifest, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total = sum(len(c["articles"]) for c in categories)
    print(f"Generated {MANIFEST_FILE}: {len(categories)} categories, {total} articles")
    for cat in categories:
        print(f"  {cat['name']}: {len(cat['articles'])} articles")
        for a in cat["articles"]:
            tag_str = f"  [{', '.join(a['tags'])}]" if a.get("tags") else ""
            print(f"    - {a['title']}{tag_str}")


if __name__ == "__main__":
    generate()
