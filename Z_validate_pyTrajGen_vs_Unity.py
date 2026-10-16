import file_operations
from rot_utility import RotMat_x, RotMat_y, RotMat_z
import numpy as np
import unitSphereModule
import matplotlib.pyplot as plt
import argparse, logging, time, sys

from main import GRAV_VEC_NAME, TIME_VEC_NAME, OUTER_FRAME_ANG_NAME, INNER_FRAME_ANG_NAME, INTERMEDIATE_FRAME_ANG_NAME

FILE_PATH = r"G:\MAGISTERKA\Unity_logged_data\log0_3.00_7.00.csv"
max_time=14.0 #s
N = 10000
ANGULAR_VEL = np.array([3*6,7*6])   # (Outer,..., Inner) [deg/s]
R0 = np.array([0,-9.81,0]) #initial position of RPM pointing downwards
ANGULAR_0 = np.array([0.0,0.0]) # [outer, ?inner, beeChamb]

def control_fun_2axis(ang_0, angular_vel, r0):
    dt = max_time/N

    r = r0
    ang = ang_0 # 0 - 360 deg
    cur_t = 0.0
    
    t_vec = np.array([0.0])
    r_vec = np.array(r0)
    r_vec = np.reshape(r_vec, (1,3))
    ang_vec = np.array([*ang_0])
    ang_vec = np.reshape(ang_vec, (1,len(ang_vec)))
    while cur_t < max_time:
        cur_t += dt

        d_ang = dt*angular_vel
        ang = ang + d_ang
        if ang[0] >= 360.0:
            ang[0] -= 360
        if ang[1] >= 360.0:
            ang[1] -= 360.0
        ang_vec = np.vstack([ang_vec, ang])

        r = np.reshape(r, (3,1))
        r =  RotMat_y(deg_ang = -ang[1]) @ RotMat_z(deg_ang = -ang[0]) @ r0
        # normalization to increase numerical stability
        r = r / np.linalg.norm(r) * 9.81
        r = np.reshape(r,(1,3))
        
        r_vec = np.concatenate((r_vec,r),axis=0)
        t_vec = np.append(t_vec,cur_t)
    return r_vec, t_vec, ang_vec


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--axis",type=int, default=3)
    parser.add_argument("-g","--generate",action="store_true")
    args = parser.parse_args(argv)

    # generate py traj
    if args.generate:
        if args.axis == 2:
            r_vec,t_vec,ang_vec = control_fun_2axis(ang_0=ANGULAR_0, angular_vel=ANGULAR_VEL, r0=R0)

    # read file with groundtruth
    ground_r_vec = np.empty(shape=(0,3))
    ground_t_vec = np.array([])
    if args.axis == 2:
        ground_ang_vec = np.empty((0,2))    #[outer, beeChamb]

    CSV_DataParser = file_operations.CSV_DataParser(FILE_PATH, maxBuffCnt=100)
    for (csv_names, csv_buffers, csv_buff_cnt) in CSV_DataParser.gen_get_data():
        # indexes
        grav_buff_index = csv_names.index(GRAV_VEC_NAME)
        time_buff_index = csv_names.index(TIME_VEC_NAME)
        outerFrame_ang_index = csv_names.index(OUTER_FRAME_ANG_NAME)
        beeChamb_ang_index  = csv_names.index(INNER_FRAME_ANG_NAME)
        grav_buff = csv_buffers[grav_buff_index]
        time_buff = csv_buffers[time_buff_index]
        outerFrame_ang = csv_buffers[outerFrame_ang_index]
        beeChamb_ang = csv_buffers[beeChamb_ang_index]
        # buffer copying
        for i in range(csv_buff_cnt):
            ground_t_vec = np.append( ground_t_vec, time_buff[i] )
            ground_r_vec = np.concatenate( (ground_r_vec, grav_buff[i:i+1,:]), axis=0 )
            if args.axis == 2:
                ground_ang_vec = np.vstack( [ground_ang_vec, [outerFrame_ang[i], beeChamb_ang[i]]] )

    # plot both data with interplation
    ground_t_vec -= ground_t_vec[0] # normalize so time starts from 0.0

    fig0, axes0 = plt.subplots(nrows=2, ncols=1)
    for i in range(2):
        ax = axes0[i]
        ax.plot(t_vec, ang_vec[:,i])
        ax.scatter(ground_t_vec, ground_ang_vec[:,i], color="orange")
        ax.set_ylabel("angle [deg]")
    ax.set_xlabel("time[s]")

    fig1,axes1 = plt.subplots(nrows=3, ncols=1)
    xyz = ["x","y","z"]
    for i in range(3):
        ax = axes1[i]
        ax.plot(t_vec, r_vec[:,i], color="orange")
        ax.scatter(ground_t_vec,ground_r_vec[:,i] )
        ax.set_ylabel(f"{xyz[i]} [m/s^2]")
    ax.set_xlabel("time[s]")
    plt.show()


if __name__ == "__main__":
    main()








