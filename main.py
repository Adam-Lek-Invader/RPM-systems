import argparse
import logging
import os, json, time
import tkinter as tk

import gui
import unitSphereModule
import file_operations

DEFAULT_CONFIG_FILE = ".rpm_plot_config.json"
GRAV_VEC_NAME = "BeeChamb_XYZ[m]"

logger = logging.getLogger(__name__)

def plot_trajectory(file_path):
    # Placeholder for plotting logic
    logger.info(f"Plotting trajectory from {file_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Trajectory Generation")
    parser.add_argument("--axis", type=int, default=3, help="Number of axes of an RPM (2 or 3)")
    parser.add_argument("-cnt","--continue", action="store_true", help="Continue from a chosen file")
    parser.add_argument("-p","--plot", action="store_false", help="Dont Plot the trajectory")
    parser.add_argument("-conf","--config", type=str, default=DEFAULT_CONFIG_FILE, help="Path to the JSON configuration file")
    parser.add_argument("-gui", "--gui", action="store_false", help="Dont Launch the GUI application")
    parser.add_argument("-f", "--file", type=str, default=None, help="Path to the file to continue from")
    args = parser.parse_args(argv)

    if args.axis not in [2, 3]:
        logger.error("Invalid number of axes. Please choose 2 or 3.")
        return 1

    # json config file read
    config_dict = file_operations.load_json_config(args.config)

    # load first screen and prepare tk
    root = tk.Tk()
    file_path = tk.StringVar(master=root)
    tk_components = gui.screen_first(root, config_dict, file_path)
    root.mainloop()

    # get all the values from the first screen
    selected_sphere_type = tk_components["sphere_type_dropdown"].get()
    selected_n = int(tk_components["sphere_n_entry"].get())
    selected_trajectory_mark_type = tk_components["trajectory_mark_type_dropdown"].get()
    selected_nei_cnt = int(tk_components["nei_cnt_entry"].get())

    # update the config .json file
    config_dict["paths"] = [os.path.dirname(path) for path in config_dict["paths"]]
    config_dict["paths_names"] = [tk_components[f"path_btn_{i+1}"].cget("text") for i in range(4)]
    config_dict["SphereType"] = selected_sphere_type
    config_dict["trajectory_mark_type"] = selected_trajectory_mark_type
    config_dict["n"] = selected_n
    config_dict["nei_cnt"] = selected_nei_cnt
    file_operations.save_json_config(args.config, config_dict)

    # second screen
    tk_components = gui.screen_second(root, file_path, tk_components)
    root.update()
    # ALL OPERATIONS
    # 1. Create Sphere
    time_start = time.perf_counter()
    sphere = unitSphereModule.unitSphere(n=selected_n, method=selected_sphere_type)
    time_end = time.perf_counter()
    tk_components["op0_led"].config(fg="green")
    tk_components["op0_createSphere_text"].config(text=f"Creation of {selected_sphere_type} with n={selected_n} and {len(sphere.points)} points completed ({time_end - time_start:.2f} s)")
    root.update()

    # 2. Assing Neighbours
    time_start = time.perf_counter()
    sphere.assign_neighbours(selected_nei_cnt)
    time_end = time.perf_counter()
    tk_components["op1_led"].config(fg="green")
    tk_components["op1_assignNeighbours_text"].config(text=f"{selected_nei_cnt} neighbours assigned for each point ({time_end - time_start:.2f} s)")
    root.update()

    # 3. Mark Trajectory
    time_start = time.perf_counter()
    if config_dict["trajectory_mark_type"] == "Position_Traj":
        mark_traj_fun = sphere.mark_trajectory
    elif config_dict["trajectory_mark_type"] == "Time_position_Traj":
        mark_traj_fun = sphere.mark_trajectory_timed

    DataParser = file_operations.CSV_DataParser(file_path.get())
    total_rows = 0
    data_index = None
    for col_names, buffers, buf_row_count in DataParser.gen_get_data():
        total_rows += buf_row_count
        if data_index is None:
            try:
                data_index = col_names.index(GRAV_VEC_NAME)
            except ValueError:
                logger.error(f"Column '{GRAV_VEC_NAME}' not found in the CSV file.")
                return 1
        mark_traj_fun(buffers[data_index])

        # update the progress
        tk_components["op2_markTraj_text"].config(text=f"Marking Trajectory... ({total_rows} rows processed)")
        root.update()

    time_end = time.perf_counter()
    tk_components["op2_led"].config(fg="green")
    tk_components["op2_markTraj_text"].config(text=f"Trajectory of {total_rows} points marked with {selected_trajectory_mark_type} ({time_end - time_start:.2f} s)")
    root.update()

    # 4. Determine velocities and accelerations @@@ to be implemented

    # All operations completed, show the results button
    tk_components["results_btn"].grid()  # show the button
    root.mainloop()

    # Third Screen
    tk_components = gui.screen_third(root, tk_components)
    root.update()
    sphere.plot_plotly()


    root.mainloop()




if __name__ == "__main__":
    main()