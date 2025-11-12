import json
import csv
from pathlib import Path
from typing import Any, List, Dict

# extract_tiktok_comments.py
# GitHub Copilot
# Reads all JSON files from ./data, extracts comment fields and writes a CSV.
# Fields extracted: cid, reply_id, reply_comment_total, create_time, digg_count, text, user.nickname, user.unique_id


DATA_DIR = Path("data")
OUTPUT_CSV = DATA_DIR / "comments_extracted.csv"
JSON_GLOB = "*.json"

def load_json_file(path: Path) -> Any:
    """Try to load a JSON file. If full-file JSON fails, try line-delimited JSON."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # try line-delimited JSON (one JSON object per line)
        objs = []
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except Exception:
                    # skip lines that are not valid JSON
                    continue
        return objs

def find_comments(obj: Any) -> List[Dict]:
    """
    Recursively search an object for lists of comment dicts.
    Heuristics: a list is treated as comments if its items are dicts and contain at least one common comment key.
    """
    comment_keys = {"cid", "create_time", "text", "digg_count", "user"}
    results: List[Dict] = []

    if isinstance(obj, dict):
        # direct 'comments' key
        if "comments" in obj and isinstance(obj["comments"], list):
            return [c for c in obj["comments"] if isinstance(c, dict)]
        # otherwise search values
        for v in obj.values():
            results.extend(find_comments(v))
        return results

    if isinstance(obj, list):
        if obj:
            if all(isinstance(it, dict) for it in obj):
                # if at least one key from comment_keys exists in the first element, accept the list
                first = obj[0]
                if any(k in first for k in comment_keys):
                    return [c for c in obj if isinstance(c, dict)]
            # otherwise inspect elements recursively
            for item in obj:
                results.extend(find_comments(item))
        return results

    return []

def extract_row(comment: Dict) -> List:
    """Extract desired fields from a comment dict into a flat list suitable for CSV."""
    user = comment.get("user") or {}
    cid = comment.get("cid")
    reply_id = comment.get("reply_id") or ""
    reply_comment_total = comment.get("reply_comment_total")
    create_time = comment.get("create_time") or ""
    digg_count = comment.get("digg_count")
    text = comment.get("text") or ""
    nickname = user.get("nickname") or ""
    unique_id = user.get("unique_id") or ""
    return [cid, reply_id, reply_comment_total, create_time, digg_count, text, nickname, unique_id]

def extract_comments():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_files = list(DATA_DIR.glob(JSON_GLOB))
    if not json_files:
        print(f"No JSON files found in {DATA_DIR.resolve()}")
        return

    rows = []
    for jf in json_files:
        try:
            data = load_json_file(jf)
        except Exception as e:
            print(f"Failed to read {jf}: {e}")
            continue
        comments = find_comments(data)
        if not comments:
            # If top-level data looks like a single comment dict, consider it
            if isinstance(data, dict) and any(k in data for k in ("cid", "comment_id", "text")):
                comments = [data]
        for c in comments:
            rows.append(extract_row(c))

    # Write CSV with header
    header = ["cid", "reply_id", "reply_comment_total", "create_time", "digg_count", "text", "user.nickname", "user.unique_id"]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in rows:
            # Ensure all values are strings to avoid csv errors
            writer.writerow(["" if v is None else v for v in r])

    print(f"Extracted {len(rows)} comments from {len(json_files)} files -> {OUTPUT_CSV}")

def main():
    extract_comments()


if __name__ == "__main__":
    main()