# file that loads EVO PM procedure from SmartPMProcedureEVO.json as a wesbite rather than a tkinter page

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from jinja2 import Template
import os
import json
import shutil
import subprocess
import sys

app = Flask(__name__)
app.secret_key = 'SmartPM'
app.config['UPLOAD_FOLDER'] = 'Images'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

# load procedure from JSON
def load_procedure(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
# save existing data
def save_procedure(data, filename='FSEInput.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# home route to display form
@app.route('/')
def index():
    procedure = load_procedure('SmartPMProcedure.json')
  # try to load existing data from FSEInput.json and merge it with the procedure

    try:
        with open('FSEInput.json', 'r') as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        saved_data = {}

    # merge saved_data into procedure
    for section, steps in saved_data.items():
        if section in procedure:
            for step, data in steps.items():
                if step in procedure[section]:
                    procedure[section][step]['Comment'] = data.get('Comment', '')
                    procedure[section][step]['SavedStatus'] = data.get('Status', '')
                    procedure[section][step]['Image'] = data.get('Image', '')

    return render_template('index.html', procedure=procedure)

# route to handle form submission and file upload
@app.route('/submit', methods=['POST'])
def submit():
    saved_data = {}

    try:
        with open('FSEInput.json', 'r') as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        saved_data = {}

    # need to iterate over the form data
    for key in request.form:
        if key.startswith('comment_'):
            section_step = key.split('_')[1:]
            section = section_step[0]
            step = section_step[1]
            comment = request.form.get(f'comment_{section}_{step}', '')
            status = request.form.get(f'status_{section}_{step}', '')

            if section not in saved_data:
                saved_data[section] = {}
            if step not in saved_data[section]:
                saved_data[section][step] = {}

            saved_data[section][step]['Comment'] = comment
            saved_data[section][step]['Status'] = status

            # upload images to folder
            image = request.files.get(f'image_{section}_{step}')
            if image and allowed_file(image.filename):
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_path)
                saved_data[section][step]['Image'] = image.filename
            elif image and not allowed_file(image.filename):
                flash('Invalid file type. Only .jpeg, .jpg, and .png files are allowed.', 'error')
                return redirect(url_for('index'))

    # save the updated procedure to FSEInput.json
    save_procedure(saved_data)

    generate_latex_and_compile(saved_data)

    flash('Data and images successfully submitted', 'success')
    flash('PDF successfully generated', 'success')
    return redirect(url_for('index'))

# Function to generate LaTeX for a section
def generate_latex_section(section_key, section_title, section_data):
    items = []
    for value in section_data:
        items.append({
            "ActionSummary": value.get("ActionSummary", ""),
            "Spec": value.get("Spec", ""),
            "Status": value.get("Status", ""),
            "Comment": value.get("Comment", ""),
            "Image": format_path_for_latex(value["Image"]) if "Image" in value and value["Image"] else ""
        })
    template = Template(table_template)
    rendered_section = template.render(section_key=section_key, section_title=section_title, items=items)
    return rendered_section

# Format image path for LaTeX
def format_path_for_latex(path):
    return path.replace('\\', '/')

# LaTeX table template
table_template = r"""
\refstepcounter{tablecount} % Increment table counter at the start of each table
\begin{table}[p]
\caption{ {{ section_title }} }
\label{tab:{{ section_key }}}
\begin{tabular}{
    @{}>{\raggedright\arraybackslash}p{0.04\linewidth}
    >{\raggedright\arraybackslash}p{0.36\linewidth}
    >{\raggedright\arraybackslash}p{0.37\linewidth}
    >{\raggedright\arraybackslash}p{0.13\linewidth}@{}}
    \textbf{No.} & \textbf{Action} & \textbf{Spec} & \textbf{Status} \\
    \hline
    {% for item in items %}
    \stepcounter{itemcount}\theitemcount & {{ item.ActionSummary }} & {{ item.Spec }} & {{ item.Status }} \\
    {% if item.Comment %}Note: & \multicolumn{3}{l}{ {{ item.Comment }} } \\\\ \hline{% else %}\hline{% endif %}
    {% if item.Image %}\includegraphics[width=\textwidth, height = 0.3\textheight]{{ '{' }}{{ item.Image }}{{ '}' }} \\\\ \hline{% endif %}
    {% endfor %}
\end{tabular}
\end{table}
"""

# LaTeX document template
latex_template = r"""
\documentclass{article}
\usepackage{array}
\usepackage{graphicx}
\newcounter{tablecount}
\newcounter{itemcount}
\begin{document}

{{ content }}

\end{document}
"""

# Function to compile LaTeX to PDF
def compile_latex(file_name):
    pdflatex_cmd = shutil.which('pdflatex')
        
    if not pdflatex_cmd:
        print("Failed to generate PDF: MikTeX is not installed")
        print("Please download and install MiKTeX from https://miktex.org/download")
        sys.exit(1) # exit the program

    try:
        result = subprocess.run([pdflatex_cmd, file_name], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"PDF generated successfully: {file_name.replace('.tex', '.pdf')}")
        else:
            print(f"Error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.output}")

# Function to generate LaTeX and compile it
def generate_latex_and_compile(data):
    sections = {
        "General Condition of System and Environment": [],
        "Safety Checks": [],
        "Computer": [],
        "Vacuum System and Column Maintenance": [],
        "Pumps": [],
        "Specimen Stage": [],
        "Detectors": [],
        "SEM Filament": [],
        "Electron Optics": [],
        "Final Tasks": []
    }

    for section, steps in data.items():
        if section in sections:
            for step, details in steps.items():
                sections[section].append({
                    "ActionSummary": step,
                    "Spec": "",
                    "Status": details.get("Status", ""),
                    "Comment": details.get("Comment", ""),
                    "Image": format_path_for_latex(os.path.join(app.config['UPLOAD_FOLDER'], details["Image"])) if "Image" in details and details["Image"] else ""
                })

    latex_sections = ""
    for section_title, section_data in sections.items():
        section_key = section_title.replace(" ", "")
        latex_sections += generate_latex_section(section_key, section_title, section_data) + "\n"

    render = Template(latex_template)
    full_render = render.render(content=latex_sections)

    with open('SmartPMReport.tex', 'w') as output_file:
        output_file.write(full_render)

    compile_latex('SmartPMReport.tex')

# route to images
@app.route('/Images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  # display the image from the image directory

# adding option to delete data
@app.route('/delete', methods=['POST'])
def delete_data():
    if os.path.exists('FSEInput.json'):
        os.remove('FSEInput.json')
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'])
    latex_files = ['SmartPMReport.aux', 'SmartPMReport.log', 'SmartPMReport.pdf', 'SmartPMReport.tex', 'texput.log']
    for file_name in latex_files:
        if os.path.exists(file_name):
            os.remove(file_name)
    flash('Data and images successfully deleted', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)