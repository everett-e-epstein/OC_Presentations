#!/usr/bin/env python3
"""Emit one HTML file per student with all draft midterm notes in draft_midterm/."""

from __future__ import annotations

import html
import re
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "draft_midterm"

# (slug, display_name, list of comment inner HTML strings — trusted, may include <a> tags)
DATA: list[tuple[str, str, list[str]]] = [
    (
        "alex-long",
        "Alex Long",
        [
            """I'm wondering if you could introduce your graphic language for the "$" signs.""",
            """You might tighten the underline beneath the emphasized words.""",
            """You might clean up the language on the "affordable community" graphic.""",
            """You don't need the "thus born the app name". Just write "Calypso" in your font.""",
            """Give the app mockup some other apps on the iPhone screen.""",
        ],
    ),
    (
        "donatella-thomas",
        "Donatella Thomas",
        [
            """I feel like we might need to start with your story first (the Why Do I Care? Section), and you can then pivot into the research.""",
            """Make your text LARGE.""",
            """Could we rework the mood board for this format?""",
            """I could imagine your instruments taking up more real estate on the wireframe.""",
            """<a href="https://threejs.org/">threejs.org</a> and <a href="https://free3d.com/3d-models/blender-guitar">free3d.com/3d-models/blender-guitar</a> and cursor — the greatness method!""",
        ],
    ),
    (
        "ella-merkel",
        "Ella Merkel",
        [
            """This question is still a bit too broad. Give me some images (of buildings? Of something else?) that shapes your own perspective.""",
            """Maybe show us a diagram of your process?""",
            """You need to clarify what is the input on the tapestry and why a tapestry? Can this be clarified without text in the presentation?""",
            """There's a bit of a disconnect between what the form is and what the question is? Does the tapestry have anything to do with architecture? How so? Give us that articulation of: Buildings — Meaning → Aesthetic Practice — Tapestry → Buildings""",
        ],
    ),
    (
        "jeremy-wilkins",
        "Jeremy Wilkins",
        [
            """I think you should start with the gradient slide of Interval""",
            """Definitely redesign the survey in your graphic language.""",
            """Animate that logo!""",
            """I'm wondering if you could animate your gradient to become flat (to clarify the move from distraction to focus — like it's coming into focus).""",
            """I feel like we might need to see an example of what it's capturing (your screen movements, your physical movements, etc.).""",
            """I feel like as a plug-in this could work beautifully.""",
            """Start with a day-in-your-life""",
        ],
    ),
    (
        "julia-beers",
        "Julia Beers",
        [
            """I think we might need a bit of a background as to what this project is resolving. Give us the full arc of your project.""",
            """Why vellum? Give us some post-rationalization beyond "liking it." """,
            """What could the print technique mean?""",
            """I think you could use a single superfamily for your type, the monospace doesn't quite pair with your header typeface.""",
            """You should clarify the distribution of this work? Perhaps there's a digital version?""",
            """Clarify this as a design framework.""",
        ],
    ),
    (
        "louisa-benedict",
        "Louisa Benedict",
        [
            """The study abroad intro is smart, and I appreciated that you began with the EU ETA point. Perhaps you can illustrate some of the panic attack of travel with some photos to clarify what this hectic character looks like.""",
            """Definitely break down what you hope to accomplish with some bullet points.""",
            """Try to reduce the amount of bullet points a bit. Give us some photos here. Image treatments.""",
            """Maybe give us some photos here of your Chris and Sarah.""",
        ],
    ),
    (
        "sam-tugman",
        "Sam Tugman",
        [
            """Love the little illustrations.""",
            """As soon as you mention the interviews, you might put in some slides of testimonials. Quote quote quote.""",
            """Maybe the color palette can be an entire page of patterning?""",
            """Lay out the "things Handled will have" as a set of bullets that come up as you narrate it.""",
            """The arrows on the "Mary Kenly" slide are a bit difficult to see.""",
            """I'm still not quite convinced of the gradient, it feels like a different logic than your flat graphics. The maroon feels right, but maybe just for the type; I'm not sure that it sits well at the top.""",
            """It would be great to see some type on those WIP pages (even if it's Lorem Ipsum).""",
        ],
    ),
    (
        "sophia-crosby",
        "Sophia Crosby",
        [
            """You might start with the name of the project then shift into your "Hi, I'm Sophia".""",
            """There's a bit of vibration of that pink against the green background.""",
            """Great pace!""",
            """I would love to see your mascot animate into focus.""",
            """I'm wondering if the building could be a "territory".""",
            """Animate the application.""",
        ],
    ),
    (
        "tala-ghezawi",
        "Tala Ghezawi",
        [
            """You might have some information graphics and maps to clarify the resources.""",
            """There are some parts of your notes that should be up on screen (like "Geographical Privilege").""",
            """Add some more slides with just imagery. You might highlight some of the text on your screen with imagery or a definition. It's pretty difficult to follow your argument without the statistics or a breakdown of your process.""",
            """Give me the "How it works" breakdown. Give us a step by step process.""",
            """The graphics look great; however, the English translation below on the newsletter feels a bit less integrated into the arabic form. Maybe shift this English graphic.""",
            """"Structured for Impact" is reading a bit light in the logomark.""",
            """You might anticipate some of the pushback on the "it's not charity"?""",
        ],
    ),
]


def comment_body(s: str) -> str:
    """Plain text → escaped; strings with link markup pass through (trusted source)."""
    if "<a " in s:
        return s
    return html.escape(s)


def student_page_html(*, student_name: str, items_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft Midterm — {html.escape(student_name)}</title>
    <link rel="icon" href="../forms_output/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="../forms_output/styles.css">
</head>
<body>
    <nav class="draft-midterm-nav-pills" aria-label="Section navigation">
        <a href="../index.html" class="eval-btn oc-btn draft-midterm-nav-pill">← Capstone evaluations</a>
    </nav>
    <h1 class="capstone-title">Draft Midterm</h1>
    <p class="subtitle">Instructor notes from draft midterm presentations.</p>

    <div class="instructor-section">
        <div class="section-title">{html.escape(student_name)}</div>
        <div class="review">
            <ul class="draft-midterm-list">
{items_html}
            </ul>
        </div>
    </div>
</body>
</html>
"""


def remove_legacy_per_note_pages(out: Path) -> None:
    for p in out.glob("*.html"):
        if p.name == "index.html":
            continue
        if re.match(r"^.+-\d{2}$", p.stem):
            p.unlink()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_legacy_per_note_pages(OUT_DIR)

    toc_links: list[str] = []

    for slug, name, comments in DATA:
        lis = []
        for raw in comments:
            inner = comment_body(raw.strip())
            lis.append(f"                <li class=\"draft-midterm-list-item\">{inner}</li>")
        items = "\n".join(lis)
        body = student_page_html(student_name=name, items_html=items)
        (OUT_DIR / f"{slug}.html").write_text(body, encoding="utf-8")
        toc_links.append(
            f'        <li><a href="{slug}.html">{html.escape(name)}</a></li>'
        )

    index_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graphic Design 472 — Draft Midterm</title>
    <link rel="icon" href="../forms_output/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="../forms_output/styles.css">
</head>
<body>
    <nav class="draft-midterm-nav-pills" aria-label="Section navigation">
        <a href="../index.html" class="eval-btn oc-btn draft-midterm-nav-pill">← Capstone evaluations</a>
    </nav>
    <h1 class="capstone-title">Draft Midterm</h1>
    <p class="subtitle">Open a student to see all instructor notes in one list.</p>
    <div class="draft-midterm-toc">
        <ul class="draft-midterm-toc-list draft-midterm-t-overview">
{chr(10).join(toc_links)}
        </ul>
    </div>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(index_body, encoding="utf-8")
    n = len(DATA) + 1
    print(f"Wrote {n} files to {OUT_DIR}")


if __name__ == "__main__":
    main()
