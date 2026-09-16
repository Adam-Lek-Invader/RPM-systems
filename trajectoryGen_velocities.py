from networkx import sigma

from rot_utility import RotMat_x, RotMat_y, RotMat_z
import numpy as np
import unitSphereModule
import scipy.integrate as integrate

import argparse, logging, time, sys


logger = logging.getLogger(__name__)
control_strategies = ["steady", "random_speed", "random_position"]
R0 = np.array([0,-1,0]) #initial position of RPM pointing downwards

def random_speed(param_vec, r, t)->tuple:
    '''
    param_vec = [avg speed, rate of returning to avg speed, rate of change of speed, step time]
    using Ornstein-Uhlenbeck randomness and Euler-Maruyama method for numerical integration
    '''
    mean = np.array([param_vec[0],param_vec[0],param_vec[0]])
    theta = param_vec[1]
    sigma = param_vec[2]
    dt = param_vec[3]
    prof_time = time.perf_counter()

    def f(t, r, angular_velocities):
            return np.cross(angular_velocities, r)

    def calc_ang_vel_using_ornstein_uhlenbeck(x,mean,dt,theta,sigma)->np.ndarray:
        '''
        x = [angular_velocity_x, angular_velocity_y, angular_velocity_z, r_x, r_y, r_z]
        '''
        angular_velocities = x
        # Euler-Maruyama method for Ornstein-Uhlenbeck process
        dW = np.random.normal(size=3) * np.sqrt(dt)
        # Update angular velocities using Ornstein-Uhlenbeck process
        drift = theta * (mean - angular_velocities) * dt
        diffusion = sigma * dW
        angular_velocities += drift + diffusion

        return angular_velocities

    t_vec,r_vec = np.array([]), np.array([[],[],[]])
    cur_t = 0.0
    r = R0
    ang_vels = mean
    while cur_t <= t:
        # compute angular velocities
        ang_vels = calc_ang_vel_using_ornstein_uhlenbeck(ang_vels, mean, dt, theta, sigma)
        # integrate
        sol = integrate.solve_ivp(lambda t, x: f(t, x, ang_vels), (0, dt), r,
                                   method="LSODA", dense_output=True, rtol=1e-6, atol=1e-9)
        t_vec = np.append(t_vec, sol.t)
        r_vec = np.append(r_vec, sol.y, axis=1)
        r = sol.y[:,-1] # update r to the last value of the solution

        cur_t += dt

    passed_time = time.perf_counter() - prof_time
    logger.info(f"Random speed trajectory generation took {passed_time:.2f} seconds")
    return t_vec,r_vec

def steady_control(angular_velocities, r, t)->tuple:
    def f(t, r):
        return np.cross(angular_velocities, r)

    sol = integrate.solve_ivp(f, (0, t), r, method="LSODA", dense_output=True, rtol=1e-6, atol=1e-9)

    return sol.t, sol.y

def random_position(param_vec, r, t)->tuple:
    '''
    param_vec = [step time, speed magnitude]
    '''
    def rand_pos():
        rand_r = np.random.rand(3)*2*np.pi
        rand_r = np.array([np.sin(rand_r[0])*np.cos(rand_r[1]), np.sin(rand_r[0])*np.sin(rand_r[1]), np.cos(rand_r[0])])
        rand_R = RotMat_x(rand_r[0]) @ RotMat_y(rand_r[1]) @ RotMat_z(rand_r[2])
        return rand_R
    speed_magnitude = param_vec[1]
    dt = param_vec[0] # time step for integration
    cur_t = 0.0
    set_r = np.random.rand(3)*
    while cur_t <= t:
        if 

def main():
    parser = argparse.ArgumentParser(description="Trajectory Generation")
    parser.add_argument("--axis", type=int, default=3, help="Number of axes of an RPM (2 or 3)")
    parser.add_argument("--control", choices=control_strategies, default=control_strategies[0], help="Control strategy")
    parser.add_argument("--values", type=float, nargs=4, default=[None, None, None, None], help="Values for the control strategy (e.g., angular velocities)")
    parser.add_argument('-t',"--time", type=float, default="0.0", help="Time of simulation in seconds")
    args = parser.parse_args()

    if args.axis not in [2, 3]:
        logger.error("Invalid number of axes. Please choose 2 or 3.")
        return 1
    logger.info(f"Selected control strategy: {args.control}")

    if args.values[0] is None:
        match args.control:
            case "steady":
                logger.info("Values are rad/s of every axis in RPM")
                return 0
            case "random_speed":
                logger.info("Values are [avg speed, rate of returning to avg speed, rate of change of speed, step time] in rad/s")
                return 0
            
    match args.control:
        case "steady":
            if args.axis == 2:
                args.values[2] = 0.0
            logger.info(f"Axis movement [rad/s]: {args.values}")
            control_fun = lambda x,t: steady_control(x, r=R0, t=t)

        case "random_speed":
            # args.values = [avg speed, rate of returning to avg speed, rate of change of speed, step time]
            if args.axis == 2:
                args.values[2] = 0.0
            logger.info(f"Random Axis movement with mean speed of axis [rad/s]: {args.values[0]} | rate of returning to mean speed: {args.values[1]} | rate of change of speed: {args.values[2]} | step time: {args.values[3]}s")
            control_fun = lambda x,t: random_speed(x, r=R0, t=t)

        case "random_position":
            if args.axis == 2:
                args.values[2] = 0.0
            logger.info(f"Random Axis movement with step time [s]: {args.values[0]} | speed magnitude [rad/s]: {args.values[1]}")
            control_fun = lambda x,t: random_position(x, r=R0, t=t)
    # control loop
    t,r = control_fun(args.values, args.time)
    #logger.info(f"Trajectory: {r.shape}")
    #logger.info(f"Trajectory: {r}")
    r = r.T
    #logger.info(f"Trajectory: {r}")
    #logger.info(f"Trajectory magnitudes: {np.linalg.norm(r, axis=1)}")

    unitSphere = unitSphereModule.unitSphere( n=50, method="polarCoordsSubdivision" )
    unitSphere.assign_neighbours(8)
    unitSphere.mark_trajectory(r)
    unitSphere.plot_plotly()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    start_time = time.time()
    main()
    logger.info(f"Execution time: {time.time() - start_time:.2f} seconds")



