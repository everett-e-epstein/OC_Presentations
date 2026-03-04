#!/usr/bin/env python3
"""
Generate individual Concept Prototype evaluation forms for each student.
Uses a radar chart (3 axes: Argument, Originality, Graphic Craft).

Also regenerates the root index.html as a tabbed hub for both evaluations.
"""

import csv
from collections import defaultdict
import os
import json
import secrets

# ---------------------------------------------------------------------------
# Question mapping for CP evaluation
# ---------------------------------------------------------------------------
QUESTIONS = {
    "01. ARGUMENT": "Q1: Argument",
    "02. ORIGINALITY": "Q2: Originality",
    "03. GRAPHIC CRAFT": "Q3: Graphic Craft",
}

COMMENT_COLUMNS = {
    "01. ARGUMENT": "How could this project be refined to better address the provided argument?",
    "02. ORIGINALITY": 'What feels especially "original" about this solution?',
    "03. GRAPHIC CRAFT": "What is the strongest and the weakest element of the graphics in this prototype?",
}

# ---------------------------------------------------------------------------
# Student display names
# ---------------------------------------------------------------------------
DISPLAY_NAME_BY_FIRST_LOWER = {
    "madelyn":   "Madelyn Baur",
    "julia":     "Julia Beers",
    "louisa":    "Louisa Benedict",
    "natalie":   "Natalie Broyles",
    "belle":     "Belle Clement",
    "sophia":    "Sophia Crosby",
    "conner":    "Conner Evans",
    "maggie":    "Maggie Evans",
    "emma":      "Emma Fingeret",
    "tala":      "Tala Ghezawi",
    "xavier":    "Xavier Girard",
    "delaney":   "Delaney Kohlstedt",
    "alex":      "Alex Long",
    "elyse":     "Elyse Lundberg",
    "ella":      "Ella Merkel",
    "hannah":    "Hannah Smith",
    "donatella": "Donatella Thomas",
    "sam":       "Sam Tugman",
    "jeremy":    "Jeremy Wilkins",
}

# Explicit aliases for shorthand / nickname reviewee names in the CSV
REVIEWEE_ALIASES = {
    "conn":       "conner",
    "don":        "donatella",
    "delaney k":  "delaney",
}

# ---------------------------------------------------------------------------
# Peer colors  (border + semi-transparent fill for radar)
# ---------------------------------------------------------------------------
PEER_COLORS = [
    {"border": "#ff2bd6", "bg": "rgba(255,43,214,0.12)"},
    {"border": "#004aea", "bg": "rgba(0,74,234,0.12)"},
    {"border": "#006834", "bg": "rgba(0,104,52,0.12)"},
    {"border": "#ff610b", "bg": "rgba(255,97,11,0.12)"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def display_name(name: str) -> str:
    raw = (name or "").strip()
    if not raw:
        return ""
    return DISPLAY_NAME_BY_FIRST_LOWER.get(raw.lower(), raw)


def _student_key(student_name: str) -> str:
    return (student_name or "").strip().lower()


def _normalize_reviewee(name: str) -> str:
    """
    Normalize a reviewee name to a canonical first-name-only lowercase key.
    Handles:
      - Explicit aliases  ("Conn" → "conner", "Don" → "donatella")
      - Known first-name keys  ("Sophia", "ella", …)
      - Full display names  ("Hannah Smith" → "hannah", "Ella Merkel" → "ella")
      - First-word of a partial name  ("Delaney K" → "delaney")
    """
    raw = name.strip()
    if not raw:
        return ""
    lower = raw.lower()

    # 1. Explicit alias
    if lower in REVIEWEE_ALIASES:
        return REVIEWEE_ALIASES[lower]

    # 2. Known first-name key
    if lower in DISPLAY_NAME_BY_FIRST_LOWER:
        return lower

    # 3. Matches a full display name  (e.g. "Hannah Smith", "Madelyn Baur")
    for key, full in DISPLAY_NAME_BY_FIRST_LOWER.items():
        if full.lower() == lower:
            return key

    # 4. First word of multi-word name  (e.g. "Delaney K" → "delaney")
    parts = lower.split()
    if len(parts) > 1 and parts[0] in DISPLAY_NAME_BY_FIRST_LOWER:
        return parts[0]

    return lower


def load_or_create_filename_map(output_dir: str) -> dict:
    map_path = os.path.join(output_dir, "_student_file_map.json")
    if os.path.exists(map_path):
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_filename_map(output_dir: str, filename_map: dict) -> None:
    map_path = os.path.join(output_dir, "_student_file_map.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(filename_map, f, indent=2, sort_keys=True)


def get_student_filename(student_name: str, filename_map: dict) -> str:
    key = _student_key(student_name)
    existing = filename_map.get(key)
    if isinstance(existing, str) and existing.endswith(".html"):
        return existing
    token = secrets.token_hex(10)
    filename = f"{token}.html"
    filename_map[key] = filename
    return filename


def cleanup_html(output_dir: str, keep: set) -> None:
    """Remove any .html files in output_dir that are not in keep."""
    try:
        for fn in os.listdir(output_dir):
            if not fn.endswith(".html"):
                continue
            if fn in keep:
                continue
            try:
                os.remove(os.path.join(output_dir, fn))
            except Exception:
                pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------
def parse_csv(filename: str) -> dict:
    """Parse the CP CSV and organize reviews by reviewee."""
    reviews_by_student = defaultdict(lambda: {"peer_reviews": [], "instructor_reviews": []})

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviewee = _normalize_reviewee(row.get("Who you are reviewing:", ""))
            reviewer = row.get("Your name:", "").strip()

            if not reviewee or not reviewer:
                continue

            review_data = {
                "reviewer": reviewer,
                "timestamp": row.get("Timestamp", ""),
                "ratings": {},
                "comments": {},
                "additional_comments": row.get("ANY ADDITIONAL COMMENTS FOR PRESENTER ...", ""),
            }

            for q_key, q_label in QUESTIONS.items():
                rating = row.get(q_key, "").strip()
                comment_col = COMMENT_COLUMNS.get(q_key, "")
                comment = row.get(comment_col, "").strip()
                review_data["ratings"][q_label] = rating
                review_data["comments"][q_label] = comment

            if reviewer.strip().lower() == "everett":
                reviews_by_student[reviewee]["instructor_reviews"].append(review_data)
            else:
                reviews_by_student[reviewee]["peer_reviews"].append(review_data)

    return reviews_by_student


# ---------------------------------------------------------------------------
# Chart data
# ---------------------------------------------------------------------------
def prepare_chart_data(data: dict) -> str:
    """Prepare JSON data for a Chart.js radar chart."""
    categories = ["Argument", "Originality", "Graphic Craft"]
    full_labels = list(QUESTIONS.values())

    datasets = []
    color_idx = 0
    peer_count = 1

    for review in data["peer_reviews"]:
        ratings_list = []
        for q_label in full_labels:
            rating = review["ratings"].get(q_label, "")
            try:
                ratings_list.append(float(rating) if rating else None)
            except ValueError:
                ratings_list.append(None)

        color = PEER_COLORS[color_idx % len(PEER_COLORS)]
        datasets.append({
            "label": f"Peer {peer_count}",
            "data": ratings_list,
            "originalData": ratings_list,
            "borderColor": color["border"],
            "backgroundColor": color["bg"],
            "pointBackgroundColor": color["border"],
            "pointRadius": 5,
            "fill": True,
            "borderWidth": 2,
        })
        color_idx += 1
        peer_count += 1

    for review in data["instructor_reviews"]:
        ratings_list = []
        for q_label in full_labels:
            rating = review["ratings"].get(q_label, "")
            try:
                ratings_list.append(float(rating) if rating else None)
            except ValueError:
                ratings_list.append(None)
        datasets.append({
            "label": "Everett",
            "data": ratings_list,
            "originalData": ratings_list,
            "borderColor": "#000000",
            "backgroundColor": "rgba(0,0,0,0.08)",
            "pointBackgroundColor": "#000000",
            "pointRadius": 5,
            "fill": True,
            "borderWidth": 3,
        })

    return json.dumps({"labels": categories, "datasets": datasets})


# ---------------------------------------------------------------------------
# HTML generation — individual student page
# ---------------------------------------------------------------------------
def generate_html_form(student_name: str, data: dict, output_dir: str, output_filename: str) -> str:
    chart_data = prepare_chart_data(data)
    student_display = display_name(student_name)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CP Evaluation - {student_display}</title>
    <link rel="icon" href="../forms_output/favicon.svg" type="image/svg+xml">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="../forms_output/styles.css">
    <style>
        /* Let the radar fill the container width as a square */
        #ratingsChart {{
            display: block;
            margin: 0 auto;
            width: 100% !important;
            height: auto !important;
        }}
    </style>
</head>
<body>
    <div class="fixed-topbar">
        <div class="oc-title">CP Evaluation 1</div>
        <button class="download-btn no-print" onclick="window.print()" aria-label="Download as PDF" title="Download as PDF">
            <svg class="download-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path d="M12 3v10m0 0l4-4m-4 4l-4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4 17v3h16v-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
    </div>

    <div class="header">
        <h2>{student_display}</h2>
    </div>

    <div class="chart-container">
        <div id="chartLegend" class="legend-pills"></div>
        <canvas id="ratingsChart"></canvas>
    </div>
"""

    # ------------------------------------------------------------------
    # Peer reviews
    # ------------------------------------------------------------------
    if data["peer_reviews"]:
        html += """
    <div class="section">
        <div class="section-title">Peer Reviews</div>
"""
        peer_number = 1
        for review in data["peer_reviews"]:
            html += f"""
        <div class="review peer-review peer-{peer_number}">
            <div class="reviewer-name">Reviewed by:<span class="peer-pill peer-pill-{peer_number}">Peer {peer_number}</span></div>
"""
            peer_number += 1

            for q_label in QUESTIONS.values():
                rating  = review["ratings"].get(q_label, "")
                comment = review["comments"].get(q_label, "")
                if rating or comment:
                    html += f"""
            <div class="question">
                <div class="question-left">
                    <div class="question-label">{q_label}</div>
"""
                    if comment:
                        html += f"""
                    <div class="comment">{comment}</div>
"""
                    html += f"""
                </div>
                <div class="rating"><span class="grade-circle">{rating}</span></div>
            </div>
"""

            if review["additional_comments"]:
                html += f"""
            <div class="additional-comments">
                <div class="additional-comments-label">Additional Comments:</div>
                <div>{review['additional_comments']}</div>
            </div>
"""
            html += """
        </div>
"""
        html += """
    </div>
"""

    # ------------------------------------------------------------------
    # Instructor reviews (Everett — may not appear in all CP evaluations)
    # ------------------------------------------------------------------
    if data["instructor_reviews"]:
        html += """
    <hr>
    <div class="instructor-section">
        <div class="section-title">Instructor Review - Everett</div>
"""
        for review in data["instructor_reviews"]:
            html += """
        <div class="review">
"""
            for q_label in QUESTIONS.values():
                rating  = review["ratings"].get(q_label, "")
                comment = review["comments"].get(q_label, "")
                if rating or comment:
                    html += f"""
            <div class="question">
                <div class="question-left">
                    <div class="question-label">{q_label}</div>
"""
                    if comment:
                        html += f"""
                    <div class="comment">{comment}</div>
"""
                    html += f"""
                </div>
                <div class="rating"><span class="grade-circle">{rating}</span></div>
            </div>
"""
            if review["additional_comments"]:
                html += f"""
            <div class="additional-comments">
                <div class="additional-comments-label">Additional Comments:</div>
                <div>{review['additional_comments']}</div>
            </div>
"""
            html += """
        </div>
"""
        html += """
    </div>
"""

    # ------------------------------------------------------------------
    # Radar chart JavaScript
    # ------------------------------------------------------------------
    html += f"""
    <script>
        const chartData = {chart_data};

        const ctx = document.getElementById('ratingsChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: chartData.labels,
                datasets: chartData.datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1,
                layout: {{
                    padding: {{ top: 10, bottom: 10, left: 30, right: 30 }}
                }},
                scales: {{
                    r: {{
                        min: 0,
                        max: 5,
                        ticks: {{
                            stepSize: 1,
                            display: false
                        }},
                        pointLabels: {{
                            font: {{ size: 15, weight: '600' }},
                            color: '#333'
                        }},
                        grid: {{ color: 'rgba(0,0,0,0.1)' }},
                        angleLines: {{ color: 'rgba(0,0,0,0.15)' }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const ds = ctx.dataset || {{}};
                                const orig = (ds.originalData && ds.originalData[ctx.dataIndex] != null)
                                    ? ds.originalData[ctx.dataIndex]
                                    : ctx.parsed.r;
                                const v = (orig == null) ? '' : String(orig);
                                return `${{ds.label}}: ${{v}}`;
                            }}
                        }}
                    }},
                    title: {{ display: false }}
                }}
            }}
        }});

        // Custom pill legend
        function legendTextColor(hex) {{
            if (!hex || typeof hex !== 'string' || !hex.startsWith('#') ||
                (hex.length !== 7 && hex.length !== 4)) return '#ffffff';
            let r, g, b;
            if (hex.length === 4) {{
                r = parseInt(hex[1]+hex[1], 16);
                g = parseInt(hex[2]+hex[2], 16);
                b = parseInt(hex[3]+hex[3], 16);
            }} else {{
                r = parseInt(hex.slice(1,3), 16);
                g = parseInt(hex.slice(3,5), 16);
                b = parseInt(hex.slice(5,7), 16);
            }}
            const lum = (0.2126*r + 0.7152*g + 0.0722*b) / 255;
            return lum > 0.65 ? '#000000' : '#ffffff';
        }}

        const legendEl = document.getElementById('chartLegend');
        if (legendEl) {{
            legendEl.innerHTML = '';
            chartData.datasets.forEach((ds, i) => {{
                const bg = ds.borderColor || '#000000';
                const pill = document.createElement('button');
                pill.type = 'button';
                pill.className = 'legend-pill';
                pill.textContent = ds.label;
                pill.style.backgroundColor = bg;
                pill.style.color = legendTextColor(bg);
                pill.addEventListener('click', () => {{
                    const visible = chart.isDatasetVisible(i);
                    chart.setDatasetVisibility(i, !visible);
                    pill.classList.toggle('is-hidden', visible);
                    chart.update();
                }});
                legendEl.appendChild(pill);
            }});
        }}
    </script>
</body>
</html>
"""

    filepath = os.path.join(output_dir, output_filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return output_filename


# ---------------------------------------------------------------------------
# cp_forms_output/index.html  (standalone CP listing)
# ---------------------------------------------------------------------------
def create_cp_index(files: list, output_dir: str, reviews_data: dict, filename_map: dict) -> None:
    filename_to_key = {v: k for k, v in filename_map.items() if isinstance(v, str)}
    total_reviews = sum(
        len(d["peer_reviews"]) + len(d["instructor_reviews"])
        for d in reviews_data.values()
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CP Evaluation Forms - Index</title>
    <link rel="icon" href="../forms_output/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="../forms_output/styles.css">
    <style>
        body {{ background-color: #f5f5f5; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .stats {{
            background-color: white; padding: 20px; margin-bottom: 30px;
            border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .student-list {{ list-style: none; padding: 0; }}
        .student-item {{
            background-color: white; margin-bottom: 10px; border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;
        }}
        .student-item:hover {{ transform: translateX(5px); }}
        .student-link {{
            display: block; padding: 20px; text-decoration: none; color: #333;
        }}
        .student-name {{ font-size: 18px; font-weight: 600; margin-bottom: 5px; }}
        .review-count {{ font-size: 14px; color: #666; }}
        .back-link {{
            display: inline-block; margin-bottom: 20px;
            color: #004aea; text-decoration: none; font-size: 16px;
        }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← All Evaluations</a>
    <h1>Graphic Design 472 — CP Evaluations</h1>
    <div class="subtitle">Concept Prototype Evaluation 1 — March 2026</div>

    <div class="stats">
        <strong>Total Students:</strong> {len(files)}<br>
        <strong>Total Reviews:</strong> {total_reviews}
    </div>

    <ul class="student-list">
"""

    for filename in sorted(files):
        key = filename_to_key.get(filename, "")
        student_short = next(
            (c for c in reviews_data.keys() if _student_key(c) == key), None
        )
        if student_short is None:
            continue
        data = reviews_data[student_short]
        sname = display_name(student_short)
        peer_count = len(data["peer_reviews"])
        instructor_count = len(data["instructor_reviews"])

        html += f"""
        <li class="student-item">
            <a href="{filename}" class="student-link">
                <div class="student-name">{sname}</div>
                <div class="review-count">
                    {peer_count} peer review{'s' if peer_count != 1 else ''}
                    {f' • {instructor_count} instructor review' if instructor_count > 0 else ''}
                </div>
            </a>
        </li>
"""

    html += """
    </ul>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Generated cp_forms_output/index.html")


# ---------------------------------------------------------------------------
# Root index.html  (unified list with per-student evaluation buttons)
# ---------------------------------------------------------------------------
def create_root_index(oc_output_dir: str, cp_output_dir: str,
                      cp_reviews_data: dict, cp_filename_map: dict) -> None:
    """
    Generate root index.html as a single student list.
    Each row shows the student name alongside buttons for every evaluation
    they have been reviewed in (OC Presentation 1, Concept Prototype 1, …).
    """
    oc_filename_map = load_or_create_filename_map(oc_output_dir)

    # Union of all student keys across both evaluations
    all_keys = sorted(set(oc_filename_map.keys()) | set(cp_filename_map.keys()))

    items_html = ""
    for key in all_keys:
        sname   = display_name(key) if key in DISPLAY_NAME_BY_FIRST_LOWER else key.title()
        oc_file = oc_filename_map.get(key)
        cp_file = cp_filename_map.get(key)

        btns = ""
        if oc_file:
            btns += (
                f'<a href="forms_output/{oc_file}" class="eval-btn oc-btn">'
                f'OC Presentation 1</a>'
            )
        if cp_file:
            btns += (
                f'<a href="cp_forms_output/{cp_file}" class="eval-btn cp-btn">'
                f'Concept Prototype 1</a>'
            )

        items_html += f"""
        <li class="student-item">
            <div class="student-row">
                <span class="student-name">{sname}</span>
                <div class="eval-btns">{btns}</div>
            </div>
        </li>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graphic Design 472 — Evaluations</title>
    <link rel="icon" href="forms_output/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="forms_output/styles.css">
    <style>
        body {{ background-color: #f5f5f5; }}

        .subtitle {{ color: #888; margin-bottom: 28px; font-size: 16px; }}

        /* ---- Student list ---- */
        .student-list {{ list-style: none; padding: 0; }}
        .student-item {{
            background-color: white;
            margin-bottom: 10px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        .student-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 16px 20px;
            flex-wrap: wrap;
        }}
        .student-name {{
            font-size: 18px;
            font-weight: 600;
            color: #111;
        }}

        /* ---- Evaluation buttons ---- */
        .eval-btns {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .eval-btn {{
            display: inline-block;
            padding: 7px 18px;
            border-radius: 999px;
            font-family: 'Diatype', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            border: 2px solid;
            transition: background-color 0.15s, color 0.15s;
            white-space: nowrap;
        }}
        .oc-btn {{
            color: #000;
            border-color: #000;
        }}
        .oc-btn:hover {{
            background-color: #000;
            color: #fff;
        }}
        .cp-btn {{
            color: #004aea;
            border-color: #004aea;
        }}
        .cp-btn:hover {{
            background-color: #004aea;
            color: #fff;
        }}
    </style>
</head>
<body>
    <h1>Graphic Design 472</h1>
    <p class="subtitle">Select a student to view their evaluation forms.</p>

    <ul class="student-list">
{items_html}
    </ul>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Generated root index.html (unified student list with evaluation buttons)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    csv_file   = "data/Concept Prototype • Evaluation 1 (Responses) - Form Responses 1.csv"
    output_dir = "cp_forms_output"
    oc_dir     = "forms_output"

    os.makedirs(output_dir, exist_ok=True)

    print("Parsing CP CSV data…")
    reviews_by_student = parse_csv(csv_file)

    filename_map = load_or_create_filename_map(output_dir)

    print(f"\nGenerating forms for {len(reviews_by_student)} students…\n")
    generated_files = []

    for student_name, data in sorted(reviews_by_student.items()):
        out_name = get_student_filename(student_name, filename_map)
        generate_html_form(student_name, data, output_dir, out_name)
        peer_count       = len(data["peer_reviews"])
        instructor_count = len(data["instructor_reviews"])
        print(f"✓ {display_name(student_name):20s}  →  {out_name}")
        print(f"    {peer_count} peer review(s)  /  {instructor_count} instructor review(s)")
        generated_files.append(out_name)

    print(f"\n{'='*60}")
    print(f"Generated {len(generated_files)} CP forms in '{output_dir}/'")
    print(f"{'='*60}\n")

    save_filename_map(output_dir, filename_map)
    create_cp_index(generated_files, output_dir, reviews_by_student, filename_map)
    create_root_index(oc_dir, output_dir, reviews_by_student, filename_map)

    cleanup_html(output_dir, keep=set(generated_files) | {"index.html"})


if __name__ == "__main__":
    main()
