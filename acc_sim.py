import numpy as np
import matplotlib.pyplot as plt
from rot_utility import RotMat_y, RotMat_z

rpm_rotFrame = 0.0 #z
rpm_beeChamb = 1.0 #y
ang_deg_beeChamb = 0.0 #y
ang_deg_rotFrame = 55.0 #z
numeric_dt = 1e-8


def calc_v_point(r_vec_local:np.ndarray, rpm_rotFrame:float, rpm_beeChamb:float, ang_deg_beeChamb:float=0.0, ang_deg_rotFrame:float=0.0):
    """
    Calculate the velocity of a point in a rotating frame.

    Parameters:
    r_vec_local (np.ndarray): Local Position vector of the point in the rotating frame.
    rpm_rotFrame (float): Rotational speed of the frame in revolutions per minute.
    rpm_beeChamb (float): Rotational speed of the bee chamber in revolutions per minute.
    ang_deg_beeChamb (float): Angular position of the bee chamber in degrees.
    ang_deg_rotFrame (float): Angular position of the rotating frame in degrees.

    Returns:
    np.ndarray: Velocity vector of the point in the rotating frame.
    """
    # Convert RPM to radians per second
    omega_rotFrame = np.array([0, 0, 2 * np.pi * rpm_rotFrame / 60.0])   #z rotation [rad/s]
    omega_beeChamb = np.array([0, 2 * np.pi * rpm_beeChamb / 60.0, 0])   #y rotation [rad/s]
    r_vec_rotated = RotMat_y(deg_ang=ang_deg_beeChamb) @ RotMat_z(deg_ang=ang_deg_rotFrame) @ r_vec_local  # Rotate the position vector by the bee chamber angle

    omega_total = omega_rotFrame + omega_beeChamb
    # Total velocity is the sum of both contributions
    v_total = np.cross(omega_total, r_vec_rotated)  # v = w x r

    return v_total, omega_total

def calc_acc_point(r_vec:np.ndarray, omega_vec:np.ndarray, ang_deg_beeChamb:float=0.0, ang_deg_rotFrame:float=0.0, a_vec:np.ndarray=np.array([0, 0, 0])):
    """
    Calculate the acceleration of a point in a rotating frame.

    Parameters:
    r_vec (np.ndarray): Stable Position vector of the point in the rotating frame.
    omega_vec (np.ndarray): Angular velocity vector of the rotating frame.
    ang_deg_beeChamb (float): Angular position of the bee chamber in degrees.
    ang_deg_rotFrame (float): Angular position of the rotating frame in degrees.
    a_vec (np.ndarray): Acceleration vector of the point in the rotating frame (default is zero).

    Returns:
    np.ndarray: Acceleration vector of the point in the rotating frame.
    """
    # Calculate the angular velocity vector
    r_vec_rotated = RotMat_y(deg_ang=ang_deg_beeChamb) @ RotMat_z(deg_ang=ang_deg_rotFrame) @ r_vec  # Rotate the position vector by the bee chamber angle
    # Calculate the acceleration contributions
    acc_from_motor_acc = np.cross(a_vec, r_vec_rotated)  # a = dw x r
    acc_from_centrifugical = np.cross(omega_vec, np.cross(omega_vec, r_vec_rotated)) # a = w x (w x r)
    acc_total = acc_from_motor_acc + acc_from_centrifugical

    return acc_total

def plot_beeChamb_acc(x_max:float,y_max:float,z_max:float,rpm_rotFrame:float,rpm_beeChamb:float, ang_deg_beeChamb:float=0.0, ang_deg_rotFrame:float=0.0, xyz_npoints:tuple[int, int, int] = (10, 10, 10)):
    """
    Plot the acceleration of a point in a rotating frame.

    Parameters:
    x_max (float): Maximum x-coordinate for the plot.
    y_max (float): Maximum y-coordinate for the plot.
    z_max (float): Maximum z-coordinate for the plot.
    rpm_rotFrame (float): Rotational speed of the frame in revolutions per minute.
    rpm_beeChamb (float): Rotational speed of the bee chamber in revolutions per minute.
    ang_deg_beeChamb (float): Angular position of the bee chamber in degrees.
    xyz_npoints (tuple[int, int, int]): Number of points along each axis for the plot.
    """
    x = np.linspace(-x_max, x_max, xyz_npoints[0])
    y = np.linspace(-y_max, y_max, xyz_npoints[1])
    z = np.linspace(-z_max, z_max, xyz_npoints[2])

    ACC_VEC_MAT = np.zeros((xyz_npoints[0], xyz_npoints[1], xyz_npoints[2], 3))
    ACC_MAG_MAT = np.zeros((xyz_npoints[0], xyz_npoints[1], xyz_npoints[2]))

    for i in range(xyz_npoints[0]):
        for j in range(xyz_npoints[1]):
            for k in range(xyz_npoints[2]):
                r_vec = np.array([x[i], y[j], z[k]])
                v_vec, omega_vec = calc_v_point(r_vec, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb, ang_deg_rotFrame)
                acc_vec = calc_acc_point(r_vec, omega_vec, ang_deg_beeChamb, ang_deg_rotFrame)
                ACC_VEC_MAT[i, j, k] = acc_vec
                ACC_MAG_MAT[i, j, k] = np.linalg.norm(acc_vec)

    X,Y,Z = np.meshgrid(x, y, z, indexing='ij')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.quiver(X,Y,Z, ACC_VEC_MAT[..., 0], ACC_VEC_MAT[..., 1], ACC_VEC_MAT[..., 2], length=0.1, normalize=True)
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(X, Y, Z, c=ACC_MAG_MAT.flatten(), cmap='viridis')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    plt.colorbar(sc, label='Acceleration Magnitude')
    
    plt.show()

def numeric_acc_point(r_vec:np.ndarray, rpm_rotFrame:float, rpm_beeChamb:float, ang_deg_beeChamb:float=0.0, ang_deg_rotFrame:float=0.0, dt:float=1e-6):
    """
    Calculate the acceleration of a point in a rotating frame using numerical differentiation.

    Parameters:
    r_vec (np.ndarray): Stable Position vector of the point in the rotating frame.
    rpm_rotFrame (float): Rotational speed of the frame in revolutions per minute.
    rpm_beeChamb (float): Rotational speed of the bee chamber in revolutions per minute.
    ang_deg_beeChamb (float): Angular position of the bee chamber in degrees.
    ang_deg_rotFrame (float): Angular position of the rotating frame in degrees.
    dt (float): Time step for numerical differentiation.

    Returns:
    np.ndarray: Acceleration vector of the point in the rotating frame.
    """

    # Calculate new angles based on the rotational speeds and time step
    ang_deg_beeChamb_past = ang_deg_beeChamb - (rpm_beeChamb * 360.0 * (dt/2) / 60.0)
    ang_deg_rotFrame_past = ang_deg_rotFrame - (rpm_rotFrame * 360.0 * (dt/2) / 60.0)
    ang_deg_beeChamb_new = ang_deg_beeChamb + (rpm_beeChamb * 360.0 * (dt/2) / 60.0)
    ang_deg_rotFrame_new = ang_deg_rotFrame + (rpm_rotFrame * 360.0 * (dt/2) / 60.0)

    # Calculate new positions before and after dt/2
    r_vec_past = RotMat_y(deg_ang=ang_deg_beeChamb_past) @ RotMat_z(deg_ang=ang_deg_rotFrame_past) @ r_vec
    r_vec_new = RotMat_y(deg_ang=ang_deg_beeChamb_new) @ RotMat_z(deg_ang=ang_deg_rotFrame_new) @ r_vec

    v_past, _ = calc_v_point(r_vec, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb_past, ang_deg_rotFrame_past)
    v_new, _ = calc_v_point(r_vec, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb_new, ang_deg_rotFrame_new)

    # Numerical differentiation to find acceleration
    acc_vec = (v_new - v_past) / dt

    return acc_vec

def find_max_acc(x_max:float,y_max:float,z_max:float,rpm_rotFrame:float,rpm_beeChamb:float)->dict:
    """
    Find the maximum acceleration in a rotating frame.

    Parameters:
    x_max (float): Maximum x-coordinate for the search.
    y_max (float): Maximum y-coordinate for the search.
    z_max (float): Maximum z-coordinate for the search.
    rpm_rotFrame (float): Rotational speed of the frame in revolutions per minute.
    rpm_beeChamb (float): Rotational speed of the bee chamber in revolutions per minute.

    Returns:
    dict: A dictionary containing the maximum acceleration magnitude and its corresponding position vector.
    """
    pass

    return dict()

if __name__ == "__main__":
    r = np.array([1.0, 0, 0])
    v_vec,omega_vec = calc_v_point(r, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb, ang_deg_rotFrame)

    a_vec_calc = calc_acc_point(r, omega_vec, ang_deg_beeChamb, ang_deg_rotFrame)
    a_vec_numeric = numeric_acc_point(r, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb, ang_deg_rotFrame, numeric_dt)

    print(f"Position: {r} [m]")
    print(f"Velocity: {v_vec} [m/s]")   
    print(f"Angular Velocity: {omega_vec} [rad/s]")
    print(f"Velocity Magnitude: {np.linalg.norm(v_vec)} [m/s]")
    print(f"Acceleration [m/s^2]: calc: {a_vec_calc}, numeric: {a_vec_numeric}")
    print(f"Acceleration Magnitude [m/s^2]: calc: {np.linalg.norm(a_vec_calc)} , numeric: {np.linalg.norm(a_vec_numeric)}")
    plot_beeChamb_acc(1, 1, 1, rpm_rotFrame, rpm_beeChamb, ang_deg_beeChamb, ang_deg_rotFrame, xyz_npoints=(10, 10, 10))




