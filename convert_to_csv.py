#!/usr/bin/env python3
"""
Convert HackerNewsRemovals README.md and archives to CSV format.
Parses the markdown list of removed stories and outputs as CSV.
"""

import re
import csv
import sys
from pathlib import Path

def parse_markdown_file(filepath):
    """Parse a markdown file and extract story data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    stories = []
    current_date = None

    # Pattern for date headers: #### **Day, Month DD, YYYY**
    date_pattern = re.compile(r'####\s*\*\*(\w+,\s+\w+\s+\d+,\s+\d+)\*\*')

    # Pattern for story entries (handles both URL formats):
    # * [ID](stats_url or hn_url) #RANK POINTS points COMMENTS comments -> [TITLE](URL)
    story_pattern = re.compile(
        r'\*\s*\[(\d+)\]\(https://(?:news\.social-protocols\.org/stats\?id=|news\.ycombinator\.com/item\?id=)\d+\)\s*'
        r'#(\d+)\s*'
        r'(\d+)\s*points?\s*'
        r'(\d+)\s*comments?\s*'
        r'->\s*\[([^\]]*)\]\(([^)]+)\)'
    )

    for line in content.split('\n'):
        # Check for date header
        date_match = date_pattern.search(line)
        if date_match:
            current_date = date_match.group(1)
            continue

        # Check for story entry
        story_match = story_pattern.search(line)
        if story_match and current_date:
            story_id, rank, points, comments, title, url = story_match.groups()
            stories.append({
                'id': story_id,
                'date': current_date,
                'rank': rank,
                'points': points,
                'comments': comments,
                'title': title,
                'url': url
            })

    return stories

def write_csv(stories, output_path):
    """Write stories to CSV file."""
    fieldnames = ['id', 'date', 'rank', 'points', 'comments', 'title', 'url']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stories)

    return len(stories)

def main():
    script_dir = Path(__file__).parent
    readme_path = script_dir / 'README.md'
    old_dir = script_dir / 'OLD'
    output_path = script_dir / 'removed_stories.csv'

    all_stories = []

    # Parse archive files first (oldest to newest)
    if old_dir.exists():
        archive_files = sorted(old_dir.glob('ARCHIVE-*.md'))
        for archive_file in archive_files:
            print(f"Parsing {archive_file.name}...")
            stories = parse_markdown_file(archive_file)
            all_stories.extend(stories)
            print(f"  Found {len(stories)} stories")

    # Parse current README.md
    if readme_path.exists():
        print(f"Parsing README.md...")
        stories = parse_markdown_file(readme_path)
        all_stories.extend(stories)
        print(f"  Found {len(stories)} stories")

    if not all_stories:
        print("Error: No stories found", file=sys.stderr)
        sys.exit(1)

    print(f"\nWriting {len(all_stories)} total stories to {output_path}...")
    count = write_csv(all_stories, output_path)

    print(f"Done! {count} stories exported to {output_path}")

if __name__ == '__main__':
    main()
