import file_operations
from rot_utility import RotMat_x, RotMat_y, RotMat_z
import numpy as np
import unitSphereModule
import matplotlib.pyplot as plt
import argparse, logging, time, sys

from main import GRAV_VEC_NAME, TIME_VEC_NAME, OUTER_FRAME_ANG_NAME, INNER_FRAME_ANG_NAME, INTERMEDIATE_FRAME_ANG_NAME

FILE_PATH = r"G:\MAGISTERKA\Unity_logged_data\log4_3.00_2.00_1.00.csv"
max_time=14.0 #s
N = 10000
ANGULAR_VEL = np.array([3*6,7*6])   # (Outer,..., Inner) [deg/s]
R0 = np.array([0,-9.81,0]) #initial position of RPM pointing downwards
ANGULAR_0 = np.array([0.0,0.0]) # [outer, ?inner, beeChamb]

def sign_rot_lambda(rot, sgn):
    if sgn == 0:
        return lambda deg: rot(deg_ang=deg)
    else:
        return lambda deg: rot(deg_ang=-deg)

def find_rot_3axis(ang_vec, r_vec, r0, time_vec):
    ROT_MATS = [RotMat_x, RotMat_y, RotMat_z]
    LABELS = ["RotX","RotY","RotZ"]
    PERMUTATIONS = [[0,1,2],[1,0,2],[0,2,1],[1,2,0],[2,0,1],[2,1,0]]
    best_mse = np.inf
    best = None
    best_r_vec = np.empty(shape=(len(time_vec),3))
    temp_r_vec = np.empty(shape=(len(time_vec),3))
    STAT_mse = np.zeros(shape=(6,8))    #[permut, sign]
    for i_permut,permut in enumerate(PERMUTATIONS):
        for i_sgn in range(8):
            mse = 0.0
            # cal what signs now
            sgn_vec = [i_sgn//4, 0, 0]
            sgn_vec[1] = (i_sgn - sgn_vec[0]*4)//2
            sgn_vec[2] = i_sgn - sgn_vec[0]*4 - sgn_vec[1]*2
            # apply signs to the correct matricies
            R1 = sign_rot_lambda(ROT_MATS[permut[0]], sgn_vec[0])
            R2 = sign_rot_lambda(ROT_MATS[permut[1]], sgn_vec[1])
            R3 = sign_rot_lambda(ROT_MATS[permut[2]], sgn_vec[2]) 
            # right var sequence
            for i_vars,var_seq in enumerate(["xyz","zyx"]):
                if var_seq == "xyz":    
                    x_i,y_i,z_i = 0,1,2
                elif var_seq == "zyx":
                    x_i,y_i,z_i = 2,1,0

                for i,real_r in enumerate(r_vec):
                    # calc the r
                    r = R1(ang_vec[i,x_i]) @ R2(ang_vec[i,y_i]) @ R3(ang_vec[i,z_i]) @ R0  
                    temp_r_vec[i,:] = r
                    mse += np.linalg.norm(real_r - r)
                mse /= len(time_vec)
                STAT_mse[i_permut, i_sgn] = mse
                if mse < best_mse:
                    best_mse = mse
                    best_r_vec = temp_r_vec.copy()
                    sgn_str = ["+-"[sgn_bool] for sgn_bool in sgn_vec]
                    best = f"{LABELS[permut[0]]}({sgn_str[0]}{var_seq[0]}) @ {LABELS[permut[1]]}({sgn_str[1]}{var_seq[1]})"
                    best += f" @ {LABELS[permut[2]]}({sgn_str[2]}{var_seq[2]}) @ r"
   
    # verbose
    #print(STAT_mse)
    return best_r_vec, best

def find_rot_2axis(ang_vec, r_vec, r0, time_vec):
    pass

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
    args = parser.parse_args(argv)        

    # read file with groundtruth
    ground_r_vec = np.empty(shape=(0,3))
    ground_t_vec = np.array([])
    if args.axis == 2:
        ground_ang_vec = np.empty((0,2))    #[outer, inner]
    else:
        ground_ang_vec = np.empty((0,3))    #[outer, intermediate, inner]

    csv_start_time = None
    CSV_DataParser = file_operations.CSV_DataParser(FILE_PATH, maxBuffCnt=100)
    for (csv_names, csv_buffers, csv_buff_cnt) in CSV_DataParser.gen_get_data():
        # initial: indexes, start time
        if csv_start_time is None:
            grav_buff_index = csv_names.index(GRAV_VEC_NAME)
            time_buff_index = csv_names.index(TIME_VEC_NAME)
            outerFrame_ang_index = csv_names.index(OUTER_FRAME_ANG_NAME)
            innerFrame_ang_index  = csv_names.index(INNER_FRAME_ANG_NAME)
            csv_start_time = csv_buffers[time_buff_index][0]
            csv_r0 = csv_buffers[grav_buff_index][0,:]
            if args.axis == 3:
                intermediateFrame_ang_index = csv_names.index(INTERMEDIATE_FRAME_ANG_NAME)
        
        # buffers from .csv
        grav_buff = csv_buffers[grav_buff_index]
        time_buff = csv_buffers[time_buff_index]
        outerFrame_ang = csv_buffers[outerFrame_ang_index]
        innerFrame_ang = csv_buffers[innerFrame_ang_index]
        if args.axis == 3:
            intermediateFrame_ang = csv_buffers[intermediateFrame_ang_index]

        # buffer copying
        for i in range(csv_buff_cnt):
            ground_t_vec = np.append( ground_t_vec, time_buff[i] )
            ground_r_vec = np.concatenate( (ground_r_vec, grav_buff[i:i+1,:]), axis=0 )
            if args.axis == 2:
                ground_ang_vec = np.vstack( [ground_ang_vec, [outerFrame_ang[i], innerFrame_ang[i]]] )
            elif args.axis == 3:
                ground_ang_vec = np.vstack( [ground_ang_vec, [outerFrame_ang[i], intermediateFrame_ang[i], innerFrame_ang[i]]] )

    # normalize so time starts from 0.0
    ground_t_vec -= csv_start_time

    # python sym
    if args.axis == 3:
        r_vec,rot_info = find_rot_3axis(ang_vec=ground_ang_vec, r_vec=ground_r_vec, r0=csv_r0, time_vec=ground_t_vec)
    elif args.axis == 2:
        r_vec,rot_info = find_rot_2axis(ang_vec=ground_ang_vec, r_vec=ground_r_vec, r0=csv_r0, time_vec=ground_t_vec)

    print(rot_info)

    fig0, axes0 = plt.subplots(nrows=args.axis, ncols=1)
    for i in range(args.axis):
        ax = axes0[i]
        ax.plot(ground_t_vec, ground_ang_vec[:,i], color="orange")
        ax.set_ylabel("angle [deg]")
        ax.grid()
    ax.set_xlabel("time[s]")

    fig1,axes1 = plt.subplots(nrows=3, ncols=1)
    xyz = ["x","y","z"]
    for i in range(3):
        ax = axes1[i]
        ax.scatter(ground_t_vec,ground_r_vec[:,i], color="blue", label="ground_truth")
        ax.plot(ground_t_vec, r_vec[:,i], color="orange", label="python sim")
        ax.set_ylabel(f"{xyz[i]} [m/s^2]")
        ax.legend()
    ax.set_xlabel("time[s]")
    plt.show()


if __name__ == "__main__":
    main()








