#!/usr/bin/env python3
"""
Generate OC Presentation 2 evaluation pages (instructor-only / same layout as OC1).
"""

from __future__ import annotations

import os
import re

from generate_forms import (
    DISPLAY_NAME_BY_FIRST_LOWER,
    cleanup_html,
    display_name,
    generate_html_form,
    get_student_filename,
    load_or_create_filename_map,
    parse_csv,
    save_filename_map,
)

CSV_FILE = "data/OC Evaluation 2 (Responses) - Form Responses 1.csv"
OUTPUT_DIR = "oc2_forms_output"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def inject_oc2_links_into_capstone_index(filename_map: dict) -> None:
    """Add an OC Presentation 2 pill for each student who has an OC2 form."""
    display_to_key = {v: k for k, v in DISPLAY_NAME_BY_FIRST_LOWER.items()}
    path = os.path.join(PROJECT_ROOT, "index.html")
    text = open(path, encoding="utf-8").read()

    for display, key in display_to_key.items():
        if key not in filename_map:
            continue
        fn = filename_map[key]
        link = (
            f'<a href="oc2_forms_output/{fn}" '
            f'class="eval-btn oc2-btn">OC Presentation 2</a>'
        )
        pattern = re.compile(
            r"(<span class=\"student-name\">"
            + re.escape(display)
            + r"</span>\n                <div class=\"eval-btns\">)(.*?)(</div>)",
            re.DOTALL,
        )

        def repl(m: re.Match, _link: str = link) -> str:
            prefix, mids, close = m.group(1), m.group(2), m.group(3)
            if "OC Presentation 2" in mids:
                return m.group(0)
            return prefix + mids.rstrip() + _link + close

        text, n = pattern.subn(repl, text, count=1)
        if n == 0:
            print(f"Warning: could not find index row for {display}")

    open(path, "w", encoding="utf-8").write(text)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Parsing OC2 CSV…")
    reviews_by_student = parse_csv(os.path.join(PROJECT_ROOT, CSV_FILE))
    filename_map = load_or_create_filename_map(
        os.path.join(PROJECT_ROOT, OUTPUT_DIR)
    )

    generated: list[str] = []
    for student_key, data in sorted(reviews_by_student.items()):
        out_name = get_student_filename(student_key, filename_map)
        generate_html_form(
            student_key,
            data,
            os.path.join(PROJECT_ROOT, OUTPUT_DIR),
            out_name,
            oc_label="OC Presentation 2",
            styles_href="../forms_output/styles.css",
            favicon_href="../forms_output/favicon.svg",
            instructor_chart_color="#e85d75",
        )
        generated.append(out_name)
        peers = len(data["peer_reviews"])
        inst = len(data["instructor_reviews"])
        print(f"  ✓ {out_name} — {display_name(student_key)} (peers={peers}, instructor={inst})")

    save_filename_map(os.path.join(PROJECT_ROOT, OUTPUT_DIR), filename_map)
    keep = set(generated) | {"index.html"}
    cleanup_html(os.path.join(PROJECT_ROOT, OUTPUT_DIR), keep=keep)
    inject_oc2_links_into_capstone_index(filename_map)

    print(f"\nDone: {len(generated)} files in {OUTPUT_DIR}/")
    print("Capstone index.html updated with OC Presentation 2 pills where data exists.")


if __name__ == "__main__":
    main()
