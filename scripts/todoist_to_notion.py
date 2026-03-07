#!/usr/bin/env python3
"""
todoist_to_notion.py
Import Todoist tasks into Notion Task List database
"""

import json
import urllib.request
import sys

NOTION_TOKEN = "YOUR_NOTION_TOKEN_HERE"  # Replace with actual token from environment
NOTION_DB_ID = "38e23c66-8d68-407c-9067-e1b7e9652f4b"
NOTION_VERSION = "2022-06-28"

def notion_create_page(task):
    """Create a Notion page from a Todoist task"""
    
    # Map Todoist priority (1-4, where 1=urgent) to Notion P1-P4
    priority_map = {1: "P4", 2: "P3", 3: "P2", 4: "P1"}
    priority = priority_map.get(task.get("priority", 1), "P4")
    
    # Extract labels
    labels = [{"name": label} for label in task.get("labels", [])]
    
    # Build the page properties
    properties = {
        "Name": {
            "title": [{"text": {"content": task["content"][:2000]}}]  # Notion limit
        },
        "Status": {
            "select": {"name": "To Do"}
        },
        "Priority": {
            "select": {"name": priority}
        }
    }
    
    # Add due date if present
    if task.get("due") and task["due"].get("date"):
        properties["Due Date"] = {
            "date": {"start": task["due"]["date"][:10]}  # YYYY-MM-DD only
        }
    
    # Add labels if present
    if labels:
        properties["Labels"] = {"multi_select": labels}
    
    # Add description if present
    if task.get("description"):
        properties["Description"] = {
            "rich_text": [{"text": {"content": task["description"][:2000]}}]
        }
    
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": properties
    }
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=data,
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as r:
            result = json.load(r)
            return result.get("id")
    except Exception as e:
        print(f"Error creating task '{task['content']}': {e}", file=sys.stderr, flush=True)
        return None


def main():
    # Load tasks from temp file
    with open("/tmp/todoist-export.json") as f:
        tasks = json.load(f)
    
    print(f"Importing {len(tasks)} tasks from Todoist to Notion...", flush=True)
    
    imported = 0
    for task in tasks:
        task_id = notion_create_page(task)
        if task_id:
            print(f"✅ {task['content'][:60]}", flush=True)
            imported += 1
        else:
            print(f"❌ Failed: {task['content'][:60]}", flush=True)
    
    print(f"\nDone! Imported {imported}/{len(tasks)} tasks", flush=True)


if __name__ == "__main__":
    main()
