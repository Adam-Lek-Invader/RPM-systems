import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import file_operations

OPTIONS_SPHERE_TYPES = ["icoSphere", "random", "polarCoordsSubdivision"]
OPTIONS_TRAJECTORY_MARK_TYPES = ["Position_Traj", "Time_position_Traj"]

def validate_integer(value):
    if value == "":          # allow empty while editing
        return True
    return value.isdigit()   # only digits

def pick_file(root, i, path_list, path_names, tk_components, file_path:tk.StringVar, one_time:bool=False):
    path = filedialog.askopenfilename(title="Select a file", initialdir=path_list[i])
    if not path:                              
        return

    # update paths
    path_dir = os.path.dirname(path)
    path_list[i] = path_dir
    print(path_dir)
    file_path.set(path)
    tk_components["current_file_value"].config(textvariable=file_path)


    # ask for a path name
    if one_time == False:
        name = tk.simpledialog.askstring("Input", f"Enter a name for {path_names[i]}:", parent=root)
        if name:
            path_names[i] = name
            tk_components[f"path_btn_{i+1}"].config(text=name)

    # continue button to change screen
    if "continue_btn" not in tk_components:
        btn = tk.Button(root, text="Load Trajectory", command=lambda: root.quit())
        btn.grid(row=5, column=0, columnspan=2, pady=10)
        tk_components["continue_btn"] = btn

def screen_first(root, config_dict:dict, file_path:tk.StringVar)->dict:
    tk_components = {}
    root.geometry("600x400")
    root.title("RPM Data Loading")
    vcmd = (root.register(validate_integer), "%P")
    path_list = config_dict["paths"]
    path_names = config_dict["paths_names"]
    
    # path buttons
    for i in range(4):
        btn = tk.Button(root, text=path_names[i], command=lambda i=i: pick_file(root, i, path_list, path_names, tk_components, file_path))
        btn.grid(row=i, column=2, padx=10, pady=5, sticky="e")
        tk_components[f"path_btn_{i+1}"] = btn
    btn = tk.Button(root, text="One Time Path", command=lambda: pick_file(root, 4, path_list, path_names, tk_components, file_path, one_time=True))
    btn.grid(row=4, column=2, padx=10, pady=5, sticky="e")
    tk_components["one_time_btn"] = btn

    # Current chosen file label
    label = tk.Label(root, text="Current Chosen File:")
    label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk_components["current_file_label"] = label
    label = tk.Label(root, textvariable=file_path)
    label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk_components["current_file_value"] = label

    # Sphere Type selection
    label = tk.Label(root, text="Sphere Type:")
    label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk_components["sphere_type_label"] = label
    dropdown = ttk.Combobox(root, values=OPTIONS_SPHERE_TYPES, state="readonly")
    dropdown.current(0)            # preselect first item
    dropdown.grid(row=1, column=1, padx=10, pady=5)
    tk_components["sphere_type_dropdown"] = dropdown

    # Sphere n selection
    label = tk.Label(root, text="Sphere n:")
    label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk_components["sphere_n_label"] = label
    n_entry = tk.Entry(root, validate="key", validatecommand=vcmd)
    n_entry.insert(0, str(config_dict["n"]))  # default value
    n_entry.grid(row=2, column=1, padx=10, pady=5)
    tk_components["sphere_n_entry"] = n_entry

    # trajectory mark type selection
    label = tk.Label(root, text="Trajectory Mark Type:")
    label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk_components["trajectory_mark_type_label"] = label
    dropdown = ttk.Combobox(root, values=OPTIONS_TRAJECTORY_MARK_TYPES, state="readonly")
    dropdown.current(0)            # preselect first item
    dropdown.grid(row=3, column=1, padx=10, pady=5)
    tk_components["trajectory_mark_type_dropdown"] = dropdown

    # cnt of neighbours selection
    label = tk.Label(root, text="Count of Neighbours:")
    label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
    tk_components["nei_cnt_label"] = label
    nei_cnt_entry = tk.Entry(root, validate="key", validatecommand=vcmd)
    nei_cnt_entry.insert(0, str(config_dict["nei_cnt"]))  # default value
    nei_cnt_entry.grid(row=4, column=1, padx=10, pady=5)
    tk_components["nei_cnt_entry"] = nei_cnt_entry

    return tk_components

def screen_second(root, file_path:tk.StringVar, tk_components:dict)->dict:  
    # close first screen components
    for widget in root.winfo_children():
        widget.destroy()
    tk_components = {}

    # loading grid for all operations
    root.title("RPM Trajectory Generation Loading")
    root.geometry("600x400")

    op0_createSphere_text = tk.Label(root, text="Creating Sphere...")
    op0_led = tk.Label(root, text="●", fg="red")
    op0_createSphere_text.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    op0_led.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk_components["op0_createSphere_text"] = op0_createSphere_text
    tk_components["op0_led"] = op0_led

    op1_assignNeighbours_text = tk.Label(root, text="Assigning Neighbours...")
    op1_led = tk.Label(root, text="●", fg="red")
    op1_assignNeighbours_text.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    op1_led.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk_components["op1_assignNeighbours_text"] = op1_assignNeighbours_text
    tk_components["op1_led"] = op1_led

    op2_markTraj_text = tk.Label(root, text="Marking Trajectory...")
    op2_led = tk.Label(root, text="●", fg="red")
    op2_markTraj_text.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    op2_led.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    tk_components["op2_markTraj_text"] = op2_markTraj_text
    tk_components["op2_led"] = op2_led

    op3_taSMG_text = tk.Label(root, text="Plotting taSMG...")
    op3_led = tk.Label(root, text="●", fg="red")
    op3_taSMG_text.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    op3_led.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    tk_components["op3_taSMG_text"] = op3_taSMG_text
    tk_components["op3_led"] = op3_led


    btn = tk.Button(root, text="Results", command=lambda: root.quit())
    btn.grid(row=4, column=0, columnspan=2, pady=10)    # Needs to be updated with each new component of the second screen, so that it is always at the bottom of the screen
    btn.grid_forget()  # hide the button until all operations are completed
    tk_components["results_btn"] = btn


    return tk_components

def screen_third(root, tk_components:dict)->dict:
    # close second screen components
    for widget in root.winfo_children():
        widget.destroy()
    tk_components = {}

    # third screen
    root.title("RPM Trajectory Results")
    root.geometry("600x400")

    label = tk.Label(root, text="Grav Vector Trajectory Will be Plotted in a New Browser Window")
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk_components["results_label"] = label

    return tk_components