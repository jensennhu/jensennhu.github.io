#!/usr/bin/env python3
"""
publish.py — Portfolio post publisher

Usage:
    python publish.py <post.md> [image1.png image2.jpg ...]

Copies the markdown file to _posts/ with a date prefix, copies images to
images/, updates the Table of Contents, then commits and pushes to GitHub.
"""

import os
import re
import sys
import shutil
import subprocess
from datetime import date

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(REPO_ROOT, "_posts")
IMAGES_DIR = os.path.join(REPO_ROOT, "images")
TOC_FILE = os.path.join(POSTS_DIR, "2099-09-09-Table_of_Contents.md")
SITE_URL = "https://jensennhu.github.io"


def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug


def extract_title(md_path):
    with open(md_path, "r") as f:
        content = f.read()
    match = re.search(r"^---\s*\n.*?^title:\s*(.+?)\s*$.*?^---", content, re.MULTILINE | re.DOTALL)
    if not match:
        print("Error: could not find 'title' in frontmatter of the markdown file.")
        sys.exit(1)
    return match.group(1).strip().strip("'\"")


def get_toc_categories():
    with open(TOC_FILE, "r") as f:
        content = f.read()
    # Find lines that are category headings (not frontmatter, not list items)
    categories = re.findall(r"^([A-Z][^\n-*]+?)\s*$", content, re.MULTILINE)
    # Filter out frontmatter values
    skip = {"layout: post", "title: Data Science Projects"}
    categories = [c for c in categories if c not in skip and not c.startswith("---")]
    return categories


def update_toc(title, post_url, category):
    with open(TOC_FILE, "r") as f:
        content = f.read()

    new_link = f"- [{title}]({post_url})"

    if category in content:
        # Insert after the category heading line
        content = re.sub(
            rf"(^{re.escape(category)}\s*\n)",
            rf"\1{new_link}\n",
            content,
            flags=re.MULTILINE,
        )
    else:
        # Append new category + link at end
        content = content.rstrip() + f"\n\n{category}\n{new_link}\n"

    with open(TOC_FILE, "w") as f:
        f.write(content)


def copy_images(image_paths):
    copied = []
    for img_path in image_paths:
        if not os.path.isfile(img_path):
            print(f"Warning: image not found, skipping: {img_path}")
            continue
        dest = os.path.join(IMAGES_DIR, os.path.basename(img_path))
        if os.path.exists(dest):
            print(f"Warning: image already exists in images/, skipping: {os.path.basename(img_path)}")
            continue
        shutil.copy2(img_path, dest)
        copied.append(dest)
        print(f"Copied image: {os.path.basename(img_path)} → images/")
    return copied


def git_commit_and_push(title, post_dest, image_dests):
    files_to_stage = [post_dest, TOC_FILE] + image_dests
    subprocess.run(["git", "add"] + files_to_stage, cwd=REPO_ROOT, check=True)
    commit_msg = f"Add post: {title}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
    result = subprocess.run(["git", "push"], cwd=REPO_ROOT)
    if result.returncode != 0:
        print("Warning: git push failed. Files are saved locally — push manually when ready.")
    else:
        print("Pushed to GitHub.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python publish.py <post.md> [image1.png image2.jpg ...]")
        sys.exit(1)

    md_path = sys.argv[1]
    image_paths = sys.argv[2:]

    if not os.path.isfile(md_path):
        print(f"Error: file not found: {md_path}")
        sys.exit(1)

    title = extract_title(md_path)
    slug = slugify(title)
    today = date.today()
    date_prefix = today.strftime("%Y-%m-%d")
    post_filename = f"{date_prefix}-{slug}.md"
    post_dest = os.path.join(POSTS_DIR, post_filename)

    if os.path.exists(post_dest):
        print(f"Error: post already exists at _posts/{post_filename}")
        sys.exit(1)

    # Copy post
    shutil.copy2(md_path, post_dest)
    print(f"Copied post: {post_filename} → _posts/")

    # Copy images
    image_dests = copy_images(image_paths)

    # Build post URL
    url_date = today.strftime("%Y/%m/%d")
    post_url = f"{SITE_URL}/{url_date}/{slug}/"
    print(f"Post URL: {post_url}")

    # Update Table of Contents
    categories = get_toc_categories()
    print("\nExisting ToC categories:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")
    print(f"  {len(categories) + 1}. New category")

    choice = input("\nAdd to which category? Enter number or name: ").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(categories):
            category = categories[idx]
        else:
            category = input("Enter new category name: ").strip()
    except ValueError:
        # They typed a name directly
        category = choice if choice in categories else choice

    update_toc(title, post_url, category)
    print(f"Updated Table of Contents under '{category}'.")

    # Commit and push
    git_commit_and_push(title, post_dest, image_dests)

    print(f"\nDone! Your post will be live at:\n  {post_url}")
    print("(Allow a minute or two for GitHub Actions to build.)")


if __name__ == "__main__":
    main()
