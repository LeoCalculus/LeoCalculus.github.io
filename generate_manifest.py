#!/usr/bin/env python3
"""
Auto-generate wiki_manifest.json by scanning the Wiki/ directory.

Usage:
    python generate_manifest.py

Structure:
    - wiki_sections.json defines sections and which folders belong to each
    - Each subfolder in Wiki/ becomes a category within its assigned section
    - Unassigned folders go into an "Other" section
    - Article metadata is extracted from YAML frontmatter or inferred

Supported frontmatter (optional, at the top of your .md file):
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
SECTIONS_FILE = "wiki_sections.json"


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
    body = content[match.end():]

    tags_inline = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.MULTILINE)
    if tags_inline:
        meta["tags"] = [
            t.strip().strip("\"'") for t in tags_inline.group(1).split(",") if t.strip()
        ]
    else:
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


def scan_category(category_dir):
    """Scan a single category folder and return its data."""
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

    return {
        "id": cat_id,
        "name": cat_name,
        "articles": articles,
    }


def load_sections_config(script_dir):
    """Load wiki_sections.json. Returns list of section defs or None."""
    sections_path = script_dir / SECTIONS_FILE
    if not sections_path.exists():
        return None
    try:
        return json.loads(sections_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: Could not parse {SECTIONS_FILE}: {e}")
        return None


def generate():
    script_dir = Path(__file__).parent
    wiki_dir = script_dir / WIKI_DIR

    if not wiki_dir.exists():
        print(f"Error: '{WIKI_DIR}/' directory not found. Create it and add category folders.")
        return

    all_categories = {}
    for category_dir in sorted(wiki_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        cat = scan_category(category_dir)
        all_categories[category_dir.name] = cat

    sections_config = load_sections_config(script_dir)

    if sections_config:
        sections = []
        assigned_folders = set()

        for sec_def in sections_config:
            sec_name = sec_def["name"]
            sec_id = slugify(sec_name)
            sec_categories = []

            for folder_name in sec_def.get("folders", []):
                if folder_name in all_categories:
                    sec_categories.append(all_categories[folder_name])
                    assigned_folders.add(folder_name)

            sections.append({
                "id": sec_id,
                "name": sec_name,
                "categories": sec_categories,
            })

        unassigned = [
            cat for name, cat in sorted(all_categories.items())
            if name not in assigned_folders
        ]
        if unassigned:
            sections.append({
                "id": "other",
                "name": "Other",
                "categories": unassigned,
            })

        manifest = {"sections": sections}
    else:
        manifest = {
            "sections": [{
                "id": "all",
                "name": "All",
                "categories": list(all_categories.values()),
            }]
        }

    manifest_path = script_dir / MANIFEST_FILE
    manifest_path.write_text(
        json.dumps(manifest, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total = sum(
        len(a)
        for s in manifest["sections"]
        for c in s["categories"]
        for a in [c["articles"]]
    )
    print(f"Generated {MANIFEST_FILE}: {len(manifest['sections'])} sections, {total} articles")
    for sec in manifest["sections"]:
        cat_count = len(sec["categories"])
        print(f"\n  [{sec['name']}] ({cat_count} categories)")
        for cat in sec["categories"]:
            print(f"    {cat['name']}: {len(cat['articles'])} articles")
            for a in cat["articles"]:
                tag_str = f"  [{', '.join(a['tags'])}]" if a.get("tags") else ""
                print(f"      - {a['title']}{tag_str}")


if __name__ == "__main__":
    generate()
