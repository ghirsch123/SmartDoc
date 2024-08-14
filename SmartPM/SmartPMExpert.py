import json
import tkinter as tk
from tkinter import ttk, messagebox
from collections import OrderedDict

# Initialize the entries dictionary
entries = {}
task_info = {}

# Load the JSON data
with open('SmartPMProcedure.json', 'r') as f:
    json_data = json.load(f, object_pairs_hook=OrderedDict)

# Function to save the modified JSON data
def save_json(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

# Function to update JSON with user inputs and auto-enumerate StepOrder
def update_json_with_inputs():
    step_order_procedure = 1
    for task_frame in task_frames:
        section = task_info[task_frame]['section']
        task_name = task_info[task_frame]['task_name']
        widgets = entries[section][task_name]
        status = widgets['status'].get()
        comment = widgets['comment'].get()
        json_data[section][task_name]['Status'] = status
        json_data[section][task_name]['Comment'] = comment
        json_data[section][task_name]['StepOrderProcedure'] = step_order_procedure
        step_order_procedure += 1

    # Set the StepOrderReport based on the original order of tasks
    for section, tasks in json_data.items():
        for i, task in enumerate(tasks):
            json_data[section][task]['StepOrderReport'] = i + 1

    save_json(json_data, 'SmartPMFSEInputs.json')
    messagebox.showinfo("Info", "Data saved successfully!")

# Function to set all statuses to "In Order"
def set_all_in_order():
    for section, tasks in entries.items():
        for task, widgets in tasks.items():
            widgets['status'].set("In Order")

# Function to move a task up in the list
def move_up(task_frame):
    index = task_frames.index(task_frame)
    if index > 0:
        task_frames.pop(index)
        task_frames.insert(index - 1, task_frame)
        for idx, frame in enumerate(task_frames):
            frame.grid(row=idx)

# Function to move a task down in the list
def move_down(task_frame):
    index = task_frames.index(task_frame)
    if index < len(task_frames) - 1:
        task_frames.pop(index)
        task_frames.insert(index + 1, task_frame)
        for idx, frame in enumerate(task_frames):
            frame.grid(row=idx)

# Function to create the GUI
def create_gui(data):
    global task_frames
    task_frames = []
    global task_info
    task_info = {}

    root = tk.Tk()
    root.title("Smart PM Procedure Input")
    root.geometry("900x600")  # Set the default window size

    # Create A Main Frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    # Create A Canvas
    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # Add A Scrollbar To The Canvas
    my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure The Canvas
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    # Create ANOTHER Frame INSIDE the Canvas
    scrollable_frame = ttk.Frame(my_canvas)

    # Add that New frame To a Window In The Canvas
    my_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update scrollregion whenever new widgets are added
    def on_frame_configure(event):
        my_canvas.configure(scrollregion=my_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    row = 0
    # Collect all tasks in a flat list for the GUI
    for section, tasks in data.items():
        entries[section] = {}
        for task, details in tasks.items():
            task_frame = ttk.Frame(scrollable_frame, padding="5")
            task_frame.grid(row=row, column=0, columnspan=4, pady=(5, 5), sticky=(tk.W, tk.E))
            task_frames.append(task_frame)
            task_info[task_frame] = {'task_name': task, 'section': section}
            
            task_label = ttk.Label(task_frame, text=task, font=('Arial', 12, 'bold'))
            task_label.grid(row=0, column=1, columnspan=4, sticky=tk.W)
            
            up_button = ttk.Button(task_frame, text="↑", command=lambda tf=task_frame: move_up(tf))
            up_button.grid(row=0, column=0, sticky=tk.W)
            
            down_button = ttk.Button(task_frame, text="↓", command=lambda tf=task_frame: move_down(tf))
            down_button.grid(row=0, column=5, sticky=tk.W)
            
            status_var = tk.StringVar(value="In Order")
            comment_var = tk.StringVar()
            
            status_label = ttk.Label(task_frame, text="Status:")
            status_label.grid(row=1, column=1, sticky=tk.W)
            statuses = details.get('Status', [])
            for idx, status in enumerate(statuses):
                rb = ttk.Radiobutton(task_frame, text=status, variable=status_var, value=status)
                rb.grid(row=1, column=2 + idx, sticky=tk.W)
            
            comment_label = ttk.Label(task_frame, text="Comment:")
            comment_label.grid(row=2, column=1, sticky=tk.W)
            comment_entry = ttk.Entry(task_frame, textvariable=comment_var, width=50)
            comment_entry.grid(row=2, column=2, columnspan=3, sticky=(tk.W, tk.E))
            
            entries[section][task] = {'status': status_var, 'comment': comment_var}
            row += 1

    set_all_button = ttk.Button(scrollable_frame, text="Set All to In Order", command=set_all_in_order)
    set_all_button.grid(row=row, column=0, columnspan=4, pady=(10, 0))

    save_button = ttk.Button(scrollable_frame, text="Save", command=update_json_with_inputs)
    save_button.grid(row=row + 1, column=0, columnspan=4, pady=(10, 0))

    root.mainloop()

# Call the function to create the GUI
create_gui(json_data)