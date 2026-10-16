import argparse
import logging
import os, json, time
import tkinter as tk
from turtle import title
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import gui
import unitSphereModule
import file_operations

DEFAULT_CONFIG_FILE = ".config_rpm_trajGen.json"
GRAV_VEC_NAME = "BeeChamb_XYZ[m]"
TIME_VEC_NAME = "Time[s]"
OUTER_FRAME_ANG_NAME = "OuterFrameAng[deg]"
INTERMEDIATE_FRAME_ANG_NAME = "IntermediateFrameAng[deg]"
INNER_FRAME_ANG_NAME = "InnerFrameAng[deg]"
CONST_G = 9.81  #gravity acceleration [m/s^2]

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
        TRAJ_FLAG = 0    
    elif config_dict["trajectory_mark_type"] == "Time_position_Traj":
        TRAJ_FLAG = 1

    # data parser
    DataParser = file_operations.CSV_DataParser(file_path.get())
    total_rows = 0
    data_index = None
    time_index = None
    for col_names, buffers, buf_row_count in DataParser.gen_get_data():
        # save rows read
        total_rows += buf_row_count
        # get data header
        if data_index is None:
            try:
                data_index = col_names.index(GRAV_VEC_NAME)
                time_index = col_names.index(TIME_VEC_NAME)
            except ValueError:
                logger.error(f"Column '{GRAV_VEC_NAME}' not found in the CSV file.")
                return 1

        # mark data
        match TRAJ_FLAG:
            case 0:
                sphere.mark_trajectory(buffers[data_index])
            case 1:
                sphere.mark_trajectory_timed(buffers[data_index], buffers[time_index])

        # update the progress
        tk_components["op2_markTraj_text"].config(text=f"Marking Trajectory... ({total_rows} rows processed)")
        root.update()

    time_end = time.perf_counter()
    tk_components["op2_led"].config(fg="green")
    tk_components["op2_markTraj_text"].config(text=f"Trajectory of {total_rows} points marked with {selected_trajectory_mark_type} ({time_end - time_start:.2f} s)")
    root.update()

    # 4. taSMG plotting
    time_start = time.perf_counter()

    taSMG_start_time = None # used so that time starts from 0.0s
    T = 0.0  # total time ( = current timestamp - start time)
    taSMG_acc_xyz_timed = np.float64(0.0) # += a_vec*dt | normalizing by g done later to lower numerical errors
    fig_taSMG = go.Figure()
    fig_taSMG.add_trace(
        go.Scatter(
            x = [],
            y = [],
            mode = "lines",
            name = "taSMG"
        )
    )
    fig_taSMG.update_xaxes(title_text="Time [seconds]")
    fig_taSMG.update_yaxes(title_text="taSMG [g]")

    fig_xyz_acc = make_subplots(rows=3, cols=1, 
                                x_title="Time [seconds]",
                                row_titles=["x gravity [m/s^2]","y gravity [m/s^2]","z gravity [m/s^2]"])
    fig_xyz_acc.add_trace(
        go.Scatter(x=[], y=[], mode="lines"),
        row=1, col=1
    )

    fig_xyz_acc.add_trace(
        go.Scatter(x=[], y=[], mode="lines"),
        row=2, col=1
    )

    fig_xyz_acc.add_trace(
        go.Scatter(x=[], y=[], mode="lines"),
        row=3, col=1
    )


    # data parser
    DataParser = file_operations.CSV_DataParser(file_path.get())
    total_rows = 0
    data_index = None
    time_index = None

    for col_names, buffers, buf_row_count in DataParser.gen_get_data():
        # save rows read
        total_rows += buf_row_count
        # get data header
        if data_index is None:
            try:
                data_index = col_names.index(GRAV_VEC_NAME)
                time_index = col_names.index(TIME_VEC_NAME)
                taSMG_start_time = buffers[time_index][0]   # first timestamp from .csv
            except Exception as e:
                logger.error(f"Index Error: {e}")
                return 1

        time_buff = np.zeros(shape=(buf_row_count))
        taSMG_buff = np.zeros(shape=(buf_row_count))
        acc_buff = np.zeros(shape=(buf_row_count, 3))

        # taSMG
        for i,t in enumerate(buffers[time_index]):
            dt = T - (t-taSMG_start_time)
            T = t-taSMG_start_time
            acc_vec = buffers[data_index][i,:]
            
            if T == 0.0:
                taSMG_acc_xyz_timed += acc_vec  # just acc_vec 
                taSMG_acc_mag = np.linalg.norm(taSMG_acc_xyz_timed)
                taSMG = taSMG_acc_mag/CONST_G #int(a*dt)/1
            else:
                taSMG_acc_xyz_timed += acc_vec*dt   # a_xyz * dt
                taSMG_acc_mag = np.linalg.norm(taSMG_acc_xyz_timed)
                taSMG = taSMG_acc_mag/(T*CONST_G) #int(a*dt)/T

            time_buff[i] = T
            taSMG_buff[i] = taSMG
            acc_buff[i,:] = acc_vec

        # add traces to plots
        fig_taSMG.data[0].x = np.append(fig_taSMG.data[0].x, time_buff)
        fig_taSMG.data[0].y = np.append(fig_taSMG.data[0].y, taSMG_buff)
        for i_xyz in range(3):
            fig_xyz_acc.data[i_xyz].x = np.append(fig_xyz_acc.data[i_xyz].x, time_buff)
            fig_xyz_acc.data[i_xyz].y = np.append(fig_xyz_acc.data[i_xyz].y, acc_buff[:,i_xyz])
            
        # update the progress
        tk_components["op3_taSMG_text"].config(text=f"Making taSMG Plots... ({total_rows} rows processed)")
        root.update()

    time_end = time.perf_counter()
    tk_components["op3_led"].config(fg="green")
    tk_components["op3_taSMG_text"].config(text=f"taSMG plots completed. {total_rows} points marked ({time_end - time_start:.2f} s)")
    root.update()


    # 5. Determine velocities and accelerations @@@ to be implemented

    # All operations completed, show the results button
    tk_components["results_btn"].grid()  # show the button
    root.mainloop()

    # Third Screen
    tk_components = gui.screen_third(root, tk_components)
    root.update()
    sphere.plot_plotly()
    fig_taSMG.show()
    fig_xyz_acc.show()


    root.mainloop()




if __name__ == "__main__":
    main()