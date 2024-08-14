import json
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import shutil

def load_procedure(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_data(data, filename='FSEInput.json'):
    print(f"Saving data to {filename}")
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

# function that removes current json file
def clear_data(filename = 'FSEInput.json'):
    current_directory = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(current_directory, 'Images')
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)

class ProcedureApp:
    def __init__(self, root, procedure, current_step = 0, saved_data=None):
        self.root = root
        self.procedure = procedure
        self.steps = self.flatten_procedure(procedure)
        self.current_step = current_step # modify current_step
        self.procedure_steps = saved_data if saved_data else [] # modify procedure step if there is saved_data, if not start from beginning
        self.image_paths = {} # dictionary to save image paths
        self.create_widgets()
        self.load_step()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # prevents user from just closing the window

    def flatten_procedure(self, procedure):
        steps = []
        for category, steps_dict in procedure.items():
            for step_name, step_data in steps_dict.items():
                step_data["Step"] = step_name
                step_data["Category"] = category
                steps.append(step_data)
        return steps

    def create_widgets(self):
        self.title = tk.Label(self.root, text="Procedure Steps", font=("Helvetica", 16))
        self.title.pack(pady=20)

        self.step_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.step_label.pack(pady=10)

        self.display_procedure = tk.Label(self.root, text="", font=("Helvetica", 10))
        self.display_procedure.pack(pady=5)

        self.references = tk.Label(self.root, text="", font=("Helvetica", 10))
        self.references.pack(pady=5)

        self.comment_label = tk.Label(self.root, text="Comment:", font=("Helvetica", 12))
        self.comment_label.pack(pady=5)

        self.comment_entry = tk.Entry(self.root, width=50)
        self.comment_entry.pack(pady=5)

        self.status_label = tk.Label(self.root, text="Status:", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.status_var = tk.StringVar(value="__none__") # setting a null value so all bullets are not selected by default
        self.status_options = ["In Order", "Out of Order", "NA", "Other"]
        self.status_radiobuttons = []
        for option in self.status_options:
            rb = tk.Radiobutton(self.root, text=option, variable=self.status_var, value=option)
            rb.pack(anchor=tk.W)
            self.status_radiobuttons.append(rb)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady = 20)

        self.back_button = tk.Button(self.button_frame, text = "Back", command = self.back_step) # adding a back button
        self.back_button.pack(side = tk.LEFT, padx = 5)

        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_step)
        self.next_button.pack(side = tk.LEFT, padx = 5)

        self.upload_button = tk.Button(self.root, text = "Upload Image", command=self.upload_image)
        self.upload_button.pack(pady = 5)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_procedure)
        self.exit_button.pack(pady=5)

        self.graham_logo()

    # function to upload images and store them in a new directory "Images"
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[('Image files', ['*.jpg', '*.jpeg', '*.png'])])
        if file_path:
            print(f"File selected: {file_path}")
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension not in [".jpg", ".jpeg", ".png"]:
                messagebox.showerror("Error", "Invalid file type. Please upload a .jpg, .jpeg, or .png file.")
            else:
                image_dir = 'Images'
                # if image directory doesn't exist, create new directory
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)

                # want each file to have a unique name
                image_filename = os.path.basename(file_path)
                new_file_path = os.path.join(image_dir, image_filename)

                base, extension = os.path.splitext(image_filename)
                # to keep track of all the files within the directory
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(image_dir, f"{base}_{counter}{extension}")
                    counter += 1
                shutil.copy(file_path, new_file_path)
                # save image path in dictionary
                self.image_paths[self.current_step] = new_file_path
                print(f"Image path stored for step {self.current_step}: {new_file_path}")
                messagebox.showinfo('Info', 'Image uploaded successfully.')

    def graham_logo(self):
        image = Image.open("Graham.png")
        image = image.resize((120, 120), Image.Resampling.LANCZOS)
        self.graham = ImageTk.PhotoImage(image)
        self.logo_label = tk.Label(self.root, image=self.graham)
        self.logo_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def load_step(self):
        if 0 <= self.current_step < len(self.steps):
            # check if current step already exists in data
            if self.current_step < len(self.procedure_steps):
                step = self.procedure_steps[self.current_step]
            else:
                step = self.steps[self.current_step]

            self.step_label.config(text=f"Step: {step['Step']} - Category: {step['Category']}")
            self.display_procedure.config(text=f"Display Procedure: {step['DisplayProcedure']}")
            self.references.config(text=f"References: {step['References']}")
            self.status_var.set(step.get('Status', "__none__"))  # initialize buttons to be whatever the current status is, if there's no status no bullets will be selected
            self.comment_entry.delete(0, tk.END)
            self.comment_entry.insert(0, step.get('Comment', '')) # if going back, get comment from previous page

            # want to disable the back button for the first page
            if self.current_step > 0:
                self.back_button.config(state=tk.NORMAL)
            else:
                self.back_button.config(state=tk.DISABLED)

        else:
            messagebox.showinfo("Info", "All steps completed.")
            self.exit_procedure()

    # function to go forward a step
    def next_step(self):
        self.save_current_step()

        comment = self.comment_entry.get()
        status = self.status_var.get()

        if status and status != "__none__" and status in self.status_options:
            step_data = self.steps[self.current_step]
            step_data["Comment"] = comment
            step_data["Status"] = status

            # Find and update the existing step data if it exists
            found = False
            for i, step in enumerate(self.procedure_steps):
                if step["Step"] == step_data["Step"] and step["Category"] == step_data["Category"]:
                    self.procedure_steps[i] = step_data
                    found = True
                    break

            if not found:
                self.procedure_steps.append(step_data)

            if self.current_step < len(self.procedure_steps):
                self.procedure_steps[self.current_step] = step_data
            else:
                self.procedure_steps.append(step_data)

            # if the current step is less than the length of the entire procedure
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1 # add one to the current_step index
                self.load_step() # and load the next step
            else:
                messagebox.showinfo("Info", "All steps completed.")
                self.exit_procedure()

        else:
            messagebox.showwarning("Warning", "Please select a status option.")

    # function to go back a step
    def back_step(self):
        if self.current_step > 0:
            self.save_current_step()
            self.current_step -= 1
            self.load_step()

    def save_current_step(self):
        status = self.status_var.get()
        comment = self.comment_entry.get()
        step_data = self.steps[self.current_step]
        step_data["Comment"] = comment
        step_data["Status"] = status

        if self.current_step in self.image_paths:
            step_data['Image'] = self.image_paths[self.current_step]
            print(f"Image path added for step {self.current_step}: {self.image_paths[self.current_step]}")

        found = False
        for i, step in enumerate(self.procedure_steps):
            if step['Step'] == step_data['Step'] and step['Category'] == step_data['Category']:
                self.procedure_steps[i] = step_data
                found = True
                break
        
        if not found:
            self.procedure_steps.append(step_data)

        # save data after each step
        save_data(self.procedure_steps)

    def exit_procedure(self):
        # ask if the user wants their progress saved
        response = messagebox.askyesnocancel("Exit", "Would you like to save your current progress before exiting?")
        if response is True:
            # if true, save data to procedure_steps
            save_data(self.procedure_steps)
            messagebox.showinfo("Info", "Progress saved.")
        elif response is False:
            # if false clear current data by deleting saved file
            clear_data()
            messagebox.showinfo("Info", "Progress cleared.")
        #save_data(self.procedure_steps)
        self.root.quit()

    # calls upon exit_procedure anyway user attempts to close the window
    def on_closing(self):
        self.exit_procedure()

def main():
    procedure = load_procedure('SmartPMProcedure.json')
    root = tk.Tk()

    # let's check to see if there's any saved data
    saved_data = []
    try:
        with open('FSEInput.json', 'r') as file: # open preexisiting file
            saved_data = json.load(file) # load current file into saved data list
    except FileNotFoundError:
        pass # if no file found pass

    if saved_data:
        last_step_index = len(saved_data) # need to get the length of saved_data to see where the json file was saved at
        current_step_index = last_step_index

        app = ProcedureApp(root, procedure, current_step_index, saved_data) # create an app with the last saved index

    else: # start from beginning
        app = ProcedureApp(root, procedure)
    
    root.mainloop()

if __name__ == "__main__":
    main()