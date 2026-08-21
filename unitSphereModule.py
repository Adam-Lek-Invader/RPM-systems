import numpy as np
import logging, time, sys

from sympy import true
from rot_utility import RotMat_x, RotMat_y, RotMat_z

logger = logging.getLogger(__name__)
class unitSpherePoint:
    id = -1  # Unique identifier for the point
    coords = np.array([np.NaN, np.NaN, np.NaN])  # Coordinates of the point on the unit sphere X Y Z
    #neighbours = dict()  # neighbour on sphere : distance to neighbour
    max_neighbour_dist = np.Inf  # highest distance to a neighbour on the sphere
    num_passed = 0  # number of times this point has been passed by a gravity vector

    def __init__(self, x:float=np.NaN, y:float=np.NaN, z:float=np.NaN):
        self.coords = np.array([x, y, z])
        self.neighbours = dict()

    def __repr__(self):
        return f"unitSpherePoint({self.coords[0]}, {self.coords[1]}, {self.coords[2]})"

    def to_tuple(self):
        return (self.coords[0], self.coords[1], self.coords[2])

    def is_inUnitSphere(self):
        return np.isclose(np.linalg.norm(self.coords), 1.0)

    def distance_to(self, other):
        if isinstance(other, unitSpherePoint):
            dx = self.coords[0] - other.coords[0]
            dy = self.coords[1] - other.coords[1]
            dz = self.coords[2] - other.coords[2]
        elif isinstance(other, (np.ndarray,list)):
            dx = self.coords[0] - other[0]
            dy = self.coords[1] - other[1]
            dz = self.coords[2] - other[2]
        else:
            raise TypeError("Distance can only be calculated between two unitSpherePoint, list or np.ndarray")
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def create_new_point(self):
        '''
        @@@ 
        '''
        # Generate random spherical coordinates
        a1,a2,a3 = np.random.uniform(0,2*np.pi,3)

        # rotate the point around the x-axis by a1, y-axis by a2, and z-axis by a3
        r0 = np.array([1,0,0], dtype=np.float32)
        r = RotMat_x(rad_ang=a1) @ RotMat_y(rad_ang=a2) @ RotMat_z(rad_ang=a3) @ r0

        # normalize to increase numerical stability
        r /= np.linalg.norm(r)

        self.coords = r
        return self.coords


class unitSphere:
    #points = []  # list of unitSpherePoint instances
    neighbours_assigned = False  # whether neighbours have been assigned to the points or not
    last_marked_point = None

    def __init__(self, n:int=0, method:str='random'):
        '''
        methods: 'random', 'polarCoordsSubdivision'
        '''
        self.points = []
        self.last_marked_point = None
        match method:
            case 'random':
                logger.info("Generating %d random points on the unit sphere",n)
                start_time = time.perf_counter()
                for _ in range(n):
                    point = unitSpherePoint()
                    point.create_new_point()
                    point.id = len(self.points)
                    self.points.append(point)
                time_passed = time.perf_counter() - start_time
                logger.info("Points generated in time: %.2f s",time_passed)
            case 'polarCoordsSubdivision':
                logger.info("Generating sphere using Polar Coordinates Subdivision with n=%d ",n)
                start_time = time.perf_counter()
                self.__PolarCoordsSubdivision(n)
                time_passed = time.perf_counter() - start_time
                logger.info("Points num: %d generated in time: %.2f s",len(self.points),time_passed)
            case default:
                raise ValueError(f"Unknown method: {method} | Available methods: 'random', 'polarCoordsSubdivision'")
        self.neighbours_assigned = False

    def __PolarCoordsSubdivision(self, n:int):
        '''
        Generate points on the unit sphere using polar coordinates subdivision.
        Distributing Points on the Sphere, I Ali Katanforoush and Mehrdad Shahshahani
        '''
        Lattitudes = [np.pi*j/(n) - np.pi/2 for j in range(1,n-1)]  # latitudes
        for lat in Lattitudes:
            n_points = int(0.5 + np.sqrt(3) * n * np.cos(lat))  # number of points at this latitude
            for k in range(n_points):
                lon = 2 * np.pi * k / n_points  # longitude
                x = np.cos(lat) * np.cos(lon)
                y = np.cos(lat) * np.sin(lon)
                z = np.sin(lat)
                point = unitSpherePoint(x, y, z)
                point.id = len(self.points)
                self.points.append(point)
        return self.points


    def __repr__(self):
        return f"unitSphere with {len(self.points)} points"

    def assign_neighbours(self, neighbour_num:int=8):
        '''
        Assign neighbours to each point on the unit sphere based on a maximum distance.
        '''
        logger.info("Starting Assigning %d neighbours", neighbour_num)
        start_time = time.perf_counter()
        for i, point in enumerate(self.points):
            for j, other_point in enumerate(self.points):
                if i != j:
                    distance = point.distance_to(other_point)

                    # if not enough enigbors, just add them
                    nei_num = len(point.neighbours.keys())
                    if nei_num < neighbour_num:
                        point.neighbours[other_point] = distance
                        if (distance > point.max_neighbour_dist) or (nei_num == 0):
                            point.max_neighbour_dist = distance
                        continue

                    # check if its closer than the max distance to a neighbour
                    if distance < point.max_neighbour_dist:
                        # find the neighbour with the max distance and remove it
                        max_neighbour = max(point.neighbours, key=point.neighbours.get)
                        del point.neighbours[max_neighbour]
                        # add the new neighbour
                        point.neighbours[other_point] = distance
                        # udate the max distance to a neighbour
                        point.max_neighbour_dist = max(point.neighbours.values())

        self.neighbours_assigned = True
        time_passed = time.perf_counter() - start_time
        logger.info("Assigning completed in time: %.2f s",time_passed)

    def find_closest(self, vec_xyz:np.ndarray)->dict:
        min_dist = np.Inf
        min_id = -1
        unitSpherePointInstance = None
        for point in self.points:
            cur_dist = point.distance_to(vec_xyz)
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_id = point.id
                unitSpherePointInstance = point
        return {"min_dist":min_dist, "point_id":min_id, "point_ref":unitSpherePointInstance}

    def mark_trajectory(self, data_xyz:np.ndarray)->int:
        # check whether neighbours are assigned
        if self.neighbours_assigned == False:
            raise ValueError("Neighbours are not assigned")

        # Find where to start
        if self.last_marked_point is None:
            found = self.find_closest(data_xyz[0,:])
            self.last_marked_point = found["point_ref"]
            self.last_marked_point.num_passed += 1
        else:
            # check wheter new data points really continue from previous last marked point
            dist_cur = self.last_marked_point.distance_to(data_xyz[0,:])
            dist_nei = self.last_marked_point.max_neighbour_dist
            nei_closest = list( self.last_marked_point.neighbours.keys() )[0]
            is_continuing = True
            while True:
                for nei in list( self.last_marked_point.neighbours.keys() ):
                    dist = nei.distance_to(data_xyz[0,:])
                    if dist < dist_nei:
                        nei_closest = nei
                        dist_nei = dist
                if dist_nei < dist_cur:
                    is_continuing = False
                    # update cur point
                    self.last_marked_point = nei_closest
                    dist_cur = dist_nei
                    # update cur point neighbours default vals
                    dist_nei = self.last_marked_point.max_neighbour_dist
                    nei_closest = list( self.last_marked_point.neighbours.keys() )[0]
                else:
                    if is_continuing == False:
                        self.last_marked_point.num_passed += 1
                    break

        # pass all data points
        nei_skips = 0
        for i,data_point in enumerate( data_xyz[1:,:] ):
            dist_cur = self.last_marked_point.distance_to(data_point)
            dist_nei = self.last_marked_point.max_neighbour_dist
            nei_closest = list( self.last_marked_point.neighbours.keys() )[0]
            first_neighbourhood = True
            while True:
                for nei in list( self.last_marked_point.neighbours.keys() ):
                    dist = nei.distance_to(data_point)
                    if dist < dist_nei:
                        nei_closest = nei
                        dist_nei = dist
                if dist_nei < dist_cur:
                    # is first check neighbourhood to check nei skips
                    if first_neighbourhood == False:
                        nei_skips += 1
                    first_neighbourhood = False
                    # update cur point to closest (relative to data point) nei
                    self.last_marked_point = nei_closest
                    dist_cur = dist_nei
                    self.last_marked_point.num_passed += 1
                    # update cur point neighbours default vals
                    dist_nei = self.last_marked_point.max_neighbour_dist
                    nei_closest = list( self.last_marked_point.neighbours.keys() )[0]
                else:
                    break
        return nei_skips           
                
                    


    def plot_plotly(self):
        '''
        Plot the unit sphere and its points using plotly.
        '''
        import plotly.graph_objects as go

        max_passings = max(point.num_passed for point in self.points)

        xs = [point.coords[0] for point in self.points]
        ys = [point.coords[1] for point in self.points]
        zs = [point.coords[2] for point in self.points]
        colors = [point.num_passed for point in self.points]

        fig = go.Figure(data=[go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode='markers',
            marker=dict(
                size=4,
                color=colors,
                colorscale='Viridis',
                cmin=0,
                cmax=max_passings,
                colorbar=dict(title='num_passed'),
            )
        )])

        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='cube'  # keeps the sphere looking spherical
            )
        )

        fig.show()

    def plot_pyplot(self):
        '''
        Plot the unit sphere and its points using matplotlib.
        '''
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # find point with max number of passings
        max_passings = max(point.num_passed for point in self.points)

        # Plot the points on the unit sphere
        for point in self.points:
            point.num_passed
            ax.scatter(point.coords[0], point.coords[1], point.coords[2], 
                       c=point.num_passed, vmin=0, vmax=max_passings, cmap='viridis')


        plt.show()

def demo_plot_pyplot():
    sphere = unitSphere(n=100)
    sphere.assign_neighbours(neighbour_num=5)
    sphere.plot_pyplot()

def demo_plot_plotly():
    sphere = unitSphere(n=50, method='polarCoordsSubdivision')
    sphere.assign_neighbours(neighbour_num=5)
    sphere.plot_plotly()

if __name__ == "__main__":
    #Logger
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )


    #demo_plot_pyplot()
    demo_plot_plotly()