from random import randint
import numpy as np


class unitSpherePoint:
    id = -1  # Unique identifier for the point
    coords = np.array([np.NaN, np.NaN, np.NaN])  # Coordinates of the point on the unit sphere X Y Z
    neighbors = dict()  # neighbor on sphere : distance to neighbor
    max_neighbor_dist = np.Inf  # highest distance to a neighbor on the sphere
    num_passed = 0  # number of times this point has been passed by a gravity vector
    is_selected = False  # whether this point is selected by the gravity vector or not

    def __init__(self, x:float=np.NaN, y:float=np.NaN, z:float=np.NaN):
        self.coords = np.array([x, y, z])

    def __repr__(self):
        return f"unitSpherePoint({self.coords[0]}, {self.coords[1]}, {self.coords[2]})"

    def to_tuple(self):
        return (self.coords[0], self.coords[1], self.coords[2])

    def is_inUnitSphere(self):
        return np.isclose(np.linalg.norm(self.coords), 1.0)

    def distance_to(self, other):
        if not isinstance(other, unitSpherePoint):
            raise TypeError("Distance can only be calculated between two unitSpherePoint instances")
        dx = self.coords[0] - other.coords[0]
        dy = self.coords[1] - other.coords[1]
        dz = self.coords[2] - other.coords[2]
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def create_new_point(self):
        '''
        Create a new point on the unit sphere using random coordinates.
        x^2 + y^2 + z^2 = r^2 = 1
        '''
        # Generate random coordinates from a normal distribution
        mag = 2.0
        while mag > 1.0:
            x = np.random.normal(0, 1)
            y = np.random.normal(0, 1)
            mag = np.sqrt(x**2 + y**2)        
        z = randint(0, 1)   # wheter z is negative or positive
        if z == 0:
            z = -1

        # find the z coordinate to ensure the point lies on the unit sphere
        z = np.sqrt(1 - x**2 - y**2) * z

        self.coords = np.array([x, y, z])
        return self.coords

        

