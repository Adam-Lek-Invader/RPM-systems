import pytest

import numpy as np
from unitSphereModule import unitSpherePoint, unitSphere

class TestUnitSpherePoint_basic:
    def test_point_initialization(self):
        point = unitSpherePoint()
        assert np.all(np.isnan(point.coords))
        assert point.is_inUnitSphere() == False
        assert point.num_passed == 0
        assert point.is_selected == False
        assert point.max_neighbor_dist == np.Inf
        assert point.neighbors == {}

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

    def test_neigbours(self):
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)

        # reference check
        point1.neighbors[point2] = 1.0
        point2.id = 7
        assert list(point1.neighbors.keys())[0].id == 7

        # uniqness check
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(0, 0, 1)
        point5 = unitSpherePoint(0, 0, 1)
        point1.neighbors[point3] = 1.0
        point1.neighbors[point4] = 1.0
        nei_list = list(point1.neighbors.keys())
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

        # dict of neighbors should be unique to each instance
        point1.neighbors[point2] = 1.0
        assert len(point1.neighbors) == 1
        assert len(point2.neighbors) == 0
        assert len(point3.neighbors) == 0

        # coords should be unique to each instance
        assert np.all(point1.coords) == np.all(np.array([1, 0, 0]))
        assert np.all(point2.coords) == np.all(np.array([0, 1, 0]))
        assert np.all(point3.coords) == np.all(np.array([0, 0, 1]))

class TestUnitSphere_basic:
    def test_initialization(self):
        sphere = unitSphere(num_points=100)
        assert len(sphere.points) == 100
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

    def test_assign_neighbors(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(1, 1, 0)
        point5 = unitSpherePoint(1, 0, 1)
        sphere = unitSphere(num_points=0)
        sphere.points = [point1, point2, point3, point4, point5]
        sphere.assign_neighbors(neighbor_num=2)

        assert sphere.neighbours_assigned == True
        point1_neighbors = list(point1.neighbors.keys())
        assert point4 in point1_neighbors
        assert point5 in point1_neighbors
        assert point1.neighbors[point4] == 1.0
        assert point1.neighbors[point5] == 1.0
        assert point1.max_neighbor_dist == 1.0

        for point in sphere.points:
            assert len(point.neighbors) == 2
            for neighbor, distance in point.neighbors.items():
                assert isinstance(neighbor, unitSpherePoint)
                assert distance > 0

        # random
        sphere = unitSphere(num_points=20)
        sphere.assign_neighbors(neighbor_num=5)
        assert sphere.neighbours_assigned == True
        for point in sphere.points:
            assert len(point.neighbors) == 5
            max_dist = 0.0
            for neighbor, distance in point.neighbors.items():
                if distance > max_dist:
                    max_dist = distance
                assert isinstance(neighbor, unitSpherePoint)
                assert distance > 0
            assert max_dist == point.max_neighbor_dist

