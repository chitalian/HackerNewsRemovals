#!/usr/bin/env python3
"""
Convert HackerNewsRemovals README.md to CSV format.
Parses the markdown list of removed stories and outputs as CSV.
"""

import re
import csv
import sys
from pathlib import Path

def parse_readme(filepath):
    """Parse the README.md file and extract story data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    stories = []
    current_date = None

    # Pattern for date headers: #### **Day, Month DD, YYYY**
    date_pattern = re.compile(r'####\s*\*\*(\w+,\s+\w+\s+\d+,\s+\d+)\*\*')

    # Pattern for story entries:
    # * [ID](stats_url) #RANK POINTS points COMMENTS comments -> [TITLE](URL)
    story_pattern = re.compile(
        r'\*\s*\[(\d+)\]\(https://news\.social-protocols\.org/stats\?id=\d+\)\s*'
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
    output_path = script_dir / 'removed_stories.csv'

    if not readme_path.exists():
        print(f"Error: {readme_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {readme_path}...")
    stories = parse_readme(readme_path)

    print(f"Writing {len(stories)} stories to {output_path}...")
    count = write_csv(stories, output_path)

    print(f"Done! {count} stories exported to {output_path}")

if __name__ == '__main__':
    main()
