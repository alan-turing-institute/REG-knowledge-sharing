#!/usr/bin/env python3
"""
Generate index.html for GitHub Pages, containing information about the next
tech talk.

Reads Lunchtime-Tech-Talks.md from the wiki and produces an HTML file with
Open Graph meta tags for Slack previews. The page redirects to the wiki.

Usage: techtalk.py INPUT_FILE OUTPUT_FILE [--date MONTH DAY]
  MONTH and DAY are integers (e.g. --date 3 17 for the 17th of March).
  Without --date, today's date is used.
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from typing import Optional

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


@dataclass
class Talk:
    month: Optional[int]
    day: int
    speaker: str
    topic: str
    meeting_room: str


def clean_markdown(text: str) -> str:
    """Strip some Markdown formatting from a cell's text content."""
    return text.replace("*", "").replace("_", "").strip()


def parse_month(text: str) -> Optional[int]:
    """Parse a month name (or abbreviation) to a month number (1-12)."""
    key = clean_markdown(text).lower()[:3]
    return MONTH_MAP.get(key)


def get_schedule_table(markdown_text: str) -> list:
    """
    Extract all table rows from the Schedule section of the markdown.
    Returns a list of rows, where each row is a list of 5 cell strings
    (the raw Markdown content of each cell).
    Raises ValueError if the Schedule section or table is not found.
    """
    lines = markdown_text.splitlines()

    # Find the Schedule section heading
    schedule_start = None
    for i, line in enumerate(lines):
        if re.match(r"^#+\s+Schedule\s*$", line):
            schedule_start = i
            break

    if schedule_start is None:
        raise ValueError("No Schedule section found")

    # Collect lines until the next heading (or end of file)
    schedule_lines = []
    for line in lines[schedule_start + 1 :]:
        if re.match(r"^#+\s+", line):
            break
        schedule_lines.append(line)

    # Parse table rows: keep only lines containing '|' that are not separators
    rows = []
    for line in schedule_lines:
        if "|" not in line:
            continue
        # Skip separator rows like | -----: | ----: | ...
        if re.match(r"^\|[\s\-:|]+\|", line):
            continue
        parts = line.split("|")
        # A row looks like "| cell | cell | ..." so parts[0] and parts[-1] are empty
        cells = [p.strip() for p in parts[1:-1]]
        if len(cells) == 5:
            rows.append(cells)

    if not rows:
        raise ValueError("No table found in Schedule section")

    return rows


def parse_talks(rows: list) -> list:
    """
    Parse table rows (as returned by get_schedule_table) into Talk objects.
    Skips the first (header) row.
    Raises ValueError if any row cannot be parsed.
    """
    talks = []
    for cells in rows[1:]:  # Skip header row
        month_str, day_str, speaker, topic, meeting_room = cells
        month = parse_month(month_str)
        try:
            day = int(clean_markdown(day_str))
        except ValueError:
            raise ValueError(f"Could not parse day: {day_str!r}")
        talks.append(
            Talk(
                month=month,
                day=day,
                speaker=clean_markdown(speaker),
                topic=clean_markdown(topic),
                meeting_room=clean_markdown(meeting_room),
            )
        )
    return talks


def fill_missing_months(talks: list) -> list:
    """
    Forward-fill missing months in the talks list.

    If the first entry has no month, looks ahead for the first entry with a
    month and uses the preceding month for the first entry. Subsequent missing
    months are filled from the entry above.
    """
    if not talks:
        return talks

    # Fill the first entry if it's missing a month
    if talks[0].month is None:
        first_month = next((t.month for t in talks if t.month is not None), None)
        if first_month is None:
            raise ValueError("No months found in talks")
        talks[0].month = 12 if first_month == 1 else first_month - 1

    # Forward-fill subsequent entries
    for i in range(1, len(talks)):
        if talks[i].month is None:
            talks[i].month = talks[i - 1].month

    return talks


def get_next_talk(talks: list, month: int, day: int) -> Talk:
    """
    Return the next talk on or after the given date.
    Raises ValueError if no upcoming talks are found.
    """
    upcoming = [
        t
        for t in talks
        if t.month is not None
        and (t.month > month or (t.month == month and t.day >= day))
    ]
    if not upcoming:
        raise ValueError("No upcoming talks")
    return upcoming[0]


def generate_html(talk: Talk, today_month: int, today_day: int) -> str:
    """Generate the HTML page for the next tech talk."""
    talk_is_today = talk.month == today_month and talk.day == today_day
    title = "Today's Tech Talk" if talk_is_today else "The Next Tech Talk"
    return (
        "<html>\n"
        "<head>\n"
        f'<meta property="og:title" content="{title} ({talk.day}/{talk.month})"/>\n'
        f'<meta property="og:description" content="*Meeting room:* {talk.meeting_room}"/>\n'
        '<meta property="twitter:label1" value="Speaker(s)"/>\n'
        f'<meta property="twitter:data1" content="{talk.speaker}"/>\n'
        '<meta property="twitter:label2" value="Topic"/>\n'
        f'<meta property="twitter:data2" content="{talk.topic}"/>\n'
        '<meta http-equiv="refresh" content="1;url=https://github.com/alan-turing-institute/REG-knowledge-sharing/wiki/Lunchtime-Tech-Talks"/>\n'
        "</head>\n"
        "<body>\n"
        "Redirecting you to the Tech Talk schedule...\n"
        "</body>\n"
        "</html>\n"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_file", help="Path to the Lunchtime-Tech-Talks.md wiki page")
    parser.add_argument("output_file", help="Path to write the output HTML file")
    parser.add_argument(
        "--date",
        nargs=2,
        type=int,
        metavar=("MONTH", "DAY"),
        help="Override today's date (default: use system date)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.date:
        month, day = args.date
    else:
        today = date.today()
        month, day = today.month, today.day

    try:
        with open(args.input_file, encoding="utf-8") as f:
            contents = f.read()
    except FileNotFoundError:
        print(f"Error: {args.input_file!r} not found.", file=sys.stderr)
        raise SystemExit(1)

    rows = get_schedule_table(contents)
    talks = parse_talks(rows)
    talks = fill_missing_months(talks)

    try:
        next_talk = get_next_talk(talks, month, day)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)

    html = generate_html(next_talk, month, day)

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated webpage for upcoming talk ({next_talk.day}/{next_talk.month}) in {args.output_file}.")


if __name__ == "__main__":
    main()
