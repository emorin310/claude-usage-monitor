#!/usr/bin/env python3
"""
raindrop_to_todoist.py
Picks up Raindrop bookmarks tagged "magi", creates Todoist tasks,
then retags them "magi-done" to avoid reprocessing.
"""

import json
import urllib.request
import urllib.parse
import sys

RAINDROP_TOKEN = "e6718e73-4640-4bc2-b87c-3c67a7cbcbcc"
TODOIST_TOKEN  = "1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
MAGI_PROJECT_ID   = "6frMrX2WHM46rH4Q"
INCOMING_SECTION_ID = "6frMrXhWc628PFVQ"

RAINDROP_BASE = "https://api.raindrop.io/rest/v1"
TODOIST_BASE  = "https://api.todoist.com/api/v1"

EDU_KEYWORDS = ["tutorial", "guide", "how to", "howto", "learn", "course",
                "docs", "documentation", "github", "udemy", "coursera",
                "youtube", "youtube.com/watch", "arxiv", "paper", "research"]


def raindrop_get(path, params=None):
    url = f"{RAINDROP_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {RAINDROP_TOKEN}"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def raindrop_put(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{RAINDROP_BASE}{path}", data=data,
        headers={"Authorization": f"Bearer {RAINDROP_TOKEN}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def todoist_post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{TODOIST_BASE}{path}", data=data,
        headers={"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def classify(title, link, tags, excerpt):
    if "education" in tags:
        return "education", "📚 Learn:"
    if "review" in tags:
        return "review", "👀 Review:"
    text = f"{title} {link} {excerpt}".lower()
    if any(k in text for k in EDU_KEYWORDS):
        return "education", "📚 Learn:"
    return "review", "👀 Review:"


def main():
    # Fetch magi-tagged bookmarks (pre-encoded query)
    data = raindrop_get(
        "/raindrops/0",
        {"search": '[{"key":"tag","val":"magi"}]'}
    )

    items = data.get("items", [])
    if not items:
        print("No new magi-tagged bookmarks.")
        return

    print(f"Found {len(items)} bookmark(s)...")

    for item in items:
        rid   = item["_id"]
        title = item.get("title", "Untitled")
        link  = item.get("link", "")
        tags  = item.get("tags", [])
        excerpt = item.get("excerpt", "")

        label, prefix = classify(title, link, tags, excerpt)
        task_title = f"{prefix} {title}"
        description = f"🔗 {link}"
        if excerpt:
            description += f"\n\n{excerpt[:300]}"

        try:
            todoist_post("/tasks", {
                "content": task_title,
                "description": description,
                "project_id": MAGI_PROJECT_ID,
                "section_id": INCOMING_SECTION_ID,
                "labels": ["magi", label],
                "priority": 2
            })
            print(f"✅ Created task: {task_title}")

            # Retag: remove "magi", add "magi-done"
            new_tags = [t for t in tags if t != "magi"] + ["magi-done"]
            raindrop_put(f"/raindrop/{rid}", {"tags": new_tags})
            print(f"   ↳ Retagged raindrop {rid} → magi-done")

        except Exception as e:
            print(f"❌ Error processing '{title}': {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
