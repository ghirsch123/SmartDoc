# known bugs, you can add steps to a section and it will auto fill and find these so long as you use the template in the .json,
# But whole new .json sections will not be found and also need added here
import json
from jinja2 import Template
from Latex_Compiler import compile_latex

# Load the JSON data
json_file_path = 'FSEInput.json'  # Ensure this is the correct path to your JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Print data structure for debugging
print("Data loaded:", type(data))
if isinstance(data, list):
    print("First item in data:", data[0])

# need to reformat images path since python saves it as images\\___.jpeg
def format_path_for_latex(path):
    formatted_path = path.replace('\\', '/')
    print(f"Formatted path for LaTeX: {formatted_path}")
    return formatted_path

# Define the LaTeX template for a generic table
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
    print(f"Rendered section for {section_key}:\n{rendered_section}")
    return rendered_section
    
# Generate LaTeX for all sections. Need it to be empty so that the json file can fill in the dictionary
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

# Populate the sections dictionary
for item in data:
    category = item.get("Category", "Uncategorized")
    if category in sections:
        sections[category].append(item)

# generate latex for all sections
latex_sections = ""
for section_title, section_data in sections.items():
    section_key = section_title.replace(" ", "")
    latex_sections += generate_latex_section(section_key, section_title, section_data) + "\n"

# need to generate latex template separate from the tables
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

render = Template(latex_template)
full_render = render.render(content=latex_sections)

# Save the rendered LaTeX tables to a file
with open('SmartPMReport.tex', 'w') as output_file:
    output_file.write(full_render)

print("LaTeX tables generated successfully.")

compile_latex('SmartPMReport.tex')