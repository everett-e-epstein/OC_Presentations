# OC Evaluation Forms Generator

This tool generates individual evaluation forms for each student in Graphic Design 452, based on peer and instructor feedback collected via Google Forms.

## What This Tool Does

- **Parses CSV data** from Google Forms responses
- **Organizes reviews** by student (reviewee)
- **Separates peer reviews** from **instructor reviews** (Everett)
- **Generates 17 individual HTML forms** that can be downloaded as PDFs
- **Creates an index page** for easy navigation

## Features

✅ **17 Individual Forms** - One for each student who was reviewed  
✅ **Visual Chart** - Interactive line chart showing all ratings at a glance  
✅ **Peer Reviews Section** - All peer feedback grouped together  
✅ **Instructor Section** - Everett's reviews clearly separated with distinct styling  
✅ **PDF Download** - Each form can be easily printed or saved as PDF  
✅ **Professional Design** - Clean, readable format matching the OC_Example.pdf style  

## How to Use

### 1. Generate the Forms

Run the Python script to generate all forms:

```bash
python3 generate_forms.py
```

This will:
- Read the CSV file from the `data/` folder
- Generate 17 HTML forms in the `forms_output/` folder
- Create an `index.html` file for easy navigation

### 2. View the Forms

Open the `index.html` file in your web browser:

```bash
open forms_output/index.html
```

Or navigate to `forms_output/` and double-click `index.html`

### 3. Download Individual Forms as PDF

For each student form:
1. Click on the student's name in the index page
2. Click the "Download as PDF" button at the top
3. Or use your browser's print function (Ctrl+P / Cmd+P)
4. Select "Save as PDF" as the destination
5. Save the PDF file

## File Structure

```
OC_Tool/
├── data/
│   └── OC • Evaluation 1 (Responses) - Form Responses 1.csv
├── forms_output/
│   ├── index.html                    # Main navigation page
│   ├── Madelyn_OC_Evaluation.html    # Individual forms...
│   ├── Julia_OC_Evaluation.html
│   ├── Belle_OC_Evaluation.html
│   └── ... (17 total)
├── generate_forms.py                 # Main script
├── README.md                         # This file
└── OC_Example.pdf                    # Reference format
```

## Form Format

Each form includes:

### Header
- Course title: "Graphic Design 452 - OC"
- Student name
- Date of evaluation

### Visual Chart
- Interactive line chart showing all ratings across 6 categories
- Each reviewer has their own colored line
- Instructor (Everett) shown with a distinct black line
- Categories: Structure, Transitions, Speaking, Visuals, Engagement, Q+A
- Y-axis: Rating scale 1-5

### Peer Reviews Section
- Reviewer name
- Project description (in their own words)
- 6 evaluation criteria with ratings and comments:
  - Q1: Structure + Sequence
  - Q2: Summaries + Transitions
  - Q3: Speaking
  - Q4: Visuals
  - Q5: Audience Engagement
  - Q6: Q+A
- Additional comments

### Instructor Review Section (Everett)
- **Clearly separated** with distinct background styling
- Same evaluation criteria as peer reviews
- Prominent visual distinction with gray background and left border

## Customization

To regenerate forms with updated data:

1. Replace the CSV file in the `data/` folder
2. Run `python3 generate_forms.py` again
3. New forms will overwrite the old ones in `forms_output/`

## Requirements

- Python 3.x (no additional packages required)
- Web browser (for viewing and downloading PDFs)

## Notes

- The script automatically separates "Everett" reviews as instructor reviews
- All other reviewers are treated as peer reviews
- Forms are styled to be print-friendly
- Each form can be downloaded independently as a PDF
