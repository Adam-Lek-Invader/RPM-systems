import pytest

import numpy as np
from unitSphereModule import unitSpherePoint, unitSphere

def make_simple_sphere()->unitSphere:
    sphere = unitSphere(n=6)
    sphere.points[0].coords = np.array([1,0,0])
    sphere.points[1].coords = np.array([-1,0,0])
    sphere.points[2].coords = np.array([0,1,0])
    sphere.points[3].coords = np.array([0,-1,0])
    sphere.points[4].coords = np.array([0,0,1])
    sphere.points[5].coords = np.array([0,0,-1])
    return sphere
class TestUnitSpherePoint_basic:
    def test_point_initialization(self):
        point = unitSpherePoint()
        assert np.all(np.isnan(point.coords))
        assert point.is_inUnitSphere() == False
        assert point.num_passed == 0
        assert point.max_neighbour_dist == np.Inf
        assert point.neighbours == {}

    def test_is_in_unit_sphere(self):
        # manual
        point = unitSpherePoint(1, 0, 0)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(0, 1, 0)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(0, 0, 1)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(1, 1, 1)
        assert point.is_inUnitSphere() == False

        # random
        for _ in range(50):
            x,y,z = np.random.normal(0, 1, 3)
            mag = np.sqrt(x**2 + y**2 + z**2)
            x,y,z = x/mag, y/mag, z/mag  # normalize to unit sphere
            point = unitSpherePoint(x, y, z)
            assert point.is_inUnitSphere() == True

        for _ in range(50):
            x,y,z = np.random.normal(0, 1, 3)
            mag = np.sqrt(x**2 + y**2 + z**2)
            x,y,z = x/mag, y/mag, z/mag  # normalize to unit sphere
            pert_x,pert_y,pert_z = np.random.normal(0, 1, 3)  # perturb the point
            x += pert_x
            y += pert_y
            z += pert_z
            mag = np.sqrt(x**2 + y**2 + z**2)
            if mag == 1:
                continue  # skip if it accidentally ends up on the unit sphere
            point = unitSpherePoint(x, y, z)
            assert point.is_inUnitSphere() == False

    def test_point_creation(self):
        point = unitSpherePoint()
        for _ in range(50):
            point.create_new_point()
            assert point.is_inUnitSphere() == True

    def test_distance_to(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(2, 0, 0)
        distance = point1.distance_to(point2)
        assert np.isclose(distance, 1.0)

        point3 = unitSpherePoint(0, 0, 1)
        distance = point1.distance_to(point3)
        assert np.isclose(distance, np.sqrt(2.0))

        point4 = unitSpherePoint(0, 1, 1)
        distance = point1.distance_to(point4)
        assert np.isclose(distance, np.sqrt(3.0))

        for _ in range(50):
            point2.create_new_point()
            distance = point1.distance_to(point2)
            expected_distance = np.linalg.norm(point1.coords - point2.coords)
            assert np.isclose(distance, expected_distance)

        # other types of data
        point2 = np.array([1,0,0])
        point3 = np.array([2,0,0])
        assert np.isclose(point1.distance_to(point2), 0.0)
        assert np.isclose(point1.distance_to(point3), 1.0)

        point2 = [1,0,0]
        point3 = [2,0,0]
        assert np.isclose(point1.distance_to(point2), 0.0)
        assert np.isclose(point1.distance_to(point3), 1.0)

        

    def test_neigbours(self):
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)

        # reference check
        point1.neighbours[point2] = 1.0
        point2.id = 7
        assert list(point1.neighbours.keys())[0].id == 7

        # uniqness check
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(0, 0, 1)
        point5 = unitSpherePoint(0, 0, 1)
        point1.neighbours[point3] = 1.0
        point1.neighbours[point4] = 1.0
        nei_list = list(point1.neighbours.keys())
        assert point5 not in nei_list
        for nei in nei_list:
            how_many_same = 0
            for other_nei in nei_list:
                if nei == other_nei:
                    how_many_same += 1
            assert how_many_same == 1

    def test_mutables_not_shared_between_instances(self):
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)

        # dict of neighbours should be unique to each instance
        point1.neighbours[point2] = 1.0
        assert len(point1.neighbours) == 1
        assert len(point2.neighbours) == 0
        assert len(point3.neighbours) == 0

        # coords should be unique to each instance
        assert np.all(point1.coords) == np.all(np.array([1, 0, 0]))
        assert np.all(point2.coords) == np.all(np.array([0, 1, 0]))
        assert np.all(point3.coords) == np.all(np.array([0, 0, 1]))

class TestUnitSphere_basic:
    def test_initialization(self):
        # random sampling
        sphere = unitSphere(n=100)
        assert len(sphere.points) == 100
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

        # Polar Coordinates Subdivision
        sphere = unitSphere(n=30, method="polarCoordsSubdivision")
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

    def test_find_closest(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(1, 1, 0)
        point5 = unitSpherePoint(1, 0, 1)
        sphere = unitSphere(n=0)
        sphere.points = [point1,point2,point3,point4,point5]
        test_point = unitSpherePoint(1.1, 0.9, 0)
        assert sphere.find_closest(test_point)["point_ref"] == point4

    def test_assign_neighbours(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(1, 1, 0)
        point5 = unitSpherePoint(1, 0, 1)
        sphere = unitSphere(n=0)
        sphere.points = [point1, point2, point3, point4, point5]
        sphere.assign_neighbours(neighbour_num=2)

        assert sphere.neighbours_assigned == True
        point1_neighbours = list(point1.neighbours.keys())
        assert point4 in point1_neighbours
        assert point5 in point1_neighbours
        assert point1.neighbours[point4] == 1.0
        assert point1.neighbours[point5] == 1.0
        assert point1.max_neighbour_dist == 1.0

        for point in sphere.points:
            assert len(point.neighbours) == 2
            for neighbour, distance in point.neighbours.items():
                assert isinstance(neighbour, unitSpherePoint)
                assert distance > 0

        sphere = make_simple_sphere()
        sphere.assign_neighbours(4)
        for p in sphere.points:
            not_nei = -p.coords
            not_nei = sphere.find_closest(not_nei)
            not_nei = not_nei["point_ref"]
            for other_p in sphere.points:
                if p == other_p:
                    continue
                if other_p == not_nei:
                    assert other_p not in list(p.neighbours.keys())
                else:
                    assert other_p in list(p.neighbours.keys())

        # random
        sphere = unitSphere(n=20)
        sphere.assign_neighbours(neighbour_num=5)
        assert sphere.neighbours_assigned == True
        for point in sphere.points:
            assert len(point.neighbours) == 5
            max_dist = 0.0
            for neighbour, distance in point.neighbours.items():
                if distance > max_dist:
                    max_dist = distance
                assert isinstance(neighbour, unitSpherePoint)
                assert distance > 0
            assert max_dist == point.max_neighbour_dist

    def test_mark_traj_same_point(self):
        sphere = make_simple_sphere()
        with pytest.raises(ValueError) : sphere.mark_trajectory(np.array([[1,0,0]])) 

        # staying in the same point
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1,0,0],[1.1, 0.1, 0], [0.9, 0.2, 0]])
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 0
        closest = sphere.find_closest([1,0,0])
        for p in sphere.points:
            if p == closest["point_ref"]:
                assert p.num_passed == 1
                assert p == sphere.last_marked_point
            else:
                assert p.num_passed == 0

    def test_make_traj_next_nei(self):
        # marking traj for next neigbours
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1.1,-0.1,0.2],[0.1, 1.1, 0], [0, -0.2, 0.9]])
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 0

        closest_list = []
        for data in data_xyz:
            closest = sphere.find_closest(data)
            closest_list.append(closest["point_ref"])

        for p in sphere.points:
            if p in closest_list:
                assert p.num_passed == 1
                if p == sphere.find_closest(data_xyz[-1])["point_ref"]:
                    assert p == sphere.last_marked_point
            else:
                assert p.num_passed == 0


    def test_make_traj_further_than_nei(self):
        # interpolate and go into circle
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1.1,-0.1,0.2],[-1, 0.1, 0], [1.1, 0, -0.2]])
        points_to_be_marked = [[1,0,0],[0,1,0],[-1,0,0],[0,0,-1]]
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 2

        passed_points = []
        for data_p in points_to_be_marked:
            closest = sphere.find_closest(data_p)
            passed_points.append( closest["point_ref"] )

        for p in sphere.points:
            if p in passed_points:
                assert p.num_passed >= 1
                if p == sphere.find_closest(data_xyz[-1])["point_ref"]:
                    assert p == sphere.last_marked_point
                    assert p.num_passed == 2
                else:
                    assert p.num_passed == 1
            else:
                assert p.num_passed == 0

