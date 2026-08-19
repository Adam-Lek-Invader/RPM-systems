import numpy as np

def RotMat_x(deg_ang=None, rad_ang=None):
    if deg_ang is not None:
        rad_ang = np.deg2rad(deg_ang)
    elif rad_ang is None:
        raise ValueError("Either deg_ang or rad_ang must be provided.")
    
    c = np.cos(rad_ang)
    s = np.sin(rad_ang)
    
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]])

def RotMat_y(deg_ang=None, rad_ang=None):
    if deg_ang is not None:
        rad_ang = np.deg2rad(deg_ang)
    elif rad_ang is None:
        raise ValueError("Either deg_ang or rad_ang must be provided.")
    
    c = np.cos(rad_ang)
    s = np.sin(rad_ang)
    
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]])

def RotMat_z(deg_ang=None, rad_ang=None):
    if deg_ang is not None:
        rad_ang = np.deg2rad(deg_ang)
    elif rad_ang is None:
        raise ValueError("Either deg_ang or rad_ang must be provided.")
    
    c = np.cos(rad_ang)
    s = np.sin(rad_ang)
    
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]])