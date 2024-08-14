#
# SmartPMEVO.py
# This file will interact with potentialy many sources
# and call other files to finish the SmartPM
# 
# SmartPMProcedure.py will be used to display procedural data to the engineer
# SmartPMReportTemplateJinja.py (not created yet, but do I need a file to handle all the variables that will go into the jinja edits, there are many of them.)
#
# SmartPM.py (this document) will be used to cordinate and pull data from
# Predictive service, CRM, Engineer, etc...

import tkinter as tk
from tkinter import messagebox
import subprocess

def run_procedure():
    subprocess.run(['python', 'SmartPMProcedure.py'])

def generate_report():
    subprocess.run(['python', 'SmartPMReport.py'])

def expert_mode():
    subprocess.run(['python', 'SmartPMExpert.py'])

def main():
    root = tk.Tk()
    root.title("SmartPM Main Menu")

    tk.Label(root, text="SmartPM Main Menu", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Run the Procedure", command=run_procedure, width=30).pack(pady=10)
    tk.Button(root, text="Generate the Report", command=generate_report, width=30).pack(pady=10)
    tk.Button(root, text="Expert Mode", command=expert_mode, width=30).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit, width=30).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()