import numpy as np
from rot_utility import RotMat_x, RotMat_y, RotMat_z


class unitSpherePoint:
    id = -1  # Unique identifier for the point
    coords = np.array([np.NaN, np.NaN, np.NaN])  # Coordinates of the point on the unit sphere X Y Z
    neighbors = dict()  # neighbor on sphere : distance to neighbor
    max_neighbor_dist = np.Inf  # highest distance to a neighbor on the sphere
    num_passed = 0  # number of times this point has been passed by a gravity vector
    is_selected = False  # whether this point is selected by the gravity vector or not

    def __init__(self, x:float=np.NaN, y:float=np.NaN, z:float=np.NaN):
        self.coords = np.array([x, y, z])
        self.neighbors = dict()

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
    points = []  # list of unitSpherePoint instances
    neighbours_assigned = False  # whether neighbors have been assigned to the points or not

    def __init__(self, num_points:int=0):
        for _ in range(num_points):
            point = unitSpherePoint()
            point.create_new_point()
            point.id = len(self.points)
            self.points.append(point)
        self.neighbours_assigned = False

    def __repr__(self):
        return f"unitSphere with {len(self.points)} points"

    def assign_neighbors(self, neighbor_num:int=8):
        '''
        Assign neighbors to each point on the unit sphere based on a maximum distance.
        '''
        for i, point in enumerate(self.points):
            for j, other_point in enumerate(self.points):
                if i != j:
                    distance = point.distance_to(other_point)

                    # if not enough enigbors, just add them
                    nei_num = len(point.neighbors.keys())
                    if nei_num < neighbor_num:
                        point.neighbors[other_point] = distance
                        if (distance > point.max_neighbor_dist) or (nei_num == 0):
                            point.max_neighbor_dist = distance
                        continue

                    # check if its closer than the max distance to a neighbor
                    if distance < point.max_neighbor_dist:
                        # find the neighbor with the max distance and remove it
                        max_neighbor = max(point.neighbors, key=point.neighbors.get)
                        del point.neighbors[max_neighbor]
                        # add the new neighbor
                        point.neighbors[other_point] = distance
                        # udate the max distance to a neighbor
                        point.max_neighbor_dist = max(point.neighbors.values())

        self.neighbours_assigned = True

    

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
    sphere = unitSphere(num_points=100)
    sphere.assign_neighbors(neighbor_num=5)
    sphere.plot_pyplot()

def demo_plot_plotly():
    sphere = unitSphere(num_points=300)
    sphere.assign_neighbors(neighbor_num=5)
    sphere.plot_plotly()

if __name__ == "__main__":
    #demo_plot_pyplot()
    demo_plot_plotly()