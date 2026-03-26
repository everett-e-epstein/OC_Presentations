#!/usr/bin/env python3
"""
Generate individual OC evaluation forms for each student.
Separates Everett's (instructor) reviews from peer reviews.
"""

import csv
from collections import defaultdict
from datetime import datetime
import os
import json
import secrets

# Question mapping from the CSV to readable labels
QUESTIONS = {
    "01. STRUCTURE + SEQUENCE": "Q1: Structure + Sequence",
    "02. SUMMARIES + TRANSITIONS (flow)": "Q2: Summaries + Transitions",
    "03. SPEAKING": "Q3: Speaking",
    "04. VISUALS": "Q4: Visuals",
    "05. AUDIENCE ENGAGEMENT": "Q5: Audience Engagement",
    "06. Q+A": "Q6: Q+A"
}

# Display names (reviewee in CSV is typically first name; we render First Last)
DISPLAY_NAME_BY_FIRST_LOWER = {
    "madelyn": "Madelyn Baur",
    "julia": "Julia Beers",
    "louisa": "Louisa Benedict",
    "natalie": "Natalie Broyles",
    "belle": "Belle Clement",
    "sophia": "Sophia Crosby",
    "conner": "Conner Evans",
    "maggie": "Maggie Evans",
    "emma": "Emma Fingeret",
    "tala": "Tala Ghezawi",
    "xavier": "Xavier Girard",
    "delaney": "Delaney Kohlstedt",
    "alex": "Alex Long",
    "elyse": "Elyse Lundberg",
    "ella": "Ella Merkel",
    "hannah": "Hannah Smith",
    "donatella": "Donatella Thomas",
    "sam": "Sam Tugman",
    "jeremy": "Jeremy Wilkins",
}

def display_name(name: str) -> str:
    raw = (name or "").strip()
    if not raw:
        return ""
    return DISPLAY_NAME_BY_FIRST_LOWER.get(raw.lower(), raw)


def _html_comment_body(text: str) -> str:
    """Preserve line breaks from form responses in HTML."""
    if not text:
        return text
    return text.replace("\r\n", "\n").replace("\n", "<br />\n")


def _student_key(student_name: str) -> str:
    return (student_name or "").strip().lower()

def load_or_create_filename_map(output_dir: str) -> dict:
    """
    Map student keys -> random filename (stable across reruns).
    Stored inside forms_output so only the instructor tooling needs it.
    """
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
    token = secrets.token_hex(10)  # 20 hex chars, hard to guess
    filename = f"{token}.html"
    filename_map[key] = filename
    return filename

def _normalize_reviewee(name: str) -> str:
    """
    Normalize a reviewee name to a canonical first-name-only lowercase key.
    Handles case variants (e.g. 'Sophia' vs 'sophia') and full names
    (e.g. 'Hannah Smith' → 'hannah') by checking against DISPLAY_NAME_BY_FIRST_LOWER.
    """
    raw = name.strip()
    if not raw:
        return ""
    lower = raw.lower()
    # If it's already a known first-name key, return it
    if lower in DISPLAY_NAME_BY_FIRST_LOWER:
        return lower
    # Check if it matches a full display name (e.g. "Hannah Smith" → "hannah")
    for key, full in DISPLAY_NAME_BY_FIRST_LOWER.items():
        if full.lower() == lower:
            return key
    # Fall back to lowercase for consistent keying
    return lower


def parse_csv(filename):
    """Parse the CSV file and organize reviews by reviewee."""
    reviews_by_student = defaultdict(lambda: {"peer_reviews": [], "instructor_reviews": []})
    
    # Mapping of question keys to their comment columns (in exact CSV order)
    comment_columns = {
        "01. STRUCTURE + SEQUENCE": ":::: Comments on structure/sequence ... is there an adequate amount of research to inform the project?",
        "02. SUMMARIES + TRANSITIONS (flow)": ":::: Comments on flow ...",
        "03. SPEAKING": ":::: Comments on oral presentation ... consider if the word choice allowed for an open interpretation of the content. ",
        "04. VISUALS": ":::: Comments on visual presentation ...",
        "05. AUDIENCE ENGAGEMENT": ":::: Comments on engaging the audience ... consider how the presenter addressed logos, ethos, and pathos in their engagement of the audience. ",
        "06. Q+A": ":::: Comments on Q+A interaction ..."
    }
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviewee = _normalize_reviewee(row.get("Who you are reviewing:", ""))
            reviewer = (row.get("Your name:", "") or "").strip()
            
            if not reviewee or not reviewer:
                continue
            
            # Parse ratings and comments
            review_data = {
                "reviewer": reviewer,
                "timestamp": row.get("Timestamp", ""),
                "project_description": row.get("In your words, describe what this project is about:", ""),
                "ratings": {},
                "comments": {},
                "additional_comments": row.get("ANY ADDITIONAL COMMENTS FOR PRESENTER ...", "")
            }
            
            # Extract ratings and comments for each question
            for q_key, q_label in QUESTIONS.items():
                rating = row.get(q_key, "").strip()
                comment_col = comment_columns.get(q_key, "")
                comment = row.get(comment_col, "").strip()
                
                review_data["ratings"][q_label] = rating
                review_data["comments"][q_label] = comment
            
            # Categorize as instructor or peer review
            if reviewer.lower() == "everett":
                reviews_by_student[reviewee]["instructor_reviews"].append(review_data)
            else:
                reviews_by_student[reviewee]["peer_reviews"].append(review_data)
    
    return reviews_by_student

def prepare_chart_data(data, *, instructor_line_color="#000000"):
    """Prepare data for Chart.js visualization."""
    import json
    
    # Define category labels (shortened for chart)
    categories = [
        "Structure",
        "Transitions", 
        "Speaking",
        "Visuals",
        "Engagement",
        "Q+A"
    ]
    
    # Full question labels for mapping
    full_labels = list(QUESTIONS.values())
    
    # Custom color scheme as specified (match pills/graph)
    colors = [
        '#ff2bd6',  # Peer 1 (magenta - more visible than yellow)
        '#004aea',  # Blue
        '#006834',  # Dark green
        '#ff610b',  # Peer 4 (orange)
    ]
    
    datasets = []
    color_index = 0
    peer_count = 1
    peer_original_series = []
    
    # Add peer review datasets (anonymized)
    for review in data["peer_reviews"]:
        ratings_list = []
        for q_label in full_labels:
            rating = review["ratings"].get(q_label, "")
            try:
                ratings_list.append(float(rating) if rating else None)
            except ValueError:
                ratings_list.append(None)
        
        peer_original_series.append(ratings_list)

        datasets.append({
            "label": f"Peer {peer_count}",  # Anonymous label
            "data": ratings_list,
            "originalData": ratings_list,
            "borderColor": colors[color_index % len(colors)],
            # Use solid fill so legend items are filled (not transparent)
            "backgroundColor": colors[color_index % len(colors)],
            "fill": False
        })
        color_index += 1
        peer_count += 1
    
    # If multiple peers have identical series, apply a tiny visual offset so lines don't overlap.
    # Also ensure earlier peers draw on top within identical groups.
    key_to_indices = {}
    for i, series in enumerate(peer_original_series):
        key = tuple(series)
        key_to_indices.setdefault(key, []).append(i)

    for _, indices in key_to_indices.items():
        if len(indices) <= 1:
            continue

        # Spread offsets around 0: e.g. 2 -> [+0.02, -0.02], 3 -> [+0.04, 0, -0.04]
        # Slightly larger step so overlaps at y=5 are visible (especially after adding 0–6 headroom)
        step = 0.08
        mid = (len(indices) - 1) / 2.0

        for rank_in_group, dataset_idx in enumerate(indices):
            delta = (mid - rank_in_group) * step

            original = datasets[dataset_idx].get("originalData", [])
            adjusted = []
            for v in original:
                if v is None:
                    adjusted.append(None)
                else:
                    nv = v + delta
                    if nv < 0:
                        nv = 0
                    # Allow slight overshoot above 5 since we render the chart on a 0–6 scale
                    if nv > 6:
                        nv = 6
                    adjusted.append(nv)

            datasets[dataset_idx]["data"] = adjusted
            # Draw earlier peers on top (Peer 1 above Peer 2, etc.) when overlapping
            datasets[dataset_idx]["order"] = 1000 - dataset_idx

    # Add instructor review dataset with distinct styling (not anonymous)
    for review in data["instructor_reviews"]:
        ratings_list = []
        for q_label in full_labels:
            rating = review["ratings"].get(q_label, "")
            try:
                ratings_list.append(float(rating) if rating else None)
            except ValueError:
                ratings_list.append(None)
        
        datasets.append({
            "label": "Everett",  # Keep instructor name
            "data": ratings_list,
            "borderColor": instructor_line_color,
            # Solid fill so legend is filled
            "backgroundColor": instructor_line_color,
            "borderWidth": 4,
            "borderDash": [],
            "fill": False
        })
    
    chart_data = {
        "labels": categories,
        "datasets": datasets
    }
    
    return json.dumps(chart_data)

def generate_html_form(
    student_name,
    data,
    output_dir,
    output_filename,
    *,
    oc_label="OC Presentation 1",
    styles_href="styles.css",
    favicon_href="favicon.svg",
    instructor_chart_color="#000000",
):
    """Generate an HTML form for a single student matching the PDF format."""
    
    # Prepare chart data
    chart_data = prepare_chart_data(
        data, instructor_line_color=instructor_chart_color
    )
    student_display = display_name(student_name)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OC Evaluation - {student_display}</title>
    <link rel="icon" href="{favicon_href}" type="image/svg+xml">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="{styles_href}">
</head>
<body>
    <div class="fixed-topbar">
        <div class="oc-title">{oc_label}</div>
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
    
    # Add peer reviews section
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
            
            if review["project_description"]:
                html += f"""
            <div class="project-description">
                "{_html_comment_body(review['project_description'])}"
            </div>
"""
            
            # Add each question with rating and comment
            for q_label in QUESTIONS.values():
                rating = review["ratings"].get(q_label, "")
                comment = review["comments"].get(q_label, "")
                
                if rating or comment:
                    html += f"""
            <div class="question">
                <div class="question-left">
                    <div class="question-label">{q_label}</div>
"""
                    if comment:
                        html += f"""
                    <div class="comment">{_html_comment_body(comment)}</div>
"""
                    html += f"""
                </div>
                <div class="rating"><span class="grade-circle">{rating}</span></div>
"""
                    html += """
            </div>
"""
            
            # Add additional comments if present
            if review["additional_comments"]:
                html += f"""
            <div class="additional-comments">
                <div class="additional-comments-label">Additional Comments:</div>
                <div>{_html_comment_body(review['additional_comments'])}</div>
            </div>
"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
"""
    
    # Add instructor reviews section (Everett)
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
            
            if review["project_description"]:
                html += f"""
            <div class="project-description">
                "{_html_comment_body(review['project_description'])}"
            </div>
"""
            
            # Add each question with rating and comment
            for q_label in QUESTIONS.values():
                rating = review["ratings"].get(q_label, "")
                comment = review["comments"].get(q_label, "")
                
                if rating or comment:
                    html += f"""
            <div class="question">
                <div class="question-left">
                    <div class="question-label">{q_label}</div>
"""
                    if comment:
                        html += f"""
                    <div class="comment">{_html_comment_body(comment)}</div>
"""
                    html += f"""
                </div>
                <div class="rating"><span class="grade-circle">{rating}</span></div>
"""
                    html += """
            </div>
"""
            
            # Add additional comments if present
            if review["additional_comments"]:
                html += f"""
            <div class="additional-comments">
                <div class="additional-comments-label">Additional Comments:</div>
                <div>{_html_comment_body(review['additional_comments'])}</div>
            </div>
"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
"""
    
    html += f"""
    <script>
        // Chart data
        const chartData = {chart_data};
        
        // Create the chart
        const ctx = document.getElementById('ratingsChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.labels,
                datasets: chartData.datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 6,
                        ticks: {{
                            stepSize: 1,
                            callback: function(value) {{
                                // Keep headroom to 6 but don't label it (so it still reads as a 1–5 rubric)
                                return value === 6 ? '' : value;
                            }}
                        }},
                        title: {{
                            display: false
                        }}
                    }},
                    x: {{
                        title: {{
                            display: false
                        }}
                    }}
                }},
                elements: {{
                    line: {{
                        tension: 0.4,
                        borderWidth: 3
                    }},
                    point: {{
                        radius: 5,
                        hitRadius: 10,
                        hoverRadius: 7
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const ds = ctx.dataset || {{}};
                                const orig = (ds.originalData && ds.originalData[ctx.dataIndex] != null) ? ds.originalData[ctx.dataIndex] : ctx.parsed.y;
                                const v = (orig == null) ? '' : String(orig);
                                return `${{ds.label}}: ${{v}}`;
                            }}
                        }}
                    }},
                    title: {{ display: false }}
                }}
            }}
        }});

        // Custom pill legend (filled pills in dataset colors)
        function legendTextColor(hex) {{
            if (!hex || typeof hex !== 'string' || !hex.startsWith('#') || (hex.length !== 7 && hex.length !== 4)) {{
                return '#ffffff';
            }}
            let r, g, b;
            if (hex.length === 4) {{
                r = parseInt(hex[1] + hex[1], 16);
                g = parseInt(hex[2] + hex[2], 16);
                b = parseInt(hex[3] + hex[3], 16);
            }} else {{
                r = parseInt(hex.slice(1, 3), 16);
                g = parseInt(hex.slice(3, 5), 16);
                b = parseInt(hex.slice(5, 7), 16);
            }}
            // Relative luminance
            const lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
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
    
    # Write the HTML file
    filepath = os.path.join(output_dir, output_filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_filename

def main():
    """Main function to generate all forms."""
    csv_file = "data/OC • Evaluation 1 (Responses) - Form Responses 1 (1).csv"
    output_dir = "forms_output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse CSV data
    print("Parsing CSV data...")
    reviews_by_student = parse_csv(csv_file)

    # Load or create stable random filenames for each student
    filename_map = load_or_create_filename_map(output_dir)
    
    # Generate HTML forms for each student
    print(f"\nGenerating forms for {len(reviews_by_student)} students...\n")
    
    generated_files = []
    for student_name, data in sorted(reviews_by_student.items()):
        out_name = get_student_filename(student_name, filename_map)
        filename = generate_html_form(student_name, data, output_dir, out_name)
        peer_count = len(data["peer_reviews"])
        instructor_count = len(data["instructor_reviews"])
        print(f"✓ Generated: {filename}")
        print(f"  - {peer_count} peer review(s)")
        print(f"  - {instructor_count} instructor review(s)")
        generated_files.append(filename)
    
    print(f"\n{'='*60}")
    print(f"Successfully generated {len(generated_files)} forms in '{output_dir}/' directory")
    print(f"{'='*60}")
    print("\nTo download as PDF:")
    print("1. Open any HTML file in a web browser")
    print("2. Click the 'Download as PDF' button (or use Ctrl/Cmd+P)")
    print("3. Save as PDF")
    
    # Persist filename map + create an index file
    save_filename_map(output_dir, filename_map)
    create_index(generated_files, output_dir, reviews_by_student, filename_map)

    # Cleanup: remove old predictable files and any stale html pages not in our new set
    cleanup_html(output_dir, keep=set(generated_files) | {"index.html"})

def create_index(files, output_dir, reviews_data, filename_map):
    """Create an index.html page to access all forms."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OC Evaluation Forms - Index</title>
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="styles.css">
    <style>
        /* Index-specific styles */
        body {
            background-color: #f5f5f5;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        
        .stats {
            background-color: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .student-list {
            list-style: none;
            padding: 0;
        }
        
        .student-item {
            background-color: white;
            margin-bottom: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .student-item:hover {
            transform: translateX(5px);
        }
        
        .student-link {
            display: block;
            padding: 20px;
            text-decoration: none;
            color: #333;
        }
        
        .student-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .review-count {
            font-size: 14px;
            color: #666;
        }
        
        .instructor-badge {
            display: inline-block;
            background-color: #333;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <h1>Graphic Design 452 - OC Evaluations</h1>
    <div class="subtitle">Evaluation 1 - February 2026</div>
    
    <div class="stats">
        <strong>Total Students:</strong> """ + str(len(files)) + """<br>
        <strong>Total Reviews:</strong> """ + str(sum(len(data["peer_reviews"]) + len(data["instructor_reviews"]) for data in reviews_data.values())) + """
    </div>
    
    <ul class="student-list">
"""
    
    # Build reverse lookup: filename -> student key
    filename_to_key = {v: k for k, v in filename_map.items() if isinstance(v, str)}

    for filename in sorted(files):
        key = filename_to_key.get(filename, "")
        # Find the original student_name (as used in reviews_data) by key
        student_short = None
        for candidate in reviews_data.keys():
            if _student_key(candidate) == key:
                student_short = candidate
                break
        if student_short is None:
            continue

        data = reviews_data[student_short]
        student_name = display_name(student_short)
        peer_count = len(data["peer_reviews"])
        instructor_count = len(data["instructor_reviews"])
        
        html += f"""
        <li class="student-item">
            <a href="{filename}" class="student-link">
                <div class="student-name">
                    {student_name}
                    {' <span class="instructor-badge">Instructor Review</span>' if instructor_count > 0 else ''}
                </div>
                <div class="review-count">
                    {peer_count} peer review{'s' if peer_count != 1 else ''}{f' • {instructor_count} instructor review' if instructor_count > 0 else ''}
                </div>
            </a>
        </li>
"""
    
    html += """
    </ul>
</body>
</html>
"""
    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ Generated index.html - Open this file to access all forms")

def cleanup_html(output_dir: str, keep: set) -> None:
    """Remove any .html files in the output_dir not in keep."""
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

if __name__ == "__main__":
    main()
