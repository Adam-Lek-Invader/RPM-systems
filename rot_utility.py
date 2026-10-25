import numpy as np

class taSMG_iterative:
    '''
    for use with timed data for iterative work to conserve space in long amounts of data
    '''
    def __init__(self, floatType=np.float64):
        self.T = floatType(0.0)
        self.g_xyz_cum = np.zeros(shape=(3), dtype=floatType)
        self.floatType = floatType

    def next_sample(self, g_xyz_new:np.ndarray, dt:float):
        dt = self.floatType(dt)
        g_xyz = (self.g_xyz_cum * self.T) + (dt*g_xyz_new).astype(self.floatType)
        self.T += dt 
        self.g_xyz_cum = g_xyz / self.T

    def get_taSMG(self)->float:
        return np.linalg.norm( self.g_xyz_cum )

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