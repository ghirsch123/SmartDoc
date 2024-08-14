# this python script is intended to be run after a .tex file has been generated to 
# turn that file into a PDF. It needs miktex to do this, so I've placed a portable
# version of this in a folder called 'miktex.' If previosly installed, this program
# will ignore this step and proceed.

import subprocess
import os
import shutil
import sys

def compile_latex(file_name):
    # can get path of current directory using __file__
    print("Starting the LaTeX compilation process...")
    current_directory = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(current_directory, file_name)
    images_dir = os.path.join(current_directory, 'Images')
    
    # see if miktex is installed globally
    pdflatex_cmd = shutil.which('pdflatex')
        
    if not pdflatex_cmd:
        # need mixtek installed to generate PDF from .tex file
        print("Failed to generate PDF: MikTeX is not installed")
        print("Please download and install MiKTeX from https://miktex.org/download")
        sys.exit(1) # exit the program

    print(f"Found pdflatex at: {pdflatex_cmd}")
    print(f"Compiling LaTeX file at: {file_path}")

    # try to run
    try:
        result = subprocess.run([pdflatex_cmd, file_path], capture_output=True, text=True, check=True)
        print("LaTeX compilation process finished.")

        print("Standard Output:\n", result.stdout)
        print("Standard Error:\n", result.stderr)

        if result.returncode == 0:
            print(f"PDF generated successfully: {file_name.replace('.tex', '.pdf')}")
            # remove images directory if PDF is generated successfully
            #if os.path.exists(images_dir):
                #shutil.rmtree(images_dir)
        else:
            print(f"Error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.output}")

if __name__ == "__main__":
    # name of latex file
    latex_file = 'SmartPMReport.tex'

    # run compiler
    compile_latex(latex_file)