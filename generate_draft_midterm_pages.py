#!/usr/bin/env python3
"""Emit one HTML file per student with all draft midterm notes in draft_midterm/."""

from __future__ import annotations

import html
import re
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "draft_midterm"

# Roster order; comment strings may include <a> tags (trusted).
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
        "belle-clement",
        "Belle Clement",
        [
            """I think "balance is important" could be on its own slide?""",
            """You might "rainbow" the top of your logo.""",
            """Show the process. You don't need to have anything finalized right now, but you should have a lot of options/mockups?""",
            """I feel like we need to have some of your own personality coming through with the brand.""",
            """Talk more about your colors""",
            """Gesture to the nutrition label redesign""",
        ],
    ),
    (
        "conner-evans",
        "Conner Evans",
        [
            """As an intro, you might frame this problem as a problem that faces not just you, but all graphic designers""",
            """It's effective to show that whole smile-y face process.""",
            """Maybe clarify that you don't own the "tool" (but maybe you own the output).""",
            """Maybe point to how your selection of tools represents your own aesthetic taste?""",
            """Note how your art-directing""",
            """It would be great to show a ton of the outputs.""",
            """You can probably drop what the acronym stands for.""",
        ],
    ),
    (
        "delaney-kohlstedt",
        "Delaney Kohlstedt",
        [
            """I could imagine the footers being a bit bolder (light condensed is really difficult at small scales)""",
            """Tighten the leading throughout by a few points.""",
            """I love the matrix, but the mustard is pretty hard to read (small contrast change here)""",
            """After the chevron history, you could just show the mark, then add your type.""",
            """Bump up the size of the Condensed type throughout.""",
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
        "elyse-lundberg",
        "Elyse Lundberg",
        [
            """For that first quote, you might highlight one specific sentence""",
            """Maybe you could have a slide with the quote from your instructor""",
            """You should illustrate the brain slides (just to simplify it a bit).""",
            """Spell out "trauma" in the slide deck. You can have some of those statistics on your page.""",
            """The stock images could be changed out.""",
            """I like the rounded typeface you're using (use it throughout).""",
            """Break down these quote pages.""",
            """Why this "VR" space as opposed to your own yoga studio?""",
            """I could see Clayla on her own white background.""",
            """Design the "What's Next?" Page a bit more.""",
            """Does Clayla need to have a body?""",
            """Perhaps consider <a href="https://cyberfeminismindex.com/">cyberfeminismindex.com</a>""",
        ],
    ),
    (
        "emma-fingeret",
        "Emma Fingeret",
        [
            """"Lanfilled" should read "Landfilled" """,
            """Maybe "Solution" feels too lofty, perhaps a "Response" """,
            """Perhaps the "Unraveled" logo matches the color of the doodle""",
            """I think you should show the photography approach as well.""",
            """Animate that logo!""",
            """I'd love to see a graphic breaking down your "program" of response before the slides.""",
            """Maybe the color of the wrap could be a place to showcase the brand.""",
        ],
    ),
    (
        "hannah-smith",
        "Hannah Smith",
        [
            """Smart to start with your personal experience.""",
            """I wonder if you can remove the watermark on the images?""",
            """Maybe explain how Collegiate sports manages your diet and schedule now — a day in the life.""",
            """Maybe instead of "app" you describe this as a "program" """,
            """Definitely walk us through how you imagine the app might work? How can it identify your general concerns?""",
            """Explain where you are in the process… Where you hope to go next?""",
            """Keep each mock up to a page.""",
            """Call out a few details on the app itself. Circle some elements.""",
            """Elaborate on how you got to your brand.""",
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
        "madelyn-baur",
        "Madelyn Baur",
        [
            """I think you should have a slide that explains "What is Play?" Before the graph""",
            """Give us some sense of what specific experts/studies you are referencing""",
            """You might break the "In terms of accessibility…" slide into two sides.""",
            """You could slow "build" up your shape""",
            """An animation would be lovely here.""",
            """You might read this quote in its entirety.""",
            """You might increase the size of the centered type throughout?""",
            """Definitely mention Lev Vygotsky for play""",
            """I think you could tighten the leading on the main logo mark and subtitle""",
        ],
    ),
    (
        "maggie-evans",
        "Maggie Evans",
        [
            """I'm not sure if I quite buy that one is treated as "Good" and one as "Bad"— I wonder if it's the difference between "Serious" and "Unserious" """,
            """I really like the animation strategies""",
            """I wonder if you can ground your critique of Children's Museums in a specific museum?""",
            """Perhaps you can reference the Bauhaus a bit?""",
            """Maybe lose the line between the mark and the type.""",
        ],
    ),
    (
        "natalie-broyles",
        "Natalie Broyles",
        [
            """You might change the color of your arrow to make it a bit more visible?""",
            """You might adjust your voice to reach the back""",
            """Fantastic use of the yellow pad.""",
            """I feel like it might be helpful to have some of the etymology up on the page?""",
            """Could we maybe have some captioning on your photo of objects midway through your presentation?""",
            """The collections page is looking really cool, and I really like the family tree tool.""",
            """On the Spotlight page: you could bring back your outline element from the collections page.""",
            """Starstar.website — definitely worth pulling back in.""",
            """<a href="https://maxbittker.github.io/broider/">maxbittker.github.io/broider</a> — consideration for the borders.""",
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
    (
        "xavier-girard",
        "Xavier Girard",
        [
            """Place your name in the same typeface as your logo mark.""",
            """I think you might need a better type pairing here (you could have a monospace for your caption).""",
            """Center some of your sentences in the page with your header typeface.""",
            """The program is currently not that visually interesting (so a blank page is not that exciting currently).""",
            """Could you break down how you selected these specific tools and why?""",
            """You should show me how you interact with the flat files — what is the Interface!""",
            """Speak to skeuomorphism. — Place us in a graphic history.""",
            """<a href="https://archive.is/20260316151404/https://www.nytimes.com/2026/03/12/magazine/ai-coding-programming-jobs-claude-chatgpt.html">NYT magazine on AI and programming (archive.is)</a>""",
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
            lis.append(f'                <li class="draft-midterm-list-item">{inner}</li>')
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
