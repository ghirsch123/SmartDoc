from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import json
import os

app = Flask(__name__)

# Load JSON data
def load_procedure(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
# save existing data
def save_procedure(data, filename='FSEInput.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

@app.route('/')
def index():
    procedure = load_procedure('SmartMentorChecklist.json')

    try:
        with open('FSEInput.json', 'r') as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        saved_data = {}

    # merge saved_data into procedure
    for section, steps in saved_data.items():
        if section in procedure['sections']:
            for step, data in steps.items():
                if step in procedure['sections'][section]:
                    procedure['sections'][section][step]['MentorInitials'] = data.get('MentorInitials', '')
                    procedure['sections'][section][step]['DateComments'] = data.get('DateComments', '')
                    procedure['sections'][section][step]['Level'] = data.get('Level', '')
                    
    procedure['Signatures'] = saved_data.get('Signatures', {
        'FSE_Signature': '',
        'FSE_Date': '',
        'Mentor_Signature': '',
        'Mentor_Date': ''
    })
    
    return render_template('index.html', procedure=procedure)

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
        if key.startswith('mentor_') or key.startswith('date_comments_') or key.startswith('level_'):
            section_step = key.split('_')[1:]
            if len(section_step) < 2:
                continue
            section = section_step[0]
            step = section_step[1]
            mentor_initials = request.form.get(f'mentor_{section}_{step}', '')
            date_comments = request.form.get(f'date_comments_{section}_{step}', '')
            level = request.form.get(f'level_{section}_{step}', '')

            if section not in saved_data:
                saved_data[section] = {}
            if step not in saved_data[section]:
                saved_data[section][step] = {}

            saved_data[section][step]['MentorInitials'] = mentor_initials
            saved_data[section][step]['DateComments'] = date_comments
            saved_data[section][step]['Level'] = level

    fse_signature = request.form.get('fse_signature', '')
    fse_date = request.form.get('fse_date', '')
    mentor_signature = request.form.get('mentor_signature', '')
    mentor_date = request.form.get('mentor_date', '')

    saved_data['Signatures'] = {
        'FSE_Signature': fse_signature,
        'FSE_Date': fse_date,
        'Mentor_Signature': mentor_signature,
        'Mentor_Date': mentor_date
    }

    # save the updated procedure to FSEInput.json
    save_procedure(saved_data)

    return redirect(url_for('index'))

# adding option to delete data
@app.route('/delete', methods=['POST'])
def delete_data():
    if os.path.exists('FSEInput.json'):
        os.remove('FSEInput.json')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
